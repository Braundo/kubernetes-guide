---
title: "Kubernetes v1.34: DRA has graduated to GA"
date: 2025-09-01
category: releases
source_url: "https://kubernetes.io/blog/2025/09/01/kubernetes-v1-34-dra-updates/"
generated: "2026-03-06T19:20:19.483500+00:00"
---

# Kubernetes v1.34: DRA has graduated to GA

**Source:** [Kubernetes Blog](https://kubernetes.io/blog/2025/09/01/kubernetes-v1-34-dra-updates/)
**Published:** 2025-09-01 | **Category:** Releases

## Summary

Kubernetes 1.34 brings Dynamic Resource Allocation (DRA) to General Availability, marking a significant milestone for specialized hardware management in production clusters. The core APIs in the resource.k8s.io group are now GA, with additional features promoted to beta and new alpha capabilities added. DRA provides a flexible framework for managing devices like GPUs and FPGAs, allowing workloads to specify required device properties while the scheduler handles actual device allocation.

## Why It Matters

DRA's graduation to GA fundamentally changes how platform teams should approach specialized hardware management in Kubernetes. Prior approaches—device plugins and manual node labeling—were rigid and prone to scheduling conflicts. DRA moves device allocation into the scheduler itself, enabling dynamic assignment based on workload requirements rather than pre-defined node labels. This improves resource utilization and reduces failed pod placements due to device contention.

For teams running GPU workloads for ML training, batch processing, or inference, this is the architecture Kubernetes expects you to adopt going forward. The GA status signals API stability—no more breaking changes to resource allocation patterns you build today. If you're currently using device plugins, start planning migration timelines now. Device plugins aren't deprecated yet, but DRA represents the upstream community's investment direction.

The scheduler integration is critical for multi-tenant environments. Instead of pods claiming devices on first-come-first-served basis at the node level, the scheduler can now make globally optimal decisions about device placement across the cluster. This prevents scenarios where pods land on nodes with insufficient device resources despite capacity existing elsewhere.

## What You Should Do

1. Run `kubectl version --short` to check your cluster version, then review which DRA features are available at your current version if you're not yet on 1.34.

2. Audit existing GPU and specialized hardware workloads to identify candidates for DRA migration—start with non-critical batch workloads before moving production inference services.

3. Check if your hardware vendor provides DRA drivers for your devices (GPUs, FPGAs, network cards) by reviewing their documentation and container registries for resource.k8s.io compatible drivers.

4. Test DRA on a non-production cluster by defining ResourceClaim objects that specify device requirements and referencing them in pod specs via `resourceClaims` fields.

5. Monitor scheduler metrics and pod scheduling latency after enabling DRA features, as the scheduler now performs additional resource matching logic during pod placement decisions.

## Further Reading

- [Kubernetes 1.34 DRA Updates Blog Post](https://kubernetes.io/blog/2025/09/01/kubernetes-v1-34-dra-updates/)
- [Dynamic Resource Allocation Documentation](https://kubernetes.io/docs/concepts/scheduling-eviction/dynamic-resource-allocation/)
- [Resource Management KEPs](https://github.com/kubernetes/enhancements/tree/master/keps/sig-node)

---
*Published 2026-03-06 on k8s.guide*
