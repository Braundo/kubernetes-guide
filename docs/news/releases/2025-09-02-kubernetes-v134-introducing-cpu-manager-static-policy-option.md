---
title: "Kubernetes v1.34: Introducing CPU Manager Static Policy Option for Uncore Cache Alignment"
date: 2025-09-02
category: releases
source_url: "https://kubernetes.io/blog/2025/09/02/kubernetes-v1-34-prefer-align-by-uncore-cache-cpumanager-static-policy-optimization/"
generated: "2026-03-06T19:20:36.939921+00:00"
---

# Kubernetes v1.34: Introducing CPU Manager Static Policy Option for Uncore Cache Alignment

**Source:** [Kubernetes Blog](https://kubernetes.io/blog/2025/09/02/kubernetes-v1-34-prefer-align-by-uncore-cache-cpumanager-static-policy-optimization/)
**Published:** 2025-09-02 | **Category:** Releases

## Summary

Kubernetes v1.34 graduates the `prefer-align-cpus-by-uncore-cache` CPU Manager Static Policy Option from alpha to beta. This feature, first introduced in v1.32, optimizes workload performance on processors with split uncore cache architectures by aligning CPU allocation with cache topology. The policy option specifically targets modern AMD64 and ARM processors that have moved away from monolithic Level 3 cache designs.

## Why It Matters

Modern processors increasingly use split uncore cache architectures to reduce latency between CPU cores and cache. When workloads span CPU cores across different cache segments, cross-cache communication introduces performance penalties that can significantly impact latency-sensitive applications. For production environments running high-performance computing, financial trading systems, or real-time data processing, these microsecond-level differences compound under load.

The CPU Manager's static policy already provides guaranteed CPU allocation for pods with integer CPU requests in the Guaranteed QoS class. This new option extends that capability by making the kubelet cache-topology aware when assigning CPUs. Without this alignment, even pods with dedicated CPUs might suffer from suboptimal cache locality, undermining the performance isolation you expect from CPU pinning.

Beta graduation signals that the feature has proven stable enough for broader production use, though it remains opt-in. Platform teams running workloads with strict performance requirements should evaluate whether their underlying hardware exhibits split uncore cache behavior and whether their applications would benefit from cache-aligned CPU allocation.

## What You Should Do

1. Verify your Kubernetes version supports this feature by running `kubectl version --short` and confirming you're on v1.32 or later for alpha, v1.34+ for beta stability.

2. Check your processor architecture documentation to confirm whether your nodes use split uncore cache topology—this applies to recent AMD EPYC and ARM-based server processors, not older monolithic cache designs.

3. Enable the CPU Manager static policy if not already configured by setting `--cpu-manager-policy=static` in kubelet flags, then add the policy option `--cpu-manager-policy-options=prefer-align-cpus-by-uncore-cache=true` on nodes where you want cache alignment.

4. Test with a representative latency-sensitive workload in a non-production environment, measuring performance metrics before and after enabling the option to validate actual benefit for your specific application profile.

5. Monitor CPU allocation patterns using `kubectl describe node` to verify CPUs assigned to Guaranteed pods align with cache topology as expected after enabling the feature.

## Further Reading

- [Kubernetes v1.34 CPU Manager Uncore Cache Alignment announcement](https://kubernetes.io/blog/2025/09/02/kubernetes-v1-34-prefer-align-by-uncore-cache-cpumanager-static-policy-optimization/)
- [CPU Manager documentation](https://kubernetes.io/docs/tasks/administer-cluster/cpu-management-policies/)
- [Control CPU Management Policies on the Node](https://kubernetes.io/docs/tasks/administer-cluster/cpu-management-policies/)

---
*Published 2026-03-06 on k8s.guide*
