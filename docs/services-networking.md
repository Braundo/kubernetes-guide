---
icon: material/server-network
---

# Services & Networking

Pods are ephemeral — they come and go. A **Service** gives you a stable way to **communicate with groups of Pods**, no matter how often those Pods restart, move, or scale.

---

## What Is a Service?

A Kubernetes **Service** is an abstraction that:

- Selects a group of Pods using a **label selector**
- Assigns a **stable IP and DNS name**
- Forwards traffic to the correct Pods, even as they change

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 8080
```

This exposes Pods with label `app=web` on port 80, forwarding traffic to their port 8080.

---

## 1. ClusterIP (default)

A **ClusterIP** Service exposes Pods **within the cluster only**.

- Internal IP address (`10.x.x.x`)
- DNS-resolvable: `web.default.svc.cluster.local`
- Default Service type

![ClusterIP Diagram](images/clusterip-light.png#only-light)
![ClusterIP Diagram](images/clusterip-dark.png#only-dark)

### Use When:
- Services communicate internally (e.g., frontend ↔ backend)
- You don’t need external access

---

## 2. NodePort

A **NodePort** Service exposes your app to the **outside world** using a static port on **every node** in the cluster.

- Uses the node's IP + assigned port (default range: `30000–32767`)
- Maps traffic from each node to the backing Pods

```yaml
spec:
  type: NodePort
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080
```

Access from outside the cluster:

```
http://<node-ip>:30080
```

![NodePort Diagram](images/nodeport-light.png#only-light)
![NodePort Diagram](images/nodeport-dark.png#only-dark)

### Use When:
- Testing external access without a LoadBalancer
- You don’t have a cloud provider (e.g., on-prem clusters)

---

## 3. LoadBalancer

A **LoadBalancer** Service provisions an **external cloud load balancer** (if supported by your environment).

- Only works with cloud providers (GCP, AWS, Azure)
- Assigns a public IP and balances across backing Pods
- Combines NodePort + external LB behind the scenes

```yaml
spec:
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 8080
```

![LoadBalancer Diagram](images/loadbalancer-light.png#only-light)
![LoadBalancer Diagram](images/loadbalancer-dark.png#only-dark)

### Use When:
- You want public access to your app in a cloud environment
- You need external DNS + SSL termination (with Ingress)

---

## 4. ExternalName (Special Case)

Maps a Kubernetes Service to an **external DNS name**.

```yaml
spec:
  type: ExternalName
  externalName: db.example.com
```

- No selectors or backing Pods
- Useful for referencing external databases, APIs, etc.

---

## Summary Table

| Type           | Visibility       | Use Case                        | Requires Cloud |
|----------------|------------------|----------------------------------|----------------|
| `ClusterIP`    | Internal only     | Pod-to-Pod communication         | No             |
| `NodePort`     | Exposes on node IP| Direct external access via port  | No             |
| `LoadBalancer` | External IP       | Cloud load balancer with public IP| ✅ Yes       |
| `ExternalName` | DNS redirect      | External services via DNS        | No             |

---

## Summary

- **Services abstract a group of Pods** behind a stable IP and DNS name.
- **ClusterIP** is the default and internal-only.
- **NodePort** opens access via node IP and high port.
- **LoadBalancer** gives you a cloud-managed endpoint.
- **ExternalName** is a DNS-level alias.

Understanding how each Service type works — and when to use it — is essential for building reliable, scalable apps in Kubernetes.