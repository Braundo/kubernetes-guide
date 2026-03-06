import json
import os
import re
import logging
from datetime import datetime, timezone

from db import get_db, mark_processed
from llm import write_article
from content_policy import (
    CATEGORY_CONFIG,
    MAX_SLUG_LENGTH,
    SLUG_STOP_WORDS,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("generate")

PLAN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plan.json")


def slugify(title):
    cleaned = re.sub(r"[^a-z0-9\s-]", " ", (title or "").lower())
    tokens = [tok for tok in re.split(r"[\s_-]+", cleaned) if tok and tok not in SLUG_STOP_WORDS]
    if not tokens:
        return "update"

    slug = ""
    for tok in tokens:
        candidate = f"{slug}-{tok}" if slug else tok
        if len(candidate) > MAX_SLUG_LENGTH:
            break
        slug = candidate

    return slug.strip("-") or "update"


def filename_for_item(item):
    published = item.get("published", "")
    try:
        day = datetime.fromisoformat(published.replace("Z", "+00:00")).strftime("%Y-%m-%d")
    except Exception:
        day = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    base = slugify(item.get("title", "untitled"))
    return f"{day}-{base}.md"


def ensure_unique_filename(folder, desired_name):
    if not os.path.exists(os.path.join(folder, desired_name)):
        return desired_name

    stem = desired_name[:-3]
    suffix = 2
    while True:
        candidate = f"{stem}-{suffix}.md"
        if not os.path.exists(os.path.join(folder, candidate)):
            return candidate
        suffix += 1


def first_sentence(text):
    content = (text or "").strip()
    if not content:
        return "Operator-focused Kubernetes update generated from curated sources."
    parts = re.split(r"(?<=[.!?])\s+", content)
    return parts[0][:220]


def source_links(item):
    sources = item.get("sources") or []
    if sources:
        lines = []
        for src in sources[:7]:
            title = src.get("title", "Source")
            url = src.get("url", "")
            lines.append(f"- [{title}]({url})")
        return "\n".join(lines)

    title = item.get("source_name", "Source")
    url = item.get("url", "")
    if url:
        return f"- [{title}]({url})"
    return "- Source unavailable"


def parse_frontmatter(path):
    try:
        with open(path) as handle:
            text = handle.read()
    except OSError:
        return {}

    if not text.startswith("---\n"):
        return {}

    end = text.find("\n---\n", 4)
    if end == -1:
        return {}

    fm = text[4:end].splitlines()
    parsed = {}
    for line in fm:
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        parsed[key.strip()] = val.strip().strip('"')
    return parsed


def extract_excerpt(path):
    try:
        with open(path) as handle:
            text = handle.read()
    except OSError:
        return ""

    if text.startswith("---\n"):
        marker = text.find("\n---\n", 4)
        if marker != -1:
            text = text[marker + 5 :]

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for ln in lines:
        if ln.startswith("#"):
            continue
        if ln.startswith("-"):
            continue
        return ln[:220]
    return ""


def clean_table_cell(value):
    text = (value or "").replace("\n", " ").strip()
    return text.replace("|", "\\|")


def related_links(category, filename):
    cfg = CATEGORY_CONFIG[category]
    root = cfg["output_dir"]

    # Parent index is always first.
    links = [f"- Parent index: [Section index]({cfg['parent_index_rel']})"]

    # Pull up to two recent sibling pages.
    siblings = []
    for name in sorted(os.listdir(root), reverse=True):
        if not name.endswith(".md") or name == "index.md" or name == filename:
            continue
        meta = parse_frontmatter(os.path.join(root, name))
        title = meta.get("title", name.replace(".md", ""))
        siblings.append((title, name))
        if len(siblings) == 2:
            break

    for title, name in siblings:
        links.append(f"- Related: [{title}]({name})")

    if len(siblings) < 2:
        fallback = {
            "security": [
                "- Related: [Release updates](../releases/index.md)",
                "- Related: [Kubernetes security primer](../../security/security.md)",
            ],
            "releases": [
                "- Related: [Security updates](../security/index.md)",
                "- Related: [Maintenance and upgrades](../../operations/maintenance.md)",
            ],
            "ecosystem": [
                "- Related: [Release updates](../releases/index.md)",
                "- Related: [Tool radar](../tool-radar/index.md)",
            ],
            "tool-radar": [
                "- Related: [Security updates](../security/index.md)",
                "- Related: [Release updates](../releases/index.md)",
            ],
        }
        for entry in fallback.get(category, []):
            if entry not in links:
                links.append(entry)
            if len([ln for ln in links if ln.startswith("- Related:")]) >= 2:
                break

    links.append("- Newsletter: [This Week in Kubernetes](../../index.md#weekly-newsletter)")

    evergreen = {
        "security": "- Evergreen reference: [Kubernetes security primer](../../security/security.md)",
        "releases": "- Evergreen reference: [Maintenance and upgrades](../../operations/maintenance.md)",
        "ecosystem": "- Evergreen reference: [Kubernetes learning paths](../../learn/index.md)",
        "tool-radar": "- Evergreen reference: [Kubectl cheat sheet](../../resources/kubectl-cheatsheet.md)",
    }
    links.append(evergreen.get(category, "- Evergreen reference: [Kubernetes learning paths](../../learn/index.md)"))
    return "\n".join(links)


def _safe_int(value):
    try:
        return int(value)
    except Exception:
        return 0


def _parse_iso_date(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def tool_momentum_label(stars, pushed_at):
    pushed = _parse_iso_date(pushed_at)
    if not pushed:
        return "Watch"
    days = (datetime.now(timezone.utc) - pushed).days
    if stars >= 5000 and days <= 45:
        return "Hot"
    if stars >= 1500 and days <= 90:
        return "Rising"
    if days <= 120:
        return "Active"
    return "Watch"


def tool_signals_section(item):
    stars = _safe_int(item.get("stars", 0))
    forks = _safe_int(item.get("forks", 0))
    issues = _safe_int(item.get("open_issues", 0))
    watchers = _safe_int(item.get("watchers", 0))
    pushed = (item.get("last_pushed", "") or "").replace("T", " ")[:10]
    momentum = tool_momentum_label(stars, item.get("last_pushed", ""))
    return (
        "## Popularity and Momentum Signals\n\n"
        "| Signal | Value |\n"
        "| --- | --- |\n"
        f"| GitHub stars | {stars:,} |\n"
        f"| Forks | {forks:,} |\n"
        f"| Open issues | {issues:,} |\n"
        f"| Watchers | {watchers:,} |\n"
        f"| Last push | {pushed or 'unknown'} |\n"
        f"| Momentum label | **{momentum}** |\n"
    )


def build_page(item, body, filename):
    now = datetime.now(timezone.utc).isoformat()
    title = item.get("title", "Untitled")
    category = item.get("category_hint", "ecosystem")
    published = (item.get("published", "") or "")[:10] or now[:10]
    deck = first_sentence(item.get("summary", ""))
    extra = ""
    if category == "tool-radar":
        extra = f"\n\n{tool_signals_section(item)}"

    return (
        "---\n"
        f"title: \"{title}\"\n"
        f"date: {published}\n"
        f"category: {category}\n"
        f"generated: \"{now}\"\n"
        "---\n\n"
        f"# {title}\n\n"
        f"{deck}\n\n"
        f"{body.strip()}{extra}\n\n"
        "## Source Links\n\n"
        f"{source_links(item)}\n\n"
        "## Related Pages\n\n"
        f"{related_links(category, filename)}\n"
    )


def render_index_entries(category):
    cfg = CATEGORY_CONFIG[category]
    root = cfg["output_dir"]

    entries = []
    for name in sorted(os.listdir(root), reverse=True):
        if not name.endswith(".md") or name == "index.md":
            continue
        path = os.path.join(root, name)
        meta = parse_frontmatter(path)
        title = meta.get("title", name.replace(".md", ""))
        date = meta.get("date", "")
        if not date and re.match(r"^\d{4}-\d{2}-\d{2}", name):
            date = name[:10]
        excerpt = meta.get("description") or extract_excerpt(path)
        entries.append((date, title, name, excerpt))

    rows = []
    for date, title, name, excerpt in entries[:12]:
        rows.append(
            f"| {clean_table_cell(date or '-')} | [{clean_table_cell(title)}]({name}) | "
            f"{clean_table_cell(excerpt or 'Operator-focused update.')} |"
        )

    link_col = "Entry" if category == "tool-radar" else "Update"
    table = [
        f"| Date | {link_col} | Summary |",
        "| --- | --- | --- |",
    ]
    if rows:
        table.extend(rows)
    else:
        table.append("| - | No updates yet | New entries will appear here after curation. |")
    return "\n".join(table)


def update_index(category):
    cfg = CATEGORY_CONFIG[category]
    path = cfg["index_file"]
    if not os.path.exists(path):
        return

    with open(path) as handle:
        content = handle.read()

    start = "<!-- AUTO-LATEST:START -->"
    end = "<!-- AUTO-LATEST:END -->"
    if start not in content or end not in content:
        return

    head, tail = content.split(start, 1)
    middle, rest = tail.split(end, 1)
    generated = render_index_entries(category)
    new_content = f"{head}{start}\n{generated}\n{end}{rest}"

    with open(path, "w") as handle:
        handle.write(new_content)


def mark_all_processed(db, item, filename):
    if item.get("id"):
        mark_processed(db, item["id"], filename)

    for source_id in item.get("source_item_ids") or []:
        mark_processed(db, source_id, filename)


def run_generate():
    if not os.path.exists(PLAN):
        log.error("No plan.json")
        return 0

    with open(PLAN) as handle:
        plan = json.load(handle)

    items = plan.get("items", [])
    if not items:
        log.info("Empty plan.")
        return 0

    db = get_db()
    generated = 0
    touched_categories = set()

    for item in items:
        category = item.get("category_hint", "ecosystem")
        cfg = CATEGORY_CONFIG.get(category)
        if not cfg:
            log.warning(f"Unknown category: {category}")
            continue

        os.makedirs(cfg["output_dir"], exist_ok=True)
        desired = filename_for_item(item)
        filename = ensure_unique_filename(cfg["output_dir"], desired)
        path = os.path.join(cfg["output_dir"], filename)

        body = write_article(item)
        if not body:
            log.error(f"LLM failed for {filename}")
            continue

        page = build_page(item, body, filename)
        with open(path, "w") as handle:
            handle.write(page)

        mark_all_processed(db, item, filename)
        touched_categories.add(category)
        generated += 1
        log.info(f"Generated: {path}")

    for category in touched_categories:
        update_index(category)

    db.close()
    log.info(f"Generated {generated} page(s).")
    return generated


if __name__ == "__main__":
    run_generate()
