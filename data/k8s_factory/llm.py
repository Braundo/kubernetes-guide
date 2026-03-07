import os
import logging
import time
import random
import email.utils
import json
from collections import deque
from datetime import datetime, timezone
import requests

from editorial_quality import assess_markdown_quality
from source_context import fetch_source_excerpt

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("llm")
TIMEOUT = 120
MAX_ATTEMPTS = int(os.environ.get("LLM_MAX_DRAFT_ATTEMPTS", "3"))
MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "1700"))
MIN_CALL_INTERVAL_SECONDS = float(os.environ.get("LLM_MIN_CALL_INTERVAL_SECONDS", "20"))
RATE_LIMIT_RETRIES = int(os.environ.get("LLM_RATE_LIMIT_RETRIES", "6"))
BASE_BACKOFF_SECONDS = float(os.environ.get("LLM_BASE_BACKOFF_SECONDS", "6"))
_LAST_CALL_MONOTONIC = 0.0
INPUT_TOKENS_PER_MIN_BUDGET = int(os.environ.get("LLM_INPUT_TOKENS_PER_MIN_BUDGET", "18000"))
OUTPUT_TOKENS_PER_MIN_BUDGET = int(os.environ.get("LLM_OUTPUT_TOKENS_PER_MIN_BUDGET", "5500"))
TOKEN_WINDOW_SECONDS = 60.0
_TOKEN_RESERVATIONS = deque()
MAX_PRIMARY_EXCERPT_CHARS = int(os.environ.get("LLM_MAX_PRIMARY_EXCERPT_CHARS", "1800"))
MAX_ROUNDUP_SOURCE_EXCERPT_CHARS = int(os.environ.get("LLM_MAX_ROUNDUP_SOURCE_EXCERPT_CHARS", "500"))
MAX_ROUNDUP_SOURCES = int(os.environ.get("LLM_MAX_ROUNDUP_SOURCES", "6"))
MAX_CONTEXT_CHARS = int(os.environ.get("LLM_MAX_CONTEXT_CHARS", "7000"))
_CONFIG_LOGGED = False

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
- Target 300-650 words.
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
- Target 380-750 words.
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
- Target 280-520 words.
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
- Target 520-900 words.
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
    data = _post_with_retry(
        url="https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": os.environ.get("LLM_API_KEY", ""),
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        payload={
            "model": os.environ.get("LLM_MODEL", "claude-sonnet-4-5-20250929"),
            "max_tokens": MAX_TOKENS,
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    usage = data.get("usage") or {}
    log.info(
        "Anthropic usage: input_tokens=%s output_tokens=%s",
        usage.get("input_tokens", "?"),
        usage.get("output_tokens", "?"),
    )
    return data["content"][0]["text"]


def _call_openai(prompt):
    data = _post_with_retry(
        url="https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.environ.get('LLM_API_KEY', '')}",
            "Content-Type": "application/json",
        },
        payload={
            "model": os.environ.get("LLM_MODEL", "gpt-4o-mini"),
            "max_tokens": MAX_TOKENS,
            "messages": [
                {"role": "system", "content": "You are a senior Kubernetes technical editor."},
                {"role": "user", "content": prompt},
            ],
        },
    )
    usage = data.get("usage") or {}
    log.info(
        "OpenAI usage: prompt_tokens=%s completion_tokens=%s",
        usage.get("prompt_tokens", "?"),
        usage.get("completion_tokens", "?"),
    )
    return data["choices"][0]["message"]["content"]


def _estimate_tokens(text):
    # Coarse estimate that works well enough for guardrail throttling.
    return max(1, int((len(text or "") + 3) / 4))


def _prune_token_window(now):
    while _TOKEN_RESERVATIONS and (now - _TOKEN_RESERVATIONS[0][0]) > TOKEN_WINDOW_SECONDS:
        _TOKEN_RESERVATIONS.popleft()


def _token_window_usage(now):
    _prune_token_window(now)
    in_used = sum(entry[1] for entry in _TOKEN_RESERVATIONS)
    out_used = sum(entry[2] for entry in _TOKEN_RESERVATIONS)
    return in_used, out_used


def _reserve_token_budget(prompt_text):
    est_in = _estimate_tokens(prompt_text)
    est_out = MAX_TOKENS

    while True:
        now = time.monotonic()
        used_in, used_out = _token_window_usage(now)

        in_ok = (used_in + est_in) <= INPUT_TOKENS_PER_MIN_BUDGET
        out_ok = (used_out + est_out) <= OUTPUT_TOKENS_PER_MIN_BUDGET
        if in_ok and out_ok:
            _TOKEN_RESERVATIONS.append((now, est_in, est_out))
            return

        if _TOKEN_RESERVATIONS:
            oldest_ts = _TOKEN_RESERVATIONS[0][0]
            wait = max(0.5, TOKEN_WINDOW_SECONDS - (now - oldest_ts) + 0.05)
        else:
            wait = 1.0

        log.info(
            "LLM token budget throttle: in_used=%s/%s out_used=%s/%s, sleeping %.1fs",
            used_in,
            INPUT_TOKENS_PER_MIN_BUDGET,
            used_out,
            OUTPUT_TOKENS_PER_MIN_BUDGET,
            wait,
        )
        time.sleep(min(wait, 5.0))


def _payload_text(payload):
    messages = payload.get("messages") or []
    if messages:
        parts = []
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                parts.append(content)
            else:
                parts.append(json.dumps(content, default=str))
        return "\n".join(parts)
    return json.dumps(payload, default=str)


def _extract_usage_tokens(response_json):
    usage = response_json.get("usage") or {}
    # Anthropic
    if "input_tokens" in usage or "output_tokens" in usage:
        return int(usage.get("input_tokens", 0) or 0), int(usage.get("output_tokens", 0) or 0)
    # OpenAI
    if "prompt_tokens" in usage or "completion_tokens" in usage:
        return int(usage.get("prompt_tokens", 0) or 0), int(usage.get("completion_tokens", 0) or 0)
    return None, None


def _update_last_token_reservation(actual_in, actual_out):
    if not _TOKEN_RESERVATIONS:
        return
    ts, reserved_in, reserved_out = _TOKEN_RESERVATIONS[-1]
    in_tokens = reserved_in if actual_in is None or actual_in <= 0 else actual_in
    out_tokens = reserved_out if actual_out is None or actual_out <= 0 else actual_out
    _TOKEN_RESERVATIONS[-1] = (ts, in_tokens, out_tokens)


def _throttle_before_call(prompt_text):
    global _LAST_CALL_MONOTONIC
    if MIN_CALL_INTERVAL_SECONDS <= 0:
        _reserve_token_budget(prompt_text)
        return

    while True:
        now = time.monotonic()
        elapsed = now - _LAST_CALL_MONOTONIC
        wait = MIN_CALL_INTERVAL_SECONDS - elapsed
        if wait > 0:
            time.sleep(wait)
            continue
        break

    _reserve_token_budget(prompt_text)


def _seconds_until_header_time(raw_value):
    value = (raw_value or "").strip()
    if not value:
        return None

    if value.isdigit():
        num = int(value)
        # Could be either delta seconds or unix timestamp.
        if num > 2_000_000_000:
            delta = num - int(time.time())
            return max(0, min(delta, 300))
        return max(0, min(num, 300))

    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        delta = (dt - datetime.now(timezone.utc)).total_seconds()
        return max(0, min(int(delta), 300))
    except Exception:
        pass

    try:
        dt = email.utils.parsedate_to_datetime(value)
        if dt is not None:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            delta = (dt - datetime.now(timezone.utc)).total_seconds()
            return max(0, min(int(delta), 300))
    except Exception:
        pass

    return None


def _retry_delay_seconds(response, attempt):
    retry_after = _seconds_until_header_time(response.headers.get("retry-after"))
    if retry_after is not None:
        return max(1, retry_after)

    for key in [
        "anthropic-ratelimit-output-tokens-reset",
        "anthropic-ratelimit-input-tokens-reset",
        "anthropic-ratelimit-requests-reset",
        "x-ratelimit-reset",
    ]:
        delay = _seconds_until_header_time(response.headers.get(key))
        if delay is not None:
            return max(1, delay)

    backoff = BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))
    jitter = random.uniform(0, 1.0)
    return min(120, backoff + jitter)


