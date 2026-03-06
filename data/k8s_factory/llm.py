import os, logging, requests
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("llm")
TIMEOUT = 120

ARTICLE_PROMPT = '''You are a senior technical writer for k8s.guide, a respected
community resource read by platform engineers and SREs who run Kubernetes
in production. Your writing is direct, opinionated, and grounded in
operational experience.

Write an article about this item. Base it ONLY on the provided summary.
Do not invent facts.

ITEM:
- Title: {title}
- Category: {category}
- Published: {published}
- Source: {url}
- Summary: {summary}

Use EXACTLY this structure (raw Markdown, no code fences around output):

## Summary

3-4 sentences. State precisely what happened. Include version numbers,
CVE IDs, or project names. Be factual and specific.

## Why It Matters

2-3 paragraphs of expert analysis. Connect this to real operational
concerns: upgrade paths, security posture, architecture decisions,
migration timelines, breaking changes. Reference Kubernetes concepts
(Gateway API, RBAC, control plane, etcd, CRDs) where relevant.
Write like a staff engineer briefing their platform team Monday morning.

## What You Should Do

4-5 numbered action items. Each MUST be concrete:
- Bad: Review the release notes
- Good: Run kubectl version --short to confirm your cluster version,
  then compare against the patched version in the advisory.
Include commands, config snippets, or specific checks.

## Further Reading

3-4 bullet points with links. Always include the source article.
Add Kubernetes docs, KEPs, or GitHub issues where relevant.

RULES:
- Max 500 words
- No filler phrases ("in this article", "lets dive in", "in conclusion")
- Technical accuracy over completeness
- Present tense for current state, past tense for events
- No Markdown code fences around the entire output
- Never use em dashes. Use commas, periods, hyphens or semicolons instead.
'''

NEWSLETTER_PROMPT = '''You are the editor of the k8s.guide weekly newsletter,
read by Kubernetes practitioners and platform engineers.

Write a weekly digest newsletter from these articles published this week.
The newsletter should feel like a knowledgeable colleague summarizing the
week in Kubernetes over coffee.

ARTICLES THIS WEEK:
{articles_summary}

Write the newsletter in Markdown using this structure:

# This Week in Kubernetes

One paragraph (3-4 sentences) overview of the weeks themes.

## Highlights

For each article, write 2-3 sentences summarizing it and why readers
should care. Use bullet points. Link to each article on k8s.guide.

## Quick Takes

2-3 sentences of editorial perspective: what patterns you see across
this weeks news, what to watch for next week.

## One Thing to Do This Week

A single, specific action item that applies to most readers based on
this weeks news.

RULES:
- Friendly but professional tone -- not corporate, not casual
- Max 600 words
- No "dear readers" or "thanks for reading" -- just content
- Include links to articles using the provided URLs
'''

def _call_anthropic(prompt):
    r = requests.post("https://api.anthropic.com/v1/messages",
        headers={"x-api-key": os.environ.get("LLM_API_KEY",""),
                 "anthropic-version": "2023-06-01",
                 "content-type": "application/json"},
        json={"model": os.environ.get("LLM_MODEL","claude-sonnet-4-5-20250929"),
              "max_tokens": 1500,
              "messages": [{"role":"user","content": prompt}]},
        timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()["content"][0]["text"]

def _call_openai(prompt):
    r = requests.post("https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ.get('LLM_API_KEY','')}",
                 "Content-Type": "application/json"},
        json={"model": os.environ.get("LLM_MODEL","gpt-4o-mini"),
              "max_tokens": 1500,
              "messages": [
                  {"role":"system","content":
                   "You are a senior Kubernetes technical writer."},
                  {"role":"user","content": prompt}]},
        timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def _call(prompt):
    p = os.environ.get("LLM_PROVIDER","anthropic").lower()
    if p == "anthropic": return _call_anthropic(prompt)
    elif p == "openai": return _call_openai(prompt)
    else: raise ValueError(f"Unknown provider: {p}")

def write_article(item):
    prompt = ARTICLE_PROMPT.format(
        title=item.get("title",""), category=item.get("category_hint",""),
        published=item.get("published","")[:10], url=item.get("url",""),
        summary=item.get("summary",""))
    log.info(f"LLM writing: {item.get('title','')[:60]}")
    try:
        return _call(prompt)
    except Exception as e:
        log.error(f"LLM failed: {e}")
        return None

def write_newsletter(articles):
    summaries = []
    for a in articles:
        cat = a.get("category_hint","")
        url_slug = a.get("generated_file","").replace(".md","")
        site_url = f"https://k8s.guide/news/{cat}/{url_slug}/"
        summaries.append(f"- [{a['title']}]({site_url}) "
                        f"(Category: {cat}, Published: "
                        f"{a.get('published','')[:10]})")
    prompt = NEWSLETTER_PROMPT.format(
        articles_summary="\n".join(summaries))
    log.info(f"LLM writing newsletter ({len(articles)} articles)")
    try:
        return _call(prompt)
    except Exception as e:
        log.error(f"Newsletter LLM failed: {e}")
        return None
