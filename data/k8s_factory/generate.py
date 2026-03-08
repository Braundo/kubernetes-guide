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
    now_local,
    infer_category,
    source_default_category,
    truncate_text,
)
from editorial_quality import assess_markdown_quality

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("generate")

PLAN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plan.json")

BYLINE_LINE_RE = re.compile(r"(?i)^\s*(editors?|author|authors?)\s*:\s*")
BYLINE_PREFIX_RE = re.compile(r"(?i)^\s*by\s+[A-Z]")
BYLINE_SENTENCE_RE = re.compile(r"(?i)\b(editors?|author|authors?|written by|byline)\b")
INDEX_MAX_AGE_DAYS = {
    "security": 45,
    "releases": 45,
    "ecosystem": 30,
    "tool-radar": 60,
}
EM_DASH = "\u2014"
EN_DASH = "\u2013"


def slugify(title):
    cleaned = re.sub(r"[^a-z0-9\s-]", " ", (title or "").lower())
    tokens = [tok for tok in re.split(r"[\s_-]+", cleaned) if tok and tok not in SLUG_STOP_WORDS]
    if not tokens:
        return "news"

    slug = ""
    for tok in tokens:
        candidate = f"{slug}-{tok}" if slug else tok
        if len(candidate) > MAX_SLUG_LENGTH:
            break
        slug = candidate

    return slug.strip("-") or "news"


def normalized_item_title(item):
    category = item.get("category_hint", "ecosystem")
    raw = strip_byline_sentences(item.get("title", "Untitled")) or "Untitled"

    if category == "tool-radar":
        base = raw.split(":", 1)[0].strip()
        if "/" in base:
            base = base.split("/")[-1].strip()
        base = re.sub(r"(?i)\btool\s*radar\b", "", base).strip(" -:")
        base = re.sub(r"\s+\([^)]*\)\s*$", "", base).strip()
        if not base:
            base = "Kubernetes Tool"
        return base

    if category == "ecosystem" and raw.lower().startswith("kubernetes ecosystem roundup"):
        return "Kubernetes ecosystem roundup"

    return raw


def display_entry_title(category, title):
    text = (title or "").strip()
    if category != "tool-radar":
        return text
    text = re.sub(r"(?i)\s+tool\s*radar\b", "", text).strip()
    text = re.sub(r"\s+\([^)]*\)\s*$", "", text).strip()
    return text or "Tool"


def filename_for_item(item):
    day = now_local().strftime("%Y-%m-%d")
    base = slugify(normalized_item_title(item))
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


def strip_byline_sentences(text):
    content = (text or "").strip()
    if not content:
        return ""
    pieces = re.split(r"(?<=[.!?])\s+", content)
    kept = []
    for piece in pieces:
        if BYLINE_SENTENCE_RE.search(piece):
            continue
        kept.append(piece)
    return " ".join(kept).strip()


def is_byline_line(line):
    content = (line or "").strip()
    if not content:
        return False
    if BYLINE_LINE_RE.match(content):
        return True
    if BYLINE_PREFIX_RE.match(content):
        return True
    return False


def _strip_md_emphasis(text):
    return re.sub(r"[*_`]+", "", (text or "")).strip()


def normalize_dash_punctuation(text):
    content = (text or "")
    if not content:
        return ""
    content = content.replace(EM_DASH, " - ")
    content = content.replace(EN_DASH, "-")
    content = re.sub(r"[ \t]+-[ \t]+", " - ", content)
    return content


def normalize_ordered_list_numbers(text):
    lines = (text or "").splitlines()
    out = []
    in_list = False
    counter = 1
    for line in lines:
        marker = re.match(r"^(\s*)\d+\.\s+(.*)$", line)
        if marker:
            if not in_list:
                in_list = True
                counter = 1
            out.append(f"{marker.group(1)}{counter}. {marker.group(2)}")
            counter += 1
            continue

        out.append(line)
        if in_list and re.match(r"^\s*##+\s+", line):
            in_list = False
    return "\n".join(out)