def _post_with_retry(url, headers, payload):
    global _LAST_CALL_MONOTONIC
    last_error = None
    prompt_text = _payload_text(payload)
    for attempt in range(1, RATE_LIMIT_RETRIES + 1):
        _throttle_before_call(prompt_text)
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=TIMEOUT,
        )
        _LAST_CALL_MONOTONIC = time.monotonic()

        if response.status_code in (429, 500, 502, 503, 504, 529):
            delay = _retry_delay_seconds(response, attempt)
            log.warning(
                "LLM API throttled/capacity-limited (status=%s, attempt=%s/%s). Sleeping %.1fs.",
                response.status_code,
                attempt,
                RATE_LIMIT_RETRIES,
                delay,
            )
            last_error = RuntimeError(f"HTTP {response.status_code}: {response.text[:200]}")
            if attempt < RATE_LIMIT_RETRIES:
                time.sleep(delay)
                continue

        try:
            response.raise_for_status()
            response_json = response.json()
            actual_in, actual_out = _extract_usage_tokens(response_json)
            _update_last_token_reservation(actual_in, actual_out)
            return response_json
        except Exception as exc:
            last_error = exc
            if attempt >= RATE_LIMIT_RETRIES:
                break
            delay = _retry_delay_seconds(response, attempt)
            log.warning(
                "LLM API call failed (attempt=%s/%s): %s. Retrying in %.1fs.",
                attempt,
                RATE_LIMIT_RETRIES,
                exc,
                delay,
            )
            time.sleep(delay)

    if last_error:
        raise last_error
    raise RuntimeError("LLM API call failed with unknown error")


