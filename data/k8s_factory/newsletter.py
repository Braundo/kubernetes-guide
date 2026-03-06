#!/usr/bin/env python3
#Generate and send a weekly newsletter via Buttondown API.
import os, sys, logging, requests
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db import get_db, get_recent_articles
from llm import write_newsletter

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("newsletter")

BUTTONDOWN_API = "https://api.buttondown.com/v1/emails"

def send_newsletter():
    db = get_db()
    articles = get_recent_articles(db, days=7)
    db.close()

    if len(articles) < 2:
        log.info(f"Only {len(articles)} articles this week. Skipping.")
        return False

    body = write_newsletter(articles)
    if not body:
        log.error("LLM failed to write newsletter.")
        return False

    week = datetime.now(timezone.utc).strftime("%b %d, %Y")
    subject = f"This Week in Kubernetes - {week}"

    api_key = os.environ.get("BUTTONDOWN_API_KEY", "")
    if not api_key or "your-" in api_key:
        log.info("No Buttondown key. Saving newsletter locally.")
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           f"newsletter-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.md")
        with open(path, "w") as f:
            f.write(f"# {subject}\n\n{body}")
        log.info(f"Saved to {path}")
        return True

    log.info(f"Sending newsletter: {subject}")
    resp = requests.post(BUTTONDOWN_API,
        headers={"Authorization": f"Token {api_key}",
                 "Content-Type": "application/json"},
        json={"subject": subject, "body": body,
              "status": "about_to_send"},
        timeout=60)

    if resp.status_code in (200, 201):
        log.info("Newsletter sent successfully!")
        return True
    else:
        log.error(f"Buttondown error {resp.status_code}: {resp.text[:200]}")
        return False

if __name__ == "__main__":
    send_newsletter()
