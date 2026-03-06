---
title: "Kubernetes v1.34: VolumeAttributesClass for Volume Modification GA"
date: 2025-09-08
category: releases
source_url: "https://kubernetes.io/blog/2025/09/08/kubernetes-v1-34-volume-attributes-class/"
generated: "2026-03-06T19:31:46.261564+00:00"
---

# Kubernetes v1.34: VolumeAttributesClass for Volume Modification GA

**Source:** [Kubernetes Blog](https://kubernetes.io/blog/2025/09/08/kubernetes-v1-34-volume-attributes-class/)
**Published:** 2025-09-08 | **Category:** Releases

## Summary

VolumeAttributesClass has graduated to General Availability in Kubernetes v1.34, released September 8, 2025. This API allows dynamic modification of volume attributes on running persistent volumes without requiring re-provisioning. Users can now change storage performance characteristics like IOPS or throughput tiers through CSI drivers by updating the volumeAttributesClassName field on PersistentVolumeClaims.

## Why It Matters

Before VolumeAttributesClass GA, changing storage performance characteristics meant creating new volumes, copying data, and updating workloads to use the new PVC. This operational overhead discouraged teams from right-sizing storage, leading to either over-provisioned volumes (wasting budget) or under-provisioned ones (causing performance issues). The GA status signals that the API is stable and won't change, making it safe to build automation and self-service tooling around dynamic volume tuning.

This matters most for stateful workloads with variable performance needs. Database clusters that need burst IOPS during migrations, data processing jobs that require temporarily elevated throughput, or multi-tenant platforms where users should self-service their storage tiers can all benefit. The cluster-scoped VolumeAttributesClass resource gives platform teams control over which modification profiles are available, maintaining governance while enabling flexibility. Storage costs become more manageable when teams can scale down performance during off-peak hours.

CSI driver support is the critical dependency. Not all storage backends support online volume modification, and driver implementations vary in what parameters they expose. Check your CSI driver documentation before planning adoption. The feature only works with CSI drivers that implement the ModifyVolume RPC, and modifications happen at the storage system level, so the underlying platform must support the requested changes.

## What You Should Do

1. Verify your CSI driver version supports VolumeAttributesClass and review which parameters it exposes for modification (typically IOPS, throughput, volume type). Check the driver's GitHub repository or documentation for ModifyVolume capability.

2. Create VolumeAttributesClass resources for your storage tiers before users need them. Define classes like "high-performance", "standard", and "low-cost" with appropriate parameters for your storage backend.

3. Test volume modification in a non-production environment by creating a PVC, writing test data, then updating the volumeAttributesClassName field and verifying the changes applied without data loss or extended downtime.

4. Update your PVC templates and documentation to include volumeAttributesClassName fields where appropriate. Add RBAC policies if you want to restrict which teams can use which storage classes.

5. Monitor CSI driver logs during initial rollout. Volume modifications are asynchronous operations that can fail if the storage backend rejects the parameters or if the volume is in an incompatible state.

## Further Reading

- [Kubernetes v1.34: VolumeAttributesClass for Volume Modification GA](https://kubernetes.io/blog/2025/09/08/kubernetes-v1-34-volume-attributes-class/)
- [VolumeAttributesClass API Reference](https://kubernetes.io/docs/concepts/storage/volume-attributes-classes/)
- [CSI Volume Modification Documentation](https://kubernetes-csi.github.io/docs/volume-modification.html)

---
*Published 2026-03-06 on k8s.guide*
