import os
import re
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOCS = os.path.join(REPO, "docs")

CATEGORY_CONFIG = {
    "security": {
        "output_dir": os.path.join(DOCS, "updates", "security"),
        "index_file": os.path.join(DOCS, "updates", "security", "index.md"),
        "parent_index_rel": "index.md",
    },
    "releases": {
        "output_dir": os.path.join(DOCS, "updates", "releases"),
        "index_file": os.path.join(DOCS, "updates", "releases", "index.md"),
        "parent_index_rel": "index.md",
    },
    "ecosystem": {
        "output_dir": os.path.join(DOCS, "updates", "ecosystem"),
        "index_file": os.path.join(DOCS, "updates", "ecosystem", "index.md"),
        "parent_index_rel": "index.md",
    },
    "tool-radar": {
        "output_dir": os.path.join(DOCS, "updates", "tool-radar"),
        "index_file": os.path.join(DOCS, "updates", "tool-radar", "index.md"),
        "parent_index_rel": "index.md",
    },
}

CATEGORY_TARGET_SHARE = {
    "ecosystem": 0.20,
    "security": 0.30,
    "releases": 0.25,
    "tool-radar": 0.25,
}

RUN_CAPS = {
    "security": 2,
    "releases": 1,
    "ecosystem": 1,
    "tool-radar": 1,
}

DAILY_CAPS = {
    "security": 4,
    "releases": 2,
    "ecosystem": 1,
    "tool-radar": 1,  # intentionally limited to avoid tool spam
}

WEEKLY_CAPS = {
    "security": 12,
    "releases": 5,
    "ecosystem": 4,
    "tool-radar": 2,
}

QUALITY_THRESHOLDS = {
    "security": 68,
    "releases": 64,
    "ecosystem": 62,
    "tool-radar": 62,
}

MAX_ITEMS_PER_RUN = 5
MAX_SLUG_LENGTH = 60

APPROVED_DOMAINS = {
    "kubernetes.io",
    "www.kubernetes.io",
    "github.com",
    "www.cncf.io",
    "cncf.io",
    "blog.aquasec.com",
    "sysdig.com",
    "www.armosec.io",
}

DOMAIN_SCORE_BOOSTS = {
    "kubernetes.io": 20,
    "www.kubernetes.io": 20,
    "github.com": 8,
    "www.cncf.io": 8,
    "cncf.io": 8,
    "blog.aquasec.com": 5,
    "sysdig.com": 4,
    "www.armosec.io": 3,
}

SLUG_STOP_WORDS = {
    "a", "an", "the", "to", "for", "on", "and", "or", "of", "in", "at", "by", "with", "from",
    "is", "are", "be", "as", "this", "that", "all", "you", "your", "now", "into", "over",
}


def normalize_space(text):
    return re.sub(r"\s+", " ", (text or "").strip())


def get_domain(url):
    try:
        return (urlparse(url).netloc or "").lower()
    except Exception:
        return ""


def is_approved_url(url):
    domain = get_domain(url)
    if not domain:
        return False
    return domain in APPROVED_DOMAINS


def infer_category(title, summary, default="ecosystem", url=""):
    text = f"{title or ''} {summary or ''}".lower()
    if re.search(r"\bcve-\d{4}-\d+\b", text):
        return "security"
    if any(k in text for k in ["vulnerability", "advisory", "exploit", "security", "malware", "supply chain"]):
        return "security"
    if any(k in text for k in ["kubernetes v", "upgrade", "release", "deprecation", "ga", "beta", "alpha"]):
        if "kubernetes" in text:
            return "releases"
    if "github.com" in (url or ""):
        return "tool-radar"
    if any(k in text for k in ["tool", "operator", "sdk", "platform", "plugin", "project"]):
        return default if default != "ecosystem" else "ecosystem"
    return default


def today_utc():
    return datetime.now(timezone.utc).date()


def parse_date_prefix(filename):
    base = os.path.basename(filename)
    prefix = base.split("-", 3)
    if len(prefix) < 3:
        return None
    try:
        return datetime.strptime("-".join(prefix[:3]), "%Y-%m-%d").date()
    except ValueError:
        return None


def count_recent_files(category, days=1):
    cfg = CATEGORY_CONFIG.get(category)
    if not cfg:
        return 0
    root = cfg["output_dir"]
    if not os.path.isdir(root):
        return 0
    cutoff = today_utc() - timedelta(days=days - 1)
    count = 0
    for name in os.listdir(root):
        if not name.endswith(".md") or name == "index.md":
            continue
        d = parse_date_prefix(name)
        if not d:
            continue
        if d >= cutoff:
            count += 1
    return count
