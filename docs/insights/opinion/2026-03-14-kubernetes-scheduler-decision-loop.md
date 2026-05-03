---
title: "The Kubernetes Scheduler: Decision Loop, Plugin Architecture, and Operational Reality"
date: 2026-03-14
category: insights
description: "The Kubernetes scheduler is not a router. It is a continuous reconciler that applies a filtering and ranking pipeline to a cluster snapshot. Understanding its plugin architecture, control flow, and failure modes is essential for diagnosing placement problems and designing workloads that behave predictably under load."
---

# The Kubernetes Scheduler: Decision Loop, Plugin Architecture, and Operational Reality

The scheduler is one of the most consequential components in a Kubernetes cluster and one of the most misunderstood. Engineers debug Pending Pods without knowing what the scheduler actually evaluated. They enable preemption without knowing how NominatedNodeName works. They tune resource requests without knowing that percentageOfNodesToScore might prevent the scheduler from ever seeing most of the cluster.

This guide covers how the scheduler actually works - the internal data structures, plugin execution order, step-by-step control flow, and the failure modes that surface in production.

---

## Situation

The Kubernetes scheduler is one of the most consequential components in a cluster and one of the least understood by the engineers who depend on it. Pods get stuck in Pending and teams reach for node selectors, affinities, and taints without understanding what the scheduler evaluated or why a node was rejected. Preemption gets enabled without understanding that `NominatedNodeName` is a hint, not a reservation. Resource requests get set without knowing that `percentageOfNodesToScore` might prevent the scheduler from ever evaluating most of the cluster.

The core mental model: the scheduler is a continuous reconciler, not a router. Its sole job is to watch for Pods with no `.spec.nodeName` and write one in. Everything else -- actually starting the Pod, pulling images, managing containers -- belongs to kubelet. The scheduler makes a prediction based on a point-in-time cache snapshot and hands off. Understanding this boundary is what separates teams that can diagnose placement problems from teams that blindly adjust parameters and hope.

The scheduler's world is built around two data structures: a scheduling queue (a heap of unscheduled Pods ordered by priority) and a cluster snapshot (a point-in-time cache of node state, Pod assignments, and resource usage). The scheduler never talks to nodes directly. It runs a Pod through a pipeline of plugins, picks a node, and writes a Binding to the API server. That is the complete output of a scheduling cycle.

---

## Mental Model

Think of the scheduler not as a router that forwards work, but as a continuous reconciler with a filtering and ranking pipeline. Its sole job is to watch for Pods with no `.spec.nodeName` and write one in. Everything else - actually starting the Pod, pulling images, managing containers - belongs to kubelet.

The scheduler's world is built around two data structures:

- **The scheduling queue** - a priority queue of unscheduled Pods
- **The cluster snapshot** - a point-in-time cache of node state, Pod assignments, and resource usage

The scheduler never talks to nodes directly. It reads cluster state from its local cache, runs a Pod through a pipeline of plugins, picks a node, and writes a Binding object to the API server. That is the entire output of a scheduling cycle.

---

## Plugin Architecture

Since 1.19, the scheduler is built entirely around the scheduling framework - a set of well-defined extension points that plugins hook into. The monolithic predicate/priority model is gone. Every scheduling decision is the product of plugins executing at specific phases.

The extension points, in order of execution:

```
PreEnqueue → QueueSort → PreFilter → Filter → PostFilter
→ PreScore → Score → NormalizeScore → Reserve → Permit
→ PreBind → Bind → PostBind
```

The extension points that matter most mechanically:

**Filter** eliminates nodes that cannot run the Pod. This is binary: a node either passes or it does not. Built-in filter plugins handle `NodeResourcesFit` (CPU/memory requests), `NodeAffinity`, `TaintToleration`, `PodTopologySpread`, `VolumeBinding`, and about a dozen others. All filter plugins run against every node in the feasible set. A single failure eliminates the node.

**Score** ranks surviving nodes. Each plugin emits a score from 0-100 for each node. Plugins include `LeastAllocated`, `ImageLocality`, `InterPodAffinity`, `NodeAffinity` (soft preferences), and others. Scores are weighted and summed. The node with the highest aggregate score wins.

**Reserve** tells the scheduler's in-memory cache to treat certain resources as already consumed, before the Binding is confirmed. This prevents a second Pod from double-booking the same resource during concurrent scheduling cycles.

**Permit** can hold a Pod in a waiting state before binding. This is how gang scheduling is implemented: wait until all Pods in a group are ready to bind simultaneously.

