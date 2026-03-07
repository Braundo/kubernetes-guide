---
title: Site Architecture and Publishing Model (2026 Refresh)
---

# Site Architecture and Publishing Model (2026 Refresh)

This document records the current structure and publishing model for k8s.guide.

## Goals

- keep learning content in one coherent section
- publish clear, actionable Kubernetes news
- reduce navigation clutter and improve wayfinding
- support newsletter, sponsorship, jobs, and affiliate-ready resources

## Top-Level Structure

- Home
- Learn Kubernetes
- Certificates
- News
- Jobs
- About

`News` is a navigation container with subpages only (no standalone landing page).

`Jobs` is organized as two subpages:

- Listings
- Contact

## Learning Structure

Learning/reference material is grouped in `Learn Kubernetes` under:

- Foundations
- Workloads
- Networking
- Configuration
- Security Fundamentals
- Operations

## News Structure

Curated news lives in:

- `docs/news/releases/`
- `docs/news/security/`
- `docs/news/ecosystem/`
- `docs/news/tool-radar/`

## URL and Slug Policy

- lowercase only
- concise and human-readable
- stop words removed where possible
- target max length about 60 chars
- date prefixes for chronology-sensitive news

## Template Standards

### Security news pages

- Advisory Summary
- Affected Components and Versions
- Why It Matters
- Recommended Actions
- Source Links
- Related Pages

### Release news pages

- Release Summary
- Key Changes
- Breaking Changes and Deprecations
- Why It Matters for Operators
- Upgrade Actions
- Source Links
- Related Pages

### Tool radar pages

- What the Tool Does
- Why It Matters
- Adoption and Maturity Signals
- Recommended Use Cases
- Popularity and Momentum Signals
- Source Links
- Related Tools and Comparisons

### Ecosystem news pages

- Overview
- Top Stories and Operator Takeaways (3 to 6 story subsections)
- Source Links
- Related Pages

## Internal Linking Rules

Each generated page links to:

- parent section index
- at least two related pages
- home newsletter section
- one relevant evergreen learning page

## Publishing Cadence Policy

Target mix by output volume:

- 30% security news
- 25% release/upgrade news
- 25% tools/reference news
- 20% ecosystem news

Cadence guardrails:

- Security: event-driven, publish quickly when high-confidence advisories appear
- Releases: publish on major/minor release events and notable operator-impact news
- Tool radar: weekly or twice-weekly, not daily
- Ecosystem: maximum one curated roundup per day, usually fewer
- Newsletter: one weekly synthesis from highest-scoring items

## Source Policy

Pipeline uses approved sources with scoring, dedupe, and quality thresholds before generation.

## Navigation Policy

Generated leaf pages are not listed in primary nav. Section landing pages provide curated entry points.
