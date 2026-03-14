---
title: "Why Kubernetes Scheduling Uses Requests, Not Limits"
date: 2026-03-10
category: insights
description: "Kubernetes schedules Pods based on resource requests, not limits. Understanding this distinction explains noisy neighbor problems, unexpected autoscaling behavior, and wasted cluster capacity, and how to fix them."
---

# Why Kubernetes Scheduling Uses Requests, Not Limits

## Situation

Kubernetes schedules Pods based on resource **requests**, not limits. This means a Pod that declares `requests.cpu: 100m` but regularly consumes `900m` will be packed onto nodes as if it were a tiny workload. A Pod that declares `requests.cpu: 4` but routinely uses `300m` will block other workloads from landing on nodes that have plenty of idle capacity.

The mismatch between what workloads claim and what they consume is the root cause behind a wide class of real-world problems: latency spikes under load, HPA scaling at the wrong time, nodes that report full capacity while actual utilization sits at 15%, and OOMKill events that feel random until you trace them to QoS class assignment.

Platform teams often discover this the hard way after their first noisy-neighbor incident or after asking why the cluster autoscaler keeps spinning up new nodes on a cluster that looks idle from the cloud console. The root cause is almost always misconfigured requests.

---

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

## Architecture and Tradeoffs

### The Scheduler's View

The Kubernetes scheduler evaluates node fit purely against allocatable capacity minus the sum of scheduled Pod requests. It has no visibility into actual CPU or memory usage, and it deliberately ignores limits. This is a design choice, not a limitation.

Scheduling against limits would require reserving worst-case capacity for every Pod, collapsing effective utilization to near zero on most clusters. Scheduling against actual utilization would require real-time feedback loops that reintroduce the non-determinism the scheduler was designed to avoid.

Requests represent a contract: the cluster guarantees a Pod at least that many resources. Everything above the request is best-effort burst capacity, governed by cgroup enforcement rather than scheduler placement.

### cgroups and the Runtime Enforcement Layer

CPU limits map to cgroup CPU quota and period. The kernel grants CPU time in slices, and if a container exhausts its quota in a period (default 100ms), it is throttled for the rest of that period regardless of node load. This is why CPU throttling can occur on a nearly idle node; the enforcement is per-period, not load-relative.

Memory limits are enforced as hard cgroup memory caps. When a container exceeds its limit, the kernel invokes the OOM killer, which sends SIGKILL to the container process. There is no warning, no graceful shutdown, and the event surfaces as `OOMKilled` in Pod status. Unlike CPU throttling, memory limit violations are always terminal.

### QoS Class and Eviction Priority

The kubelet assigns a QoS class to every Pod based on request/limit configuration. Under memory pressure, eviction order follows QoS class: `BestEffort` first (no requests or limits set), then `Burstable` (requests less than limits, or only requests set), then `Guaranteed` (requests equal to limits for all containers).

This means request configuration affects not just placement at schedule time, but survival probability at runtime. A Pod with no requests set is at the front of the eviction queue the moment any node comes under pressure.

### Overcommit: The Intended Model

Overcommitment is the intended operating model. Clusters are designed to pack workloads that collectively declare more in requests than the node can satisfy simultaneously. This works because most workloads don't peak at the same time. When they do, QoS classes and eviction policies determine who survives.

The tradeoff is explicit: higher utilization and density in exchange for the possibility of interference under load. Getting requests right is how you control where your workloads land in that tradeoff.

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

## Failure Modes to Plan For

### Noisy Neighbor CPU Contention

Under-requested Pods get scheduled alongside each other on the same node. At runtime they compete for CPU time, causing latency spikes that are hard to correlate with the actual cause. The affected Pod looks fine in isolation; the problem is the co-location decision made at schedule time based on incorrect request data.

**Signal:** Latency p99 spikes on lightly loaded nodes. CPU throttling visible in `container_cpu_cfs_throttled_seconds_total` even when node CPU is below 70%.

### HPA Scaling Loops