**Bind** writes the Binding object to the API server, setting `.spec.nodeName` on the Pod.

---

## Step-by-Step Control Flow

Here is what happens from the moment a Pod is created to the moment it lands on a node.

### 1. Pod enters the scheduling queue

A new Pod arrives in the API server with no `.spec.nodeName`. The scheduler's informer picks this up and enqueues it into `activeQ` - a heap ordered by priority and, within equal priority, by arrival time.

Pods can also sit in `backoffQ` (if a previous scheduling attempt failed, with exponential backoff) or `unschedulableQ` (if they have been rejected and are waiting for a cluster event that might change their eligibility).

### 2. Scheduling cycle begins

The scheduler's main goroutine pops a Pod from `activeQ` and begins a scheduling cycle. This is single-threaded per profile - cycles do not run concurrently for the same scheduler profile. This is deliberate: it prevents the cache from becoming inconsistent between concurrent decisions.

### 3. Snapshot

Before running any plugin, the scheduler takes a snapshot of the NodeInfo cache. This is a point-in-time view of each node's allocatable resources, already-assigned Pods, labels, taints, and conditions. The snapshot is what plugins actually read - not live API server state. This keeps scheduling fast and consistent within a cycle.

### 4. PreFilter

Plugins do upfront computation and validation. `PodTopologySpread` precomputes which topology domains exist. `NodeAffinity` compiles the affinity expressions. If a PreFilter plugin fails, the Pod is immediately marked unschedulable - no node evaluation happens.

### 5. Filter (Feasibility phase)

The scheduler evaluates every node in the snapshot against all Filter plugins. Kubernetes does not necessarily evaluate all nodes if the cluster is large. The `percentageOfNodesToScore` parameter (default: a dynamic percentage that scales down as cluster size grows, with a floor of 5%) limits how many nodes are evaluated once enough feasible nodes are found. This is a deliberate throughput tradeoff with real operational consequences.

For each node, all Filter plugins run. The first failure short-circuits that node - it is moved to a failed list with the reason recorded.

### 6. PostFilter (Preemption)

If no node passes the Filter phase, PostFilter runs. The default PostFilter plugin is the preemption plugin. It looks for nodes where evicting lower-priority Pods would make the node feasible for the current Pod. If it finds a candidate, it nominates that node (writes `pod.Status.NominatedNodeName`) and initiates eviction of the victim Pods. The current Pod is then re-queued - not immediately scheduled. It will win the next cycle once victims are gone.

This is the critical subtlety: preemption does not guarantee the nominating Pod gets the node. Another Pod could take it first. `NominatedNodeName` is a hint, not a reservation.

### 7. Score

Surviving nodes are scored by each Score plugin. Scores are normalized to 0-100 per plugin, then multiplied by the plugin's weight, then summed. The node with the highest total score is selected. If there is a tie, the scheduler breaks it by selecting a node uniformly at random from the tied set.

### 8. Reserve

The winning node's resources are updated in the in-memory cache - the Pod's requests are subtracted from the node's available capacity. This happens before the Binding is written, so that any concurrent scheduling cycle operating from a fresh snapshot sees the updated state.

### 9. Bind

The default Bind plugin creates a Binding object:

```yaml
apiVersion: v1
kind: Binding
metadata:
  name: my-pod
  namespace: default
target:
  apiVersion: v1
  kind: Node
  name: node-3
```

The API server processes this, sets `pod.spec.nodeName = "node-3"`, and persists it to etcd.

### 10. kubelet takes over

The kubelet on `node-3` is watching for Pods with `.spec.nodeName` matching its own node name. It picks up the Pod and begins its own lifecycle loop.

---

## Runtime Behavior in Real Clusters

### Throughput and latency

The scheduler processes one Pod per cycle. The scheduling framework parallelizes scoring and filtering across nodes using goroutines. The bottleneck is usually the Bind step - the API server write - which takes tens of milliseconds under normal load. For workloads with large burst arrival rates, this is where scheduling latency compounds.

### Cache drift

The scheduler's node cache is eventually consistent with the API server. Between a Pod being scheduled and kubelet reporting it running, there is a window where the scheduler's cache shows the node as having those resources consumed, but the node itself has not started the Pod yet. If the scheduler crashes and restarts during this window, it re-reads state from the API server, and any in-flight Bind that did not complete leaves a Pod with no node assigned - it re-enters the queue. Reserve state is not persisted; it is reconstructed from actual Pod assignments on restart.

### percentageOfNodesToScore

