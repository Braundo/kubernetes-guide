import html
import logging
import re

import requests

log = logging.getLogger("source_context")

UA = "k8s-guide-news-bot/2.1 (+https://k8s.guide)"
TIMEOUT = 12
MAX_EXCERPT_CHARS = 3200
_CACHE = {}


def _clean_html_to_text(raw_html):
    text = raw_html or ""
    text = re.sub(r"(?is)<(script|style|noscript|svg|iframe)[^>]*>.*?</\1>", " ", text)
    text = re.sub(r"(?is)<br\s*/?>", "\n", text)
    text = re.sub(r"(?is)</p\s*>", "\n\n", text)
    text = re.sub(r"(?is)</li\s*>", "\n", text)
    text = re.sub(r"(?is)<li[^>]*>", "- ", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = html.unescape(text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_primary_html(raw_html):
    content = raw_html or ""
    for tag in ("article", "main"):
        pattern = re.compile(rf"(?is)<{tag}\b[^>]*>(.*?)</{tag}>")
        matches = pattern.findall(content)
        if matches:
            return max(matches, key=len)

    body_match = re.search(r"(?is)<body\b[^>]*>(.*?)</body>", content)
    if body_match:
        return body_match.group(1)
    return content


def _compact_excerpt(text, max_chars=MAX_EXCERPT_CHARS):
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text or "") if p.strip()]
    chosen = []
    size = 0
    for para in paragraphs:
        if len(para) < 80:
            continue
        if para.lower().startswith(("cookie", "privacy", "subscribe", "sign up", "copyright")):
            continue
        if size + len(para) > max_chars and chosen:
            break
        chosen.append(para)
        size += len(para)
        if len(chosen) >= 6:
            break
    return "\n\n".join(chosen).strip()


def fetch_source_excerpt(url, max_chars=MAX_EXCERPT_CHARS):
    if not url:
        return ""
    if url in _CACHE:
        return _CACHE[url]

    try:
        response = requests.get(url, headers={"User-Agent": UA}, timeout=TIMEOUT)
        response.raise_for_status()
        html_blob = response.text or ""
        primary = _extract_primary_html(html_blob)
        cleaned = _clean_html_to_text(primary)
        excerpt = _compact_excerpt(cleaned, max_chars=max_chars)
    except Exception as exc:
        log.debug(f"source excerpt fetch failed for {url}: {exc}")
        excerpt = ""

    _CACHE[url] = excerpt
    return excerpt
