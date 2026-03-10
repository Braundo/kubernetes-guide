import json
import os
import re
import logging
from datetime import datetime, timezone
from urllib.parse import urlparse

from db import get_db, get_unprocessed_items
from content_policy import (
    CATEGORY_CONFIG,
    CATEGORY_TARGET_SHARE,
    RUN_CAPS,
    DAILY_CAPS,
    WEEKLY_CAPS,
    QUALITY_THRESHOLDS,
    MAX_ITEMS_PER_RUN,
    MAX_SOURCE_AGE_DAYS,
    ENFORCE_DISCOVERY_FREQUENCY_CAPS,
    DOMAIN_SCORE_BOOSTS,
    get_domain,
    count_recent_files,
    now_local,
    parse_datetime,
    infer_category,
    source_default_category,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("analyze")

PLAN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plan.json")
REVIEW_SHORTLIST_LIMIT = int(os.environ.get("PIPELINE_REVIEW_SHORTLIST_LIMIT", "20"))
REVIEW_MAX_PER_CATEGORY = int(os.environ.get("PIPELINE_REVIEW_MAX_PER_CATEGORY", "8"))

BASE_SCORES = {
    "security": 72,
    "releases": 64,
    "tool-radar": 60,
    "ecosystem": 56,
}

CATEGORY_ORDER = ["security", "releases", "tool-radar", "ecosystem"]
GENERIC_TITLE_TOKENS = {
    "tool",
    "radar",
    "news",
    "update",
    "updates",
    "briefing",
    "deep",
    "dive",
    "spotlight",
}


def source_age_days(item):
    now = now_local()
    category = item.get("category_hint", "ecosystem")
    if category == "tool-radar":
        raw = item.get("last_pushed") or item.get("published")
    else:
        raw = item.get("published")

    dt = parse_datetime(raw)
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt_local = dt.astimezone(now.tzinfo)
    return (now.date() - dt_local.date()).days


def is_item_fresh(item):
    age = source_age_days(item)
    if age is None:
        return False
    if age < 0:
        return False
    max_age = MAX_SOURCE_AGE_DAYS.get(item.get("category_hint", "ecosystem"), 30)
    return age <= max_age


def canonical_tokens(title):
    cleaned = re.sub(r"[^a-z0-9\s]", " ", (title or "").lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return [
        t
        for t in cleaned.split()
        if len(t) > 1 and t not in GENERIC_TITLE_TOKENS
    ]


def canonical_title(title):
    return " ".join(canonical_tokens(title))


def github_repo_slug(url):
    try:
        parsed = urlparse(url or "")
    except Exception:
        return ""
    if parsed.netloc.lower() != "github.com":
        return ""
    parts = [segment for segment in (parsed.path or "").split("/") if segment]
    if len(parts) < 2:
        return ""
    return f"{parts[0].lower()}/{parts[1].lower()}"


def titles_too_similar(a, b, url_a="", url_b=""):
    repo_a = github_repo_slug(url_a)
    repo_b = github_repo_slug(url_b)
    if repo_a and repo_b and repo_a == repo_b:
        return True

    aa = set(canonical_tokens(a))
    bb = set(canonical_tokens(b))
    if not aa or not bb:
        return False
    if aa == bb:
        return True

    smaller = min(len(aa), len(bb))
    overlap = len(aa & bb)
    if smaller <= 2:
        return overlap >= smaller
    if smaller <= 4:
        return overlap >= (smaller - 1)
    return overlap >= max(4, int(0.7 * smaller))


def shortlist_topic_key(item):
    category = item.get("category_hint", "ecosystem")
    repo = github_repo_slug(item.get("url", ""))
    if repo:
        return f"{category}:repo:{repo}"
    title_key = canonical_title(item.get("title", ""))
    return f"{category}:title:{title_key}"


def score_item(item):
    cat = item.get("category_hint", "ecosystem")
    title = (item.get("title") or "").lower()
    summary = (item.get("summary") or "").lower()
    domain = get_domain(item.get("url", ""))

    score = BASE_SCORES.get(cat, 50)
    score += DOMAIN_SCORE_BOOSTS.get(domain, 0)

    if cat == "security" and re.search(r"\bcve-\d{4}-\d+\b", title):
        score += 12
    if cat == "releases" and re.search(r"\bv\d+\.\d+\b", title):
        score += 8
    if cat == "releases" and "kubernetes" in title:
        score += 6
    if cat == "tool-radar":
        stars = int(item.get("stars", 0) or 0)
        score += min(stars // 100, 12)
    if "kubecon" in title and cat == "ecosystem":
        score -= 8
    if "announcement" in title and cat == "ecosystem":
        score -= 4

    if len(summary) > 250:
        score += 5
    elif len(summary) < 80:
        score -= 8

    age = source_age_days(item)
    if age is None:
        score -= 20
    elif age < 0:
        score = 0
    else:
        if age <= 2:
            score += 10
        elif age <= 7:
            score += 6
        elif age <= 14:
            score += 3
        elif age <= 30:
            score += 1
        else:
            score -= 15

        max_age = MAX_SOURCE_AGE_DAYS.get(cat, 30)
        if age > max_age:
            score = 0

    return max(0, min(score, 100))


def passes_frequency_guardrails(category):
    if not ENFORCE_DISCOVERY_FREQUENCY_CAPS:
        return True

    daily_cap = DAILY_CAPS.get(category, 1)
    weekly_cap = WEEKLY_CAPS.get(category, 5)

    if count_recent_files(category, days=1) >= daily_cap:
        return False
    if count_recent_files(category, days=7) >= weekly_cap:
        return False
    return True


def select_by_category(items):
    selected = []
    seen_topics = []

    by_cat = {k: [] for k in CATEGORY_CONFIG.keys()}
    for item in items:
        if not is_item_fresh(item):
            continue
        by_cat.setdefault(item.get("category_hint", "ecosystem"), []).append(item)

    # Curate ecosystem into one roundup candidate with 3-7 sources.
    eco_candidates = by_cat.get("ecosystem", [])
    curated_eco = None
    if eco_candidates and passes_frequency_guardrails("ecosystem"):
        top = []
        for candidate in eco_candidates:
            if candidate["score"] < QUALITY_THRESHOLDS["ecosystem"]:
                continue
            if any(
                titles_too_similar(
                    candidate.get("title", ""),
                    existing.get("title", ""),
                    candidate.get("url", ""),
                    existing.get("url", ""),
                )
                for existing in top
            ):
                continue
            top.append(candidate)
            if len(top) == 7:
                break
        if len(top) >= 3:
            now = now_local()
            curated_eco = {
                "id": None,
                "title": "Kubernetes Ecosystem Briefing",
                "summary": (
                    "High-signal ecosystem developments and why they matter for "
                    "platform engineering teams."
                ),
                "published": now.isoformat(),
                "source_name": "Curated Ecosystem Feed",
                "category_hint": "ecosystem",
                "url": top[0].get("url", ""),
                "content_hash": f"ecosystem-roundup-{now.strftime('%Y%m%d')}",
                "sources": [
                    {
                        "title": src.get("title", ""),
                        "url": src.get("url", ""),
                        "source_name": src.get("source_name", ""),
                        "published": src.get("published", ""),
                    }
                    for src in top[:7]
                ],
                "source_item_ids": [src.get("id") for src in top[:7] if src.get("id")],
                "score": max(src.get("score", 0) for src in top),
            }

    for category in CATEGORY_ORDER:
        if category == "ecosystem":
            if curated_eco:
                selected.append(curated_eco)
            continue

        if not passes_frequency_guardrails(category):
            continue

        cap = RUN_CAPS.get(category, 1)
        threshold = QUALITY_THRESHOLDS.get(category, 60)

        chosen = 0
        for item in by_cat.get(category, []):
            if chosen >= cap:
                break
            if item["score"] < threshold:
                continue
            title = item.get("title", "")
            if any(
                titles_too_similar(
                    title,
                    seen.get("title", ""),
                    item.get("url", ""),
                    seen.get("url", ""),
                )
                for seen in seen_topics
            ):
                continue
            selected.append(item)
            seen_topics.append({"title": title, "url": item.get("url", "")})
            chosen += 1

    # Enforce global cap while preserving category order and score.
    selected.sort(
        key=lambda x: (
            CATEGORY_ORDER.index(x.get("category_hint", "ecosystem"))
            if x.get("category_hint", "ecosystem") in CATEGORY_ORDER
            else 99,
            -x.get("score", 0),
        )
    )
    selected = selected[:MAX_ITEMS_PER_RUN]
    return selected


def _item_key(item):
    item_id = item.get("id")
    if item_id:
        return f"id:{item_id}"
    content_hash = item.get("content_hash")
    if content_hash:
        return f"hash:{content_hash}"
    return f"title:{canonical_title(item.get('title', ''))}"


def build_review_shortlist(items, recommended):
    recommended_keys = {_item_key(item) for item in recommended}
    shortlisted = []
    seen = set()
    seen_topics = set()

    category_order = ["security", "releases", "ecosystem", "tool-radar"]
    per_category = {cat: [] for cat in category_order}
    category_counts = {cat: 0 for cat in category_order}

    for item in sorted(items, key=lambda x: x.get("score", 0), reverse=True):
        if not is_item_fresh(item):
            continue

        key = _item_key(item)
        if key in seen:
            continue
        seen.add(key)

        copy = dict(item)
        copy["recommended"] = key in recommended_keys
        topic_key = shortlist_topic_key(copy)
        if topic_key in seen_topics:
            continue
        seen_topics.add(topic_key)
        cat = copy.get("category_hint", "ecosystem")
        if cat not in per_category:
            cat = "ecosystem"
        per_category[cat].append(copy)

    limit = max(1, REVIEW_SHORTLIST_LIMIT)
    while len(shortlisted) < limit:
        progressed = False
        for cat in category_order:
            if len(shortlisted) >= limit:
                break
            if category_counts[cat] >= max(1, REVIEW_MAX_PER_CATEGORY):
                continue
            if not per_category[cat]:
                continue
            shortlisted.append(per_category[cat].pop(0))
            category_counts[cat] += 1
            progressed = True
        if not progressed:
            break

    return shortlisted


def generate_plan():
    db = get_db()
    items = get_unprocessed_items(db)
    db.close()

    if not items:
        log.info("Nothing to plan.")
        plan = {"generated_at": datetime.now(timezone.utc).isoformat(), "items": []}
        with open(PLAN, "w") as handle:
            json.dump(plan, handle, indent=2)
        return plan

    for item in items:
        original = item.get("category_hint", "ecosystem")
        default = source_default_category(item.get("source_name", ""), original)
        inferred = infer_category(
            title=item.get("title", ""),
            summary=item.get("summary", ""),
            default=default,
            url=item.get("url", ""),
        )
        if inferred != original:
            log.info(
                "Reclassified plan candidate: %s -> %s | %s",
                original,
                inferred,
                item.get("title", "")[:90],
            )
        item["category_hint"] = inferred
        item["score"] = score_item(item)

    items.sort(key=lambda x: x["score"], reverse=True)
    selected = select_by_category(items)
    review_items = build_review_shortlist(items, selected)
    recommended_ids = {_item_key(item) for item in selected}
    recommended_in_review = sum(1 for item in review_items if _item_key(item) in recommended_ids)

    plan = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_mix": CATEGORY_TARGET_SHARE,
        "total_candidates": len(items),
        "total_selected": len(selected),
        "total_review_items": len(review_items),
        "recommended_in_review": recommended_in_review,
        "items": selected,
        "review_items": review_items,
    }

    with open(PLAN, "w") as handle:
        json.dump(plan, handle, indent=2, default=str)

    log.info(f"Plan: selected {len(selected)} from {len(items)} candidates")
    return plan


if __name__ == "__main__":
    generate_plan()
