# k8s.guide Updates Pipeline

This pipeline publishes curated update content into the `Updates` section only.

## Canonical output locations

- `docs/updates/security/`
- `docs/updates/releases/`
- `docs/updates/ecosystem/`
- `docs/updates/tool-radar/`

Each category also updates its own landing table:

- `docs/updates/<category>/index.md` between `AUTO-LATEST` markers.

## Run command (recommended)

From the repo root:

```bash
.venv/bin/pip install -r requirements.txt
LLM_PROVIDER=anthropic \
LLM_API_KEY=YOUR_ANTHROPIC_KEY \
GITHUB_TOKEN=YOUR_GITHUB_TOKEN \
.venv/bin/python data/k8s_factory/run_pipeline.py --github
```

## What gets committed and pushed

`run_pipeline.py` commits generated updates from:

- `docs/updates/`
- `data/k8s_factory/plan.json`

Then pushes to `origin main`, which triggers site publish.

## URL pattern after publish

- `/updates/security/<slug>/`
- `/updates/releases/<slug>/`
- `/updates/ecosystem/<slug>/`
- `/updates/tool-radar/<slug>/`
