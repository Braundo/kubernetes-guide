---
title: "Why Kubernetes Scheduling Uses Requests, Not Limits"
date: 2026-03-10
category: playbooks
description: "Kubernetes schedules Pods based on resource requests, not limits. Understanding this distinction explains noisy neighbor problems, unexpected autoscaling behavior, and wasted cluster capacity, and how to fix them."
---

# Why Kubernetes Scheduling Uses Requests, Not Limits

One of the most consequential design details in Kubernetes is that the scheduler only considers resource **requests** when deciding where a Pod can run. Resource **limits** are ignored entirely during scheduling and are enforced later at runtime by the kubelet and the Linux kernel.

This single distinction explains a surprising number of real-world problems: noisy neighbors, unexpected autoscaler behavior, CPU throttling at low utilization, and clusters that appear full while actual workload usage is a fraction of allocated capacity.

---

## Requests vs. Limits

Kubernetes allows containers to declare two separate resource values:

| Field | Meaning |
|---|---|
| `request` | The guaranteed minimum the Pod needs; used by the scheduler |
| `limit` | The maximum the container is allowed to consume; enforced at runtime |

```yaml
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 2
    memory: 2Gi
```

The scheduler sees this Pod as needing `0.5 CPU` and `512Mi` of memory. The fact that it could burst to `2 CPU` and `2Gi` is irrelevant to placement decisions. The limits are invisible to the scheduler.

---

## How the Scheduler Uses Requests

Scheduling comes down to a feasibility check against a node's remaining allocatable capacity. Capacity is tracked as the sum of all scheduled Pod requests: not actual utilization, and not limits.

**Example:**

A node with `8 CPU` and `32Gi` of memory already has Pods scheduled with a combined `7 CPU` and `20Gi` in requests. Remaining capacity: `1 CPU`, `12Gi`.

A new Pod with `requests.cpu: 500m` and `requests.memory: 1Gi` fits. It gets scheduled to this node, even though its limits are `cpu: 4` and `memory: 8Gi`. The limits play no role in this decision.

---

## Why Kubernetes Was Designed This Way

Kubernetes inherited this model from Google's Borg scheduler. The core philosophy: schedule based on guaranteed needs, not theoretical maximums.

If the scheduler considered limits instead of requests, cluster utilization would collapse. Imagine 100 Pods, each with a `cpu` limit of `2`. The scheduler would have to assume 200 CPU of demand. In practice, those same Pods might collectively use 15 CPU at peak. Scheduling against limits would make that cluster effectively useless for all but the first few Pods.

Requests enable safe overcommitment. The cluster runs efficiently because most workloads don't consume their maximum simultaneously. This is the same reasoning behind memory overcommit in operating systems: it works well when load is distributed and bursty, and fails badly when it isn't.

---

## When Requests Are Too Low

If requests are underestimated, Kubernetes packs too many workloads onto nodes.

**Example:** A Pod declares `requests.cpu: 100m` but routinely uses `900m`. The scheduler sees a small Pod and places many of them on the same node. At runtime, those Pods compete for actual CPU time.

Symptoms of under-requesting:

- Latency spikes under load
- CPU throttling even on underloaded nodes
- Autoscaler scaling out when nodes aren't actually full
- Noisy neighbor behavior between otherwise unrelated workloads

The autoscaler case is worth calling out specifically: HPA scales on CPU utilization as a percentage of requests. A Pod using `900m` of a `100m` request shows 900% utilization, which triggers aggressive scaling, even if the node has plenty of headroom.

---

## When Requests Are Too High

Over-requesting has the opposite problem: capacity is reserved but never used.

**Example:** A Pod declares `requests.cpu: 4` but consistently uses `300m`. The scheduler reserves 4 CPU worth of space. Other Pods can't be scheduled to that node even though most of that allocation is idle.

Symptoms of over-requesting:

- Nodes appear full while actual CPU and memory utilization is low
- Cluster autoscaler provisions additional nodes unnecessarily
- Infrastructure costs increase without a corresponding workload increase
- Pod scheduling fails with `Insufficient cpu` on nodes that have idle capacity

