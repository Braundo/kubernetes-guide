---
title: "Kubernetes v1.34: Finer-Grained Control Over Container Restarts"
date: 2025-08-29
category: releases
source_url: "https://kubernetes.io/blog/2025/08/29/kubernetes-v1-34-per-container-restart-policy/"
generated: "2026-03-06T19:20:02.265178+00:00"
---

# Kubernetes v1.34: Finer-Grained Control Over Container Restarts

**Source:** [Kubernetes Blog](https://kubernetes.io/blog/2025/08/29/kubernetes-v1-34-per-container-restart-policy/)
**Published:** 2025-08-29 | **Category:** Releases

## Summary

Kubernetes 1.34 introduces Container Restart Policy and Rules, an alpha feature that enables per-container restart policies within a Pod. Previously, all containers in a Pod shared a single restart policy (Always, OnFailure, or Never) defined at the Pod level. This new capability allows individual containers to override the Pod's global restart policy and conditionally restart based on exit codes. The feature is gated behind the alpha feature gate `ContainerRestartRules`.

## Why It Matters

This addresses a long-standing limitation in Pod lifecycle management that forced operators into awkward workarounds. The single restart policy model breaks down in multi-container Pods where different containers serve different purposes—a sidecar that should always restart differs fundamentally from a setup container that should run once and exit cleanly. Until now, you either split workloads across multiple Pods (increasing scheduling overhead and complicating networking) or accepted suboptimal restart behavior that cluttered logs and consumed resources.

Exit code-based restart logic is particularly valuable for batch workloads and complex application patterns. A container that exits with code 0 after successful completion shouldn't restart, while code 1 might indicate a transient failure worth retrying. Previously, this logic lived in shell wrapper scripts or required external controllers watching Pod events—both brittle patterns that complicate debugging and increase mean time to recovery.

As an alpha feature, this won't appear in production clusters without explicit opt-in via feature gates on the kubelet and API server. The API will likely evolve before reaching beta. Expect changes to field names, validation rules, and possibly the conditions syntax. Plan for migration work if you adopt this in non-production environments during the alpha phase.

## What You Should Do

1. Verify your cluster version with `kubectl version --short` and confirm whether you're running 1.34 or have upgrade plans that include it within your testing timeline.

2. Enable the feature gate in a development cluster by adding `--feature-gates=ContainerRestartRules=true` to both kube-apiserver and kubelet startup arguments to evaluate the API surface before it stabilizes.

3. Identify multi-container Pods in your cluster that would benefit from this feature using `kubectl get pods --all-namespaces -o json | jq '.items[] | select(.spec.containers | length > 1) | .metadata.name'` and document current restart behavior workarounds.

4. Review your sidecar patterns, init container workflows, and batch Jobs where containers have different lifecycle requirements—these are prime candidates for per-container restart policies once the feature reaches beta.

5. Monitor the KEP and alpha feedback cycles closely if you plan to adopt this feature, as breaking API changes are expected before general availability.

## Further Reading

- [Kubernetes 1.34 Container Restart Policy announcement](https://kubernetes.io/blog/2025/08/29/kubernetes-v1-34-per-container-restart-policy/)
- [Kubernetes Pod Lifecycle documentation](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [Feature Gates reference](https://kubernetes.io/docs/reference/command-line-tools-reference/feature-gates/)

---
*Published 2026-03-06 on k8s.guide*
