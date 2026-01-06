---
icon: lucide/share-2
---

# Networking Concepts

Networking in Kubernetes is simple on the surface, but powerful under the hood. Every Pod gets an IP address, Services provide stable endpoints, and the network model enables communication across the entire cluster - often without needing to understand the low-level implementation details.

---

<h2>Core Principles of Kubernetes Networking</h2>

1. <strong>Each Pod gets a unique IP</strong>
   - No NAT between Pods
   - All containers within a Pod share the same network namespace

2. <strong>All Pods can reach each other</strong>
   - Flat network model (no IP masquerading between Pods)

3. <strong>Services provide stable access to Pods</strong>
   - Pods are ephemeral - Services give them a consistent IP + DNS name

---

<h2>Network Abstraction Layers</h2>

| Layer        | Purpose                                   |
|--------------|--------------------------------------------|
| <strong>Pod Network</strong> | Every Pod gets an IP, routable in-cluster |
| <strong>Service</strong>      | Provides a stable endpoint for Pod groups |
| <strong>Ingress</strong>      | Exposes HTTP/S services externally       |
| <strong>NetworkPolicy</strong>| Controls traffic between Pods (optional) |

---

<h2>DNS in Kubernetes</h2>

Kubernetes includes built-in **DNS resolution** for:

- Services: `my-service.my-namespace.svc.cluster.local`
- Pods (not recommended for direct use)

DNS is powered by CoreDNS by default, running in the `kube-system` namespace.

```shell
nslookup my-service.default.svc.cluster.local
```

---

## Pod-to-Pod Communication

- All Pods are routable via their internal IP addresses
- No need for manual port forwarding
- Backed by a **Container Network Interface (CNI)** plugin (e.g., Calico, Flannel)

---

## Service Types (Covered in next section)

- `ClusterIP` – default; internal-only
- `NodePort` – exposes on every node
- `LoadBalancer` – cloud provider external IP
- `ExternalName` – DNS alias

---

<h2>Summary</h2>

- Kubernetes networking gives every Pod a unique IP and makes service discovery simple.
- All Pods can talk to each other by default-use NetworkPolicies to restrict if needed.
- Understanding the network model is key for debugging, scaling, and securing your apps.

!!! tip
    Use DNS names for service discovery, and always test network policies and connectivity in staging before rolling out to production.