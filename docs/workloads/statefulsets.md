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

## Rolling Updates and Partitions

StatefulSets support rolling updates with identity-aware ordering.

For cautious rollouts, use partitioned updates so higher ordinals update first while lower ordinals stay pinned until you advance.

## Storage Lifecycle

Each replica receives its own PVC, for example:

- `data-web-0`
- `data-web-1`

PVC and PV retention behavior depends on storage class reclaim policy and StatefulSet PVC retention configuration.

## When Not to Use StatefulSet

Do not use StatefulSet just because an app writes logs or temp files.

If the workload is horizontally replaceable and does not require replica identity, use Deployment for simpler operations.

## Related Concepts

- [Pods and Deployments](pods-deployments.md)
- [Storage](../storage/storage.md)
- [Services](../networking/services-networking.md)
