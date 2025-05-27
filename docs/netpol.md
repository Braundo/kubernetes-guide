---
icon: material/shield-key-outline
---

<h1>Network Policies</h1>

By default, <strong>all Pods in a Kubernetes cluster can talk to each other</strong>. This is convenient, but risky—especially in multi-tenant clusters or production environments.

<strong>NetworkPolicies</strong> let you control <strong>which Pods can talk to which other Pods</strong> (and even external IPs).

> Think of it like a firewall for Pod-to-Pod traffic—but defined in YAML.

---

<h2>Key Concepts</h2>

- NetworkPolicies apply to <strong>Pods</strong> (via label selectors)
- They control <strong>ingress</strong>, <strong>egress</strong>, or both
- They require a <strong>network plugin (CNI)</strong> that supports them (e.g., Calico, Cilium)

> No policies = allow all  
> Any policy = default deny (for the targeted direction)

---

<h2>Minimal Example</h2>

Allow only traffic to a Pod from Pods with a specific label:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: backend
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
```

This says:  **only Pods labeled `app=frontend` can access Pods labeled `app=backend`.**

---

<h2>Policy Scope</h2>

| Field         | Controls                              |
|---------------|----------------------------------------|
| `podSelector` | Which Pods the policy applies <strong>to</strong>   |
| `ingress`     | Who can reach the Pod                  |
| `egress`      | Where the Pod is allowed to send traffic |

---

## Egress Example

```yaml
egress:
  - to:
      - ipBlock:
          cidr: 10.0.0.0/24
    ports:
      - protocol: TCP
        port: 443
```

This allows outbound HTTPS traffic only to `10.0.0.0/24`.

---

## Tips & Gotchas

- If a Pod is **not selected by any policy**, it is **open by default**
- If a Pod **is selected**, and you define `ingress`, **all other traffic is denied**
- You must allow **DNS** explicitly if you restrict egress (e.g., UDP 53)
- Labels matter — both on the **target** and the **allowed sources**

---

## CNI Support

Not all network plugins support NetworkPolicies. Some common ones that do:

- ✅ Calico
- ✅ Cilium
- ✅ Antrea
- ❌ Flannel (without plugins)
- ❌ Amazon VPC CNI (limited support unless enhanced)

---

<h2>Summary</h2>

- <strong>NetworkPolicies</strong> let you control pod-to-pod and pod-to-external communication.
- By default, all traffic is allowed—add a policy to restrict.
- Use label selectors to target specific Pods for fine-grained control.
- NetworkPolicies control **Pod-level traffic** based on labels and CIDRs
- Define **who can talk to what**, and where traffic can go
- Essential for **zero-trust network design** inside the cluster
- Start with `ingress` rules, then layer on `egress` if needed