def _call(prompt):
    provider = (os.environ.get("LLM_PROVIDER", "anthropic") or "anthropic").lower()
    if provider == "anthropic":
        return _call_anthropic(prompt)
    if provider == "openai":
        return _call_openai(prompt)
    raise ValueError(f"Unknown provider: {provider}")


def _log_runtime_config_once():
    global _CONFIG_LOGGED
    if _CONFIG_LOGGED:
        return
    _CONFIG_LOGGED = True
    log.info(
        "LLM runtime config: provider=%s model=%s max_tokens=%s max_attempts=%s min_interval=%ss in_budget=%s out_budget=%s",
        (os.environ.get("LLM_PROVIDER", "anthropic") or "anthropic"),
        os.environ.get("LLM_MODEL", "claude-sonnet-4-5-20250929"),
        MAX_TOKENS,
        MAX_ATTEMPTS,
        MIN_CALL_INTERVAL_SECONDS,
        INPUT_TOKENS_PER_MIN_BUDGET,
        OUTPUT_TOKENS_PER_MIN_BUDGET,
    )


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

    source_excerpt = fetch_source_excerpt(item.get("url", ""), max_chars=MAX_PRIMARY_EXCERPT_CHARS)
    if source_excerpt:
        lines.append("\nSource page excerpt:\n" + _limit(source_excerpt, MAX_PRIMARY_EXCERPT_CHARS))

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
    for idx, src in enumerate(sources[:MAX_ROUNDUP_SOURCES], 1):
        title = src.get("title", "")
        url = src.get("url", "")
        published = (src.get("published", "") or "")[:10] or "unknown"
        excerpt = fetch_source_excerpt(url, max_chars=MAX_ROUNDUP_SOURCE_EXCERPT_CHARS)
        lines.append(f"\n{idx}. {title}")
        lines.append(f"   - URL: {url}")
        lines.append(f"   - Published: {published}")
        if excerpt:
            lines.append(f"   - Source excerpt: {_limit(excerpt, MAX_ROUNDUP_SOURCE_EXCERPT_CHARS)}")
    context = "\n".join(lines).strip()
    return _limit(context, MAX_CONTEXT_CHARS)


def _build_prompt(category, payload, issues):
    revision_block = _revision_block(issues)
    context_block = _limit(payload.get("context_block", ""), MAX_CONTEXT_CHARS)
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
    _log_runtime_config_once()
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
    _log_runtime_config_once()
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
