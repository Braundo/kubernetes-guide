---
icon: material/database
---

# StatefulSets

A **StatefulSet** is a Kubernetes controller for deploying and scaling **stateful applications**. Unlike Deployments, StatefulSets maintain **persistent identity and storage** for each Pod across rescheduling and restarts.

---

## Why Use a StatefulSet?

Use a StatefulSet when your app requires:

✅ **Stable network identity** (e.g., `pod-0`, `pod-1`)  
✅ **Persistent storage per Pod** that survives rescheduling  
✅ **Ordered Pod startup, scaling, and deletion**

Examples: databases (PostgreSQL, Cassandra), Zookeeper, Kafka, etc.

---

## How It Differs from Deployments

StatefulSets guarantee **identity and storage**, while Deployments prioritize **replica management** without caring about which Pod is which.

![StatefulSets Diagram](images/sts-light.png#only-light)
![StatefulSets Diagram](images/sts-dark.png#only-dark)

**Top Half (Deployment):** Pod reschedule = new IP, broken volume mount  
**Bottom Half (StatefulSet):** Pod is recreated with the **same IP**, **same volume**

---

## Key Features

| Feature                 | Deployment         | StatefulSet         |
|-------------------------|--------------------|----------------------|
| Pod name                | Random (e.g., `pod-abc123`) | Stable (e.g., `web-0`, `web-1`) |
| Pod start/delete order  | Any                | Ordered             |
| Persistent VolumeClaim  | Shared or ephemeral | One per Pod         |
| DNS hostname            | Random             | Stable via headless service |

---

## Sample YAML

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  serviceName: "web"  # Headless service
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
          image: nginx
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
            storage: 1Gi
```

---

## Networking & DNS

Pods in a StatefulSet get predictable hostnames:

```
web-0.web.default.svc.cluster.local
web-1.web.default.svc.cluster.local
```

This is enabled by the **headless Service**:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  clusterIP: None  # Headless
  selector:
    app: web
  ports:
    - port: 80
```

---

## Volume Behavior

Each Pod gets its own PVC:

- `web-0` → `data-web-0`
- `web-1` → `data-web-1`

These volumes are **retained** even if the Pod is deleted.

---

## Summary

StatefulSets are essential when:

- Each Pod must retain **identity**, **storage**, and **DNS**
- Order of startup or shutdown matters
- Storage must be preserved between Pod rescheduling

Use them wisely—they’re powerful but can be overkill for stateless services.