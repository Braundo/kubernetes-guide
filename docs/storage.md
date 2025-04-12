---
icon: material/database-outline
---

# Storage in Kubernetes

Kubernetes provides flexible ways to **persist data**, from temporary in-Pod storage to persistent disks that survive Pod and node failure. You’ll most commonly use **Volumes**, **PersistentVolumes (PVs)**, and **PersistentVolumeClaims (PVCs)** to manage storage in production.

---

## Types of Storage

Kubernetes supports several storage mechanisms:

| Type                  | Description                                               |
|-----------------------|-----------------------------------------------------------|
| `emptyDir`            | Temporary, pod-level storage. Deleted when Pod is gone.   |
| `hostPath`            | Mounts a path on the host node. Avoid in production.      |
| `configMap` / `secret`| Used for injecting configs/secrets into containers.       |
| `persistentVolume`    | Abstracts physical storage (EBS, NFS, GCE PD, etc.).      |
| `volumeClaimTemplate` | Used by StatefulSets to dynamically provision volumes.    |

---

## Volumes

Basic `volumes` are attached to a Pod spec and live as long as the Pod.

```yaml
volumes:
  - name: cache
    emptyDir: {}
```

> Use `emptyDir` for scratch space or caching — not persistent data.

---

## PersistentVolumes (PVs) and PersistentVolumeClaims (PVCs)

To persist data **beyond the life of a Pod**, use the **PV + PVC model**:

- A **PV** is a piece of actual storage (disk, NFS, etc.)
- A **PVC** is a user’s request for storage
- Kubernetes binds them together dynamically

### PVC Example

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-storage
spec:
  accessModes: ["ReadWriteOnce"]
  resources:
    requests:
      storage: 1Gi
```

### Pod using the PVC

```yaml
volumes:
  - name: app-data
    persistentVolumeClaim:
      claimName: app-storage

containers:
  - name: web
    volumeMounts:
      - name: app-data
        mountPath: /data
```

---

## Volume Modes & Access

- **Volume Modes:**
  - `Filesystem` (default): mounts as a directory
  - `Block`: exposes the raw device

- **Access Modes:**
  - `ReadWriteOnce`: one node read/write
  - `ReadOnlyMany`: multiple nodes read-only
  - `ReadWriteMany`: shared read/write (NFS, etc.)

---

## StorageClasses

A `StorageClass` defines **how** storage should be provisioned dynamically.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast
provisioner: kubernetes.io/gce-pd
parameters:
  type: pd-ssd
```

> The cluster admin defines StorageClasses; PVCs can request one by name.

```yaml
storageClassName: fast
```

---

## Dynamic vs Static Provisioning

- **Dynamic:** PVC automatically provisions a volume using a `StorageClass`.
- **Static:** Admin manually creates PVs, and users bind to them with matching PVCs.

---

## Best Practices

- Use `ReadWriteOnce` unless your workload **requires** multi-node access.
- Leverage `StorageClass` for automated provisioning.
- Clean up PVCs when no longer needed — they may retain bound disks.
- Use StatefulSets if each Pod needs its **own** PVC.

---

## Summary

Storage in Kubernetes is abstracted through PVs and PVCs for flexibility and portability. Whether your app is stateless or stateful, Kubernetes can handle your storage needs — just make sure to pick the right type of volume for the job.