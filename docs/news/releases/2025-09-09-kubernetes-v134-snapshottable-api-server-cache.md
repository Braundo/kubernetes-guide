---
title: "Kubernetes v1.34: Snapshottable API server cache"
date: 2025-09-09
category: releases
source_url: "https://kubernetes.io/blog/2025/09/09/kubernetes-v1-34-snapshottable-api-server-cache/"
generated: "2026-03-06T19:32:04.534015+00:00"
---

# Kubernetes v1.34: Snapshottable API server cache

**Source:** [Kubernetes Blog](https://kubernetes.io/blog/2025/09/09/kubernetes-v1-34-snapshottable-api-server-cache/)
**Published:** 2025-09-09 | **Category:** Releases

## Summary

Kubernetes v1.34 promotes the snapshottable API server cache feature to Beta, completing a multi-release effort to serve virtually all read requests directly from the API server's cache. This milestone builds on consistent reads from cache (Beta in v1.31) and represents the final major component in a long-standing initiative to reduce API server memory usage and etcd load caused by list requests. The feature aims to improve API server stability and performance predictability in production clusters.

## Why It Matters

List requests have been the primary culprit behind API server performance issues and etcd overload for years. Every watch operation, every controller reconciliation loop, and every CLI tool querying cluster state generates list requests that traditionally hammered etcd. When you've debugged why your control plane suddenly spiked to 32GB memory during a routine deployment or why etcd latency jumped from 5ms to 500ms, you've felt this pain directly. The snapshottable cache fundamentally changes this operational reality by making the API server's cache the source of truth for read operations.

This is not just an incremental improvement. By serving reads from cache snapshots rather than hitting etcd, you decouple read performance from your etcd cluster's performance characteristics. This matters most during high-churn scenarios: large-scale rollouts, cluster autoscaling events, or when multiple operators are reconciling resources simultaneously. Your etcd cluster can focus on writes while the API server handles the read amplification that comes from dozens of controllers watching the same resources.

The Beta promotion means this feature is enabled by default and considered stable enough for production evaluation. If you run large clusters (500+ nodes) or operate in multi-tenant environments where noisy neighbors impact control plane stability, this feature directly addresses your operational constraints. The graduation path from the earlier consistent reads work (v1.31) shows the Kubernetes community's methodical approach to control plane reliability, something you should factor into your upgrade planning.

## What You Should Do

1. Verify your cluster version with `kubectl version --short` and review your upgrade timeline to v1.34, prioritizing clusters with known API server memory pressure or etcd performance issues.

2. Monitor API server memory usage and etcd request rates before and after upgrading to establish a baseline, paying attention to LIST operation latencies in your metrics dashboards.

3. Review your API server logs for cache-related warnings or errors after upgrade, particularly if you use custom resources with large object counts or high watch cardinality.

4. Test the feature in staging environments with production-like workloads, especially if you run custom controllers that issue frequent list requests or have operators with aggressive resync intervals.

5. Document baseline control plane performance metrics (API server CPU/memory, etcd disk IOPS, p95 request latency) to measure improvement and inform future capacity planning.

## Further Reading

- [Kubernetes v1.34: Snapshottable API server cache](https://kubernetes.io/blog/2025/09/09/kubernetes-v1-34-snapshottable-api-server-cache/)
- [Kubernetes API server documentation](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-apiserver/)
- [etcd performance tuning guide](https://etcd.io/docs/latest/tuning/)

---
*Published 2026-03-06 on k8s.guide*
