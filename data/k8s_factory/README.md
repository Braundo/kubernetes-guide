# k8s.guide News Pipeline

This pipeline publishes curated content into the `News` section only.
It is configured for quality-first output (low volume, higher editorial depth).

## Canonical output locations

- `docs/news/security/`
- `docs/news/releases/`
- `docs/news/ecosystem/`
- `docs/news/tool-radar/`

Each category also refreshes its own landing table:

- `docs/news/<category>/index.md` between `AUTO-LATEST` markers.

## Run command (recommended)

From the repo root:

```bash
.venv/bin/pip install -r requirements.txt
LLM_PROVIDER=anthropic \
LLM_API_KEY=YOUR_ANTHROPIC_KEY \
GITHUB_TOKEN=YOUR_GITHUB_TOKEN \
.venv/bin/python data/k8s_factory/run_pipeline.py --github
```

## Human-in-the-loop review flow

The default run now pauses before writing articles and publishing.

Step 1: propose topics

```bash
.venv/bin/python data/k8s_factory/run_pipeline.py --github
```

This writes:

- `data/k8s_factory/review_topics.md`
- `data/k8s_factory/review_state.json`

Step 2: approve what to publish

```bash
# Publish specific topics
.venv/bin/python data/k8s_factory/run_pipeline.py --approve 1,3

# Publish all proposed topics
.venv/bin/python data/k8s_factory/run_pipeline.py --approve all

# Publish none (skip all proposed topics)
.venv/bin/python data/k8s_factory/run_pipeline.py --approve none
```

Optional bypass (fully automatic):

```bash
.venv/bin/python data/k8s_factory/run_pipeline.py --github --auto-publish
```

## What gets committed and pushed

`run_pipeline.py` commits generated news pages from:

- `docs/news/`

Then pushes to `origin main`, which triggers site publish.

## Editorial quality controls

- Drafts are generated with source-page context excerpts, not RSS summaries alone.
- The writer retries a limited number of times when quality checks fail (default: 2 attempts, configurable).
- Hard quality gates reject drafts that are:
  - too short by category
  - missing required section depth
  - using banned filler phrases (for example "details were not provided")
  - using bot-like placeholders such as `Curated Intro`.
- `run_pipeline.py` performs a final markdown quality verification before commit/push.

## Anthropic rate-limit safeguards

The writer includes built-in throttling and retry/backoff to stay under account-level token/request limits.

Optional environment variables:

- `LLM_MAX_TOKENS` (default `1700`): per-call output cap.
- `LLM_MIN_CALL_INTERVAL_SECONDS` (default `20`): minimum spacing between API calls.
- `LLM_RATE_LIMIT_RETRIES` (default `6`): retry attempts for 429/5xx responses.
- `LLM_BASE_BACKOFF_SECONDS` (default `6`): exponential backoff base.
- `LLM_MAX_DRAFT_ATTEMPTS` (default `3`): quality-revision attempts per article.
- `LLM_INPUT_TOKENS_PER_MIN_BUDGET` (default `18000`): client-side input token budget per rolling minute.
- `LLM_OUTPUT_TOKENS_PER_MIN_BUDGET` (default `5500`): client-side output token budget per rolling minute.
- `LLM_MAX_PRIMARY_EXCERPT_CHARS` (default `1800`): source excerpt cap for single-source pages.
- `LLM_MAX_ROUNDUP_SOURCE_EXCERPT_CHARS` (default `500`): per-source excerpt cap for ecosystem roundups.
- `LLM_MAX_ROUNDUP_SOURCES` (default `6`): max source count passed to one ecosystem generation call.
- `LLM_MAX_CONTEXT_CHARS` (default `7000`): hard cap for prompt context block.
- `PIPELINE_LOCK_STALE_SECONDS` (default `21600`): stale lock cleanup window.
- `PIPELINE_MAX_ITEMS_PER_RUN` (default `1`): analyze-time cap on total candidates selected into a plan.
- `PIPELINE_MAX_GENERATE_PER_RUN` (default `1`): final publish cap per run (applies to approved and auto-publish modes).

### Recommended profile: maximum quality within Tier-1 limits

```bash
LLM_PROVIDER=anthropic \
LLM_MODEL=claude-sonnet-4-6 \
LLM_MAX_TOKENS=1700 \
LLM_MAX_DRAFT_ATTEMPTS=3 \
LLM_MIN_CALL_INTERVAL_SECONDS=20 \
LLM_INPUT_TOKENS_PER_MIN_BUDGET=18000 \
LLM_OUTPUT_TOKENS_PER_MIN_BUDGET=5500 \
LLM_BASE_BACKOFF_SECONDS=6 \
PIPELINE_MAX_ITEMS_PER_RUN=1 \
PIPELINE_MAX_GENERATE_PER_RUN=1 \
.venv/bin/python data/k8s_factory/run_pipeline.py --github
```

## URL pattern after publish

- `/news/security/<slug>/`
- `/news/releases/<slug>/`
- `/news/ecosystem/<slug>/`
- `/news/tool-radar/<slug>/`
