#!/usr/bin/env python3
import os
import sys
import logging
from datetime import datetime, timezone

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import get_db, get_recent_articles
from llm import write_newsletter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("newsletter")

BUTTONDOWN_API = "https://api.buttondown.com/v1/emails"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ISSUES_DIR = os.path.join(REPO, "data", "k8s_factory", "newsletter_issues")
ISSUES_INDEX = os.path.join(ISSUES_DIR, "index.md")


def issue_filename(now):
    return f"{now.strftime('%Y-%m-%d')}-weekly-kubernetes-news.md"


def write_issue_file(subject, body):
    os.makedirs(ISSUES_DIR, exist_ok=True)
    now = datetime.now(timezone.utc)
    filename = issue_filename(now)
    path = os.path.join(ISSUES_DIR, filename)

    with open(path, "w") as handle:
        handle.write(
            "---\n"
            f"title: \"{subject}\"\n"
            f"date: {now.strftime('%Y-%m-%d')}\n"
            "category: newsletter\n"
            "---\n\n"
            f"# {subject}\n\n"
            f"{body.strip()}\n"
        )

    update_issue_index()
    return path


def update_issue_index():
    files = []
    if os.path.isdir(ISSUES_DIR):
        for name in sorted(os.listdir(ISSUES_DIR), reverse=True):
            if name == "index.md" or not name.endswith(".md"):
                continue
            files.append(name)

    lines = [
        "---",
        "title: Newsletter Issues",
        "---",
        "",
        "# Newsletter Issues",
        "",
        "Published weekly issues are archived here.",
        "",
    ]

    if not files:
        lines.append("No issue has been published from the new pipeline yet.")
    else:
        for name in files[:20]:
            label = name.replace(".md", "").replace("-", " ").title()
            lines.append(f"- [{label}]({name})")

    with open(ISSUES_INDEX, "w") as handle:
        handle.write("\n".join(lines) + "\n")


def send_newsletter(send_to_buttondown=True):
    db = get_db()
    articles = get_recent_articles(db, days=7)
    db.close()

    if len(articles) < 3:
        log.info(f"Only {len(articles)} processed articles in last 7 days. Skipping newsletter.")
        return False

    body = write_newsletter(articles)
    if not body:
        log.error("LLM failed to write newsletter.")
        return False

    now = datetime.now(timezone.utc)
    subject = f"This Week in Kubernetes - {now.strftime('%b %d, %Y')}"

    issue_path = write_issue_file(subject, body)
    log.info(f"Saved issue to {issue_path}")

    api_key = (os.environ.get("BUTTONDOWN_API_KEY") or "").strip()
    if not send_to_buttondown:
        return True
    if not api_key or "your-" in api_key:
        log.info("No valid Buttondown API key; skipped send.")
        return True

    log.info(f"Sending newsletter draft: {subject}")
    resp = requests.post(
        BUTTONDOWN_API,
        headers={
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "subject": subject,
            "body": body,
            "status": "about_to_send",
        },
        timeout=60,
    )

    if resp.status_code in (200, 201):
        log.info("Newsletter sent successfully.")
        return True

    log.error(f"Buttondown error {resp.status_code}: {resp.text[:200]}")
    return False


if __name__ == "__main__":
    send_newsletter(send_to_buttondown=True)
