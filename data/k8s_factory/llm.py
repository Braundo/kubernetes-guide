import os
import logging
import requests

from editorial_quality import assess_markdown_quality
from source_context import fetch_source_excerpt

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("llm")
TIMEOUT = 120
MAX_ATTEMPTS = 3

COMMON_RULES = """
Editorial rules:
- Write like a senior platform engineer briefing peers.
- Prioritize concrete operator impact, not generic commentary.
- Do not invent facts beyond the provided context blocks.
- Use clean Markdown only, no code fences around the full response.
- No hype language, no fluff, no self-referential AI wording.
- Never include source bylines, editor names, or author credits.
- Never use placeholder phrases like "details were not provided".
"""

SECURITY_PROMPT = """You are writing publication-grade security news for k8s.guide.

Write Markdown with exactly these H2 sections in this order:

## Advisory Summary
## Affected Components and Versions
## Why It Matters
## Recommended Actions

Depth requirements:
- Target 350-750 words.
- Every section must include meaningful details.
- "Recommended Actions" must include a numbered plan with concrete validation steps.

{context_block}

{revision_block}

{rules}
"""

RELEASE_PROMPT = """You are writing publication-grade release news for k8s.guide.

Write Markdown with exactly these H2 sections in this order:

## Release Summary
## Key Changes
## Breaking Changes and Deprecations
## Why It Matters for Operators
## Upgrade Actions

Depth requirements:
- Target 450-900 words.
- Use concrete release details from source context.
- "Breaking Changes and Deprecations" must include specific risk checks.
- If an official source does not enumerate deprecations, provide a concrete audit checklist instead of vague disclaimers.

{context_block}

{revision_block}

{rules}
"""

TOOL_PROMPT = """You are writing publication-grade tool radar coverage for k8s.guide.

Write Markdown with exactly these H2 sections in this order:

## What the Tool Does
## Why It Matters
## Adoption and Maturity Signals
## Recommended Use Cases

Depth requirements:
- Target 320-650 words.
- Connect capabilities to real Kubernetes platform workflows.
- "Recommended Use Cases" should include where this tool fits and where it may not fit.

{context_block}

{revision_block}

{rules}
"""

ECOSYSTEM_PROMPT = """You are writing a high-signal Kubernetes ecosystem briefing for k8s.guide.

Write Markdown with exactly these H2 sections in this order:

## Overview
## Top Stories and Operator Takeaways

Formatting requirements for "Top Stories and Operator Takeaways":
- Include 3 to 6 H3 story subheadings in this format: `### <story title>`.
- Under each story subheading, include:
  1) what changed and why the signal matters in context
  2) a clear operator takeaway with near-term implications/actions

Depth requirements:
- Target 600-1100 words.
- The article must read like an editorial briefing, not scraped notes.
- Do not use headings like "Curated Intro" or "Top Signals This Cycle".

{context_block}

{revision_block}

{rules}
"""

NEWSLETTER_PROMPT = """You are the editor of the k8s.guide weekly newsletter.

Write Markdown with this structure:

# This Week in Kubernetes
## Highlights
## Quick Takes
## One Thing to Do This Week

Articles:
{articles_summary}

Rules:
- Max 600 words
- Focus on operator impact and actionability
- No filler greetings
"""


def _call_anthropic(prompt):
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": os.environ.get("LLM_API_KEY", ""),
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": os.environ.get("LLM_MODEL", "claude-sonnet-4-5-20250929"),
            "max_tokens": 2200,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["content"][0]["text"]


def _call_openai(prompt):
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.environ.get('LLM_API_KEY', '')}",
            "Content-Type": "application/json",
        },
        json={
            "model": os.environ.get("LLM_MODEL", "gpt-4o-mini"),
            "max_tokens": 2200,
            "messages": [
                {"role": "system", "content": "You are a senior Kubernetes technical editor."},
                {"role": "user", "content": prompt},
            ],
        },
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def _call(prompt):
    provider = (os.environ.get("LLM_PROVIDER", "anthropic") or "anthropic").lower()
    if provider == "anthropic":
        return _call_anthropic(prompt)
    if provider == "openai":
        return _call_openai(prompt)
    raise ValueError(f"Unknown provider: {provider}")


def _limit(text, max_chars):
    content = (text or "").strip()
    if len(content) <= max_chars:
        return content
    return content[: max_chars - 1].rstrip() + "…"