In a 1000-node cluster, the scheduler might only score 50 nodes by default. This means a Pod will never see most of the cluster. For workloads with specific placement requirements, this is usually fine because Filter eliminates ineligible nodes before the scoring cutoff is reached. But for workloads that rely on finding the globally best node, this is a real limitation. Increasing the parameter raises scheduling latency. Leaving it at defaults means placement quality is bounded by the sample.

### Multiple scheduler profiles

You can run the scheduler with multiple profiles, each with different plugin configurations and weights. Pods select a profile via `schedulerName`. This is how you run a latency-optimized profile for frontend Pods and a bin-packing profile for batch jobs on the same cluster without running two separate scheduler processes.

---

## Architecture and Tradeoffs

**The scheduler is optimistic, not transactional.** It makes a decision based on a snapshot, writes a Binding, and moves on. It does not confirm that kubelet successfully started the Pod before considering the slot filled. If kubelet fails to start the Pod (image pull failure, OOM at runtime, admission webhook rejection at the node level), the Pod re-enters Pending and the scheduler runs again. The slot the scheduler thought it filled is eventually released.

**Separation of scheduling from execution is architecturally clean but creates a modeling burden.** The scheduler must model kubelet's behavior - it has to know what resource requests mean, what taints do, what volume availability looks like - without actually running the code that enforces those constraints. Divergence between the scheduler's model and kubelet's enforcement is a real source of bugs, particularly for extended resources and NUMA topology.

**Gang scheduling is awkward in the base scheduler.** The Permit extension point allows waiting, but there is no native concept of scheduling all N Pods of a job atomically. Projects like Volcano and the Coscheduler plugin implement this on top of the framework. The base scheduler's single-Pod-at-a-time model means you can deadlock gang-scheduled workloads if the cluster is nearly full: each job gets partial placement, no job can proceed.

**The in-memory cache is the scheduler's source of truth during a cycle.** If you update a node's labels between cycles, the next cycle sees the new labels. If you update them during a cycle that already snapshotted the old state, that cycle uses stale data. This window is small in practice but matters when debugging surprising scheduling decisions.

---

## Failure Modes to Plan For

### Pod stuck in Pending

The most common case. Causes include:

- **No node passes the Filter phase.** Check `kubectl describe pod` - the scheduler emits Events explaining why each node was rejected. Common reasons: insufficient CPU/memory, taint not tolerated, affinity not matched, topology spread constraint unsatisfiable.
- **percentageOfNodesToScore cutoff reached before finding a feasible node.** Rare but possible if constraints are tight and the scheduler stops early.
- **The scheduler itself is down or crash-looping.** All new Pods stay Pending indefinitely. Detectable by watching `scheduler_pending_pods` and `scheduler_scheduling_duration_seconds` metrics.

### Preemption does not fire when expected

Preemption only triggers if the Pod has a PriorityClass higher than the victims. If the preempting Pod has default priority (0) and so do the victims, no preemption occurs. Preemption also will not evict Pods protected by PodDisruptionBudgets if eviction would violate the budget, or Pods in namespaces with `preemptionPolicy: Never`.

### Scheduling loops

A Pod can oscillate between Pending and Bound if kubelet repeatedly fails to start it and the scheduler keeps placing it somewhere. The backoff queue provides some damping, but a persistent image pull failure or a misconfigured node-level admission webhook can create this pattern. It surfaces as a Pod in Pending with many scheduling events and a rapidly increasing restart count.

### Cache inconsistency after API server disruption

The scheduler uses watch plus list to sync its cache. If the watch is disrupted and the re-list returns different state than the watch would have delivered, you can briefly have a stale cache. The scheduler handles this with re-list logic, but the window where it might double-schedule a resource is real. Kubernetes tolerates this at the kubelet and Pod level precisely because it expects the scheduler to make optimistic decisions that occasionally need correction.

### Custom scheduler extenders (the legacy model)

Some clusters still run webhook-based extenders from the pre-plugin era. These are called over HTTP during the scheduling cycle, adding latency and a network failure mode inside what should be an in-process operation. If the extender is slow or down, every scheduling cycle stalls or fails. The plugin model exists to eliminate this pattern. If you are maintaining extenders, migration to in-tree plugins is worth the investment.

---

## Synthesis

The scheduler's core insight is that scheduling is a stateless transformation applied to a snapshot. A Pod plus a cluster snapshot goes in; a node name comes out. The plugin framework makes this pipeline composable without making it concurrent - a deliberate tradeoff that sacrifices throughput for consistency.

