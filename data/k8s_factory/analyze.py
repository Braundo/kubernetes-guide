import json
import os
import re
import logging
from datetime import datetime, timezone

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

BASE_SCORES = {
    "security": 72,
    "releases": 64,
    "tool-radar": 60,
    "ecosystem": 56,
}

CATEGORY_ORDER = ["security", "releases", "tool-radar", "ecosystem"]


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


def canonical_title(title):
    cleaned = re.sub(r"[^a-z0-9\s]", " ", (title or "").lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    tokens = [t for t in cleaned.split() if len(t) > 2]
    return " ".join(tokens)


def titles_too_similar(a, b):
    aa = set(canonical_title(a).split())
    bb = set(canonical_title(b).split())
    if not aa or not bb:
        return False
    overlap = len(aa & bb)
    return overlap >= max(4, int(0.7 * min(len(aa), len(bb))))


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
    seen_titles = []

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
            if any(titles_too_similar(candidate.get("title", ""), t) for t in [x.get("title", "") for x in top]):
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
            if any(titles_too_similar(title, seen) for seen in seen_titles):
                continue
            selected.append(item)
            seen_titles.append(title)
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

    plan = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_mix": CATEGORY_TARGET_SHARE,
        "total_candidates": len(items),
        "total_selected": len(selected),
        "items": selected,
    }

    with open(PLAN, "w") as handle:
        json.dump(plan, handle, indent=2, default=str)

    log.info(f"Plan: selected {len(selected)} from {len(items)} candidates")
    return plan


if __name__ == "__main__":
    generate_plan()
