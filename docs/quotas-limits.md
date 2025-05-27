---
icon: material/scale-balance
---

<h1>Resource Quotas & LimitRanges</h1>

In a multi-tenant Kubernetes environment, you need to make sure no single team or workload can hog all the resources. Kubernetes provides two key tools for this: <strong>ResourceQuotas</strong> and <strong>LimitRanges</strong>.

These help admins enforce <strong>fair resource allocation</strong>, <strong>cost controls</strong>, and <strong>capacity planning</strong>.

---

<h2>ResourceQuota</h2>

A <strong>ResourceQuota</strong> sets a hard cap on the total resource usage (CPU, memory, object counts, etc.) within a namespace.

If the sum of all Pods in the namespace exceeds the quota, new requests are denied.

<h3>Example: Memory & CPU Quota</h3>

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: dev
spec:
  hard:
    requests.cpu: "2"
    requests.memory: "4Gi"
    limits.cpu: "4"
    limits.memory: "8Gi"
```

This restricts total <strong>requested</strong> and <strong>limited</strong> CPU/memory for all Pods in the <code>dev</code> namespace.

<h3>Example: Object Count Quota</h3>

```yaml
spec:
  hard:
    pods: "10"
    configmaps: "20"
    persistentvolumeclaims: "5"
```

You can limit the number of objects like Pods, ConfigMaps, or PVCs to enforce soft multi-tenancy boundaries.

---

<h2>LimitRange</h2>

A <strong>LimitRange</strong> sets default values and upper/lower bounds for container-level resource usage <strong>within a namespace</strong>.

It ensures developers don’t accidentally omit or misuse resource definitions.

<h3>Example: Default Limits and Requests</h3>

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-resources
spec:
  limits:
  - default:
      cpu: 500m
      memory: 512Mi
    defaultRequest:
      cpu: 250m
      memory: 256Mi
    type: Container
```

This sets:

- A **default request and limit** if none is provided in the Pod spec.
- A guardrail to prevent containers from consuming too much by default.

---

## When to Use Quotas vs LimitRanges

| Feature              | ResourceQuota                      | LimitRange                             |
|----------------------|-------------------------------------|-----------------------------------------|
| Scope                | Namespace-wide                      | Per container                           |
| Controls total usage | ✅                                   | ❌                                       |
| Sets defaults        | ❌                                   | ✅                                       |
| Enforces boundaries  | ✅ (hard enforcement)                | ✅ (via defaults and min/max)           |
| Common Use           | Multi-team environments             | Developer guardrails                    |

---

<h2>Summary</h2>
<ul>
  <li><strong>ResourceQuotas</strong>: Limit total resources in a namespace.</li>
  <li><strong>LimitRanges</strong>: Set defaults and max/min per container.</li>
  <li>Both are essential for multi-tenant, production-grade clusters.</li>
</ul>

<h2>Best Practices</h2>
<ul>
  <li>Always set quotas and limits in shared clusters. It keeps things fair, predictable, and safe for everyone.</li>
  <li>Monitor usage with `kubectl describe quota` or metrics dashboards.</li>
  <li>Document enforced limits for your teams to avoid confusion and failures.</li>
</ul>

