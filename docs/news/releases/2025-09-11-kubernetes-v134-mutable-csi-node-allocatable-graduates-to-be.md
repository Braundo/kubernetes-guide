---
title: "Kubernetes v1.34: Mutable CSI Node Allocatable Graduates to Beta"
date: 2025-09-11
category: releases
source_url: "https://kubernetes.io/blog/2025/09/11/kubernetes-v1-34-mutable-csi-node-allocatable-count/"
generated: "2026-03-06T19:32:48.326839+00:00"
---

# Kubernetes v1.34: Mutable CSI Node Allocatable Graduates to Beta

**Source:** [Kubernetes Blog](https://kubernetes.io/blog/2025/09/11/kubernetes-v1-34-mutable-csi-node-allocatable-count/)
**Published:** 2025-09-11 | **Category:** Releases

## Summary

Kubernetes v1.34 promotes the Mutable CSI Node Allocatable feature to Beta, allowing CSI drivers to dynamically update the number of volumes that can be attached to nodes during runtime. First introduced as Alpha in v1.33, this feature addresses a longstanding issue where static volume attachment limits caused pod scheduling failures when actual node capacity diverged from reported values. The promotion to Beta indicates the feature is now enabled by default and considered stable for production use.

## Why It Matters

Static volume attachment reporting has been a persistent pain point for stateful workloads. When CSI drivers could only report attachment limits at initialization, any runtime changes (manual volume operations, hot-plugged hardware, or cross-driver capacity conflicts) left the scheduler working with stale data. This resulted in pods being scheduled to nodes that appeared to have capacity but couldn't actually attach the required volumes, causing startup failures and requiring manual intervention to reschedule.

The operational impact is most severe in multi-tenant clusters running mixed workloads with different storage backends, or environments where infrastructure teams perform out-of-band volume management. In these scenarios, the scheduler's view of available attachment slots becomes increasingly inaccurate over time, leading to cascading failures during pod deployments or node maintenance windows. Dynamic capacity updates mean the scheduler makes decisions based on current reality rather than initialization-time snapshots, directly improving reliability for StatefulSets and other volume-dependent workloads.

With Beta promotion in v1.34, this becomes default behavior. If your CSI drivers support the feature, attachment capacity information will automatically stay synchronized without requiring feature gate configuration. This is a meaningful improvement for anyone running storage-intensive workloads, particularly in environments with GPU nodes, specialized hardware, or multiple CSI drivers competing for attachment slots.

## What You Should Do

1. Verify your cluster version and check if the feature is active by running `kubectl version --short` to confirm v1.34+, then inspect your CSI driver pods to determine if they support dynamic capacity reporting (check driver documentation or release notes).

2. Review your monitoring dashboards for historical pod scheduling failures related to volume attachment limits. Look for events containing "AttachVolume.Attach failed" or "exceeded max volume count" to establish a baseline before the feature takes effect.

3. If you manage custom CSI drivers or use third-party storage solutions, contact your storage vendor to confirm driver compatibility with mutable node allocatable counts and identify required driver version upgrades.

4. Test the feature in a staging environment by deliberately changing attachment capacity (attach volumes via your cloud provider's console or CLI) and observe whether the scheduler correctly reflects updated limits without node restarts.

5. Update your runbooks for volume attachment troubleshooting to account for dynamic capacity changes, and remove any workarounds that involved node cordons or manual pod rescheduling due to stale attachment limits.

## Further Reading

- [Kubernetes v1.34 Mutable CSI Node Allocatable Announcement](https://kubernetes.io/blog/2025/09/11/kubernetes-v1-34-mutable-csi-node-allocatable-count/)
- [Container Storage Interface (CSI) Documentation](https://kubernetes-csi.github.io/docs/)
- [Kubernetes Storage Capacity Tracking](https://kubernetes.io/docs/concepts/storage/storage-capacity/)

---
*Published 2026-03-06 on k8s.guide*
