---
title: "Cluster API v1.12: Introducing In-place Updates and Chained Upgrades"
date: 2026-03-06
category: releases
description: "Cluster API v1.12.0 shipped on January 27, 2026, introducing two significant lifecycle management capabilities: in-place updates and chained upgrades."
generated: "2026-03-06T21:12:15.984802-06:00"
---

# Cluster API v1.12: Introducing In-place Updates and Chained Upgrades

Cluster API v1.12.0 shipped on January 27, 2026, introducing two significant lifecycle management capabilities: in-place updates and chained upgrades.

## Release Summary

This release focuses on lowering upgrade and lifecycle friction in real-world Cluster API operations. In-place updates and chained upgrades reduce the amount of manual orchestration required during routine cluster changes while preserving the declarative workflow platform teams already use. For operators managing many clusters, that translates into safer upgrade sequencing and fewer brittle runbook steps.

## Key Changes

**In-place updates** change how CAPI handles certain Machine spec modifications. Previously, any change to a Machine spec triggered a rollout - a new Machine is created and the old one deleted, mirroring how Kubernetes handles Pod replacement in Deployments. With v1.12.0, CAPI can now apply eligible changes directly to existing Machines without replacement, when doing so is safe and appropriate. The controller determines which path to take; operators continue editing the Cluster or Machine spec exactly as before.

**Chained upgrades** address sequencing complexity when multiple upgrade steps are required across a cluster. Rather than operators manually orchestrating the order of control plane and worker upgrades, CAPI now chains dependent upgrade operations automatically. This is particularly relevant when upgrading Kubernetes versions across a KubeadmControlPlane and associated MachineDeployments, where ordering constraints must be respected.

Both features are surfaced through the existing declarative API. No new spec fields or feature gate toggles are required to opt in to the default behavior - the controller evaluates conditions at reconciliation time and selects the appropriate strategy.

## Breaking Changes and Deprecations

The v1.12.0 announcement does not enumerate specific API deprecations or removals. Before upgrading, run the following audit against your environment:

- **CRD version checks**: Confirm all CAPI CRDs in use (Cluster, Machine, MachineDeployment, KubeadmControlPlane, and provider-specific resources) are at API versions supported by v1.12.0. Remove any references to previously deprecated alpha versions if your manifests still carry them.
- **Provider compatibility**: Verify that your infrastructure provider (CAPZ, CAPA, CAPV, etc.) has released a version explicitly tested against CAPI v1.12.0. In-place update behavior may depend on provider-level hooks; mismatched providers may fall back to replacement rollouts or fail reconciliation.
- **Webhook configurations**: Review any MutatingWebhookConfigurations or ValidatingWebhookConfigurations targeting CAPI resources. Changes to reconciliation paths could interact unexpectedly with custom admission logic that assumes rollout-only behavior.
- **GitOps and automation pipelines**: If CI pipelines or GitOps controllers watch Machine status for rollout completion signals, validate that in-place update status transitions expose equivalent conditions. Pipelines keyed on Machine replacement events may not fire during in-place updates.
- **Cluster topology users**: If you use ClusterClass-based topology, test mutation behavior in a non-production cluster first. Chained upgrade logic interacts with topology reconciliation; confirm the sequencing matches your upgrade runbooks.

## Why It Matters for Operators

Rolling replacement has been the only available strategy in CAPI for most Machine spec changes. For large clusters or environments where node replacement is expensive - due to licensing, hardware provisioning time, or stateful workloads - this created pressure to batch changes or avoid them altogether. In-place updates lower that cost for eligible mutations.

Chained upgrades remove a class of manual intervention that platform teams have historically scripted around. Kubernetes version upgrades across control plane and worker tiers require strict ordering, and CAPI previously left that sequencing to the operator. Automating it reduces the window for human error during version bumps and tightens upgrade execution time.

Together, these changes make CAPI clusters more practical to operate at scale, particularly for teams managing many clusters with overlapping lifecycle events.

## Upgrade Actions

1. Review your infrastructure provider's release notes and confirm a v1.12.0-compatible version is available before upgrading CAPI core.
2. Audit active MachineDeployment and KubeadmControlPlane objects for any spec fields referencing deprecated API constructs from earlier CAPI versions.
3. Test in-place update behavior in a staging cluster by applying a low-risk Machine spec change and confirming the controller selects the expected strategy via `kubectl describe` on the Machine object.
4. Update any pipeline health checks that rely on Machine replacement events to also handle in-place update status conditions.
5. If using ClusterClass topology, run a dry-run upgrade against a non-production cluster before applying chained upgrade workflows in production.
6. Pin provider versions explicitly in your management cluster deployment manifests to prevent accidental mismatches after the CAPI core upgrade.

## Source Links

- [Kubernetes Blog](https://kubernetes.io/blog/2026/01/27/cluster-api-v1-12-release/)

## Related Pages

- Parent index: [News](index.md)
- Related: [News](index.md)
- Related: [Maintenance and upgrades](../operations/maintenance.md)
- Newsletter: [This Week in Kubernetes](../index.md#weekly-newsletter)
- Evergreen reference: [Maintenance and upgrades](../operations/maintenance.md)
