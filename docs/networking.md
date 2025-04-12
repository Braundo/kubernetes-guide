---
icon: material/lan
---

# Networking Overview

Networking in Kubernetes is simple on the surface, but powerful under the hood. Every Pod gets an IP address, Services provide stable endpoints, and the network model enables communication across the entire cluster — often without needing to understand the low-level implementation details.

---

## Core Principles of Kubernetes Networking

1. **Each Pod gets a unique IP**
   - No NAT between Pods
   - All containers within a Pod share the same network namespace

2. **All Pods can reach each other**
   - Flat network model (no IP masquerading between Pods)

3. **Services provide stable access to Pods**
   - Pods are ephemeral — Services give them a consistent IP + DNS name

---

## Network Abstraction Layers

| Layer        | Purpose                                   |
|--------------|--------------------------------------------|
| **Pod Network** | Every Pod gets an IP, routable in-cluster |
| **Service**      | Provides a stable endpoint for Pod groups |
| **Ingress**      | Exposes HTTP/S services externally       |
| **NetworkPolicy**| Controls traffic between Pods (optional) |

---

## DNS in Kubernetes

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
- `NodePort` – exposes via node IP + static port
- `LoadBalancer` – provision external LB (cloud)
- `ExternalName` – maps to external DNS

---

## Key Takeaways

- Kubernetes assumes a **flat, open network** where every Pod can talk to every other Pod
- You don’t need to assign IPs or manage routes — the CNI plugin does that
- Communication is typically via **Service abstraction**, not direct Pod IPs
- You can add **NetworkPolicies** to restrict traffic if needed

---

## Summary

- Every Pod gets an IP — networking is **native**, not container-to-container port mapping
- Services, not Pods, are the preferred way to access applications
- DNS is built-in and resolves Services by name
- You don’t manage the network manually — but understanding its behavior is essential