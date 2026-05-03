---
title: "Kubernetes 1.35 GA: In-Place Pod Resizing Stable and Restart Semantics Formalized"
date: 2026-03-28
category: releases
description: "Kubernetes 1.35 has reached general availability with in-place pod resource resizing now stable. This release resolves a critical terminology gap that has caused operational confusion across production environments."
generated: "2026-03-28T15:00:12.917430-05:00"
---

# Kubernetes 1.35 GA: In-Place Pod Resizing Stable and Restart Semantics Formalized

Kubernetes 1.35 has reached general availability with in-place pod resource resizing now stable. This release resolves a critical terminology gap that has caused operational confusion across production environments.

## Release Summary

The distinction between container restarts, pod recreation, and in-place resizing directly affects how operators interpret metrics, write runbooks, and respond to incidents. The distinction between container restarts, pod recreation, and in-place resizing directly affects how operators interpret metrics, write runbooks, and respond to incidents. Understanding when the pod UID changes versus when restart counts increment is no longer academic theory but required knowledge for accurate troubleshooting. The release clarifies kubelet behavior around spec watching and configuration updates, addressing the root cause of numerous "why didn't my config apply?" investigations that waste on-call time.

## Key Changes

In-place pod resource resizing for CPU and memory has graduated to GA in 1.35. CPU adjustments happen without incrementing the restart counter and without changing pod UID or IP. Memory resizing behavior depends on the resize policy: with the RestartContainer policy, memory changes increment the restart count by one while preserving pod identity. This means operators can now adjust resource limits on running pods without triggering full pod recreation, which previously required draining nodes or rolling updates.

The release formalizes how kubelet monitors pod specifications. Kubelet only reacts to changes in the pod spec itself, not to referenced ConfigMaps, Secrets, or custom resources like Istio service mesh configurations. When these external objects change, kubelet remains idle unless the pod spec hash changes. This explains why configuration updates often appear to fail when operators expect automatic propagation.

Mutating admission webhooks now have explicit boundary conditions. They modify pod specs only at creation time during the admission phase. After a pod passes admission, these webhooks cannot trigger container restarts or spec modifications. This limitation affects workflows that assumed post-creation mutation was possible for configuration drift correction or runtime policy enforcement.

The restart count metric now has clear semantics tied to pod UID persistence. When a container process restarts inside an existing pod, the restart count increments and pod UID remains unchanged. During pod recreation events like rolling updates or node drains, the pod UID changes and restart count resets to zero. This reset behavior has caused operators to miss chronic restart patterns when they span pod recreation boundaries.

## Breaking Changes and Deprecations

No explicit API deprecations were announced in the provided context. Operators should audit their monitoring and alerting infrastructure against the clarified restart semantics:

- Check if restart count alerts account for pod UID changes that reset counters to zero. Alerts that only watch restart count without tracking pod recreation will miss failures.
- Verify that runbooks distinguish between container restarts (same UID, counter increments) and pod recreation (new UID, counter resets). Incorrect terminology leads to wrong troubleshooting paths.
- Review configuration update workflows that assume kubelet watches ConfigMaps or Secrets. These patterns require pod spec changes or manual pod deletion to take effect.
- Audit automation that relies on mutating webhooks to modify running pods post-admission. These workflows will silently fail as webhooks only fire during creation.
- Validate resource resize policies in production workloads. Memory resizes with RestartContainer policy increment restart counts, potentially triggering false-positive alerts.

## Why It Matters for Operators

The formalization of restart semantics in 1.35 directly affects incident response accuracy. When an on-call engineer sees a restart count of 2, they now have clarity: if the pod UID hasn't changed, two container processes have restarted inside the same pod object. If the UID changed during investigation, the pod was recreated and previous restart history is lost. This distinction changes how operators correlate restarts with deployment events, node issues, or application bugs.

Configuration management strategies require adjustment. The kubelet's exclusive focus on pod spec changes means that updating a ConfigMap and expecting automatic application is fundamentally misaligned with Kubernetes internals. Operators must either implement pod restart automation after config changes or adopt init containers that poll for external updates. Relying on implicit propagation wastes troubleshooting time in production.

In-place resizing reduces disruption for resource tuning but introduces new monitoring complexity. CPU adjustments are invisible to restart counters, making it harder to correlate performance changes with resize events. Memory resizes with restart policies create restart count noise that must be filtered from genuine failure signals. Operators need enhanced observability around resize events separate from traditional restart tracking.

## Upgrade Actions

Update monitoring dashboards to include pod UID as a dimension alongside restart count. This allows tracking restart patterns across pod recreation events that would otherwise reset visible counters. Configure alerts to detect UID changes separately from restart count thresholds.

Review and update incident runbooks to use precise terminology. Replace generic "pod restart" language with specific questions: Did the UID change? Did the IP change? Did the restart count increment? These questions lead to different diagnostic paths for kubelet issues, scheduler problems, or application crashes.

Audit configuration management automation for incorrect assumptions about kubelet watch behavior. Implement explicit pod rollout triggers after ConfigMap or Secret updates rather than expecting automatic propagation. Document which configuration types require pod spec changes versus external reloads.

Test in-place resize policies in non-production environments before upgrading workloads. Measure the operational impact of RestartContainer memory policies on restart count metrics and adjust alerting thresholds accordingly. Ensure capacity planning accounts for the ability to resize without recreation.

Inventory uses of mutating admission webhooks that might assume post-creation modification capabilities. Redesign these workflows to apply all necessary mutations during pod admission or implement external controllers that manage pod lifecycle explicitly.

## Source Links

- [CNCF Blog](https://www.cncf.io/blog/2026/03/17/when-kubernetes-restarts-your-pod-and-when-it-doesnt/)

## Related Pages

- Parent index: [News](index.md)
- Related: [Cluster API v1.12: Introducing In-place Updates and Chained Upgrades](2026-03-06-cluster-api-v1-12-introducing-place-updates-chained-upgrades.md)
- Related: [Kubernetes Gateway API v1.5.0: TLSRoute Reaches Stable](2026-02-27-gateway-api-v1.5.0-tlsroute-stable.md)
- Newsletter: [This Week in Kubernetes](../index.md#weekly-newsletter)
- Evergreen reference: [Maintenance and upgrades](../operations/maintenance.md)
