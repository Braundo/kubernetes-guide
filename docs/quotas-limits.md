---
icon: material/scale-balance
---

In a multi-tenant Kubernetes environment, it's important to prevent any single team, namespace, or workload from consuming all available cluster resources. Kubernetes provides two mechanisms to enforce this: **ResourceQuotas** and **LimitRanges**.

These tools help cluster administrators enforce **fair resource allocation**, **cost controls**, and **capacity planning** across teams and environments.

---

## ResourceQuota

A **ResourceQuota** defines a hard cap on the total resource usage (CPU, memory, object counts, etc.) within a namespace.

If the total usage across all Pods in the namespace exceeds the defined quota, further resource requests will be denied.

### Example: Memory & CPU Quota

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

This restricts total **requested** and **limited** CPU/memory for all Pods in the `dev` namespace.

### Example: Object Count Quota

```yaml
spec:
  hard:
    pods: "10"
    configmaps: "20"
    persistentvolumeclaims: "5"
```

You can limit the number of objects like Pods, ConfigMaps, or PVCs to enforce soft multi-tenancy boundaries.

---

## LimitRange

A **LimitRange** sets default values and upper/lower bounds for container-level resource usage **within a namespace**.

It ensures developers don’t accidentally omit or misuse resource definitions.

### Example: Default Limits and Requests

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

## Best Practices

- Use **ResourceQuotas** in shared clusters to prevent noisy neighbor problems.
- Apply **LimitRanges** to avoid under- or over-provisioned workloads.
- Combine both to enforce sane defaults and total caps.
- Monitor usage with `kubectl describe quota` or metrics dashboards.
- Document enforced limits for your teams to avoid confusion and failures.

---

## Summary

Kubernetes ResourceQuotas and LimitRanges are essential for managing shared cluster resources. They provide controls at both the namespace and container level, making it easier to ensure fairness, reduce waste, and maintain a healthy multi-tenant environment.