---
title: "Kubernetes v1.34: PSI Metrics for Kubernetes Graduates to Beta"
date: 2025-09-04
category: releases
source_url: "https://kubernetes.io/blog/2025/09/04/kubernetes-v1-34-introducing-psi-metrics-beta/"
generated: "2026-03-06T19:21:32.127112+00:00"
---

# Kubernetes v1.34: PSI Metrics for Kubernetes Graduates to Beta

**Source:** [Kubernetes Blog](https://kubernetes.io/blog/2025/09/04/kubernetes-v1-34-introducing-psi-metrics-beta/)
**Published:** 2025-09-04 | **Category:** Releases

## Summary

Kubernetes v1.34 promotes Pressure Stall Information (PSI) Metrics to Beta status. PSI is a Linux kernel feature (version 4.20+) that measures actual resource contention by tracking how long tasks are stalled waiting for CPU, memory, or I/O resources. Unlike traditional utilization metrics, PSI quantifies when demand exceeds supply, exposing "some" pressure (at least one task stalled) and "full" pressure metrics.

## Why It Matters

Traditional resource metrics like CPU and memory utilization tell you how much capacity you're consuming, but they don't reveal when workloads are actually suffering. A node at 70% CPU utilization might be performing fine, or it might have applications constantly stalling on resource access. PSI closes this observability gap by measuring the operational impact of resource pressure rather than just capacity consumption.

For platform teams running large clusters, this is a fundamental shift in how you diagnose performance issues and set autoscaling thresholds. Instead of reactive scaling based on percentage metrics that may trigger too early or too late, you can now make decisions based on actual application stall time. This is particularly valuable for rightsizing nodes, debugging noisy neighbor problems in multi-tenant clusters, and identifying I/O bottlenecks that CPU and memory metrics miss entirely.

The Beta graduation means the feature API is stable enough for production use, though it may still see refinements before GA. Platform teams should note this requires Linux kernel 4.20 or later on worker nodes, which may require OS upgrades on older node pools before the metrics become available.

## What You Should Do

1. Verify your node OS kernels meet the minimum requirement by running `kubectl get nodes -o wide` to check OS versions, then SSH to a sample node and run `uname -r` to confirm kernel version 4.20+.

2. Check if PSI metrics are already exposed on your nodes by executing `kubectl debug node/<node-name> -it --image=busybox -- cat /proc/pressure/cpu` on a 4.20+ kernel node to see if the kernel feature is enabled.

3. Review your monitoring stack configuration to ingest PSI metrics once available in v1.34, particularly the `container_cpu_pressure`, `container_memory_pressure`, and `container_io_pressure` metric families that will be exposed via kubelet.

4. Plan node pool upgrades for clusters running older Linux distributions that may not meet the kernel 4.20 requirement, prioritizing pools that run performance-sensitive workloads where stall detection provides the most value.

5. Establish baseline PSI thresholds for your workloads after upgrade by monitoring "some" and "full" pressure percentages during normal operation, then use these baselines to set meaningful alerts and autoscaling policies.

## Further Reading

- [Kubernetes v1.34: PSI Metrics for Kubernetes Graduates to Beta](https://kubernetes.io/blog/2025/09/04/kubernetes-v1-34-introducing-psi-metrics-beta/)
- [Linux kernel PSI documentation](https://docs.kernel.org/accounting/psi.html)
- [Kubernetes Enhancement Proposal for PSI metrics](https://github.com/kubernetes/enhancements/tree/master/keps/sig-node)

---
*Published 2026-03-06 on k8s.guide*
