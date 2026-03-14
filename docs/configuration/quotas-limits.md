---
icon: lucide/scale
title: Kubernetes Resource Quotas Explained (Controlling Resource Usage)
description: Learn how Kubernetes ResourceQuotas limit resource consumption at the namespace level and prevent noisy-neighbor issues.
hide:
 - footer
---

# Quotas and LimitRanges

In shared clusters, guardrails are required to keep one namespace from exhausting capacity for everyone else.

Two native controls work together:

- ResourceQuota: namespace-wide aggregate limits
- LimitRange: per-container and per-pod defaults or boundaries

## ResourceQuota example

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-a-quota
  namespace: team-a
spec:
  hard:
    requests.cpu: "8"
    requests.memory: 16Gi
    limits.cpu: "16"
    limits.memory: 32Gi
    pods: "60"
    services.loadbalancers: "2"
```

This prevents unchecked growth in compute and expensive objects.

## LimitRange example

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: team-a-defaults
  namespace: team-a
spec:
  limits:
    - type: Container
      defaultRequest:
        cpu: 200m
        memory: 256Mi
      default:
        cpu: 500m
        memory: 512Mi
      min:
        cpu: 100m
        memory: 128Mi
      max:
        cpu: "2"
        memory: 2Gi
```

This enforces sane per-container boundaries and fills in defaults when developers omit resources.

## Admission behavior

The API server applies LimitRange defaults first, then evaluates ResourceQuota usage.

If quota would be exceeded, object creation is rejected with `403 Forbidden`.

## Operational guidance

- pair ResourceQuota with LimitRange in every shared namespace
- define quota by team environment and expected workload profile
- review quota usage regularly during growth periods
- keep exception process controlled and documented

## Useful checks

```bash
kubectl get quota -A
kubectl describe quota team-a-quota -n team-a
kubectl get limitrange -A
kubectl describe limitrange team-a-defaults -n team-a
```

## Common mistakes

- quota without limitrange, causing frequent request rejections
- quota values copied between namespaces with different workload patterns
- no object count limits, leading to runaway pod or job creation

## Summary

ResourceQuota controls namespace budgets. LimitRange enforces local standards. Together they provide predictable multi-tenant cluster behavior.

## Related Concepts

- [Resource Requests and Limits](limits-requests.md)
- [Namespaces](../getting-started/namespaces.md)
- [Scaling and HPA](../workloads/scaling-hpa.md)