def _revision_block(issues):
    if not issues:
        return ""
    bullets = "\n".join(f"- {issue}" for issue in issues[:8])
    return (
        "Revise the draft to fix these quality issues before finalizing:\n"
        f"{bullets}\n"
    )


def _item_context(item):
    lines = [
        "Primary source context:",
        f"- Title: {item.get('title', '')}",
        f"- Source URL: {item.get('url', '')}",
        f"- Source published date: {(item.get('published', '') or '')[:10] or 'unknown'}",
        f"- Feed summary: {_limit(item.get('summary', '') or '', 800)}",
    ]

    source_excerpt = fetch_source_excerpt(item.get("url", ""), max_chars=2400)
    if source_excerpt:
        lines.append("\nSource page excerpt:\n" + _limit(source_excerpt, 2400))

    if item.get("category_hint") == "tool-radar":
        lines.extend(
            [
                "",
                "GitHub signals:",
                f"- Stars: {int(item.get('stars', 0) or 0):,}",
                f"- Forks: {int(item.get('forks', 0) or 0):,}",
                f"- Open issues: {int(item.get('open_issues', 0) or 0):,}",
                f"- Watchers: {int(item.get('watchers', 0) or 0):,}",
                f"- Last push: {(item.get('last_pushed', '') or '')[:10] or 'unknown'}",
            ]
        )

    return "\n".join(lines).strip()


def _roundup_context(item):
    sources = item.get("sources") or []
    if not sources:
        return _item_context(item)

    lines = []
    lines.append("Roundup source set:")
    for idx, src in enumerate(sources[:7], 1):
        title = src.get("title", "")
        url = src.get("url", "")
        published = (src.get("published", "") or "")[:10] or "unknown"
        excerpt = fetch_source_excerpt(url, max_chars=1000)
        lines.append(f"\n{idx}. {title}")
        lines.append(f"   - URL: {url}")
        lines.append(f"   - Published: {published}")
        if excerpt:
            lines.append(f"   - Source excerpt: {_limit(excerpt, 900)}")
    return "\n".join(lines).strip()


def _build_prompt(category, payload, issues):
    revision_block = _revision_block(issues)
    context_block = payload.get("context_block", "")
    rules = payload.get("rules", COMMON_RULES)

    if category == "security":
        return SECURITY_PROMPT.format(
            context_block=context_block,
            revision_block=revision_block,
            rules=rules,
        )
    if category == "releases":
        return RELEASE_PROMPT.format(
            context_block=context_block,
            revision_block=revision_block,
            rules=rules,
        )
    if category == "tool-radar":
        return TOOL_PROMPT.format(
            context_block=context_block,
            revision_block=revision_block,
            rules=rules,
        )
    return ECOSYSTEM_PROMPT.format(
        context_block=context_block,
        revision_block=revision_block,
        rules=rules,
    )


def write_article(item):
    category = item.get("category_hint", "ecosystem")
    payload = {"rules": COMMON_RULES}
    payload["context_block"] = _roundup_context(item) if category == "ecosystem" else _item_context(item)

    last_issues = []
    log.info(f"LLM writing {category}: {item.get('title', '')[:80]}")
    for attempt in range(1, MAX_ATTEMPTS + 1):
        prompt = _build_prompt(category, payload, last_issues)
        try:
            draft = _call(prompt)
        except Exception as exc:
            log.error(f"LLM failed (attempt {attempt}/{MAX_ATTEMPTS}): {exc}")
            continue

        issues = assess_markdown_quality(category, draft)
        if not issues:
            return draft

        last_issues = issues
        issue_preview = "; ".join(issues[:3])
        log.warning(
            f"LLM draft quality issues for {category} attempt {attempt}/{MAX_ATTEMPTS}: {issue_preview}"
        )

    log.error(f"LLM quality gate failed for {category}: {'; '.join(last_issues[:5])}")
    return None


def write_newsletter(articles):
    summaries = []
    for article in articles:
        category = article.get("category_hint", "")
        generated_file = (article.get("generated_file") or "").replace(".md", "")
        site_url = f"https://k8s.guide/news/{category}/{generated_file}/"
        summaries.append(
            f"- [{article.get('title', '')}]({site_url}) (Category: {category}, Published: {(article.get('published') or '')[:10]})"
        )

    prompt = NEWSLETTER_PROMPT.format(articles_summary="\n".join(summaries))
    log.info(f"LLM writing newsletter ({len(articles)} articles)")
    try:
        return _call(prompt)
    except Exception as exc:
        log.error(f"Newsletter LLM failed: {exc}")
        return None
