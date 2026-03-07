#!/usr/bin/env python3
import json
import os
import sys
import logging
import traceback
import subprocess
import re
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import get_db, log_run_start, log_run_end, mark_processed
from crawler import run_crawl
from analyze import generate_plan
from generate import run_generate
from content_policy import CATEGORY_CONFIG
from editorial_quality import required_sections_for, assess_markdown_quality

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


def parse_option_value(argv, flag):
    for idx, arg in enumerate(argv):
        if arg == flag:
            if idx + 1 >= len(argv):
                raise ValueError(f"{flag} requires a value")
            return argv[idx + 1]
        if arg.startswith(f"{flag}="):
            return arg.split("=", 1)[1]
    return None


def category_from_path(path):
    normalized = path.replace("\\", "/")
    for category in CATEGORY_CONFIG.keys():
        marker = f"/news/{category}/"
        if marker in normalized:
            return category
    return None


def verify_generated_markdown():
    errors = []
    byline_re = re.compile(r"(?im)^\s*(editors?|author|authors?)\s*:")
    date_re = re.compile(r"(?im)^date:\s*(\d{4}-\d{2}-\d{2})\s*$")
    today = datetime.now().astimezone().date()
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
            if category:
                quality_issues = assess_markdown_quality(category, content)
                for issue in quality_issues:
                    errors.append(f"{path}: quality check failed - {issue}")
            date_match = date_re.search(content)
            if date_match:
                try:
                    parsed = datetime.strptime(date_match.group(1), "%Y-%m-%d").date()
                    if parsed > today:
                        errors.append(f"{path}: has future publish date {parsed.isoformat()}")
                except ValueError:
                    errors.append(f"{path}: has invalid publish date {date_match.group(1)}")

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
    items = []
    for idx, item in enumerate(plan.get("items", []), 1):
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
                "item": item,
            }
        )

    state = {
        "created_at": datetime.now().astimezone().isoformat(),
        "include_github": bool(include_github),
        "total_candidates": plan.get("total_candidates", 0),
        "total_selected": len(items),
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
        "Select topics to publish by review ID:",
        "",
        "- Publish all: `.venv/bin/python data/k8s_factory/run_pipeline.py --approve all`",
        "- Publish specific: `.venv/bin/python data/k8s_factory/run_pipeline.py --approve 1,3`",
        "- Publish none: `.venv/bin/python data/k8s_factory/run_pipeline.py --approve none`",
        "",
        "| ID | Category | Score | Source Date | Topic |",
        "| --- | --- | ---: | --- | --- |",
    ]

    for entry in state.get("items", []):
        lines.append(
            f"| {entry['review_id']} | {clean_cell(entry.get('category', ''))} | "
            f"{entry.get('score', 0)} | {clean_cell(entry.get('published', '')) or '-'} | "
            f"[{clean_cell(entry.get('title', 'Untitled'))}]({clean_cell(entry.get('url', ''))}) |"
        )

    lines.append("")
    lines.append("## Summaries")
    lines.append("")
    for entry in state.get("items", []):
        summary = clean_cell(entry.get("summary", "")) or "No summary available."
        lines.append(f"- `{entry['review_id']}` {summary}")

    with open(REVIEW_MD_PATH, "w") as handle:
        handle.write("\n".join(lines).strip() + "\n")


def topic_preview(state, limit=5):
    entries = state.get("items", [])[:limit]
    parts = []
    for entry in entries:
        parts.append(f"{entry.get('review_id')}. {entry.get('title', 'Untitled')}")
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

    for entry in state.get("items", []):
        rid = int(entry.get("review_id", 0) or 0)
        if rid in approved_ids:
            selected.append(entry.get("item", {}))
            continue

        item_id = entry.get("id")
        if item_id:
            skipped_item_ids.add(int(item_id))

        for sid in entry.get("source_item_ids") or []:
            if sid:
                skipped_item_ids.add(int(sid))

    return selected, sorted(skipped_item_ids)


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


def main():
    argv = sys.argv[1:]
    include_github = "--github" in argv
    auto_publish = "--auto-publish" in argv

    try:
        approve_value = parse_option_value(argv, "--approve")
    except ValueError as exc:
        log.error(str(exc))
        return 1

    log.info("=== Pipeline starting ===")

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
            selected_items, skipped_ids = split_selected_and_skipped(state, approved_ids)
            mark_skipped_items(skipped_ids)

            if not selected_items:
                clear_review_files()
                db = get_db()
                log_run_end(db, run_id, 0, 0, "success_review_none")
                db.close()
                notify_openclaw("k8s.guide news review: no topics approved; nothing published.")
                log.info("No topics approved. Done.")
                return 0

            log.info(f"--- Generate ({len(selected_items)} approved item(s)) ---")
            generated = run_generate(plan_items=selected_items)

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
                f"{selected} topic(s) selected. Review data/k8s_factory/review_topics.md and approve with "
                "`.venv/bin/python data/k8s_factory/run_pipeline.py --approve 1,2` (or all/none). "
                f"Preview: {topic_preview(state)}"
            )
            log.info("Awaiting human topic approval. No pages generated yet.")
            return 0

        log.info(f"--- Generate ({selected} item(s)) ---")
        generated = run_generate()

        log.info("--- Verify ---")
        if not verify_generated_markdown():
            log.error("Verification failed.")
            db = get_db()
            log_run_end(db, run_id, crawled, generated, "failed_verify")
            db.close()
            return 1

        log.info("--- Commit & Push ---")
        pushed = git_push()

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
