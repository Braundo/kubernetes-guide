---
icon: material/database-outline
---

<h1>Storage in Kubernetes</h1>

Kubernetes provides flexible ways to <strong>persist data</strong>, from temporary in-Pod storage to persistent disks that survive Pod and node failure. You’ll most commonly use <strong>Volumes</strong>, <strong>PersistentVolumes (PVs)</strong>, and <strong>PersistentVolumeClaims (PVCs)</strong> to manage storage in production.

---

<h2>Types of Storage</h2>

Kubernetes supports several storage mechanisms:

| Type                  | Description                                               |
|-----------------------|-----------------------------------------------------------|
| <code>emptyDir</code>            | Temporary, pod-level storage. Deleted when Pod is gone.   |
| <code>hostPath</code>            | Mounts a path on the host node. Avoid in production.      |
| <code>configMap</code> / <code>secret</code>| Used for injecting configs/secrets into containers.       |
| <code>persistentVolume</code>    | Abstracts physical storage (EBS, NFS, GCE PD, etc.).      |
| <code>volumeClaimTemplate</code> | Used by StatefulSets to dynamically provision volumes.    |

---

<h2>Volumes</h2>

Basic <code>volumes</code> are attached to a Pod spec and live as long as the Pod.

```yaml
volumes:
  - name: cache
    emptyDir: {}
```

> Use <code>emptyDir</code> for scratch space or caching - not persistent data.

---

<h2>PersistentVolumes (PVs) and PersistentVolumeClaims (PVCs)</h2>

To persist data <strong>beyond the life of a Pod</strong>, use the <strong>PV + PVC model</strong>:

- A <strong>PV</strong> is a piece of actual storage (disk, NFS, etc.)
- A <strong>PVC</strong> is a user’s request for storage
- Kubernetes binds them together dynamically

<h3>PVC Example</h3>

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

<h3>Pod using the PVC</h3>

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

**Volume Modes:**

  - `Filesystem` (default): mounts as a directory
  - `Block`: exposes the raw device

<br>

**Access Modes:**

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
- Clean up PVCs when no longer needed - they may retain bound disks.
- Use StatefulSets if each Pod needs its **own** PVC.

---

## Summary

Storage in Kubernetes is abstracted through PVs and PVCs for flexibility and portability. Whether your app is stateless or stateful, Kubernetes can handle your storage needs - just make sure to pick the right type of volume for the job.