def normalize_ecosystem_top_stories(text):
    match = re.search(r"^## Top Stories and Operator Takeaways\s*$", text, flags=re.MULTILINE)
    if not match:
        return text

    start = match.end()
    next_section = re.search(r"^##\s+", text[start:], flags=re.MULTILINE)
    section_end = start + next_section.start() if next_section else len(text)
    section = text[start:section_end]

    items = []
    current = None
    for raw in section.splitlines():
        line = raw.strip()
        marker = re.match(r"^(?:\d+\.|[-*])\s+(.*)$", line)
        if marker:
            if current:
                items.append(current)
            current = {"title": _strip_md_emphasis(marker.group(1)), "body": []}
            continue

        if current is None:
            continue
        if not line:
            if current["body"] and current["body"][-1] != "":
                current["body"].append("")
            continue
        current["body"].append(line)

    if current:
        items.append(current)

    if len(items) < 2:
        return text

    rebuilt = ["## Top Stories and Operator Takeaways", ""]
    for idx, item in enumerate(items, 1):
        title = item["title"] or f"Signal {idx}"
        rebuilt.append(f"### {title}")
        rebuilt.append("")
        paragraph = re.sub(r"\s+", " ", " ".join([ln for ln in item["body"] if ln])).strip()
        if paragraph:
            rebuilt.append(paragraph)
        else:
            rebuilt.append(
                "Validate whether this development changes platform roadmap, "
                "cluster policy, upgrade sequencing, or day-2 operations."
            )
        rebuilt.append("")

    new_section = "\n".join(rebuilt).rstrip() + "\n"
    return text[: match.start()] + new_section + text[section_end:]


def sanitize_generated_body(text, category):
    content = normalize_dash_punctuation((text or "").replace("\r\n", "\n")).strip()
    if not content:
        return ""

    lines = []
    for line in content.splitlines():
        if is_byline_line(line):
            continue
        lines.append(line)
    content = "\n".join(lines)
    content = normalize_ordered_list_numbers(content)
    if category == "ecosystem":
        content = normalize_ecosystem_top_stories(content)
    return content.strip()


def _cmp_text(text):
    normalized = re.sub(r"\s+", " ", (text or "")).strip().lower()
    normalized = normalized.replace("…", "...")
    normalized = normalized.strip("\"'` ")
    normalized = re.sub(r"[.?!:;]+$", "", normalized)
    return normalized


def _is_duplicate_deck_sentence(first_sentence, deck):
    first_cmp = _cmp_text(first_sentence)
    deck_cmp = _cmp_text(deck)
    if not first_cmp or not deck_cmp:
        return False
    if first_cmp == deck_cmp:
        return True

    # Decks are often intentionally truncated with an ellipsis.
    first_head = re.sub(r"(?:\.\.\.)+$", "", first_cmp).strip()
    deck_head = re.sub(r"(?:\.\.\.)+$", "", deck_cmp).strip()
    if not first_head or not deck_head:
        return False
    if first_head.startswith(deck_head):
        return True
    if deck_head.startswith(first_head) and len(first_head) >= 40:
        return True
    return False


def strip_duplicate_deck_from_body(body, deck):
    content = (body or "").strip()
    if not content or not _cmp_text(deck):
        return content

    lines = content.splitlines()
    for idx, line in enumerate(lines):
        current = line.strip()
        if not current:
            continue
        if current.startswith("#"):
            continue
        if re.match(r"^[-*]\s+", current):
            continue
        if re.match(r"^\d+\.\s+", current):
            continue

        paragraph_end = idx
        paragraph_lines = []
        while paragraph_end < len(lines):
            part = lines[paragraph_end].strip()
            if not part:
                break
            if paragraph_end > idx and part.startswith("#"):
                break
            paragraph_lines.append(part)
            paragraph_end += 1

        paragraph = re.sub(r"\s+", " ", " ".join(paragraph_lines)).strip()
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", paragraph) if s.strip()]
        if not sentences:
            return content

        first_sentence = sentences[0]
        if not _is_duplicate_deck_sentence(first_sentence, deck):
            return content

        remainder = " ".join(sentences[1:]).strip()
        if remainder:
            lines[idx] = remainder
            for i in range(idx + 1, paragraph_end):
                lines[i] = ""
        else:
            for i in range(idx, paragraph_end):
                lines[i] = ""
        return "\n".join(lines).strip()

    return content


def first_sentence(text):
    content = strip_byline_sentences(text)
    if not content:
        return "Operator-focused Kubernetes news generated from curated sources."
    parts = re.split(r"(?<=[.!?])\s+", content)
    seed = parts[0] if parts else content
    return truncate_text(seed, max_chars=220, prefer_sentence=False)


def deck_from_body(body, fallback):
    lines = [ln.strip() for ln in (body or "").splitlines() if ln.strip()]
    for ln in lines:
        if ln.startswith("#"):
            continue
        if re.match(r"^[-*]\s+", ln):
            continue
        if re.match(r"^\d+\.\s+", ln):
            continue
        candidate = re.sub(r"\s+", " ", ln).strip()
        if len(candidate) >= 50:
            return truncate_text(candidate, max_chars=220, prefer_sentence=True)
    return fallback


def source_links(item):
    sources = item.get("sources") or []
    if sources:
        lines = []
        for src in sources[:7]:
            title = strip_byline_sentences(src.get("title", "Source")) or "Source"
            title = normalize_dash_punctuation(title)
            url = src.get("url", "")
            lines.append(f"- [{title}]({url})")
        return "\n".join(lines)

    title = normalize_dash_punctuation(item.get("source_name", "Source"))
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
        if is_byline_line(ln) or BYLINE_SENTENCE_RE.search(ln):
            continue
        return truncate_text(ln, max_chars=220, prefer_sentence=True)
    return ""


