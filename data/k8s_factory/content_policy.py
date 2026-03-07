import os
import re
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOCS = os.path.join(REPO, "docs")

CATEGORY_CONFIG = {
    "security": {
        "output_dir": os.path.join(DOCS, "news", "security"),
        "index_file": os.path.join(DOCS, "news", "security", "index.md"),
        "parent_index_rel": "index.md",
    },
    "releases": {
        "output_dir": os.path.join(DOCS, "news", "releases"),
        "index_file": os.path.join(DOCS, "news", "releases", "index.md"),
        "parent_index_rel": "index.md",
    },
    "ecosystem": {
        "output_dir": os.path.join(DOCS, "news", "ecosystem"),
        "index_file": os.path.join(DOCS, "news", "ecosystem", "index.md"),
        "parent_index_rel": "index.md",
    },
    "tool-radar": {
        "output_dir": os.path.join(DOCS, "news", "tool-radar"),
        "index_file": os.path.join(DOCS, "news", "tool-radar", "index.md"),
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

# Maximum source staleness for publish eligibility.
MAX_SOURCE_AGE_DAYS = {
    "security": 30,
    "releases": 45,
    "ecosystem": 14,
    "tool-radar": 60,
}

MAX_ITEMS_PER_RUN = int(os.environ.get("PIPELINE_MAX_ITEMS_PER_RUN", "1"))
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
    "blog.trailofbits.com",
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
    "blog.trailofbits.com": 5,
}

SLUG_STOP_WORDS = {
    "a", "an", "the", "to", "for", "on", "and", "or", "of", "in", "at", "by", "with", "from",
    "is", "are", "be", "as", "this", "that", "all", "you", "your", "now", "into", "over",
}

SOURCE_DEFAULT_CATEGORY = {
    "Kubernetes Blog": "ecosystem",
    "CNCF Blog": "ecosystem",
    "Aqua Security Blog": "security",
    "Sysdig Security Blog": "security",
    "Trail of Bits Blog": "security",
    "GitHub Trending": "tool-radar",
}

_VERSION_RE = re.compile(
    r"\b(?:kubernetes|k8s)?\s*v?1\.\d{1,2}(?:\.\d+)?(?:\s*(?:rc|alpha|beta)\d*)?\b",
    re.IGNORECASE,
)

RELEASE_URL_HINTS = (
    "/releases/",
    "/release-notes",
    "/changelog",
    "/kubernetes-",
)

RELEASE_TEXT_HINTS = (
    "release notes",
    "release note",
    "changelog",
    "patch release",
    "minor release",
    "major release",
    "release candidate",
    "upgrade guide",
    "version skew",
    "breaking changes",
    "deprecations",
)

RELEASE_VERSION_CONTEXT_HINTS = (
    "release",
    "upgrade",
    "deprecat",
    "beta",
    "alpha",
    "ga",
    "stable",
    "removed in",
    "breaking",
)

NON_RELEASE_GOVERNANCE_HINTS = (
    "spotlight",
    "interview",
    "community update",
    "case study",
    "maintainer profile",
    "sig ",
    "working group",
)

SECURITY_RE = re.compile(
    r"\b("
    r"cve-\d{4}-\d+|"
    r"vulnerability|"
    r"advisory|"
    r"exploit|"
    r"malware|"
    r"supply chain|"
    r"privilege escalation|"
    r"remote code execution|"
    r"rce"
    r")\b",
    re.IGNORECASE,
)

TOOL_HINTS = (
    "tool radar",
    "operator",
    "plugin",
    "sdk",
)


def normalize_space(text):
    return re.sub(r"\s+", " ", (text or "").strip())


def truncate_text(text, max_chars=220, prefer_sentence=False):
    content = normalize_space(text)
    if len(content) <= max_chars:
        return content

    sample = content[: max_chars + 1]

    if prefer_sentence:
        sentence_cut = max(sample.rfind(". "), sample.rfind("! "), sample.rfind("? "))
        if sentence_cut >= int(max_chars * 0.45):
            return sample[: sentence_cut + 1].strip()

    word_cut = sample.rfind(" ")
    if word_cut < int(max_chars * 0.6):
        word_cut = max_chars

    trimmed = sample[:word_cut].rstrip(" ,;:-")
    return f"{trimmed}…"


def now_local():
    # Use system local timezone to avoid UTC rollover generating "tomorrow" titles/dates.
    return datetime.now().astimezone()


def parse_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


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


def source_default_category(source_name, fallback="ecosystem"):
    fallback_value = fallback if fallback in CATEGORY_CONFIG else "ecosystem"
    return SOURCE_DEFAULT_CATEGORY.get((source_name or "").strip(), fallback_value)


def _looks_like_release_update(text, url):
    content = (text or "").lower()
    link = (url or "").lower()
    has_version = _VERSION_RE.search(content) is not None
    has_release_url = any(hint in link for hint in RELEASE_URL_HINTS)
    has_release_text = any(hint in content for hint in RELEASE_TEXT_HINTS)
    has_version_context = any(hint in content for hint in RELEASE_VERSION_CONTEXT_HINTS)
    has_non_release_hint = any(hint in content for hint in NON_RELEASE_GOVERNANCE_HINTS)

    if has_release_url and (has_version or "kubernetes" in content or "k8s" in content):
        return True

    if has_release_text and ("kubernetes" in content or "k8s" in content or has_version):
        return True

    if has_version and ("kubernetes" in content or "k8s" in content) and has_version_context:
        return True

    if has_non_release_hint and not (has_version and has_release_text):
        return False

    return False


def infer_category(title, summary, default="ecosystem", url=""):
    default_category = default if default in CATEGORY_CONFIG else "ecosystem"
    text = f"{title or ''} {summary or ''}".lower()
    link = (url or "").lower()

    if SECURITY_RE.search(text):
        return "security"

    if "github.com" in link:
        return "tool-radar"
    if any(hint in text for hint in TOOL_HINTS) and default_category == "tool-radar":
        return "tool-radar"

    if _looks_like_release_update(text, link):
        return "releases"

    return default_category


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
