---
title: KEDA Tool Radar (Event-Driven Autoscaling)
date: 2026-03-06
category: tool-radar
description: Radar update for KEDA and event-driven autoscaling patterns in Kubernetes clusters.
---

# KEDA Tool Radar (Event-Driven Autoscaling)

KEDA is a CNCF project focused on event-driven autoscaling for Kubernetes workloads.

## What the Tool Does

KEDA extends autoscaling beyond CPU and memory by connecting Kubernetes workloads to event sources such as queues, streams, and cloud services.

## Why It Is Worth Watching

For asynchronous workloads, default HPA signals are often insufficient. KEDA can improve scaling behavior and cost efficiency where event depth or external signals better represent demand.

## Maturity and Adoption Notes

KEDA is established with broad adoption in event-driven architectures. Teams should still tune scaler thresholds and cooldown behavior carefully to avoid oscillation.

## Popularity and Momentum Signals

| Signal | Value |
| --- | --- |
| GitHub stars | 9,963 |
| Forks | 1,338 |
| Open issues | 246 |
| Watchers | 86 |
| Last push | 2026-03-06 |
| Momentum label | **Hot** |

## Category

Autoscaling and event-driven workload operations.

## Source Links

- [KEDA repository](https://github.com/kedacore/keda)
- [Horizontal Pod Autoscaler docs](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)

## Related Pages

- Parent index: [Tool Radar](index.md)
- Related: [Flux tool radar](2026-03-flux-gitops-radar.md)
- Related: [Port Killer tool radar](2025-12-port-killer-devex-radar.md)
- Newsletter: [This Week in Kubernetes](../../index.md#weekly-newsletter)
- Evergreen reference: [Scaling and HPA](../../workloads/scaling-hpa.md)