Over-requesting is common in organizations where teams have learned (often the hard way) that under-requesting causes throttling. The response is to inflate requests defensively, which shifts the problem from runtime contention to wasted capacity and higher bills.

---

## What Limits Actually Do

Limits are not a scheduler concept. They are a runtime enforcement mechanism implemented by the container runtime and the Linux kernel via cgroups.

**CPU limits** are enforced using cgroup CPU throttling. If a container exceeds its CPU limit within a scheduling period (typically 100ms), its CPU time is restricted for the remainder of that period. This can cause latency spikes even when the node has available CPU. A container at `cpu: 1000m` limit on a lightly loaded node can still be throttled; the kernel enforces the limit regardless of what other Pods are doing. This is why CPU limits are often more harmful than helpful for latency-sensitive services.

**Memory limits** are hard caps. If a container exceeds its memory limit, the kernel sends `SIGKILL`; this appears as an `OOMKilled` status in the Pod. Unlike CPU throttling, there is no graceful degradation. The container simply dies. This happens regardless of how much memory the node has available.

---

## Requests Determine QoS Class

Kubernetes assigns every Pod a Quality of Service (QoS) class based on how its requests and limits are configured. This class affects eviction priority during node memory or resource pressure.

| QoS Class | Criteria |
|---|---|
| `Guaranteed` | Every container has `requests == limits` for both CPU and memory |
| `Burstable` | At least one container has `requests < limits`, or only requests are set |
| `BestEffort` | No requests or limits are set on any container |

Under memory pressure, the kubelet evicts Pods in this order: `BestEffort` first, then `Burstable`, then `Guaranteed`. Setting accurate requests and appropriate limits is therefore both a scheduler concern and an eviction-resilience concern.

---

## Enterprise Capacity Implications

Platform teams at larger organizations consistently run into two failure modes:

**Over-requesting** tends to emerge from teams that have experienced throttling or OOMKill events. The instinctive fix is to increase requests and limits. Without feedback loops or quotas, this produces clusters where nodes look full but average utilization is 10-20%.

**Under-requesting** tends to emerge from developer-facing platforms where teams are optimizing for fast scheduling or minimizing resource quota consumption. Pods land on nodes they'll overwhelm at runtime, and problems surface as intermittent latency and autoscaler puzzles.

Both are management and observability problems as much as they are technical ones.

---

## Mature Platform Practices

Organizations that get this right typically introduce several layers of guardrails:

**LimitRanges** define default and minimum requests at the namespace level. Pods deployed without resource declarations get sensible defaults rather than BestEffort class and unbounded consumption.

**ResourceQuotas** cap the total requests and limits a namespace can accumulate, preventing any single team from consuming disproportionate cluster capacity.

**Request vs. usage dashboards** expose the gap between what Pods declare and what they actually use. Prometheus metrics like `kube_pod_container_resource_requests` and `container_cpu_usage_seconds_total` make this straightforward to visualize.

**VPA in recommendation mode** can surface right-sized request values based on historical usage without automatically modifying running Pods. It provides data-driven tuning rather than guesswork.

**Scheduled right-sizing reviews:** teams periodically review their request configurations against actual metrics and adjust. This is a process question, not just a tooling one.

---

## Key Takeaway

The scheduler makes placement decisions based on what a Pod guarantees it needs (requests). It has no visibility into what a Pod might consume at peak (limits). Getting requests right is not an optimization. It is foundational to cluster stability, cost efficiency, and autoscaler correctness.

Limits protect neighbors and prevent runaway processes. Requests protect scheduling accuracy and cluster economics. Both matter, but they operate at different layers and serve different purposes.

---

## Related Pages

- Parent index: [Playbooks](index.md)
- Related: [Pods and Deployments](../../workloads/pods-deployments.md)
- Related: [Scaling with HPA](../../workloads/scaling-hpa.md)
- Related: [Operations and Maintenance](../../operations/maintenance.md)
- Newsletter: [This Week in Kubernetes](../../index.md#weekly-newsletter)
