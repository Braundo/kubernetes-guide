---
icon: lucide/archive
title: Kubernetes Storage Explained (Persistent Volumes and Claims)
description: Learn how Kubernetes storage works, including PersistentVolumes, PersistentVolumeClaims, and storage classes.
hide:
 - footer
---

# Storage Overview

Container filesystems are ephemeral. For durable data, Kubernetes provides persistent storage primitives.

## Ephemeral vs Persistent Storage

Ephemeral options:

- `emptyDir`: temporary storage tied to pod lifetime.
- `hostPath`: host-node path mount (use sparingly, mainly for node-level agents).

Persistent options:

- PersistentVolume (PV)
- PersistentVolumeClaim (PVC)
- StorageClass

## PV, PVC, and StorageClass

| Object | Purpose | Typical owner |
| :--- | :--- | :--- |
| PV | Actual storage resource | Platform automation or admin |
| PVC | Workload storage request | App team |
| StorageClass | Provisioning policy | Platform team |

## PVC Example

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: db-data
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  storageClassName: standard
```

## Access Modes

- `ReadWriteOnce` (RWO): mounted read-write by one **node** at a time. Multiple pods on the same node can all mount it.
- `ReadWriteOncePod` (RWOP): mounted read-write by exactly one **pod**. Stricter than RWO. Added in Kubernetes 1.22 for single-writer guarantees at the pod level.
- `ReadWriteMany` (RWX): mounted read-write by many nodes simultaneously. Requires a compatible backend (NFS, CephFS, cloud file shares).
- `ReadOnlyMany` (ROX): mounted read-only by many nodes.

## StorageClass Example (CSI)

Prefer CSI drivers and dynamic provisioning.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gp3-encrypted
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  encrypted: "true"
allowVolumeExpansion: true
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
```

Note: `provisioner` is environment-specific. Use the CSI driver for your platform.

`volumeBindingMode: WaitForFirstConsumer` delays PV provisioning until a pod using the PVC is scheduled. This ensures the volume is created in the same availability zone as the pod. Use this mode for zonal storage backends (most cloud block storage). The default `Immediate` mode provisions the volume when the PVC is created, which can cause zone mismatches.

## Reclaim Policy

- `Delete`: deleting PVC removes backing storage.
- `Retain`: backing volume remains for manual recovery.

For critical stateful workloads, `Retain` can reduce accidental data loss risk.

## Mounting a PVC in a Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  volumes:
    - name: app-storage
      persistentVolumeClaim:
        claimName: db-data
  containers:
    - name: app
      image: nginx:1.27
      volumeMounts:
        - name: app-storage
          mountPath: /data
```

## Volume Snapshots

CSI-backed storage supports point-in-time volume snapshots via the `VolumeSnapshot` API (requires the `external-snapshotter` controller):

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: db-snapshot-2026-05-03
spec:
  volumeSnapshotClassName: csi-snapclass
  source:
    persistentVolumeClaimName: db-data
```

Restore by creating a new PVC with `dataSource` pointing to the snapshot. Snapshots are much faster than full backup/restore for large volumes and are useful for pre-upgrade checkpoints.

## Operational Checks

```bash
kubectl get pvc
kubectl get pv
kubectl describe pvc db-data
kubectl get volumesnapshot
```

If PVC remains `Pending`, validate storage class name, CSI driver health, and topology constraints (`WaitForFirstConsumer` PVCs stay Pending until a pod is scheduled).

## Related Concepts

- [StatefulSets](../workloads/statefulsets.md)
- [Resource Quotas and Limits](../configuration/quotas-limits.md)
- [Maintenance](../operations/maintenance.md)
