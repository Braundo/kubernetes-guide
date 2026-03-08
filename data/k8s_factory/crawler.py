import sys
import os
import time
import hashlib
import re
import logging
from datetime import datetime, timezone, timedelta

import feedparser
import requests

from db import get_db, insert_item, item_exists_by_url
from content_policy import (
    infer_category,
    is_approved_url,
    is_kubernetes_relevant,
    normalize_space,
    source_default_category,
    truncate_text,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("crawler")

UA = "k8s-guide-news-bot/2.0 (+https://k8s.guide)"
TIMEOUT = 30
DELAY = 2
RETRIES = 2

RSS_SOURCES = [
    {
        "url": "https://kubernetes.io/feed.xml",
        "default_category": "ecosystem",
        "name": "Kubernetes Blog",
    },
    {
        "url": "https://www.cncf.io/feed/",
        "default_category": "ecosystem",
        "name": "CNCF Blog",
    },
    {
        "url": "https://aws.amazon.com/blogs/containers/feed/",
        "default_category": "ecosystem",
        "name": "AWS Containers Blog",
    },
    {
        "url": "https://cloud.google.com/blog/products/containers-kubernetes/rss/",
        "default_category": "ecosystem",
        "name": "Google Cloud Kubernetes Blog",
    },
    {
        "url": "https://techcommunity.microsoft.com/t5/azure-kubernetes-service-aks/bg-p/AzureKubernetesServiceBlog/rss",
        "default_category": "ecosystem",
        "name": "Azure AKS Blog",
    },
    {
        "url": "https://www.cilium.io/blog/rss.xml",
        "default_category": "ecosystem",
        "name": "Cilium Blog",
    },
    {
        "url": "https://isovalent.com/blog/rss/",
        "default_category": "ecosystem",
        "name": "Isovalent Blog",
    },
    {
        "url": "https://grafana.com/blog/rss/",
        "default_category": "ecosystem",
        "name": "Grafana Blog",
    },
    {
        "url": "https://www.redhat.com/en/blog/channel/kubernetes/feed",
        "default_category": "ecosystem",
        "name": "Red Hat Kubernetes Blog",
    },
    {
        "url": "https://blog.aquasec.com/rss.xml",
        "default_category": "security",
        "name": "Aqua Security Blog",
    },
    {
        "url": "https://sysdig.com/feed/",
        "default_category": "security",
        "name": "Sysdig Security Blog",
    },
    {
        "url": "https://blog.trailofbits.com/index.xml",
        "default_category": "security",
        "name": "Trail of Bits Blog",
    },
]

BYLINE_KEYWORDS = ("editor", "editors", "author", "authors", "written by", "byline")


def strip_byline_sentences(text):
    content = normalize_space(text)
    if not content:
        return ""

    sentences = re.split(r"(?<=[.!?])\s+", content)
    kept = []
    for sentence in sentences:
        lower = sentence.lower()
        if any(k in lower for k in BYLINE_KEYWORDS):
            continue
        kept.append(sentence)
    return normalize_space(" ".join(kept))


def fetch_rss(source):
    url = source["url"]
    log.info(f"Fetching: {url}")

    resp = None
    for attempt in range(RETRIES + 1):
        try:
            resp = requests.get(url, headers={"User-Agent": UA}, timeout=TIMEOUT)
            resp.raise_for_status()
            break
        except requests.RequestException as exc:
            if attempt < RETRIES:
                time.sleep(DELAY * (attempt + 1))
            else:
                log.error(f"Failed {url}: {exc}")
                return []

    feed = feedparser.parse(resp.text)
    items = []
    for entry in feed.entries:
        title = normalize_space(entry.get("title", ""))
        link = normalize_space(entry.get("link", ""))
        if not title or not link:
            continue
        if not is_approved_url(link):
            continue

        published = ""
        for attr in ("published_parsed", "updated_parsed"):
            parsed = getattr(entry, attr, None)
            if parsed:
                published = datetime(*parsed[:6], tzinfo=timezone.utc).isoformat()
                break

        raw_summary = entry.get("summary", entry.get("description", ""))
        summary = re.sub(r"<[^>]+>", "", raw_summary).strip()
        summary = strip_byline_sentences(summary)
        summary = truncate_text(summary, max_chars=1200, prefer_sentence=True)
        if not is_kubernetes_relevant(title, summary, link, source["name"]):
            continue

        category = infer_category(
            title=title,
            summary=summary,
            default=source_default_category(source["name"], source["default_category"]),
            url=link,
        )

        items.append(
            {
                "url": link,
                "title": title,
                "summary": summary,
                "published": published,
                "source_name": source["name"],
                "category_hint": category,
                "content_hash": hashlib.sha256(f"{title}|{link}".encode()).hexdigest()[:16],
                "stars": 0,
                "forks": 0,
                "open_issues": 0,
                "watchers": 0,
                "last_pushed": "",
            }
        )

    log.info(f"  {len(items)} items from {source['name']}")
    return items


def fetch_github():
    token = (os.environ.get("GITHUB_TOKEN") or "").strip()
    if not token:
        log.info("No GITHUB_TOKEN; skipping GitHub tool scan.")
        return []

    log.info("Searching GitHub for emerging Kubernetes tools")
    pushed_days = int(os.environ.get("GITHUB_PUSHED_DAYS", "180"))
    min_stars = int(os.environ.get("GITHUB_MIN_STARS", "80"))
    per_page = int(os.environ.get("GITHUB_PER_PAGE", "30"))
    pushed_since = (datetime.now(timezone.utc) - timedelta(days=pushed_days)).strftime("%Y-%m-%d")
    queries = [
        f"topic:kubernetes stars:>{min_stars} pushed:>{pushed_since}",
        f"kubernetes in:name,description,readme stars:>{max(min_stars, 120)} pushed:>{pushed_since}",
    ]

    repos_by_url = {}
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": UA,
    }
    for query in queries:
        try:
            resp = requests.get(
                "https://api.github.com/search/repositories",
                headers=headers,
                params={
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": max(10, min(per_page, 50)),
                },
                timeout=TIMEOUT,
            )
            resp.raise_for_status()
        except Exception as exc:
            log.error(f"GitHub fetch failed for query '{query}': {exc}")
            continue
        for repo in resp.json().get("items", []):
            url = repo.get("html_url", "")
            if not url:
                continue
            existing = repos_by_url.get(url)
            if existing is None or int(repo.get("stargazers_count", 0) or 0) > int(
                existing.get("stargazers_count", 0) or 0
            ):
                repos_by_url[url] = repo

    if not repos_by_url:
        return []

    repos = sorted(
        repos_by_url.values(),
        key=lambda repo: int(repo.get("stargazers_count", 0) or 0),
        reverse=True,
    )
    items = []
    for repo in repos[: max(20, per_page)]:
        link = repo.get("html_url", "")
        if not link or not is_approved_url(link):
            continue

        repo_name = normalize_space(repo.get("name", "") or repo.get("full_name", ""))
        title = f"{repo_name} tool radar".strip()
        summary = strip_byline_sentences(normalize_space(repo.get("description", "")))
        summary = truncate_text(summary, max_chars=600, prefer_sentence=True)
        if not is_kubernetes_relevant(title, summary, link, "GitHub Trending"):
            continue
        items.append(
            {
                "url": link,
                "title": title,
                "summary": summary,
                "published": repo.get("pushed_at", "") or repo.get("created_at", ""),
                "source_name": "GitHub Trending",
                "category_hint": "tool-radar",
                "content_hash": hashlib.sha256(link.encode()).hexdigest()[:16],
                "stars": int(repo.get("stargazers_count", 0) or 0),
                "forks": int(repo.get("forks_count", 0) or 0),
                "open_issues": int(repo.get("open_issues_count", 0) or 0),
                "watchers": int(repo.get("watchers_count", 0) or 0),
                "last_pushed": repo.get("pushed_at", ""),
            }
        )

    log.info(f"  {len(items)} GitHub repos")
    return items


def run_crawl(include_github=False):
    db = get_db()
    total = 0

    for source in RSS_SOURCES:
        for item in fetch_rss(source):
            if item_exists_by_url(db, item["url"]):
                continue
            insert_item(db, item)
            total += 1
        time.sleep(DELAY)

    if include_github:
        for item in fetch_github():
            if item_exists_by_url(db, item["url"]):
                continue
            insert_item(db, item)
            total += 1

    log.info(f"Crawl done. {total} new items.")
    db.close()
    return total


if __name__ == "__main__":
    run_crawl("--github" in sys.argv)
