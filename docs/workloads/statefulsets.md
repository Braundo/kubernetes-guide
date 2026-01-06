---
icon: lucide/database-zap
---

<h1>StatefulSets</h1>

A <strong>StatefulSet</strong> is a Kubernetes controller for running <strong>stateful apps</strong> - apps that need each Pod to keep its identity and storage, even if rescheduled. Think databases, message queues, or anything that can't just be replaced with a blank copy.

---

<h2>Why Use a StatefulSet?</h2>

Use a StatefulSet when your app needs:

- <strong>Stable network identity</strong> (like <code>pod-0</code>, <code>pod-1</code>)
- <strong>Persistent storage per Pod</strong> that sticks around if the Pod is rescheduled
- <strong>Ordered startup, scaling, and deletion</strong>

<strong>Examples:</strong> Databases (PostgreSQL, Cassandra), Zookeeper, Kafka, etc.

---

<h2>How It Differs from Deployments</h2>

StatefulSets guarantee identity and storage for each Pod, while Deployments just care about keeping the right number of Pods running (not which is which).

![StatefulSets Diagram](../images/sts-light.png#only-light)
![StatefulSets Diagram](../images/sts-dark.png#only-dark)

<strong>Top Half (Deployment):</strong> Pod reschedule = new IP, broken volume mount  
<strong>Bottom Half (StatefulSet):</strong> Pod is recreated with the <strong>same IP</strong>, <strong>same volume</strong>

---

<h2>Key Features</h2>

| Feature                 | Deployment         | StatefulSet         |
|-------------------------|--------------------|----------------------|
| Pod name                | Random (e.g., <code>pod-abc123</code>) | Stable (e.g., <code>web-0</code>, <code>web-1</code>) |
| Pod start/delete order  | Any                | Ordered             |
| Persistent VolumeClaim  | Shared/ephemeral   | One per Pod         |
| DNS hostname            | Random             | Stable via headless service |

---

<h2>Sample YAML</h2>

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
      tolerations:
      - key: "node-role.kubernetes.io/master"
        operator: "Exists"
        effect: "NoSchedule"
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

<h2>Summary</h2>
<ul>
<li><strong>StatefulSets</strong> are for apps that need stable identity and storage.</li>
<li>Use them for databases, queues, and apps that can't just be replaced with a blank Pod.</li>
<li>Deployments are for stateless, replaceable workloads.</li>
</ul>

!!! tip
    Only use StatefulSets when you really need sticky identity or storage. For most apps, Deployments are simpler and easier to manage.