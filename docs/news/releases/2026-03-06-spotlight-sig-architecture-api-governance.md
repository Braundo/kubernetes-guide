---
title: "Spotlight on SIG Architecture: API Governance"
date: 2026-03-06
category: releases
description: "The Kubernetes SIG Architecture blog series has published its fifth installment, this time focusing on the API Governance sub-project. The piece is an interview with Jordan Liggitt, who has served as an API reviewer sinc"
generated: "2026-03-06T20:47:21.232512-06:00"
---

# Spotlight on SIG Architecture: API Governance

The Kubernetes SIG Architecture blog series has published its fifth installment, this time focusing on the API Governance sub-project. The piece is an interview with Jordan Liggitt, who has served as an API reviewer sinc

## Release Summary

The Kubernetes SIG Architecture blog series has published its fifth installment, this time focusing on the API Governance sub-project. The piece is an interview with Jordan Liggitt, who has served as an API reviewer since 2016 and API approver since 2017, and who has been a continuous contributor to Kubernetes since 2014. The interview surfaces the organizational structure and mandate of API Governance, a sub-project that sits within SIG Architecture and holds direct influence over what APIs enter the Kubernetes codebase, how they evolve, and when they are deprecated or removed.

## Key Changes

This post is a process and governance artifact rather than a code release, but it carries operational weight because API Governance decisions directly gate what surfaces in every Kubernetes release. Key points from the interview:

- **API Governance lineage**: Jordan Liggitt has been shaping Kubernetes APIs from the early beta era, including the transition from v1beta3 to v1, giving the sub-project deep institutional context on API stability contracts.
- **Sub-project scope**: API Governance owns review and approval authority over all additions to and modifications of core Kubernetes APIs. This is the team that evaluates KEPs affecting API surface before they proceed.
- **Reviewer and approver pipeline**: The interview confirms the two-tier model—API reviewers and API approvers—which is the gate that controls API promotion, deprecation timelines, and compatibility guarantees. Understanding this pipeline matters when teams are planning feature adoption timelines.
- **Authentication and authorization origins**: Liggitt's background includes building Kubernetes auth primitives, which continues to inform how API Governance evaluates security-adjacent API changes.

## Breaking Changes and Deprecations

The source does not enumerate specific deprecations or removals tied to a numbered release. Because API Governance is the body that controls deprecation schedules, operators should treat this as a prompt to audit their clusters against known API lifecycle rules. Use the following checklist:

- **Run `kubectl api-resources`** and cross-reference all resource versions in active manifests against the Kubernetes API deprecation policy (minimum three release deprecation window for GA APIs).
- **Check for any beta APIs in production workloads**. Beta APIs carry no long-term stability guarantee and are subject to removal after two releases following deprecation notice.
- **Audit admission webhooks and CRD conversion webhooks** that reference specific API versions—these break silently when a version is removed.
- **Review stored object versions in etcd** using `etcd-check` or the API server's storage version migration tooling. Objects stored at a deprecated version may not survive an API removal.
- **Inspect RBAC rules** that grant access to versioned resources. Removed API versions invalidate version-specific RBAC bindings without warning.
- **Audit any tools in CI/CD pipelines** (Helm charts, kustomize bases, Argo/Flux manifests) that pin deprecated API versions.

## Why It Matters for Operators

API Governance is not an abstract committee. It is the function that determines whether a feature you depend on becomes stable, stays in beta indefinitely, or gets removed. Knowing that this sub-project operates with a long-tenured lead who has shaped API contracts since the pre-1.0 era tells you the review bar is high and deprecation decisions are deliberate, not accidental. When API Governance signals intent to deprecate or graduate an API, that signal should immediately trigger migration planning—not observation. Operators who treat beta APIs as stable references will eventually absorb the cost of this sub-project doing its job correctly.

The two-tier reviewer/approver structure also means API changes move through a defined human gate, which has historically kept Kubernetes API surface more stable than comparable projects. That stability is a product of this governance structure, and understanding who enforces it helps operators interpret the reliability signals embedded in API version strings.

## Upgrade Actions

- Subscribe to the Kubernetes changelog and KEP tracker for any API Governance-tagged proposals affecting APIs you currently consume.
- Run a full API version audit before any minor version upgrade using `kubectl convert` and the deprecation warnings emitted at API server startup.
- Map your workload manifests, Helm values, and operator CRDs against the current API lifecycle matrix and flag anything at alpha or beta that lacks a migration path.
- Engage with SIG Architecture API Governance via the `#sig-architecture` Slack channel or bi-weekly meetings if you have production APIs in a deprecation window and need clarity on timeline.

## Source Links

- [Kubernetes Blog](https://kubernetes.io/blog/2026/02/12/sig-architecture-api-spotlight/)

## Related Pages

- Parent index: [Section index](index.md)
- Related: [Before You Migrate: Five Surprising Ingress-NGINX Behaviors You Need to Know](2026-03-06-before-migrate-five-surprising-ingress-nginx-behaviors-need.md)
- Related: [Security news](../security/index.md)
- Newsletter: [This Week in Kubernetes](../../index.md#weekly-newsletter)
- Evergreen reference: [Maintenance and upgrades](../../operations/maintenance.md)
