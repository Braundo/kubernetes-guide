---
icon: lucide/circle-gauge
title: Kubernetes Resource Requests and Limits Explained (CPU and Memory)
description: Learn how CPU and memory requests and limits work in Kubernetes and how they affect scheduling and performance.
hide:
 - footer
---

# Resource Requests and Limits

Resource settings are one of the most important workload controls in Kubernetes.

They determine scheduling quality, runtime stability, and autoscaling behavior.

## Core model

- `requests`: minimum resources reserved for scheduling
- `limits`: maximum runtime resources a container may use

If requests are too low, pods get packed too tightly and become unstable under load. If they are too high, cluster capacity is wasted.

## CPU and memory behavior

CPU and memory limits fail differently:

- CPU over limit: throttling, usually latency increase
- Memory over limit: OOM kill, container restart

That is why memory sizing errors are typically more disruptive.

## Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: ghcr.io/example/api:v5.2.1
          resources:
            requests:
              cpu: 250m
              memory: 512Mi
            limits:
              cpu: 1000m
              memory: 1Gi
```

## QoS classes

Pod QoS class is derived from resource configuration.

- Guaranteed: requests equal limits for all containers
- Burstable: at least one request set, but not all equal to limits
- BestEffort: no requests or limits

In node pressure events, BestEffort is usually evicted first.

## Sizing guidance

- Start from observed p50 and p95 usage, not guesses
- Keep requests close to realistic baseline load
- Set memory limits with enough headroom for peak behavior
- Avoid setting very low CPU limits on latency-sensitive services

## Relationship to autoscaling

HPA resource targets depend on requests. Bad request values produce bad scaling decisions.

Always tune requests before tuning autoscaler thresholds.

## Operational checks

```bash
kubectl top pods -A
kubectl describe pod <pod-name>
kubectl get pod <pod-name> -o jsonpath='{.status.containerStatuses[*].lastState}'
```

Look for `OOMKilled` events and sustained CPU throttling signals in metrics.

## Summary

Requests drive placement. Limits enforce runtime caps. Correct values improve stability, cost efficiency, and autoscaling quality.

## Related Concepts

- [Scaling and HPA](../workloads/scaling-hpa.md)
- [Resource Quotas](quotas-limits.md)
- [Troubleshooting](../operations/troubleshooting.md)
