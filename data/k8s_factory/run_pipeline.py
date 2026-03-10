#!/usr/bin/env python3
import json
import atexit
import os
import sys
import logging
import traceback
import subprocess
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import get_db, log_run_start, log_run_end, mark_processed
from crawler import run_crawl
from analyze import generate_plan
from generate import run_generate, update_index
from content_policy import CATEGORY_CONFIG
from editorial_quality import required_sections_for, assess_markdown_quality
from topic_requests import add_request as add_topic_request, pending_requests, resolve_requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), "run.log")),
    ],
)
log = logging.getLogger("pipeline")
PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(PIPELINE_DIR, "..", ".."))
REVIEW_STATE_PATH = os.path.join(PIPELINE_DIR, "review_state.json")
REVIEW_MD_PATH = os.path.join(PIPELINE_DIR, "review_topics.md")
RUN_LOCK_PATH = os.path.join(PIPELINE_DIR, ".run_pipeline.lock")
RUN_LOCK_STALE_SECONDS = int(os.environ.get("PIPELINE_LOCK_STALE_SECONDS", str(6 * 3600)))
MAX_GENERATE_PER_RUN = int(os.environ.get("PIPELINE_MAX_GENERATE_PER_RUN", "1"))
QUALITY_VERIFY_WINDOW_DAYS = int(os.environ.get("PIPELINE_VERIFY_QUALITY_WINDOW_DAYS", "0"))
TOPIC_TOKEN_STOP_WORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "into",
    "about",
    "this",
    "that",
    "tool",
    "radar",
    "news",
    "update",
    "updates",
    "briefing",
    "deep",
    "dive",
    "kubernetes",
}


def parse_option_value(argv, flag):
    for idx, arg in enumerate(argv):
        if arg == flag:
            if idx + 1 >= len(argv):
                raise ValueError(f"{flag} requires a value")
            return argv[idx + 1]
        if arg.startswith(f"{flag}="):
            return arg.split("=", 1)[1]
    return None


def parse_option_values(argv, flag):
    values = []
    idx = 0
    while idx < len(argv):
        arg = argv[idx]
        if arg == flag:
            if idx + 1 >= len(argv):
                raise ValueError(f"{flag} requires a value")
            values.append(argv[idx + 1])
            idx += 2
            continue
        if arg.startswith(f"{flag}="):
            values.append(arg.split("=", 1)[1])
        idx += 1
    return values


def _is_stale_lock(path):
    try:
        age = int(datetime.now(timezone.utc).timestamp() - os.path.getmtime(path))
        return age > RUN_LOCK_STALE_SECONDS
    except OSError:
        return False


