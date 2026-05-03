---
icon: lucide/database-zap
title: Kubernetes StatefulSets Explained (Stateful Applications and Identity)
description: Learn how StatefulSets manage stateful workloads, stable identities, and persistent storage in Kubernetes.
hide:
 - footer
---

# StatefulSets

StatefulSets are for workloads that need stable identity and persistent storage per replica.

Typical examples include databases, queue brokers, and clustered stateful systems.

## What StatefulSets Guarantee

- Stable pod ordinal names: `app-0`, `app-1`, `app-2`
- Stable DNS names through a headless service
- One PersistentVolumeClaim per pod from `volumeClaimTemplates`
- Ordered rollout and scale behavior by default

Important: StatefulSets do not guarantee a fixed pod IP across restarts. They guarantee stable identity (name/DNS) and stable volume association.

## StatefulSet vs Deployment

| Concern | Deployment | StatefulSet |
| :--- | :--- | :--- |
| Pod identity | interchangeable | stable ordinal identity |
| Storage | often shared/ephemeral patterns | dedicated PVC per pod |
| Ordering | parallel by default | ordered semantics |
| Typical use | stateless services | stateful clustered systems |

![StatefulSets Diagram](../images/sts-light.png#only-light)
![StatefulSets Diagram](../images/sts-dark.png#only-dark)

## Required Companion: Headless Service

StatefulSets rely on a headless Service for stable DNS records.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  clusterIP: None
  selector:
    app: web
  ports:
    - port: 80
      name: http
```

Pods then resolve as:

- `web-0.web.<namespace>.svc.cluster.local`
- `web-1.web.<namespace>.svc.cluster.local`

## StatefulSet Example

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  serviceName: web
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: nginx
          image: nginx:1.27
          volumeMounts:
            - name: data
              mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 10Gi
```

## Pod Management Policy

By default, StatefulSets use `OrderedReady` semantics: pods are created and deleted one at a time in ordinal order. For workloads that do not need strict ordering during scale-up (like sharded caches), `Parallel` mode starts and stops all pods simultaneously.

```yaml
spec:
  podManagementPolicy: Parallel
```

Use `OrderedReady` (the default) when pod `N` depends on pod `N-1` being ready before it can initialize, which is common for clustered databases and consensus systems.

## Rolling Updates and Partitions

StatefulSets support rolling updates with identity-aware ordering.

For cautious rollouts, use the `partition` field. Only pods with ordinal >= partition are updated; lower ordinals remain at the old version until you advance the partition.

```yaml
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 2
```

With 3 replicas and `partition: 2`, only pod `app-2` updates immediately. Set to `1` to also update `app-1`, then `0` to complete the rollout.

## Storage Lifecycle

Each replica receives its own PVC named after the `volumeClaimTemplate` plus the pod ordinal:

- `data-web-0`
- `data-web-1`

PVC and PV retention behavior depends on storage class reclaim policy. By default, PVCs are **not** deleted when a StatefulSet is scaled down or deleted -- they persist until manually removed. This is intentional to prevent data loss.

Since Kubernetes 1.27 (stable), you can configure automatic PVC deletion with `persistentVolumeClaimRetentionPolicy`:

```yaml
spec:
  persistentVolumeClaimRetentionPolicy:
    whenDeleted: Delete   # delete PVCs when StatefulSet is deleted
    whenScaled: Retain    # keep PVCs when scaling down
```

Use `Delete` carefully -- it is irreversible for stateful systems.

## When Not to Use StatefulSet

Do not use StatefulSet just because an app writes logs or temp files.

If the workload is horizontally replaceable and does not require replica identity, use Deployment for simpler operations.

## Related Concepts

- [Pods and Deployments](pods-deployments.md)
- [Storage](../storage/storage.md)
- [Services](../networking/services-networking.md)
