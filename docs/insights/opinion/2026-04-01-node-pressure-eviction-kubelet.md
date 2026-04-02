---
title: "Node Pressure and Eviction: What Kubelet Actually Does When Things Get Tight"
date: 2026-04-01
category: insights
description: "Kubelet's eviction manager is the last line of defense before a node becomes unstable. Understanding how eviction thresholds work, why QoS class determines who dies first, and where the gap between scheduler requests and actual runtime usage causes cascading failures is essential for running Kubernetes reliably under real load."
---

# Node Pressure and Eviction: What Kubelet Actually Does When Things Get Tight

Most Kubernetes operators know eviction exists. Fewer understand what kubelet actually measures, in what order it acts, and why the wrong pods keep getting killed. The gap between what the scheduler knows and what the node is actually doing is where eviction failures live - and closing that gap is what separates clusters that stay healthy under load from clusters that spiral into cascading eviction storms.

This guide covers kubelet's eviction manager in full: the signals it watches, the threshold model, the QoS eviction ranking algorithm, how node pressure conditions and taints interact with the scheduler, and the failure modes that surface when real workload memory diverges from requested memory.

---

## Situation

The scheduler makes placement decisions based on resource requests. Kubelet enforces limits at the container level. The eviction manager operates at a third level entirely - it watches actual node-level signals and evicts Pods when the node itself is under pressure, regardless of what individual containers are doing.

This three-layer model is the source of most eviction confusion. A node can have plenty of allocatable memory from the scheduler's perspective - all Pods' requests sum to well below the node's capacity - while kubelet is simultaneously evicting Pods because the actual working set of those Pods has blown past their requests and the node is running out of real memory. The scheduler does not see this. The node pressure that triggers eviction is invisible to placement decisions until kubelet writes a condition to the API server and the condition taints the node.

The signals kubelet watches are filesystem usage, memory availability, inode counts, and PID counts. Of these, memory pressure is the most operationally common and the most misunderstood. The rest of this guide focuses primarily on memory eviction because that is where the subtlety lives, with disk and PID covered in the failure modes section.

---

## Mental Model

Think of kubelet's eviction manager as a threshold-triggered feedback loop that runs independently of the scheduler. Its inputs are node-level signals - not Pod-level metrics. Its output is Pod eviction ordered by a ranking function based on QoS class, actual usage relative to requests, and priority.

The central insight is that eviction is a node-level intervention, not a Pod-level one. Kubelet does not evict Pods because any individual Pod is misbehaving. It evicts Pods because the node as a whole is approaching a resource cliff, and it needs to free resources fast enough to prevent the node from becoming completely unavailable. The question of which Pod to evict is secondary to the question of when to evict at all - and the when is controlled entirely by eviction thresholds.

---

## How Kubelet Measures Memory

Before understanding eviction thresholds, you need to understand what `memory.available` actually means - because it is not what most engineers assume.

Kubelet derives `memory.available` from cgroup accounting: it is the node's total memory minus the working set of all processes on the node (including the OS, kubelet itself, system daemons, and all container workloads). It is not derived from Pod requests. It is not the scheduler's view of allocatable memory. It is a live measurement of actual physical memory usage.

The formula:
```
memory.available = node total memory - working set memory
```

