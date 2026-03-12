---
icon: lucide/book-open
title: Playbooks
description: Operator playbooks and field guidance for Kubernetes reliability, resiliency, and platform architecture decisions.
hide:
 - footer
---

# Playbooks

Playbooks are practical, opinionated operator guides for decisions that are bigger than day-to-day news.
Use this section for topics like HA architecture, multi-cluster failover design, upgrade strategy, and production reliability patterns.

<!-- AUTO-LATEST:START -->
| Date | News | Summary |
| --- | --- | --- |
| 2026-03-11 | [How Traffic Actually Flows in Kubernetes: Services, kube-proxy, and Cloud Load Balancers](2026-03-11-how-traffic-flows-in-kubernetes.md) | A Kubernetes Service is not a load balancer - it is a routing abstraction. Understanding the three layers that actually move traffic (node dataplane, cloud load balancer, application connections) explains most real-world… |
| 2026-03-10 | [True HA in Kubernetes: Why Multi-Zone Alone Isn't Enough](2026-03-10-true-ha-resiliency-beyond-multi-zone.md) | Multi-zone clusters remove the zone-failure risk but create a false sense of security. Real high availability requires coordinating PDBs, topology spread constraints, affinity rules, probes, graceful shutdown, and… |
| 2026-03-10 | [Why Kubernetes Scheduling Uses Requests, Not Limits](2026-03-10-kubernetes-scheduling-requests-not-limits.md) | Kubernetes schedules Pods based on resource requests, not limits. Understanding this distinction explains noisy neighbor problems, unexpected autoscaling behavior, and wasted cluster capacity, and how to fix them. |
<!-- AUTO-LATEST:END -->

## Related

- [Release news](../releases/index.md)
- [Security news](../security/index.md)
- [Kubernetes learning paths](../../learn/index.md)