HPA computes utilization as actual usage divided by requested capacity. A Pod using `900m` against a `100m` request shows 900% utilization. HPA scales out aggressively. New replicas land and also show 900% utilization (because they're also under-requested). The autoscaler keeps scaling. The cluster grows without the workload actually being CPU-constrained.

**Signal:** Replica counts growing while node CPU utilization stays flat. HPA `current` vs `desired` replicas diverging under normal load.

### Phantom Capacity Exhaustion

Over-requested Pods consume allocatable capacity that is never actually used. Nodes appear full to the scheduler while actual workload resource usage may be a fraction of what's reserved. New Pods fail to schedule with `Insufficient cpu` on nodes that look busy in `kubectl describe node` but idle in Prometheus.

**Signal:** Pending Pods with `Insufficient cpu` or `Insufficient memory`, combined with low actual CPU/memory utilization on nodes. Cluster autoscaler provisioning new nodes while existing nodes sit at low utilization.

### OOMKill Cascades

Pods with `requests.memory` set too low land on nodes without sufficient real headroom. Under load, memory consumption exceeds the limit and the container is OOMKilled. If the Deployment has low replica count, this can knock out a significant fraction of available endpoints. With rolling restarts and readiness probes, traffic continues routing to the limited remaining healthy replicas, which then face elevated load and themselves become more likely to OOMKill.

**Signal:** `OOMKilled` in Pod status, restarting containers in `kubectl get pods`, rapid restart count growth visible in `kube_pod_container_status_restarts_total`.

### BestEffort Eviction Under Pressure

Pods deployed without any resource declarations receive `BestEffort` QoS class. Under node memory pressure, these are the first evicted by the kubelet, regardless of how important the workload is. Teams that skip resource declarations to simplify deployment manifests may find their workloads evicted during periods of cluster activity that seem unrelated.

**Signal:** Pods unexpectedly evicted with reason `Evicted`, particularly on nodes running memory-intensive workloads.

---

## Practical Implementation Path

### Step 1: Audit Current Request Configuration

Start with visibility before changing anything. Identify Pods with no resource declarations (BestEffort), and Pods with significant gaps between requests and actual usage.

```bash
# Find BestEffort pods (no requests set)
kubectl get pods -A -o json | jq -r '
  .items[] |
  select(.spec.containers[].resources.requests == null) |
  "\(.metadata.namespace)/\(.metadata.name)"
'

# Compare requests vs actual usage (requires metrics-server)
kubectl top pods -A --sort-by=cpu
```

Prometheus queries for the gap:

```promql
# CPU request vs actual usage ratio
sum(rate(container_cpu_usage_seconds_total[5m])) by (pod, namespace)
  /
sum(kube_pod_container_resource_requests{resource="cpu"}) by (pod, namespace)
```

### Step 2: Set Namespace-Level Defaults with LimitRange

Before right-sizing individual workloads, establish a safety floor. A `LimitRange` ensures new Pods without explicit declarations get sensible defaults rather than BestEffort class.

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-resource-limits
spec:
  limits:
  - type: Container
    defaultRequest:
      cpu: 100m
      memory: 128Mi
    default:
      cpu: 500m
      memory: 512Mi
    max:
      cpu: "4"
      memory: 8Gi
```

### Step 3: Use VPA in Recommendation Mode

Vertical Pod Autoscaler in `Off` mode generates right-sizing recommendations based on historical usage without modifying running Pods. This provides data-driven starting points rather than guesswork.

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: my-app-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  updatePolicy:
    updateMode: "Off"
```

Check recommendations with `kubectl describe vpa my-app-vpa`.

### Step 4: Set Accurate Requests, Be Cautious with CPU Limits

For latency-sensitive services, consider omitting CPU limits entirely or setting them generously above the request. CPU throttling at the cgroup level causes latency spikes that don't show up as CPU pressure in node metrics. Memory limits should always be set to prevent runaway consumption and OOMKill cascades.

A practical starting profile for most web services:

```yaml
resources:
  requests:
    cpu: 200m      # Based on observed p95 usage
    memory: 256Mi  # Based on observed steady-state + headroom
  limits:
    memory: 512Mi  # Hard cap to prevent OOMKill cascades
    # CPU limit omitted intentionally for latency-sensitive services
```

### Step 5: Establish ResourceQuotas per Namespace

Cap total request and limit accumulation per namespace to prevent runaway over-requesting across teams.

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-quota
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 40Gi
    limits.cpu: "80"
    limits.memory: 160Gi
```

### Step 6: Build Continuous Feedback Loops

Right-sizing is not a one-time exercise. As workloads evolve, their resource profiles change. Build dashboards that surface the request-to-usage gap on a per-namespace and per-team basis. Review them as part of regular capacity planning cycles. Alert when a namespace's average utilization-to-request ratio drops below 20%, which indicates systematic over-requesting.

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

## Source Links

- [Resource requests and limits](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Configure default memory requests and limits for a namespace](https://kubernetes.io/docs/tasks/administer-cluster/manage-resources/memory-default-namespace/)
- [LimitRange](https://kubernetes.io/docs/concepts/policy/limit-range/)
- [ResourceQuota](https://kubernetes.io/docs/concepts/policy/resource-quotas/)
- [Vertical Pod Autoscaler](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler)
- [Pod Quality of Service classes](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/)
- [Node-pressure eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/)

---

## Related Pages

- Parent index: [Opinion & Overview](index.md)
- Related: [Pods and Deployments](../../workloads/pods-deployments.md)
- Related: [Scaling with HPA](../../workloads/scaling-hpa.md)
- Related: [Operations and Maintenance](../../operations/maintenance.md)
- Newsletter: [This Week in Kubernetes](../../index.md#weekly-newsletter)