What trips engineers up is the boundary between the scheduler's model and runtime reality. The scheduler does not run your containers. It makes a prediction - "this node can run this Pod" - based on a cache, then hands off. Everything that happens after the Binding write is kubelet's problem. The operational implication is that Pending to Running is not atomic, and many failure modes live in the gap between "scheduler said yes" and "kubelet confirmed it."

The deeper architectural point: the scheduler is replaceable and extensible precisely because Kubernetes separated placement decisions from execution enforcement. Every time you extend it - extenders, profiles, custom plugins - you are taking on the responsibility of keeping your model consistent with what kubelet actually enforces.

---

## Mastery Check

If a high-priority Pod is preempting victims on a node, and another Pod with equal priority is created at the same moment - what happens? Does the second Pod compete for the same node, or does `NominatedNodeName` protect the first Pod's claim?

The second Pod does compete. `NominatedNodeName` is written to the Pod's status as a hint to the scheduler, not a hard reservation. It tells the scheduler to consider that node during the next scheduling cycle, but it does not prevent another Pod from being placed there first. If a different scheduling cycle runs between the nomination and the re-queue, that cycle can bind any Pod to the node regardless of the nomination.

Operationally, this means burst workloads with preemption enabled can exhibit non-deterministic placement ordering. Multiple high-priority Pods may nominate the same set of victim nodes simultaneously, trigger parallel victim eviction, and then race to claim nodes as they become available. In a nearly-full cluster with many equal-priority bursting jobs, the outcome depends on which scheduling cycles happen to run first. The system is eventually consistent - all Pods will eventually be placed or blocked - but the order is not guaranteed and cannot be made deterministic without external coordination such as a gang-scheduling plugin or a batch scheduling layer like Volcano.

---

## Practical Implementation Path

Set resource requests accurately before tuning anything else. The scheduler allocates based on requests, not limits. Pods with no requests set are treated as having zero resource requirements and can be placed anywhere, leading to noisy neighbor problems that manifest as kubelet evictions rather than scheduler rejections. Audit requests across all workloads with `kubectl top pods` and the `kube-scheduler` metrics before making any other scheduling changes.

Understand `percentageOfNodesToScore` for your cluster size before enabling complex affinity or topology spread constraints. In a 500+ node cluster, the scheduler may evaluate fewer than 50 nodes per cycle by default. If your constraints are tight, the scheduler may exhaust its feasible node sample without finding a valid candidate even when one exists. Raise the parameter selectively for workloads that require global placement visibility, and accept the increased scheduling latency that comes with it.

Use PriorityClasses deliberately. Preemption is on by default for any Pod with a priority higher than its victims. In clusters with mixed workloads, failing to assign PriorityClasses means all Pods have equal priority and preemption never fires -- or worse, all Pods have default priority and any new Pod can preempt any existing Pod. Define at least three tiers: system-critical (for DaemonSets and node-level infrastructure), workload (for production services), and batch (for jobs that can be safely preempted).

For custom controllers and admission webhooks that affect scheduling, test behavior with `--dry-run=client` and against a staging cluster before production rollout. Admission webhooks that reject Pods at the node level create a class of failure where the scheduler says yes but kubelet says no -- the Pod re-enters Pending with an `FailedScheduling` or `FailedMount` event that looks like a scheduling failure but is actually a node-level enforcement failure. Distinguishing these requires reading both scheduler events and kubelet events on the Pod.

Migrate from webhook-based scheduler extenders to the scheduling framework plugin model. Extenders add an HTTP round-trip inside each scheduling cycle and create a single point of failure for all placement decisions. The plugin model is in-process, testable, and the direction the upstream project has moved for all new scheduling extension.

---

## Source Links

- [Kubernetes scheduler framework documentation](https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/)
- [Kubernetes scheduling policies and profiles](https://kubernetes.io/docs/reference/scheduling/config/)
- [Pod Priority and Preemption](https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/)
- [Resource management for Pods and containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [scheduler source: scheduling cycle and binding cycle](https://github.com/kubernetes/kubernetes/tree/master/pkg/scheduler)

---

## Related Pages

- Parent index: [Opinion & Overview](index.md)
- Related: [Why Kubernetes Scheduling Uses Requests, Not Limits](2026-03-10-kubernetes-scheduling-requests-not-limits.md)
- Related: [True HA in Kubernetes: Why Multi-Zone Alone Isn't Enough](2026-03-10-true-ha-resiliency-beyond-multi-zone.md)
- Evergreen reference: [Kubernetes overview](../../getting-started/overview.md)
