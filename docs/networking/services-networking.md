---
icon: lucide/network
title: Kubernetes Services Explained (ClusterIP, NodePort, LoadBalancer)
description: Learn how Kubernetes Services work, how traffic flows to Pods, and when to use ClusterIP, NodePort, and LoadBalancer with real examples.
hide:
  - footer
---

<h1>Services & Networking</h1>

Pods are short-lived - they can appear and disappear at any time. A <strong>Service</strong> gives you a stable way to talk to a group of Pods, no matter how often those Pods restart or move.

---

<h2>What Is a Service?</h2>

A Kubernetes <strong>Service</strong> is like a switchboard operator for your Pods:
- Selects a group of Pods (using labels)
- Gives them a stable IP and DNS name
- Forwards traffic to the right Pods, even as they change

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

This exposes Pods with label <code>app=web</code> on port 80, forwarding traffic to their port 8080.

---

<h2>1. ClusterIP (default)</h2>

A <strong>ClusterIP</strong> Service is for internal communication only. Think of it as a company’s internal phone extension - only people inside the building (cluster) can call it.

- Internal IP address (e.g., <code>10.x.x.x</code>)
- DNS: <code>web.default.svc.cluster.local</code>
- Default Service type

![ClusterIP Diagram](../images/clusterip-light.png#only-light)
![ClusterIP Diagram](../images/clusterip-dark.png#only-dark)

<strong>Use When:</strong>

- Apps need to talk to each other inside the cluster (e.g., frontend ↔ backend)
- No external access needed

---

<h2>2. NodePort</h2>

A <strong>NodePort</strong> Service lets people outside your cluster reach your app using a static port on every node. It’s like giving every employee in the company a direct phone number that rings their internal extension.

- Uses each node’s IP + port (range: <code>30000–32767</code>)
- Forwards traffic from node to the right Pods

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

![NodePort Diagram](../images/nodeport-light.png#only-light)
![NodePort Diagram](../images/nodeport-dark.png#only-dark)

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

![LoadBalancer Diagram](../images/loadbalancer-light.png#only-light)
![LoadBalancer Diagram](../images/loadbalancer-dark.png#only-dark)

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
| `ClusterIP`    | Internal only     | Pod-to-Pod communication         | ❌ No             |
| `NodePort`     | Exposes on node IP| Direct external access via port  | ❌ No             |
| `LoadBalancer` | External IP       | Cloud load balancer with public IP| ✅ Yes       |
| `ExternalName` | DNS redirect      | External services via DNS        | ❌ No             |

---

## Summary

- **Services abstract a group of Pods** behind a stable IP and DNS name.
- **ClusterIP** is the default and internal-only.
- **NodePort** opens access via node IP and high port.
- **LoadBalancer** gives you a cloud-managed endpoint.
- **ExternalName** is a DNS-level alias.

<br>
Understanding how each Service type works  -  and when to use it  -  is essential for building reliable, scalable apps in Kubernetes.
<br>

---

## Related Concepts

- [Kubernetes Networking Overview](networking/)
- [Ingress](ingress/) for HTTP routing
- [Pods and Deployments](../workloads/pods-deployments/)