`working set` is RSS (Resident Set Size - the portion of a process's memory held in RAM) plus cache that cannot be reclaimed without causing a page fault. This is stricter than RSS alone. A process that has read a lot of files might show low RSS but high working set because its file-backed pages are in use.

This is the first place operators get confused: the scheduler's `allocatable` memory and kubelet's `memory.available` are computed differently and can diverge significantly. Allocatable memory is:
```
allocatable = capacity - kube-reserved - system-reserved - eviction-hard threshold
```

The scheduler uses `allocatable` to decide whether a Pod fits. Kubelet uses `memory.available` - a live measurement - to decide whether to evict. A node can be fully scheduled and simultaneously memory-pressured because the running workloads are consuming far more memory than their requests declared.

---

## Eviction Thresholds: Soft and Hard

Kubelet supports two threshold types for each signal:

**Hard thresholds** trigger immediate eviction with no grace period. When `memory.available` crosses a hard threshold, kubelet begins evicting Pods immediately, regardless of their graceful termination period. The default hard threshold is:
```
memory.available < 100Mi
```
You should never hit this threshold in production. By the time kubelet is evicting against a hard threshold, the node is already in distress.

**Soft thresholds** trigger eviction only after the condition has persisted for a configurable grace period (`eviction-soft-grace-period`). Soft thresholds give operators a chance to signal that this is a genuine sustained pressure condition, not a transient spike. A reasonable production configuration:
```
--eviction-soft=memory.available<500Mi
--eviction-soft-grace-period=memory.available=1m30s
--eviction-max-pod-grace-period=120
```
This tells kubelet: if `memory.available` stays below 500Mi for 90 seconds, begin evicting with up to a 120-second SIGTERM grace period before SIGKILL.

The `eviction-max-pod-grace-period` caps how long kubelet will wait for Pods to terminate during soft eviction. Without this cap, a Pod with `terminationGracePeriodSeconds: 3600` could hold resources for an hour while the node continues degrading.

### Configuring thresholds

Thresholds can be set as absolute values or percentages:
```
--eviction-hard=memory.available<10%,nodefs.available<5%,nodefs.inodesFree<5%
--eviction-soft=memory.available<20%,nodefs.available<10%
```
Percentages are relative to the total capacity of the resource - total node memory for `memory.available`, filesystem capacity for `nodefs`. Absolute values are usually safer for memory (a percentage of a large node may still be a lot of memory) and percentages work well for disk.

---

## QoS Classes and Eviction Order

When kubelet decides which Pods to evict, it uses a ranking algorithm. The first axis of ranking is QoS class:

**BestEffort** - Pods with no resource requests and no limits. These are evicted first. They are making no resource promises and the node gave them whatever was left over. Under pressure, they go first.

**Burstable** - Pods with requests set, but where at least one container has limits higher than requests, or has no limits set. These are evicted second, ranked by how far their actual usage exceeds their requests.

**Guaranteed** - Pods where every container has requests exactly equal to limits. These are evicted last. They made precise resource promises and the node held capacity for them. Kubelet will exhaust BestEffort and Burstable candidates before touching Guaranteed Pods.

Within the same QoS class, kubelet ranks by **actual usage minus requests as a percentage of requests**. A Burstable Pod using 3x its memory request ranks higher for eviction than a Burstable Pod using 1.1x its request. This is the right behavior: the Pod that diverged most from its declared requirements is the least trustworthy resource consumer.

The full ranking logic, in priority order:
1. QoS class (BestEffort → Burstable → Guaranteed)
2. For Burstable: `(actual memory usage - memory request) / memory request` descending
3. Pod priority (lower priority evicted before higher priority within the same QoS tier)
4. For BestEffort: total actual usage descending

### The Guaranteed trap

Guaranteed QoS protects Pods from eviction, but it does not protect them from the OOM killer. If a Guaranteed Pod hits its memory limit, the kernel's OOM killer fires - kubelet does not get a chance to gracefully terminate the container. The container restarts with `OOMKilled` reason. This is categorically different from eviction: it is violent, immediate, and does not respect `terminationGracePeriodSeconds`.

If your Guaranteed Pods are OOMKilling regularly, you have either set limits too low or the workload's memory requirements are genuinely unbounded. Raising requests and limits together (both must change for Guaranteed) is the only solution; eviction tuning will not help here.

---

## Node Conditions and Taints

When a threshold is crossed, kubelet sets a node condition on the Node object:

| Signal | Condition |
|--------|-----------|
| `memory.available` | `MemoryPressure=True` |
| `nodefs.available` / `nodefs.inodesFree` | `DiskPressure=True` |
| `pid.available` | `PIDPressure=True` |

These conditions are visible immediately via `kubectl describe node`. They also cause kubelet to add a taint to the node:

- `node.kubernetes.io/memory-pressure:NoSchedule`
- `node.kubernetes.io/disk-pressure:NoSchedule`
- `node.kubernetes.io/pid-pressure:NoSchedule`

The `NoSchedule` taint prevents the scheduler from placing new Pods on the pressured node. This is the feedback loop between kubelet and the scheduler: kubelet signals pressure via conditions and taints, and the scheduler responds by routing new workloads elsewhere. New Pods are only scheduled to the node once the pressure condition clears and the taint is removed.

This mechanism has a timing gap. The scheduler sees allocatable resources and routes a Pod to the node before the pressure condition fires. Between the Pod being scheduled (binding written) and kubelet detecting pressure, the new Pod starts consuming memory that pushes the node further into distress. This is especially acute for Pods with high startup memory consumption that have modest steady-state requests.

---

## Architecture and Tradeoffs

**Eviction is a reactive safety mechanism, not a proactive resource manager.** By the time kubelet triggers eviction, the node is already under real pressure. Eviction does not prevent resource exhaustion - it responds to it. The Kubernetes answer to proactive resource management is Vertical Pod Autoscaler, LimitRange, and accurate request configuration. Eviction is the fallback when those controls have failed or were never set up.

**The gap between requests and actual usage is the root cause of most eviction cascades.** When workloads significantly exceed their requests, the scheduler over-places nodes (because it only sees requests), and the node runs hot. Under burst conditions, multiple Pods simultaneously spike above their requests, and the node goes from nominal to eviction pressure in minutes. The correct fix is accurate requests - not more aggressive eviction thresholds.

**Soft thresholds are the right lever for most clusters; hard thresholds are a last resort.** Hard eviction is violent: no grace period, Pods terminate immediately, in-flight requests are dropped. Soft eviction with a reasonable grace period gives Pods time to drain connections and complete work. Tuning soft thresholds to trigger earlier - at 25-30% of total memory remaining - gives the cluster time to route new traffic away from the node before hard pressure is reached.

**`eviction-minimum-reclaim` prevents threshold oscillation.** If a Pod is evicted and the node recovers just enough to clear the threshold, the condition clears - but if nothing else changes, the node may immediately drop below threshold again on the next measurement cycle. Setting `eviction-minimum-reclaim` tells kubelet to continue evicting until `memory.available` is at least N above the threshold, providing a buffer that prevents rapid on/off oscillation of the pressure condition.

**imagefs versus nodefs.** Kubernetes distinguishes between the filesystem used for container images and writable layers (`imagefs`) and the filesystem used for Pod volumes and emptyDir (`nodefs`). On many clusters these are the same filesystem, but if you run containerd with a separate image store, they can be different. Disk eviction thresholds apply separately to each. If you hit disk pressure but your node's main filesystem is fine, check imagefs usage - a large number of stale images from aggressive image pull policies can fill `imagefs` independently of workload data.

---

## Failure Modes to Plan For

### Eviction storm: one node's problem becomes everyone's problem

A node under memory pressure begins evicting Pods. Those Pods, if managed by Deployments or StatefulSets, are rescheduled to other nodes. Those nodes now receive additional load. If those nodes were also running near capacity, the evicted Pods push them over their own eviction thresholds. The result is a cascading eviction across multiple nodes.

The upstream fix is cluster-level headroom: maintain a meaningful cushion of unallocated capacity so that evicted Pods can land somewhere without causing additional pressure. Pod Disruption Budgets do not protect against eviction - they only apply to voluntary disruption. Pods evicted due to node pressure are evicted involuntarily.

### Wrong Pods getting evicted

If your most critical workloads are BestEffort or Burstable without accurate requests, they are eviction candidates ahead of less important workloads that happen to have Guaranteed QoS. Set appropriate requests and limits on all production workloads and use PriorityClasses to express business criticality. PriorityClass influences eviction ordering within the same QoS tier.

A PriorityClass does not override QoS class in the eviction ranking - a high-priority BestEffort Pod is still evicted before a low-priority Guaranteed Pod. Both dimensions matter: set QoS correctly (via accurate requests/limits) and set priority correctly (via PriorityClass).

### OOMKill instead of graceful eviction

If a container hits its memory limit, the kernel kills it before kubelet's eviction manager can act. This is the OOM killer, not eviction. The Pod restarts (based on `restartPolicy`) with `OOMKilled` as the termination reason. You see this as repeated container restarts with non-zero exit codes (typically 137).

This is distinct from eviction and requires a different fix: increase memory limits (or remove them if the workload is legitimately unbounded and you accept Burstable QoS). Eviction threshold tuning will not prevent OOMKill.

### Disk pressure from emptyDir abuse

emptyDir volumes write to `nodefs`. Workloads that use emptyDir as scratch space for large temporary files - builds, log buffering, ML checkpointing - can fill the node's disk rapidly. Disk pressure fires before memory pressure in most of these cases. The fix is to either bound emptyDir with `sizeLimit` (enforced by kubelet in Kubernetes 1.28+) or use PersistentVolumes backed by separate storage.

### PID pressure in environments with many containers

Each container process consumes a PID slot on the node. Nodes running hundreds of containers with workloads that fork frequently (shells, language runtimes, process supervisors) can exhaust `pid.available`. PID pressure taints the node and prevents new Pod scheduling but does not evict existing Pods - kubelet only evicts for memory and disk pressure, not PID pressure. A PID-exhausted node will refuse to start new containers without surfacing a clear eviction signal. Diagnose with `kubectl describe node` and look for `PIDPressure=True`.

### Eviction loop: Pod keeps getting evicted and rescheduled

A Pod is evicted from a pressured node. The scheduler places it on another node. That node is also pressured. The Pod is evicted again. This cycle continues until the Pod lands on a node with enough actual headroom.

If all nodes are pressured, the Pod will eventually be evicted everywhere and may enter a Pending state until pressure clears. This is the correct behavior - eviction is working - but the root cause is cluster-wide resource exhaustion. The operational response is capacity expansion, not eviction threshold adjustment.

---

## Practical Implementation Path

**Set `kube-reserved` and `system-reserved` before doing anything else.** These kubelet flags tell the scheduler to subtract a fixed amount of memory from each node's allocatable capacity - memory reserved for kubelet itself, container runtime (containerd), and OS daemons. Without these reservations, the scheduler treats the full node capacity as available for Pods, and kubelet, containerd, and the OS compete with Pods for memory. A reasonable starting point for a general-purpose node:

```
--kube-reserved=cpu=200m,memory=300Mi
--system-reserved=cpu=200m,memory=300Mi
--eviction-hard=memory.available<200Mi
```

The eviction-hard threshold should also be reflected in the allocatable calculation - Kubernetes subtracts it automatically when computing `allocatable`. If your `kube-reserved` and `system-reserved` are too small, the OS and kubelet will consume what you thought was Pod headroom, and eviction will fire much earlier than your thresholds suggest.

**Audit actual memory usage against requests for every production workload.** The command:
```bash
kubectl top pods -A --sort-by=memory
```
gives you current working set usage. Compare against `kubectl get pods -o json | jq` to extract requests. Any Pod consistently using more than 80% of its memory request is a candidate for request adjustment. Any Pod routinely exceeding its limit is OOMKilling or about to.

**Configure soft eviction thresholds that give you time to respond.** A reasonable production baseline for a node with 16Gi total memory:
```
--eviction-soft=memory.available<1500Mi,nodefs.available<15%
--eviction-soft-grace-period=memory.available=2m0s,nodefs.available=2m0s
--eviction-max-pod-grace-period=180
--eviction-minimum-reclaim=memory.available=200Mi,nodefs.available=500Mi
```
This gives kubelet a 2-minute window to confirm genuine sustained pressure before acting, allows Pods up to 3 minutes to gracefully terminate, and requires the node to recover at least 200Mi above the threshold before stopping eviction.

**Use Guaranteed QoS for stateful and latency-sensitive workloads.** Set `requests == limits` on every container in these Pods. This is the only way to prevent kubelet from evicting them ahead of less critical workloads. For stateless burst workloads, Burstable is acceptable - just set honest requests so the scheduler's view of the node matches reality.

**Monitor `kubelet_evictions_total`, node conditions, and `memory_working_set_bytes`.** These three metrics tell you whether eviction is actively firing, which nodes are in pressure states, and how actual usage compares to what the scheduler believes. Alert on `memory.available` dropping below your soft threshold sustained for more than one minute - that is your early warning before eviction fires. Alert on `kubelet_evictions_total` increasing - that is confirmation that kubelet is already acting.

**Run a node-local DNS cache (NodeLocal DNSCache) and vertical autoscaler on system components.** These reduce the base memory footprint of non-workload processes on each node, improving actual headroom. They do not replace accurate request configuration, but they reduce the noise floor that your eviction thresholds need to account for.

---

## Mastery Check

A production cluster is running two Deployments on the same node. Deployment A is Guaranteed with 2Gi memory request and limit. Deployment B is Burstable with 1Gi request and a 4Gi limit. Memory pressure fires. Deployment B has an actual working set of 1.1Gi - barely above its request. Deployment A's single Pod is using 2Gi exactly. Which is evicted?

Deployment B is evicted first. Guaranteed QoS protects Deployment A regardless of who is using more absolute memory. Within the Burstable tier, Deployment B is using 10% above its request - a positive overage. That makes it a candidate. Deployment A has no overage (using exactly its request), is Guaranteed, and is not evicted unless all BestEffort and Burstable candidates are exhausted first.

The follow-up: what if Deployment A's memory usage suddenly spikes to 2.5Gi? The container will be OOMKilled by the kernel - it hit its 2Gi limit. That is not eviction. The container restarts. Eviction does not rescue workloads that exceed their own limits; it only rescues the node from workloads that collectively exceed node-level capacity. The two mechanisms operate in parallel on different signals.

---

## Source Links

- [Kubernetes node pressure eviction documentation](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/)
- [Resource management for Pods and containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Pod Quality of Service classes](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/)
- [kubelet configuration: eviction thresholds](https://kubernetes.io/docs/reference/config-api/kubelet-config.v1beta1/)
- [Node-level resource management with kube-reserved and system-reserved](https://kubernetes.io/docs/tasks/administer-cluster/reserve-compute-resources/)

---

## Related Pages

- Parent index: [Opinion & Overview](index.md)
- Related: [The Kubernetes Scheduler: Decision Loop, Plugin Architecture, and Operational Reality](2026-03-14-kubernetes-scheduler-decision-loop.md)
- Related: [Why Kubernetes Scheduling Uses Requests, Not Limits](2026-03-10-kubernetes-scheduling-requests-not-limits.md)
- Evergreen reference: [Resource limits and requests](../../configuration/limits-requests.md)
- Newsletter: [This Week in Kubernetes](../../index.md#weekly-newsletter)
