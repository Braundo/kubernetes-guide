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
    "security": 300,
    "releases": 430,
    "ecosystem": 700,
    "tool-radar": 320,
}

MIN_SECTION_WORDS = {
    "security": {
        "Advisory Summary": 60,
        "Affected Components and Versions": 45,
        "Why It Matters": 80,
        "Recommended Actions": 80,
    },
    "releases": {
        "Release Summary": 75,
        "Key Changes": 100,
        "Breaking Changes and Deprecations": 90,
        "Why It Matters for Operators": 90,
        "Upgrade Actions": 85,
    },
    "ecosystem": {
        "Overview": 150,
        "Top Stories and Operator Takeaways": 430,
    },
    "tool-radar": {
        "What the Tool Does": 65,
        "Why It Matters": 95,
        "Adoption and Maturity Signals": 65,
        "Recommended Use Cases": 85,
    },
}

MIN_SECTION_SENTENCES = {
    "security": {
        "Advisory Summary": 2,
        "Affected Components and Versions": 2,
        "Why It Matters": 3,
        "Recommended Actions": 3,
    },
    "releases": {
        "Release Summary": 3,
        "Key Changes": 4,
        "Breaking Changes and Deprecations": 4,
        "Why It Matters for Operators": 4,
        "Upgrade Actions": 4,
    },
    "ecosystem": {
        "Overview": 4,
        "Top Stories and Operator Takeaways": 10,
    },
    "tool-radar": {
        "What the Tool Does": 3,
        "Why It Matters": 4,
        "Adoption and Maturity Signals": 3,
        "Recommended Use Cases": 4,
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
EM_DASH = "\u2014"
EN_DASH = "\u2013"


def required_sections_for(category):
    return REQUIRED_SECTIONS.get(category, [])


def word_count(text):
    return len(WORD_RE.findall(text or ""))


def sentence_count(text):
    pieces = re.split(r"(?<=[.!?])\s+", (text or "").strip())
    return len([piece for piece in pieces if WORD_RE.search(piece or "")])


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

    if EM_DASH in text:
        issues.append("contains em dash character; use commas or hyphens")
    if EN_DASH in text:
        issues.append("contains en dash character; use hyphen")

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

    sentence_limits = MIN_SECTION_SENTENCES.get(category, {})
    for name, min_sentences in sentence_limits.items():
        if name not in sections:
            continue
        count = sentence_count(sections.get(name, ""))
        if count < min_sentences:
            issues.append(
                f"section '{name}' is too shallow: {count} sentences (minimum {min_sentences})"
            )

    if category == "ecosystem" and "Top Stories and Operator Takeaways" in sections:
        stories = _h3_sections(sections["Top Stories and Operator Takeaways"])
        if len(stories) < 3:
            issues.append("ecosystem section needs at least 3 story subheadings (###)")
        if len(stories) > 7:
            issues.append("ecosystem section should not exceed 7 story subheadings (###)")
        for title, body in stories:
            wc = word_count(body)
            if wc < 120:
                issues.append(f"story '{title}' is too short: {wc} words (minimum 120)")
            if sentence_count(body) < 4:
                issues.append(f"story '{title}' lacks depth: fewer than 4 sentences")
            paragraphs = [p for p in re.split(r"\n\s*\n", body) if p.strip()]
            if len(paragraphs) < 2:
                issues.append(f"story '{title}' must contain at least 2 paragraphs")

    if category == "releases" and "Breaking Changes and Deprecations" in sections:
        body = sections["Breaking Changes and Deprecations"].lower()
        if "none" in body and word_count(body) < 45:
            issues.append("breaking changes section is vague; add concrete audit/verification steps")
        if "not a code release" in lower or "process and governance artifact" in lower:
            issues.append("release article appears misclassified; route this item to ecosystem")

    return issues
