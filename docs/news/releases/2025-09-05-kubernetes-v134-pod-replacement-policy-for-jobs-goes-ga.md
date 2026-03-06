---
title: "Kubernetes v1.34: Pod Replacement Policy for Jobs Goes GA"
date: 2025-09-05
category: releases
source_url: "https://kubernetes.io/blog/2025/09/05/kubernetes-v1-34-pod-replacement-policy-for-jobs-goes-ga/"
generated: "2026-03-06T19:21:50.685297+00:00"
---

# Kubernetes v1.34: Pod Replacement Policy for Jobs Goes GA

**Source:** [Kubernetes Blog](https://kubernetes.io/blog/2025/09/05/kubernetes-v1-34-pod-replacement-policy-for-jobs-goes-ga/)
**Published:** 2025-09-05 | **Category:** Releases

## Summary

Kubernetes v1.34 promotes the Pod replacement policy for Jobs to general availability (GA). This feature controls when the Job controller creates replacement Pods, addressing a default behavior where the controller immediately recreates Pods upon failure or termination, potentially causing multiple Pods to run simultaneously beyond the specified parallelism. For Indexed Jobs, this previously meant multiple Pods could run for the same index, breaking frameworks like TensorFlow and JAX that expect exactly one Pod per worker index.

## Why It Matters

The default Job controller behavior has been a pain point for distributed workloads that rely on strict single-Pod-per-index semantics. Machine learning frameworks like TensorFlow and JAX fail with duplicate task registration errors when two Pods run with the same worker index—something that happens naturally when the controller creates replacements before terminations complete. This isn't theoretical: the error message `/job:worker/task:4: Duplicate task registration` shows up in production ML training jobs, forcing teams into workarounds like custom operators or careful parallelism tuning.

This GA feature lets you defer replacement Pod creation until the terminating Pod fully completes, ensuring index uniqueness. For platform teams running batch workloads or ML training pipelines, this solves a category of race conditions that have been difficult to prevent at the application layer. The move to GA means it's stable for production use without feature gates, making it safe to standardize in your Job templates.

The timing matters for teams on older Kubernetes versions running ML workloads. If you've built custom logic to avoid index collisions, you can now simplify back to native Job semantics. This also affects capacity planning: the default behavior can cause temporary overcommitment when replacement Pods start before terminating Pods release resources, potentially triggering node scaling or OOM conditions in tight resource configurations.

## What You Should Do

1. Check your Kubernetes version with `kubectl version --short` to confirm you're running v1.34 or later, where this feature is GA and enabled by default without feature gates.

2. Identify Indexed Jobs in your cluster, particularly ML training workloads: `kubectl get jobs --all-namespaces -o json | jq '.items[] | select(.spec.completionMode=="Indexed") | {name: .metadata.name, namespace: .metadata.namespace}'`

3. Add the `podReplacementPolicy: Failed` field to Job specs for workloads requiring strict index uniqueness, ensuring replacements only start after Pods fully terminate rather than when termination begins.

4. Test the policy change in staging with representative workloads, monitoring for changes in completion time since waiting for full termination adds latency to failure recovery.

5. Review Jobs with tight resource limits where the default behavior may have caused temporary overcommitment—the new policy can reduce peak resource consumption during Pod churn.

## Further Reading

- [Kubernetes v1.34 Pod Replacement Policy announcement](https://kubernetes.io/blog/2025/09/05/kubernetes-v1-34-pod-replacement-policy-for-jobs-goes-ga/)
- [Kubernetes Jobs documentation](https://kubernetes.io/docs/concepts/workloads/controllers/job/)
- [Indexed Jobs specification](https://kubernetes.io/docs/concepts/workloads/controllers/job/#completion-mode)

---
*Published 2026-03-06 on k8s.guide*
