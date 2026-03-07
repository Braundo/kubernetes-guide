#!/usr/bin/env python3
import os
import sys
import logging
import traceback
import subprocess
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import get_db, log_run_start, log_run_end
from crawler import run_crawl
from analyze import generate_plan
from generate import run_generate
from content_policy import CATEGORY_CONFIG

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), "run.log")),
    ],
)
log = logging.getLogger("pipeline")
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

CATEGORY_REQUIRED_SECTIONS = {
    "security": [
        "## Advisory Summary",
        "## Affected Components and Versions",
        "## Why It Matters",
        "## What to Do",
    ],
    "releases": [
        "## Release Summary",
        "## Key Changes",
        "## Breaking Changes and Deprecations",
        "## Why It Matters for Operators",
        "## Suggested Actions",
    ],
    "ecosystem": [
        "## Curated Intro",
        "## Top Signals This Cycle",
    ],
    "tool-radar": [
        "## What the Tool Does",
        "## Why It Is Worth Watching",
        "## Maturity and Adoption Notes",
        "## Category",
    ],
}


def category_from_path(path):
    normalized = path.replace("\\", "/")
    for category in CATEGORY_CONFIG.keys():
        marker = f"/updates/{category}/"
        if marker in normalized:
            return category
    return None


def verify_generated_markdown():
    errors = []
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
                required.extend(CATEGORY_REQUIRED_SECTIONS.get(category, []))

            for marker in required:
                if marker not in content:
                    errors.append(f"{path}: missing section {marker}")

    for err in errors:
        log.error(f"VERIFY: {err}")
    return len(errors) == 0


def git_push():
    os.chdir(REPO)
    tracked_paths = [
        "docs/updates/",
        "data/k8s_factory/plan.json",
    ]

    diff_cmd = ["git", "diff", "--quiet", "--", *tracked_paths]
    changed = subprocess.run(diff_cmd).returncode != 0

    untracked = subprocess.run(
        [
            "git",
            "ls-files",
            "--others",
            "--exclude-standard",
            "docs/updates/",
        ],
        capture_output=True,
        text=True,
    )

    if not changed and not untracked.stdout.strip():
        log.info("No generated changes to commit.")
        return 0

    subprocess.run(["git", "add", "docs/updates/"], check=True)
    subprocess.run(["git", "add", "data/k8s_factory/plan.json"], check=False)

    changed_files = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True)
    generated_count = sum(1 for line in changed_files.stdout.splitlines() if line.endswith(".md") and "index.md" not in line)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    message = f"feat(updates): publish {generated_count} curated updates [{ts}]"
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


def main():
    include_github = "--github" in sys.argv
    log.info("=== Pipeline starting ===")

    db = get_db()
    run_id = log_run_start(db)
    db.close()

    try:
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

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".last_run"), "w") as handle:
            handle.write(datetime.now(timezone.utc).isoformat())

        notify_openclaw(f"k8s.guide updates pipeline: {generated} pages generated, {pushed} pushed.")
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
