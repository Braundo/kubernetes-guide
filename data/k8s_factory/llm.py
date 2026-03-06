import os
import logging
import requests

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("llm")
TIMEOUT = 120

COMMON_RULES = """
Rules:
- Be concise, specific, and operationally useful.
- Do not invent facts outside provided item context.
- Use clean Markdown, no code fences around full output.
- Avoid hype, filler, and broad marketing language.
- No em dashes.
"""

SECURITY_PROMPT = """You are writing for k8s.guide security updates.

Write Markdown with exactly these sections:

## Advisory Summary
## Affected Components and Versions
## Why It Matters
## What to Do

Use the provided item only.

Item:
- Title: {title}
- Published: {published}
- Source: {url}
- Summary: {summary}

{rules}
"""

RELEASE_PROMPT = """You are writing for k8s.guide release updates.

Write Markdown with exactly these sections:

## Release Summary
## Key Changes
## Breaking Changes and Deprecations
## Why It Matters for Operators
## Suggested Actions

Use the provided item only.

Item:
- Title: {title}
- Published: {published}
- Source: {url}
- Summary: {summary}

{rules}
"""

TOOL_PROMPT = """You are writing for k8s.guide tool radar.

Write Markdown with exactly these sections:

## What the Tool Does
## Why It Is Worth Watching
## Maturity and Adoption Notes
## Category

Use the provided item only.

Item:
- Title: {title}
- Published: {published}
- Source: {url}
- Summary: {summary}

{rules}
"""

ECOSYSTEM_PROMPT = """You are writing a curated Kubernetes ecosystem roundup for operators.

Write Markdown with exactly these sections:

## Curated Intro
## Top Signals This Cycle

For "Top Signals This Cycle", include 3 to 7 numbered items. Each item must include:
- signal summary
- one short "Why it matters" sentence

Roundup sources:
{sources}

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
            "max_tokens": 1500,
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
            "max_tokens": 1500,
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


def _sources_text(item):
    sources = item.get("sources") or []
    if not sources:
        return f"- {item.get('title', '')} ({item.get('url', '')})"

    lines = []
    for src in sources[:7]:
        lines.append(f"- {src.get('title', '')} ({src.get('url', '')})")
    return "\n".join(lines)


def write_article(item):
    category = item.get("category_hint", "ecosystem")
    payload = {
        "title": item.get("title", ""),
        "published": (item.get("published", "") or "")[:10],
        "url": item.get("url", ""),
        "summary": item.get("summary", ""),
        "rules": COMMON_RULES,
    }

    if category == "security":
        prompt = SECURITY_PROMPT.format(**payload)
    elif category == "releases":
        prompt = RELEASE_PROMPT.format(**payload)
    elif category == "tool-radar":
        prompt = TOOL_PROMPT.format(**payload)
    else:
        prompt = ECOSYSTEM_PROMPT.format(sources=_sources_text(item), rules=COMMON_RULES)

    log.info(f"LLM writing {category}: {item.get('title', '')[:80]}")
    try:
        return _call(prompt)
    except Exception as exc:
        log.error(f"LLM failed: {exc}")
        return None


def write_newsletter(articles):
    summaries = []
    for article in articles:
        category = article.get("category_hint", "")
        generated_file = (article.get("generated_file") or "").replace(".md", "")
        site_url = f"https://k8s.guide/updates/{category}/{generated_file}/"
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
