---
icon: lucide/book-open
title: Opinion & Overview
description: Opinionated Kubernetes analysis, architecture tradeoffs, and operator guidance from real-world platform engineering practice.
hide:
 - footer
---

# Opinion & Overview

These are practical, opinionated operator guides for decisions that are bigger than daily update cycles.
Use this section for architecture tradeoffs, reliability and resilience patterns, and clear point-of-view guidance for platform teams.

<!-- AUTO-LATEST:START -->
| Date | Article | Summary |
| --- | --- | --- |
| 2026-04-01 | [Node Pressure and Eviction: What Kubelet Actually Does When Things Get Tight](2026-04-01-node-pressure-eviction-kubelet.md) | Kubelet's eviction manager is the last line of defense before a node becomes unstable. Understanding how eviction thresholds work, why QoS class determines who dies first, and where the gap between scheduler requests and… |
| 2026-03-17 | [Horizontal Pod Autoscaler: From Metrics to Scheduling Pressure](2026-03-17-hpa-metrics-to-scheduling-pressure.md) | HPA is a proportional feedback controller, not a provisioning system. Understanding its formula, metrics pipeline lag, and stabilization layer is what separates operators who tune it reliably from those who chase… |
| 2026-03-16 | [How etcd Consistency Guarantees Shape Kubernetes Control Plane Behavior](2026-03-16-etcd-consistency-kubernetes-control-plane.md) | etcd is not just a database. It is the linearizable coordination primitive that every Kubernetes controller is built on top of. |
| 2026-03-14 | [The Kubernetes Scheduler: Decision Loop, Plugin Architecture, and Operational Reality](2026-03-14-kubernetes-scheduler-decision-loop.md) | The Kubernetes scheduler is not a router. It is a continuous reconciler that applies a filtering and ranking pipeline to a cluster snapshot. |
| 2026-03-12 | [Why Every Pod Gets a Real IP: The Kubernetes Flat Network Model, CNIs, and Ingress Controllers](2026-03-12-kubernetes-flat-network-cni-ingress.md) | Kubernetes enforces a simple rule: every Pod can reach every other Pod directly, without NAT. This single constraint drives the entire networking architecture - from CNI plugin selection to ingress controller design. |
| 2026-03-11 | [How Traffic Actually Flows in Kubernetes: Services, kube-proxy, and Cloud Load Balancers](2026-03-11-how-traffic-flows-in-kubernetes.md) | A Kubernetes Service is not a load balancer - it is a routing abstraction. Understanding the three layers that actually move traffic (node dataplane, cloud load balancer, application connections) explains most real-world… |
| 2026-03-10 | [True HA in Kubernetes: Why Multi-Zone Alone Isn't Enough](2026-03-10-true-ha-resiliency-beyond-multi-zone.md) | Multi-zone clusters remove the zone-failure risk but create a false sense of security. Real high availability requires coordinating PDBs, topology spread constraints, affinity rules, probes, graceful shutdown, and… |
| 2026-03-10 | [Why Kubernetes Scheduling Uses Requests, Not Limits](2026-03-10-kubernetes-scheduling-requests-not-limits.md) | Kubernetes schedules Pods based on resource requests, not limits. Understanding this distinction explains noisy neighbor problems, unexpected autoscaling behavior, and wasted cluster capacity, and how to fix them. |
<!-- AUTO-LATEST:END -->

## Related

- [Tool Radar](../tool-radar/index.md)
- [News](../../news/index.md)
