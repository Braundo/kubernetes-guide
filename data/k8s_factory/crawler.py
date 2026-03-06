import sys, os, time, hashlib, re, logging
import feedparser, requests
from datetime import datetime, timezone
from db import get_db, insert_item, item_exists_by_url

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("crawler")

UA = "k8s-guide-bot/1.0 (+https://k8s.guide)"
TIMEOUT, DELAY, RETRIES = 30, 2, 2

RSS_SOURCES = [
    {"url": "https://kubernetes.io/feed.xml",
     "category": "releases", "name": "Kubernetes Blog"},
    {"url": "https://www.cncf.io/feed/",
     "category": "ecosystem", "name": "CNCF Blog"},
    {"url": "https://sysdig.com/blog/feed/",
     "category": "security", "name": "Sysdig Security"},
    {"url": "https://blog.aquasec.com/rss.xml",
     "category": "security", "name": "Aqua Security Blog"},
    {"url": "https://www.armosec.io/blog/feed/",
     "category": "security", "name": "ARMO Security Blog"},
]

def fetch_rss(source):
    url = source["url"]
    log.info(f"Fetching: {url}")
    for attempt in range(RETRIES + 1):
        try:
            resp = requests.get(url, headers={"User-Agent": UA},
                                timeout=TIMEOUT)
            resp.raise_for_status()
            break
        except requests.RequestException as e:
            if attempt < RETRIES:
                time.sleep(DELAY * (attempt + 1))
            else:
                log.error(f"Failed {url}: {e}")
                return []
    feed = feedparser.parse(resp.text)
    items = []
    for entry in feed.entries:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        if not title or not link: continue
        pub = ""
        for attr in ("published_parsed", "updated_parsed"):
            pp = getattr(entry, attr, None)
            if pp:
                pub = datetime(*pp[:6], tzinfo=timezone.utc).isoformat()
                break
        summary = re.sub(r"<[^>]+>", "",
            entry.get("summary", entry.get("description", ""))
        ).strip()[:1000]
        items.append({"url": link, "title": title, "summary": summary,
            "published": pub, "source_name": source["name"],
            "category_hint": source["category"],
            "content_hash": hashlib.sha256(
                f"{title}|{link}".encode()).hexdigest()[:16]})
    log.info(f"  {len(items)} items from {source['name']}")
    return items

def fetch_github():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        log.info("No GITHUB_TOKEN; skipping.")
        return []
    log.info("Searching GitHub...")
    try:
        resp = requests.get("https://api.github.com/search/repositories",
            headers={"Authorization": f"Bearer {token}",
                     "Accept": "application/vnd.github+json",
                     "User-Agent": UA},
            params={"q": "topic:kubernetes created:>2025-12-01 stars:>50",
                    "sort": "stars", "order": "desc", "per_page": 20},
            timeout=TIMEOUT)
        resp.raise_for_status()
    except Exception as e:
        log.error(f"GitHub failed: {e}")
        return []
    items = []
    for r in resp.json().get("items", []):
        items.append({"url": r["html_url"],
            "title": f"{r['full_name']}: {r.get('description','')[:150]}",
            "summary": r.get("description", "")[:500],
            "published": r.get("created_at", ""),
            "source_name": "GitHub Trending",
            "category_hint": "tool-radar",
            "content_hash": hashlib.sha256(
                r["html_url"].encode()).hexdigest()[:16],
            "stars": r.get("stargazers_count", 0)})
    log.info(f"  {len(items)} repos")
    return items

def run_crawl(include_github=False):
    db = get_db()
    total = 0
    for src in RSS_SOURCES:
        for item in fetch_rss(src):
            if not item_exists_by_url(db, item["url"]):
                insert_item(db, item)
                total += 1
        time.sleep(DELAY)
    if include_github:
        for item in fetch_github():
            if not item_exists_by_url(db, item["url"]):
                insert_item(db, item)
                total += 1
    log.info(f"Crawl done. {total} new items.")
    db.close()
    return total

if __name__ == "__main__":
    run_crawl("--github" in sys.argv)
