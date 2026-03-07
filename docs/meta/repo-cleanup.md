---
title: Repository Cleanup Summary (March 2026)
---

# Repository Cleanup Summary (March 2026)

## Purpose

Align file layout with the live site information architecture and remove legacy paths that no longer match navigation.

## Final Content Structure

- Learning and operations content remains in:
  - `docs/getting-started/`
  - `docs/workloads/`
  - `docs/networking/`
  - `docs/configuration/`
  - `docs/security/`
  - `docs/operations/`
  - `docs/storage/`
- Certification content:
  - `docs/certifications/`
- News content (canonical generated namespace):
  - `docs/news/releases/`
  - `docs/news/security/`
  - `docs/news/ecosystem/`
  - `docs/news/tool-radar/`
- Business and conversion pages:
  - `docs/jobs/`
  - `docs/sponsor/`
  - `docs/resources/recommended-resources.md`
  - `docs/about/index.md`

## Removed Legacy Sections and Files

- Removed legacy Updates tree: `docs/updates/`
- Removed legacy tool/reference entry stubs:
  - `docs/tools/index.md`
  - `docs/reference/index.md`
- Removed legacy jobs landing bridge:
  - `docs/jobs/index.md`
- Removed unused resource pages not present in nav:
  - `docs/resources/about.md`
  - `docs/resources/quiz.md`
- Removed stale duplicate asset:
  - `docs/logo-v2.png`
- Removed macOS artifacts under docs:
  - `.DS_Store` files

## Path and Naming Alignment

- Replaced `intelligence/*` paths with `news/*`.
- Replaced `tools/radar/*` generated stream path with `news/tool-radar/*`.
- Updated navigation and internal links to match the new canonical layout.
- Maintained `News` as a nav container (expand/collapse), not a standalone page.

## Validation

- `python -m compileall data/k8s_factory` passes.
- `python -m zensical build` passes.
- Internal markdown link audit reports `0` broken links.