def acquire_run_lock():
    if os.path.exists(RUN_LOCK_PATH) and _is_stale_lock(RUN_LOCK_PATH):
        try:
            os.remove(RUN_LOCK_PATH)
            log.warning("Removed stale pipeline lock file.")
        except OSError:
            pass

    try:
        fd = os.open(RUN_LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(fd, "w") as handle:
            handle.write(f"pid={os.getpid()} started={datetime.now(timezone.utc).isoformat()}\n")
        return True
    except FileExistsError:
        return False


def release_run_lock():
    try:
        if os.path.exists(RUN_LOCK_PATH):
            os.remove(RUN_LOCK_PATH)
    except OSError:
        pass


def category_from_path(path):
    normalized = path.replace("\\", "/")
    for category in CATEGORY_CONFIG.keys():
        marker = f"/news/{category}/"
        if marker in normalized:
            return category
    return None


def _canonical_topic_tokens(text):
    cleaned = re.sub(r"[^a-z0-9\s]", " ", (text or "").lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return [
        token
        for token in cleaned.split()
        if len(token) > 1 and token not in TOPIC_TOKEN_STOP_WORDS
    ]


def _github_repo_slug(url):
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


def topic_key(item):
    category = item.get("category_hint", "ecosystem")
    repo = _github_repo_slug(item.get("url", ""))
    if repo:
        return f"{category}:repo:{repo}"

    cve_match = re.search(r"(?i)\b(cve-\d{4}-\d+)\b", item.get("title", "") or "")
    if cve_match:
        return f"{category}:{cve_match.group(1).lower()}"

    title_tokens = _canonical_topic_tokens(item.get("title", ""))
    if title_tokens:
        return f"{category}:title:{' '.join(title_tokens[:10])}"
    return f"{category}:url:{(item.get('url', '') or '').lower()}"


def sync_news_indexes():
    for category in CATEGORY_CONFIG.keys():
        try:
            update_index(category)
        except Exception as exc:
            log.warning("Index sync skipped for category %s: %s", category, exc)


def dedupe_items_by_topic(items):
    kept = []
    dropped = []
    seen = set()
    ranked = sorted(items or [], key=lambda it: it.get("score", 0), reverse=True)
    for item in ranked:
        key = topic_key(item)
        if key in seen:
            dropped.append(item)
            continue
        seen.add(key)
        kept.append(item)
    return kept, dropped


def _topic_tokens_for_match(text):
    tokens = _canonical_topic_tokens(text)
    return [token for token in tokens if len(token) >= 3][:10]


def _match_score(topic_tokens, item):
    hay = " ".join(
        [
            item.get("title", ""),
            item.get("summary", ""),
            item.get("url", ""),
            item.get("source_name", ""),
        ]
    ).lower()
    if not topic_tokens:
        return 0
    return sum(1 for token in topic_tokens if token in hay)


def _collect_topic_supporting_sources(topic_entry, review_items, max_sources=6):
    direct = []
    for url in topic_entry.get("sources") or []:
        direct.append(
            {
                "title": url,
                "url": url,
                "source_name": "User Provided Source",
                "published": "",
            }
        )

    tokens = _topic_tokens_for_match(topic_entry.get("topic", ""))
    candidates = []
    for item in review_items or []:
        score = _match_score(tokens, item)
        if score <= 0:
            continue
        candidates.append((score, item.get("score", 0), item))
    candidates.sort(reverse=True, key=lambda row: (row[0], row[1]))

    seen_urls = {src.get("url", "") for src in direct}
    sources = list(direct)
    for _, _, item in candidates:
        url = item.get("url", "")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        sources.append(
            {
                "title": item.get("title", "") or item.get("source_name", "Source"),
                "url": url,
                "source_name": item.get("source_name", ""),
                "published": item.get("published", ""),
            }
        )
        if len(sources) >= max_sources:
            break
    return sources


def build_manual_topic_items(topic_entries, plan):
    review_items = plan.get("review_items") or plan.get("items") or []
    now_iso = datetime.now(timezone.utc).isoformat()
    built = []

    for entry in topic_entries or []:
        topic_text = (entry.get("topic") or "").strip()
        if not topic_text:
            continue
        sources = _collect_topic_supporting_sources(entry, review_items)
        recommended = len(sources) > 0
        summary = (entry.get("notes") or "").strip()
        if not summary:
            summary = (
                "User-requested deep dive. Include operational implications, tradeoffs, and "
                "specific actions for platform teams."
            )
        built.append(
            {
                "id": None,
                "manual_topic": True,
                "manual_topic_id": entry.get("id"),
                "title": topic_text,
                "summary": summary,
                "published": now_iso,
                "source_name": "User Topic Request",
                "category_hint": entry.get("category_hint", "ecosystem"),
                "url": sources[0].get("url", "") if sources else "",
                "content_hash": f"manual-topic-{entry.get('id')}",
                "sources": sources,
                "supporting_sources": sources,
                "source_item_ids": [],
                "score": 99 if recommended else 72,
                "recommended": recommended,
                "origin": "manual-topic",
            }
        )
    return built


def merge_manual_topics_into_plan(plan, manual_items):
    if not manual_items:
        return plan

    merged = dict(plan)
    selected = list(plan.get("items") or [])
    review = list(plan.get("review_items") or plan.get("items") or [])

    for item in manual_items:
        key = topic_key(item)
        if any(topic_key(existing) == key for existing in selected):
            continue
        selected.append(item)
        review.insert(0, item)

    review, _ = dedupe_items_by_topic(review)
    selected, _ = dedupe_items_by_topic(selected)

    merged["items"] = selected
    merged["review_items"] = review
    merged["total_selected"] = len(selected)
    merged["total_review_items"] = len(review)
    merged["recommended_in_review"] = sum(1 for item in review if item.get("recommended"))
    merged["manual_topic_count"] = len(manual_items)
    return merged


def verify_generated_markdown():
    errors = []
    byline_re = re.compile(r"(?im)^\s*(editors?|author|authors?)\s*:")
    date_re = re.compile(r"(?im)^date:\s*(\d{4}-\d{2}-\d{2})\s*$")
    title_re = re.compile(r"(?im)^title:\s*\"?(.+?)\"?\s*$")
    link_re = re.compile(r"\[[^\]]+\]\(([^)\s]+)\)")
    today = datetime.now().astimezone().date()
    seen_topic_dates = {}
    for config in CATEGORY_CONFIG.values():
        root = config["output_dir"]
        if not os.path.isdir(root):
            continue
        for name in os.listdir(root):
            if name == "index.md" or not name.endswith(".md"):
                continue
            path = os.path.join(root, name)
            with open(path) as handle:
                content = handle.read()
            if "---" not in content:
                errors.append(f"{path}: missing front matter")

            required = ["## Source Links", "## Related Pages"]
            category = category_from_path(path)
            if category:
                required.extend(required_sections_for(category))

            for marker in required:
                if marker not in content:
                    errors.append(f"{path}: missing section {marker}")
            if byline_re.search(content):
                errors.append(f"{path}: contains source byline/editor credits")

            title_match = title_re.search(content)
            title_value = title_match.group(1).strip() if title_match else name[:-3]
            parsed_date = None
            date_match = date_re.search(content)
            if date_match:
                try:
                    parsed_date = datetime.strptime(date_match.group(1), "%Y-%m-%d").date()
                    if parsed_date > today:
                        errors.append(f"{path}: has future publish date {parsed_date.isoformat()}")
                    key = f"{category}:{parsed_date.isoformat()}:{' '.join(_canonical_topic_tokens(title_value))}"
                    if key in seen_topic_dates:
                        errors.append(
                            f"{path}: duplicate same-day topic of {seen_topic_dates[key]}"
                        )
                    else:
                        seen_topic_dates[key] = path
                except ValueError:
                    errors.append(f"{path}: has invalid publish date {date_match.group(1)}")

            enforce_quality = True
            if parsed_date is not None:
                age = (today - parsed_date).days
                enforce_quality = age <= QUALITY_VERIFY_WINDOW_DAYS

            if category and enforce_quality:
                quality_issues = assess_markdown_quality(category, content)
                for issue in quality_issues:
                    errors.append(f"{path}: quality check failed - {issue}")

            for target in link_re.findall(content):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                rel = target.split("#", 1)[0].split("?", 1)[0]
                if not rel or not rel.endswith(".md"):
                    continue
                candidate = os.path.normpath(os.path.join(os.path.dirname(path), rel))
                if not os.path.exists(candidate):
                    errors.append(f"{path}: broken internal markdown link -> {rel}")

    for err in errors:
        log.error(f"VERIFY: {err}")
    return len(errors) == 0


def git_push():
    os.chdir(REPO)
    tracked_paths = [
        "docs/news/",
    ]

    diff_cmd = ["git", "diff", "--quiet", "--", *tracked_paths]
    changed = subprocess.run(diff_cmd).returncode != 0

    untracked = subprocess.run(
        [
            "git",
            "ls-files",
            "--others",
            "--exclude-standard",
            "docs/news/",
        ],
        capture_output=True,
        text=True,
    )

    if not changed and not untracked.stdout.strip():
        log.info("No generated changes to commit.")
        return 0

    subprocess.run(["git", "add", "docs/news/"], check=True)

    changed_files = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True)
    generated_count = sum(1 for line in changed_files.stdout.splitlines() if line.endswith(".md") and "index.md" not in line)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    message = f"feat(news): publish {generated_count} curated news pages [{ts}]"
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    log.info(f"Pushed {generated_count} generated page(s).")
    return generated_count


def notify_openclaw(message):
    try:
        sock_path = os.path.expanduser("~/.openclaw/daemon.sock")
        if not os.path.exists(sock_path):
            return
        subprocess.run(["openclaw", "notify", message], capture_output=True, timeout=10)
        log.info("OpenClaw notification sent.")
    except Exception as exc:
        log.debug(f"OpenClaw notify skipped: {exc}")


def clean_cell(value):
    return (value or "").replace("|", "\\|").replace("\n", " ").strip()


def write_review_state(plan, include_github):
    review_source = plan.get("review_items") or plan.get("items", [])
    items = []
    for idx, item in enumerate(review_source, 1):
        items.append(
            {
                "review_id": idx,
                "category": item.get("category_hint", ""),
                "score": item.get("score", 0),
                "title": item.get("title", "Untitled"),
                "published": (item.get("published", "") or "")[:10],
                "url": item.get("url", ""),
                "summary": (item.get("summary", "") or "")[:220],
                "id": item.get("id"),
                "source_item_ids": item.get("source_item_ids") or [],
                "recommended": bool(item.get("recommended", False)),
                "origin": item.get("origin", "discovered"),
                "manual_topic_id": item.get("manual_topic_id"),
                "item": item,
            }
        )

    state = {
        "created_at": datetime.now().astimezone().isoformat(),
        "include_github": bool(include_github),
        "total_candidates": plan.get("total_candidates", 0),
        "total_selected": plan.get("total_selected", 0),
        "total_review_items": len(items),
        "recommended_in_review": sum(1 for entry in items if entry.get("recommended")),
        "manual_topic_count": sum(1 for entry in items if entry.get("origin") == "manual-topic"),
        "items": items,
    }

    with open(REVIEW_STATE_PATH, "w") as handle:
        json.dump(state, handle, indent=2)

    return state


def write_review_markdown(state):
    lines = [
        "# Pending Topic Review",
        "",
        f"Generated: `{state.get('created_at', '')}`",
        "",
        f"Candidates found: `{state.get('total_candidates', 0)}`",
        "",
        f"Review shortlist size: `{state.get('total_review_items', 0)}`",
        "",
        f"Recommended by planner: `{state.get('recommended_in_review', 0)}`",
        "",
        f"Custom topics queued: `{state.get('manual_topic_count', 0)}`",
        "",
        f"Quality-first publish cap per run: `{MAX_GENERATE_PER_RUN}`",
        "",
        "Select topics to publish by review ID:",
        "",
        "- Publish all: `.venv/bin/python data/k8s_factory/run_pipeline.py --approve all`",
        "- Publish specific: `.venv/bin/python data/k8s_factory/run_pipeline.py --approve 1,3`",
        "- Publish none: `.venv/bin/python data/k8s_factory/run_pipeline.py --approve none`",
        "- Add custom topic: `.venv/bin/python data/k8s_factory/topic_requests.py add --topic \"<your topic>\" --notes \"<angle>\" --source <url>`",
        "",
        "| ID | Recommended | Origin | Category | Score | Source Date | Topic |",
        "| --- | --- | --- | --- | ---: | --- | --- |",
    ]

    for entry in state.get("items", []):
        rec = "yes" if entry.get("recommended") else ""
        origin = "manual" if entry.get("origin") == "manual-topic" else "discovered"
        topic_title = clean_cell(entry.get("title", "Untitled"))
        topic_url = clean_cell(entry.get("url", ""))
        topic_cell = f"[{topic_title}]({topic_url})" if topic_url else topic_title
        lines.append(
            f"| {entry['review_id']} | {rec} | {origin} | {clean_cell(entry.get('category', ''))} | "
            f"{entry.get('score', 0)} | {clean_cell(entry.get('published', '')) or '-'} | "
            f"{topic_cell} |"
        )

    lines.append("")
    lines.append("## Summaries")
    lines.append("")
    for entry in state.get("items", []):
        summary = clean_cell(entry.get("summary", "")) or "No summary available."
        prefix = "[recommended] " if entry.get("recommended") else ""
        if entry.get("origin") == "manual-topic" and not entry.get("recommended"):
            summary = f"{summary} (Add at least one supporting source URL before approving.)"
        lines.append(f"- `{entry['review_id']}` {prefix}{summary}")

    with open(REVIEW_MD_PATH, "w") as handle:
        handle.write("\n".join(lines).strip() + "\n")


def topic_preview(state, limit=5):
    entries = state.get("items", [])[:limit]
    parts = []
    for entry in entries:
        marker = "*" if entry.get("recommended") else ""
        prefix = "[manual] " if entry.get("origin") == "manual-topic" else ""
        parts.append(f"{entry.get('review_id')}. {prefix}{entry.get('title', 'Untitled')}{marker}")
    return " | ".join(parts)


def load_review_state():
    if not os.path.exists(REVIEW_STATE_PATH):
        return None
    with open(REVIEW_STATE_PATH) as handle:
        return json.load(handle)


def clear_review_files():
    for path in [REVIEW_STATE_PATH, REVIEW_MD_PATH]:
        if os.path.exists(path):
            os.remove(path)


def parse_approved_ids(value, total):
    if total <= 0:
        return set()

    text = (value or "").strip().lower()
    if text == "all":
        return set(range(1, total + 1))
    if text == "none":
        return set()

    chosen = set()
    for token in text.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            left, right = token.split("-", 1)
            if not left.isdigit() or not right.isdigit():
                raise ValueError(f"Invalid review range: {token}")
            start, end = int(left), int(right)
            if start > end:
                start, end = end, start
            for idx in range(start, end + 1):
                if idx < 1 or idx > total:
                    raise ValueError(f"Review ID out of range: {idx}")
                chosen.add(idx)
            continue

        if not token.isdigit():
            raise ValueError(f"Invalid review ID: {token}")
        idx = int(token)
        if idx < 1 or idx > total:
            raise ValueError(f"Review ID out of range: {idx}")
        chosen.add(idx)

    return chosen


def split_selected_and_skipped(state, approved_ids):
    selected = []
    skipped_item_ids = set()
    selected_topic_ids = set()
    skipped_topic_ids = set()

    for entry in state.get("items", []):
        rid = int(entry.get("review_id", 0) or 0)
        if rid in approved_ids:
            selected.append(entry.get("item", {}))
            if entry.get("manual_topic_id"):
                selected_topic_ids.add(str(entry.get("manual_topic_id")))
            continue

        item_id = entry.get("id")
        if item_id:
            skipped_item_ids.add(int(item_id))
        if entry.get("manual_topic_id"):
            skipped_topic_ids.add(str(entry.get("manual_topic_id")))

        for sid in entry.get("source_item_ids") or []:
            if sid:
                skipped_item_ids.add(int(sid))

    return (
        selected,
        sorted(skipped_item_ids),
        sorted(selected_topic_ids),
        sorted(skipped_topic_ids),
    )


def collect_item_ids(items):
    ids = set()
    for item in items or []:
        item_id = item.get("id")
        if item_id:
            ids.add(int(item_id))
        for sid in item.get("source_item_ids") or []:
            if sid:
                ids.add(int(sid))
    return sorted(ids)


def collect_manual_topic_ids(items):
    ids = set()
    for item in items or []:
        req_id = item.get("manual_topic_id")
        if req_id:
            ids.add(str(req_id))
    return sorted(ids)


def cap_items_for_quality(items, label):
    if MAX_GENERATE_PER_RUN <= 0 or len(items) <= MAX_GENERATE_PER_RUN:
        return items, []

    ranked = sorted(items, key=lambda it: it.get("score", 0), reverse=True)
    kept = ranked[:MAX_GENERATE_PER_RUN]
    dropped = ranked[MAX_GENERATE_PER_RUN:]
    log.info(
        "Quality-first cap active for %s: %s selected, %s deferred/skipped (max=%s).",
        label,
        len(kept),
        len(dropped),
        MAX_GENERATE_PER_RUN,
    )
    return kept, dropped


def mark_skipped_items(item_ids):
    if not item_ids:
        return
    db = get_db()
    try:
        for item_id in item_ids:
            mark_processed(db, item_id, "skipped-by-review")
    finally:
        db.close()


def touch_last_run():
    with open(os.path.join(PIPELINE_DIR, ".last_run"), "w") as handle:
        handle.write(datetime.now(timezone.utc).isoformat())


def queue_cli_topic_requests(argv):
    topics = parse_option_values(argv, "--topic")
    if not topics:
        return 0

    category = parse_option_value(argv, "--topic-category") or ""
    notes = parse_option_value(argv, "--topic-notes") or ""
    sources = parse_option_values(argv, "--topic-source")

    added = 0
    for topic in topics:
        entry = add_topic_request(
            topic=topic,
            category=category,
            notes=notes,
            sources=sources,
            requested_by="cli",
        )
        if entry:
            added += 1
    return added


def main():
    if not acquire_run_lock():
        log.error(
            "Another pipeline run appears active. Exiting to avoid overlapping LLM calls. "
            f"Lock: {RUN_LOCK_PATH}"
        )
        return 1
    atexit.register(release_run_lock)

    argv = sys.argv[1:]
    include_github = "--github" in argv
    auto_publish = "--auto-publish" in argv

    try:
        approve_value = parse_option_value(argv, "--approve")
        queued_topics = queue_cli_topic_requests(argv)
    except ValueError as exc:
        log.error(str(exc))
        return 1

    log.info("=== Pipeline starting ===")
    if queued_topics:
        log.info("Queued %s custom topic request(s) from CLI flags.", queued_topics)

    db = get_db()
    run_id = log_run_start(db)
    db.close()

    try:
        # Approval pass: publish selected items from pending review queue.
        if approve_value is not None:
            state = load_review_state()
            if not state or not state.get("items"):
                log.error("No pending review queue found. Run pipeline without --approve first.")
                db = get_db()
                log_run_end(db, run_id, 0, 0, "failed_no_review_queue")
                db.close()
                return 1

            approved_ids = parse_approved_ids(approve_value, len(state.get("items", [])))
            (
                selected_items,
                skipped_ids,
                approved_topic_ids,
                skipped_topic_ids,
            ) = split_selected_and_skipped(state, approved_ids)
            selected_items, duplicate_items = dedupe_items_by_topic(selected_items)
            selected_items, dropped_items = cap_items_for_quality(selected_items, "approved topics")
            overflow_ids = collect_item_ids(dropped_items + duplicate_items)
            overflow_topic_ids = collect_manual_topic_ids(dropped_items + duplicate_items)
            all_skipped_ids = sorted(set(skipped_ids + overflow_ids))
            all_skipped_topic_ids = sorted(set(skipped_topic_ids + overflow_topic_ids))
            mark_skipped_items(all_skipped_ids)

            if not selected_items:
                clear_review_files()
                resolve_requests(all_skipped_topic_ids, "skipped")
                db = get_db()
                log_run_end(db, run_id, 0, 0, "success_review_none")
                db.close()
                notify_openclaw("k8s.guide news review: no topics approved; nothing published.")
                log.info("No topics approved. Done.")
                return 0

            log.info(f"--- Generate ({len(selected_items)} approved item(s)) ---")
            generated = run_generate(plan_items=selected_items)
            sync_news_indexes()

            log.info("--- Verify ---")
            if not verify_generated_markdown():
                log.error("Verification failed.")
                db = get_db()
                log_run_end(db, run_id, 0, generated, "failed_verify")
                db.close()
                return 1

            log.info("--- Commit & Push ---")
            pushed = git_push()
            clear_review_files()
            resolve_requests(approved_topic_ids, "published")
            resolve_requests(all_skipped_topic_ids, "skipped")

            db = get_db()
            log_run_end(db, run_id, 0, generated, "success")
            db.close()

            touch_last_run()
            notify_openclaw(f"k8s.guide news pipeline: {generated} approved pages generated, {pushed} pushed.")
            log.info(f"=== Done: {generated} approved page(s) generated ===")
            return 0

        log.info("--- Crawl ---")
        crawled = run_crawl(include_github=include_github)

        log.info("--- Analyze ---")
        plan = generate_plan()
        manual_topic_entries = pending_requests()
        if manual_topic_entries:
            manual_items = build_manual_topic_items(manual_topic_entries, plan)
            plan = merge_manual_topics_into_plan(plan, manual_items)
            log.info(
                "Merged %s pending custom topic request(s) into review queue.",
                len(manual_items),
            )

        selected = len(plan.get("items", []))
        if selected == 0:
            log.info("No high-signal items selected. Done.")
            db = get_db()
            log_run_end(db, run_id, crawled, 0, "success_noop")
            db.close()
            return 0

        # Default behavior: require manual topic approval before generation/publish.
        if not auto_publish:
            state = write_review_state(plan, include_github=include_github)
            write_review_markdown(state)
            for entry in state.get("items", []):
                log.info(
                    f"REVIEW {entry['review_id']}: [{entry.get('category', '')}] "
                    f"score={entry.get('score', 0)} title={entry.get('title', '')}"
                )
            db = get_db()
            log_run_end(db, run_id, crawled, 0, "awaiting_review")
            db.close()

            notify_openclaw(
                "k8s.guide news review ready: "
                f"{state.get('total_candidates', selected)} candidate(s) found, "
                f"{state.get('total_review_items', selected)} topic(s) in review shortlist, "
                f"{state.get('recommended_in_review', selected)} recommended. "
                f"Custom topics queued: {state.get('manual_topic_count', 0)}. "
                "Review data/k8s_factory/review_topics.md and approve with "
                "`.venv/bin/python data/k8s_factory/run_pipeline.py --approve 1,2` (or all/none). "
                f"Preview: {topic_preview(state)}"
            )
            log.info("Awaiting human topic approval. No pages generated yet.")
            return 0

        auto_candidates, auto_duplicates = dedupe_items_by_topic(plan.get("items", []))
        auto_items, _ = cap_items_for_quality(auto_candidates, "auto-publish plan")
        resolve_requests(collect_manual_topic_ids(auto_duplicates), "skipped")
        log.info(f"--- Generate ({len(auto_items)} item(s)) ---")
        generated = run_generate(plan_items=auto_items)
        sync_news_indexes()

        log.info("--- Verify ---")
        if not verify_generated_markdown():
            log.error("Verification failed.")
            db = get_db()
            log_run_end(db, run_id, crawled, generated, "failed_verify")
            db.close()
            return 1

        log.info("--- Commit & Push ---")
        pushed = git_push()
        resolve_requests(collect_manual_topic_ids(auto_items), "published")

        db = get_db()
        log_run_end(db, run_id, crawled, generated, "success")
        db.close()

        touch_last_run()
        notify_openclaw(f"k8s.guide news pipeline: {generated} pages generated, {pushed} pushed.")
        log.info(f"=== Done: {generated} page(s) generated ===")
        return 0

    except Exception as exc:
        log.error(f"FAILED: {exc}\n{traceback.format_exc()}")
        db = get_db()
        log_run_end(db, run_id, 0, 0, "failed", str(exc))
        db.close()
        notify_openclaw(f"k8s.guide pipeline FAILED: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
