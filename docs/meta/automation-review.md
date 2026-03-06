---
title: Automation Pipeline Review (March 2026)
---

# Automation Pipeline Review (March 2026)

This document records the post-cleanup review of the update-generation pipeline and the changes made to align it with the live site structure.

## Scope Reviewed

- Source ingestion and classification: `crawler.py`
- Scoring, dedupe, and selection: `analyze.py`
- Content policy and output paths: `content_policy.py`
- Markdown generation and index refresh: `generate.py`
- Newsletter synthesis links: `llm.py` and `newsletter.py`
- Commit/publish automation: `run_pipeline.py`

## Structural Alignment Changes

- Generated content root moved from mixed paths to one canonical namespace:
  - `docs/updates/releases/`
  - `docs/updates/security/`
  - `docs/updates/ecosystem/`
  - `docs/updates/tool-radar/`
- Pipeline commit tracking updated to `docs/updates/` only.
- Commit message namespace updated from `feat(intelligence)` to `feat(updates)`.
- Newsletter canonical links now point to `/updates/<category>/<slug>/`.

## Quality and Cadence Guardrails

`content_policy.py` was tuned to reduce daily noise while preserving event-driven coverage:

- Run caps:
  - Security: 2
  - Releases: 1
  - Ecosystem: 1
  - Tool Radar: 1
- Daily caps:
  - Security: 4
  - Releases: 2
  - Ecosystem: 1
  - Tool Radar: 1
- Weekly caps:
  - Security: 12
  - Releases: 5
  - Ecosystem: 4
  - Tool Radar: 2

This keeps security and release responsiveness while preventing tool/ecosystem spam.

## Bug and Drift Fixes

- GitHub tool query no longer uses a hardcoded stale date. It now uses a rolling 90-day push window.
- Tool radar watcher metric now uses `watchers_count` from GitHub search results instead of `subscribers_count`.
- Related-link generation now resolves to `updates/*` paths and no longer references removed `intelligence/*` paths.

## Operational Notes

- Generated page validation still enforces required sections (`Source Links`, `Related Pages`) before commit/push.
- Ecosystem remains curated as a single roundup candidate (3-7 items) when sufficient quality signals exist.
- Newsletter remains home-anchored for subscribers (`/#weekly-newsletter`) while generation archives stay outside published docs.