def clean_table_cell(value):
    text = normalize_dash_punctuation((value or "").replace("\n", " ").strip())
    return text.replace("|", "\\|")


def yaml_quote(value):
    return (value or "").replace("\\", "\\\\").replace('"', '\\"')


def parse_date_value(value):
    if not value:
        return None
    try:
        return datetime.strptime((value or "")[:10], "%Y-%m-%d").date()
    except Exception:
        return None


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
        label = display_entry_title(category, title)
        links.append(f"- Related: [{label}]({name})")

    if len(siblings) < 2:
        fallback = {
            "security": [
                "- Related: [Release news](../releases/index.md)",
                "- Related: [Kubernetes security primer](../../security/security.md)",
            ],
            "releases": [
                "- Related: [Security news](../security/index.md)",
                "- Related: [Maintenance and upgrades](../../operations/maintenance.md)",
            ],
            "ecosystem": [
                "- Related: [Release news](../releases/index.md)",
                "- Related: [Tool radar](../tool-radar/index.md)",
            ],
            "tool-radar": [
                "- Related: [Security news](../security/index.md)",
                "- Related: [Release news](../releases/index.md)",
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
    now = now_local()
    if pushed.tzinfo is None:
        pushed = pushed.replace(tzinfo=timezone.utc)
    days = (now - pushed.astimezone(now.tzinfo)).days
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
    now_dt = now_local()
    now = now_dt.isoformat()
    title = normalize_dash_punctuation(normalized_item_title(item))
    category = item.get("category_hint", "ecosystem")
    published = now_dt.strftime("%Y-%m-%d")
    deck = normalize_dash_punctuation(deck_from_body(body, first_sentence(item.get("summary", ""))))
    body = strip_duplicate_deck_from_body(body, deck)
    extra = ""
    if category == "tool-radar":
        extra = f"\n\n{tool_signals_section(item)}"

    return (
        "---\n"
        f"title: \"{yaml_quote(title)}\"\n"
        f"date: {published}\n"
        f"category: {category}\n"
        f"description: \"{yaml_quote(deck)}\"\n"
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
    today = now_local().date()
    max_age_days = INDEX_MAX_AGE_DAYS.get(category, 45)

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
        date_obj = parse_date_value(date)
        if date_obj:
            age = (today - date_obj).days
            if age < 0 or age > max_age_days:
                continue
        excerpt = meta.get("description") or extract_excerpt(path)
        if BYLINE_SENTENCE_RE.search(excerpt):
            excerpt = "Operator-focused news."
        excerpt = truncate_text(excerpt, max_chars=220, prefer_sentence=True)
        entries.append((date, title, name, excerpt))

    rows = []
    for date, title, name, excerpt in entries[:12]:
        display_title = display_entry_title(category, title)
        rows.append(
            f"| {clean_table_cell(date or '-')} | [{clean_table_cell(display_title)}]({name}) | "
            f"{clean_table_cell(excerpt or 'Operator-focused news.')} |"
        )

    link_col = "Tool" if category == "tool-radar" else "News"
    table = [
        f"| Date | {link_col} | Summary |",
        "| --- | --- | --- |",
    ]
    if rows:
        table.extend(rows)
    else:
        table.append("| - | No news yet | New entries will appear here after curation. |")
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


def run_generate(plan_items=None):
    if plan_items is None:
        if not os.path.exists(PLAN):
            log.error("No plan.json")
            return 0
        with open(PLAN) as handle:
            plan = json.load(handle)
        items = plan.get("items", [])
    else:
        items = plan_items

    if not items:
        log.info("Empty plan.")
        return 0

    db = get_db()
    generated = 0
    touched_categories = set()

    for item in items:
        original = item.get("category_hint", "ecosystem")
        default = source_default_category(item.get("source_name", ""), original)
        category = infer_category(
            title=item.get("title", ""),
            summary=item.get("summary", ""),
            default=default,
            url=item.get("url", ""),
        )
        if category != original:
            log.info(
                "Reclassified generate candidate: %s -> %s | %s",
                original,
                category,
                item.get("title", "")[:90],
            )
        item["category_hint"] = category
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
        body = sanitize_generated_body(body, category)
        if not body:
            log.error(f"Generated body empty after sanitization for {filename}")
            continue
        quality_issues = assess_markdown_quality(category, body)
        if quality_issues:
            log.error(
                f"Generated body failed quality gate for {filename}: "
                + "; ".join(quality_issues[:5])
            )
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
