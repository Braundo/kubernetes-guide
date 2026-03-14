---
icon: lucide/maximize-2
title: Kubernetes Horizontal Pod Autoscaling Explained (HPA and Metrics)
description: Learn how Kubernetes HPA works, how metrics drive scaling decisions, and common autoscaling patterns and pitfalls.
hide:
 - footer
---

# Scaling and HPA

Scaling in Kubernetes has three layers:

- workload scaling: change pod replicas
- node scaling: add or remove cluster nodes
- resource sizing: change CPU or memory requests per pod

This page focuses on workload scaling with Horizontal Pod Autoscaler (HPA).

## Manual scaling

Manual scaling is still useful for planned events:

```bash
kubectl scale deployment web --replicas=8
```

For live traffic variability, manual scaling does not react quickly enough.

## How HPA works

HPA watches metrics and adjusts replica count toward a target.

Typical loop:

1. read metrics for current pods
2. compare current utilization to desired target
3. compute desired replica count
4. update target Deployment or StatefulSet

## Prerequisites

HPA is only as good as metric quality.

Required baseline:

- metrics pipeline available (`metrics-server` for CPU or memory)
- workload has realistic `resources.requests`
- readiness probes are configured so new pods enter traffic safely

If `requests` are missing, percentage-based resource targets become unreliable.

## HPA example

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web
  minReplicas: 2
  maxReplicas: 12
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 20
          periodSeconds: 60
```

This configuration scales up aggressively and scales down more cautiously to reduce flapping.

## HPA troubleshooting

```bash
kubectl get hpa
kubectl describe hpa web-hpa
kubectl top pods -l app=web
```

Common failure patterns:

- `Unknown` targets due to missing metrics pipeline
- very slow response because pods have long startup times
- oscillation caused by too-tight thresholds and no stabilization

## HPA, VPA, and node autoscaling

- HPA scales pod count
- VPA adjusts pod resource requests
- node autoscaler or Karpenter adds infrastructure capacity

You can combine them, but avoid configuring HPA and VPA to fight on the same signal without a design.

## Practical guidance

- Start with CPU utilization targets around 50 to 70 percent
- Tune using real production latency and error metrics, not only CPU
- Set sensible min and max replica limits to protect cost and stability
- Validate behavior with load tests before relying on autoscaling in production

## Summary

HPA is a control loop, not a magic switch. It works well when metrics are trustworthy, pod requests are accurate, and rollout health checks are disciplined.

## Related Concepts

- [Pods and Deployments](pods-deployments.md)
- [Resource Requests and Limits](../configuration/limits-requests.md)
- [Kubernetes Troubleshooting](../operations/troubleshooting.md)
