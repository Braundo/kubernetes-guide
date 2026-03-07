import re

REQUIRED_SECTIONS = {
    "security": [
        "## Advisory Summary",
        "## Affected Components and Versions",
        "## Why It Matters",
        "## Recommended Actions",
    ],
    "releases": [
        "## Release Summary",
        "## Key Changes",
        "## Breaking Changes and Deprecations",
        "## Why It Matters for Operators",
        "## Upgrade Actions",
    ],
    "ecosystem": [
        "## Overview",
        "## Top Stories and Operator Takeaways",
    ],
    "tool-radar": [
        "## What the Tool Does",
        "## Why It Matters",
        "## Adoption and Maturity Signals",
        "## Recommended Use Cases",
    ],
}

MIN_TOTAL_WORDS = {
    "security": 260,
    "releases": 340,
    "ecosystem": 560,
    "tool-radar": 240,
}

MIN_SECTION_WORDS = {
    "security": {
        "Advisory Summary": 45,
        "Affected Components and Versions": 35,
        "Why It Matters": 55,
        "Recommended Actions": 55,
    },
    "releases": {
        "Release Summary": 50,
        "Key Changes": 70,
        "Breaking Changes and Deprecations": 60,
        "Why It Matters for Operators": 60,
        "Upgrade Actions": 55,
    },
    "ecosystem": {
        "Overview": 120,
        "Top Stories and Operator Takeaways": 320,
    },
    "tool-radar": {
        "What the Tool Does": 45,
        "Why It Matters": 55,
        "Adoption and Maturity Signals": 45,
        "Recommended Use Cases": 45,
    },
}

BANNED_PHRASES = [
    "specific details were not provided",
    "details were not provided",
    "not provided in the release announcement",
    "curated intro",
    "top signals this cycle",
    "signal under review",
    "as an ai",
    "language model",
    "editors:",
    "author:",
    "authors:",
    "operator takeaway:",
    "why it matters:",
]

WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'/-]*")
H2_RE = re.compile(r"(?m)^##\s+(.+?)\s*$")
H3_RE = re.compile(r"(?m)^###\s+(.+?)\s*$")


def required_sections_for(category):
    return REQUIRED_SECTIONS.get(category, [])


def word_count(text):
    return len(WORD_RE.findall(text or ""))


def _sections(text):
    content = text or ""
    matches = list(H2_RE.finditer(content))
    parsed = {}
    for idx, match in enumerate(matches):
        name = match.group(1).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
        parsed[name] = content[start:end].strip()
    return parsed


def _h3_sections(text):
    content = text or ""
    matches = list(H3_RE.finditer(content))
    parsed = []
    for idx, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
        parsed.append((title, content[start:end].strip()))
    return parsed


def assess_markdown_quality(category, markdown_text):
    issues = []
    text = (markdown_text or "").strip()
    lower = text.lower()

    for phrase in BANNED_PHRASES:
        if phrase in lower:
            issues.append(f"contains banned filler phrase: {phrase}")

    required = required_sections_for(category)
    sections = _sections(text)
    for heading in required:
        name = heading.replace("## ", "", 1).strip()
        if name not in sections:
            issues.append(f"missing required section: {heading}")

    total = word_count(text)
    min_total = MIN_TOTAL_WORDS.get(category, 200)
    if total < min_total:
        issues.append(f"too short: {total} words (minimum {min_total})")

    section_limits = MIN_SECTION_WORDS.get(category, {})
    for name, min_words in section_limits.items():
        if name not in sections:
            continue
        section_words = word_count(sections.get(name, ""))
        if section_words < min_words:
            issues.append(
                f"section '{name}' is too thin: {section_words} words (minimum {min_words})"
            )

    if category == "ecosystem" and "Top Stories and Operator Takeaways" in sections:
        stories = _h3_sections(sections["Top Stories and Operator Takeaways"])
        if len(stories) < 3:
            issues.append("ecosystem section needs at least 3 story subheadings (###)")
        if len(stories) > 7:
            issues.append("ecosystem section should not exceed 7 story subheadings (###)")
        for title, body in stories:
            wc = word_count(body)
            if wc < 80:
                issues.append(f"story '{title}' is too short: {wc} words (minimum 80)")

    if category == "releases" and "Breaking Changes and Deprecations" in sections:
        body = sections["Breaking Changes and Deprecations"].lower()
        if "none" in body and word_count(body) < 45:
            issues.append("breaking changes section is vague; add concrete audit/verification steps")
        if "not a code release" in lower or "process and governance artifact" in lower:
            issues.append("release article appears misclassified; route this item to ecosystem")

    return issues
