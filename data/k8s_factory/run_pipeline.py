#!/usr/bin/env python3
#Full pipeline orchestrator
import sys, os, logging, traceback, subprocess
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db import get_db, log_run_start, log_run_end
from crawler import run_crawl
from analyze import generate_plan
from generate import run_generate

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(),
              logging.FileHandler(os.path.join(
                  os.path.dirname(os.path.abspath(__file__)), "run.log"))])
log = logging.getLogger("pipeline")
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def verify():
    errs = []
    for root, _, files in os.walk(os.path.join(REPO, "docs", "automation")):
        for f in files:
            if f.endswith(".md") and f != "index.md":
                p = os.path.join(root, f)
                with open(p) as fh: c = fh.read()
                if "---" not in c: errs.append(f"{p}: no frontmatter")
                if len(c) < 200: errs.append(f"{p}: too short")
    for e in errs: log.error(f"VERIFY: {e}")
    return len(errs) == 0

def git_push():
    os.chdir(REPO)
    r1 = subprocess.run(["git","diff","--quiet","docs/news/"],
                        capture_output=True)
    untracked = subprocess.run(
        ["git","ls-files","--others","--exclude-standard","docs/news/"],
        capture_output=True, text=True)
    if r1.returncode == 0 and not untracked.stdout.strip():
        log.info("No changes.")
        return 0
    subprocess.run(["git","add","docs/news/"], check=True)
    subprocess.run(["git","add","data/k8s_factory/plan.json"], check=False)
    count = subprocess.run(["git","diff","--cached","--name-only"],
        capture_output=True, text=True)
    n = sum(1 for l in count.stdout.strip().split("\n")
            if l.endswith(".md")) if count.stdout.strip() else 0
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    subprocess.run(["git","commit","-m",
        f"feat(news): add {n} new articles [{ts}]"], check=True)
    subprocess.run(["git","push","origin","main"], check=True)
    log.info(f"Pushed {n} articles.")
    return n

def notify_openclaw(message):
    #Send notification via OpenClaw if available.
    try:
        sock_path = os.path.expanduser("~/.openclaw/daemon.sock")
        if not os.path.exists(sock_path):
            return
        # Use the openclaw CLI to send a notification to yourself
        subprocess.run(["openclaw", "notify", message],
                       capture_output=True, timeout=10)
        log.info("OpenClaw notification sent.")
    except Exception as e:
        log.debug(f"OpenClaw notify skipped: {e}")

def main():
    gh = "--github" in sys.argv
    log.info("=== Pipeline starting ===")
    db = get_db()
    rid = log_run_start(db)
    db.close()
    try:
        log.info("--- Crawl ---")
        new = run_crawl(include_github=gh)
        log.info("--- Analyze ---")
        plan = generate_plan()
        planned = len(plan.get("items",[]))
        if planned == 0:
            log.info("No new items. Done.")
            db = get_db()
            log_run_end(db, rid, new, 0, "success_noop")
            db.close()
            return 0
        log.info(f"--- Generate ({planned} items) ---")
        gen = run_generate()
        log.info("--- Verify ---")
        if not verify():
            log.error("Verification failed.")
            db = get_db()
            log_run_end(db, rid, new, gen, "failed_verify")
            db.close()
            return 1
        log.info("--- Commit & Push ---")
        pushed = git_push()
        db = get_db()
        log_run_end(db, rid, new, gen, "success")
        db.close()
        with open(os.path.join(os.path.dirname(
                os.path.abspath(__file__)), ".last_run"), "w") as f:
            f.write(datetime.now(timezone.utc).isoformat())

        # Notify
        msg = f"k8s.guide pipeline: {gen} articles published to site."
        notify_openclaw(msg)
        log.info(f"=== Done: {gen} articles published ===")
        return 0
    except Exception as e:
        log.error(f"FAILED: {e}\n{traceback.format_exc()}")
        db = get_db()
        log_run_end(db, rid, 0, 0, "failed", str(e))
        db.close()
        notify_openclaw(f"k8s.guide pipeline FAILED: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
