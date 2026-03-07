# k8s.guide News Pipeline

This pipeline publishes curated content into the `News` section only.

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
- The writer retries up to 3 times when quality checks fail.
- Hard quality gates reject drafts that are:
  - too short by category
  - missing required section depth
  - using banned filler phrases (for example "details were not provided")
  - using bot-like placeholders such as `Curated Intro`.
- `run_pipeline.py` performs a final markdown quality verification before commit/push.

## URL pattern after publish

- `/news/security/<slug>/`
- `/news/releases/<slug>/`
- `/news/ecosystem/<slug>/`
- `/news/tool-radar/<slug>/`
