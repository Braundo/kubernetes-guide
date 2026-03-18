---
title: "Horizontal Pod Autoscaler: From Metrics to Scheduling Pressure"
date: 2026-03-17
category: insights
description: "HPA is a proportional feedback controller, not a provisioning system. Understanding its formula, metrics pipeline lag, and stabilization layer is what separates operators who tune it reliably from those who chase oscillations indefinitely."
---

# Horizontal Pod Autoscaler: From Metrics to Scheduling Pressure

Most teams treat HPA as a set-and-forget configuration. Point it at CPU, set a target percentage, and let it do its thing. That framing breaks down the moment you need to understand why a scale-up happened 45 seconds after a traffic spike, why replicas are bouncing between values, or why the desired count is correct but nothing is actually changing. HPA is a proportional feedback controller layered on top of Kubernetes' existing reconciliation machinery. Its behavior is entirely predictable once you understand the formula, the metrics pipeline it depends on, and the stabilization mechanisms that keep it from overreacting.

---

## Situation

HPA is not a provisioning system and it is not a prediction engine. It observes a metric signal, compares that signal to a configured target, and adjusts a replica count to drive the signal back toward the target. That is the complete mechanism. Metric sources, scaling policies, and stabilization windows are all levers for managing the quality and stability of that control loop, not fundamentally different features.

The most important mental model shift: HPA does not create or delete Pods. It writes a replica count to the scale subresource of a target object, typically a Deployment or StatefulSet. The target controller then reconciles toward that count. HPA is a second-order controller sitting on top of the existing reconciliation layer, which means it is entirely decoupled from scheduling, node capacity, quota, and PodDisruptionBudgets. It can write a replica count the cluster cannot satisfy. It has no awareness of whether that is the case. That is by design, and understanding this boundary explains a significant class of "HPA isn't working" reports.

The reason this matters operationally: when Pods end up Pending after an HPA scale-up, the cause is not HPA misbehaving. It is the gap between what HPA can request and what the cluster can currently schedule. Those are separate systems with separate remediation paths.

---

## Architecture and Tradeoffs

### The control loop mechanics

HPA runs in kube-controller-manager as the horizontal-pod-autoscaler controller. Its sync period defaults to 15 seconds, configurable via `--horizontal-pod-autoscaler-sync-period`. Each cycle follows the same sequence: fetch the current replica count from the target's scale subresource, fetch current metric values from the configured pipeline, compute a desired replica count, apply policy and stabilization constraints, and write the result back if it differs from the current count.

The scaling formula for resource metrics is:

```
desiredReplicas = ceil(currentReplicas x (currentMetricValue / desiredMetricValue))
```

This is a ratio-based proportional controller. Four replicas at 80% CPU against a 50% target produces `ceil(4 x (80/50)) = ceil(6.4) = 7`. Two behaviors emerge directly from this formula.

First, a tolerance band: HPA ignores ratio deviations within 10% of 1.0 (configurable via `--horizontal-pod-autoscaler-tolerance`). A ratio of 0.95 produces no action. A ratio of 0.85 triggers a scale-down. This prevents constant micro-adjustments when metrics hover near the target.

Second, conservative handling of unready Pods: during scale-up, unready Pods are excluded from the metric average, which biases the calculation toward adding more replicas. During scale-down, unready Pods are treated as consuming at the target level, suppressing scale-down until the cluster stabilizes. This is intentional. Scaling down during a rollout before new Pods are healthy would cause cascading failures.

If metrics cannot be fetched for some Pods, HPA defaults to the conservative side: scale-up assumes missing Pods are at full utilization, scale-down pauses entirely.

### The metrics pipeline and its latency

Most HPA confusion originates not in the controller itself but in the data pipeline feeding it. There are three separate metric sources, each with a distinct data path.

**Resource metrics (CPU, memory)** flow through metrics-server, which implements the `metrics.k8s.io/v1beta1` API by aggregating resource usage from the kubelet's `/metrics/resource` endpoint on each node. The full latency chain looks like this:

```
container cgroup stats
  -> kubelet scrapes every ~15s
  -> metrics-server aggregates (15s default scrape interval)
  -> metrics.k8s.io API becomes available
  -> HPA sync cycle fetches (15s default)
```

End to end, this means up to 45 seconds of lag between actual CPU usage changing and HPA acting on it. This is not a bug. It is the steady-state pipeline latency under default configuration.

**Custom metrics** flow through the `custom.metrics.k8s.io/v1beta2` API, implemented by an adapter. Prometheus Adapter is the most common choice. The adapter translates HPA queries into PromQL, fetches from Prometheus, and returns the result. A common failure mode here: if the adapter's PromQL query does not correctly scope by namespace or label selector, HPA receives aggregate values across unrelated workloads and behaves unpredictably, often scaling to zero or to max.

**External metrics** follow the same adapter pattern via `external.metrics.k8s.io`, but target signals with no relationship to Kubernetes objects: queue depth in SQS, messages waiting in Kafka, external API rate. HPA accesses these with `type: External` in the metric spec.

### Scaling policies and stabilization windows

Stabilization windows and scaling policies are the mechanisms that make HPA production-safe. They are also frequently misconfigured or left at defaults without understanding what those defaults mean.

The stabilization window is a lookback buffer. When HPA computes a new desired replica count, it does not act on that value directly. It takes the most conservative value across all computed results within the window period: the maximum for scale-down decisions, the minimum for scale-up. The default scale-down stabilization window is 300 seconds. Even if every sync for the past four minutes computes a lower replica count, HPA waits for five full minutes of consistent signal before acting. The default scale-up stabilization window is 0 seconds, meaning HPA acts on the first scale-up signal without waiting for confirmation.

```yaml
behavior:
  scaleDown:
    stabilizationWindowSeconds: 300
  scaleUp:
    stabilizationWindowSeconds: 0
```

The asymmetry reflects a deliberate risk tradeoff. CPU spikes are immediately dangerous to service health. Over-provisioning is expensive but not dangerous. The defaults encode that priority.

Scaling policies constrain how much the replica count can change in a given period:

```yaml
behavior:
  scaleUp:
    policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 4
        periodSeconds: 15
    selectPolicy: Max
  scaleDown:
    policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```

`selectPolicy: Max` means HPA uses whichever policy allows the larger change. The combination of `Percent: 100` and `Pods: 4` allows exponential growth during a traffic surge: either doubling, or adding 4 pods, whichever is larger, every 15 seconds. For scale-down, `selectPolicy: Min` is the default, meaning the most conservative policy wins. This is intentional; scale-down should be cautious, scale-up should be fast.

### A concrete scale-up walkthrough

Setup: Deployment with 3 replicas, HPA targeting 50% CPU, usage spikes to 90%.

| Time | Event |
|---|---|
| T+0s | CPU spikes to 90% across all Pods |
| T+15s | kubelet scrapes cgroup stats |
| T+30s | metrics-server aggregates, serves via metrics.k8s.io |
| T+45s | HPA sync: fetches 3 replicas, 90% CPU, computes `ceil(3 x 1.8) = 6`, writes replicas=6 |
| T+45s | Deployment controller creates 3 new Pods |
| T+45s+ | Scheduler assigns new Pods to nodes |
| T+60s+ | Pods start, pass readiness probes |
| T+90s | HPA sync: CPU now ~45% across 6 Pods, within tolerance, no action |

Note that HPA does not wait for the Pods it triggered to become ready before the next sync cycle. The sync 15 seconds later will observe the 3 new Pods as unready and handle them conservatively: they are excluded from the metric average on scale-up calculations, which may push the computed desired count even higher before the cluster catches up.

### HPA and Cluster Autoscaler interaction

When HPA scales up faster than existing node capacity can accommodate, new Pods land in Pending state. Cluster Autoscaler sees those Pending Pods and provisions new nodes. The timing gap between these two systems is critical to understand.

HPA acts within 15 to 45 seconds. CA node provisioning takes 2 to 5 minutes depending on the cloud provider. CA scale-down has a 10-minute default cooldown. During the CA provisioning window, Pods are Pending, existing Pods are handling elevated load, and HPA may continue requesting higher replica counts. For latency-sensitive services, the right mitigation is conservative minimum replicas: pre-provision enough headroom that HPA scale-up can be satisfied from existing node capacity without waiting for CA to intervene.

---

## Failure Modes to Plan For

### HPA stuck, will not scale up

Start with `kubectl describe hpa <name>` and look at the `Conditions` field. `AbleToScale: False` or `ScalingLimited: True` will include an exact reason. If conditions look healthy, verify that metrics-server is running: `kubectl get --raw /apis/metrics.k8s.io/v1beta1/pods`. If that request fails, HPA has no data and will not act. Also check whether the current replica count is already at `maxReplicas`. HPA respects that ceiling silently.

### HPA oscillating between replica counts

This is a stabilization window problem. CPU is genuinely variable, and if the metric hovers near the target threshold, HPA will flip between scale-up and scale-down signals on successive sync cycles. The remedies are: add a scale-up stabilization window to require consistency before acting, increase the target utilization to create more margin between the threshold and normal operating range, or widen the tolerance band.

### Correct desired replicas, actual replicas unchanged

HPA is writing to the scale subresource, but something downstream is blocking reconciliation. Check for a paused Deployment rollout, a PodDisruptionBudget blocking disruption, Pods in Pending state due to node capacity, or an RBAC issue preventing the HPA controller from patching the scale subresource on a custom resource type.

### Custom metrics HPA does not scale

Check whether the API is registered at all: `kubectl get --raw /apis/custom.metrics.k8s.io/v1beta2/`. Then inspect `kubectl describe hpa` for `unable to get metric` in the conditions. If the API exists but the metric is not found, the problem is in the Prometheus Adapter rules: verify that the PromQL query correctly scopes to the right namespace, label set, and resource name that HPA is requesting.

### Startup overshooting

When new Pods take time to become ready, the next HPA sync sees high CPU plus a batch of unready Pods and may compute a still-higher desired replica count. With a 0-second scale-up stabilization window, this fires immediately, potentially triggering another batch of Pod creation before the first batch is healthy. The fix is a short scale-up stabilization window (30 to 60 seconds), readiness probes tuned to pass as quickly as correct health allows, and startup probes to separate initialization latency from readiness.

---

## Practical Implementation Path

### Never target the same metric with both HPA and VPA

VPA adjusts resource requests and limits on existing Pods, requiring restart. HPA adjusts replica count. They operate on different dimensions and can be composed, but not on the same metric. If VPA reduces CPU requests, utilization ratios rise, HPA scales out, and VPA reduces requests further. The controllers fight indefinitely. The safe pattern: use VPA in `Off` or `Initial` mode for right-sizing resource requests, use HPA for throughput scaling, and never configure both to react to CPU utilization simultaneously.

### Set minimum replicas conservatively for latency-sensitive services

`minReplicas: 1` is correct for batch workloads and appropriate for services where cold-start latency is acceptable. For services with latency SLOs, the minimum replica count should reflect the load you expect to absorb before HPA's first scale-up fires, accounting for the full 45-second pipeline lag. A service that can sustain expected load on its minimum replica count buys time for HPA to react without SLO impact.

### Use KEDA when you need scale-to-zero

Native HPA cannot scale below 1 replica. For event-driven workloads or batch processors with true idle periods, KEDA wraps HPA via a `ScaledObject` CRD and a custom metrics adapter. When queue depth is zero, KEDA patches replicas to 0 directly. When a message arrives, it scales to `minReplicaCount` and hands scaling logic back to HPA. If your workload genuinely idles, KEDA is the correct tool for the job rather than working around HPA's floor.

### Treat the default stabilization windows as a starting point, not a final answer

The 300-second scale-down window and 0-second scale-up window are reasonable defaults for CPU-driven workloads. Services with slow startup times need a non-zero scale-up stabilization window to avoid overshoot. Services with bursty but short traffic spikes may need a shorter scale-down window to avoid holding excess capacity too long after a spike clears. Tune based on your observed P99 startup time and your tolerance for over-provisioning versus under-provisioning.

### Design for non-uniform load distribution awareness

HPA averages metrics across all Pods in the target. A workload where one Pod carries 90% of load while the rest sit idle will report a healthy average and receive no HPA intervention. This is a structural incompatibility between HPA and workloads with stateful or sticky routing. HPA is well-suited for stateless services where load distributes roughly uniformly across replicas. If your distribution is skewed by design, per-Pod metrics dashboards and manual scaling policies for outlier scenarios are necessary supplements.

---

## Mastery Check

A Deployment is running 10 replicas. The HPA targets 60% CPU. metrics-server reports current CPU at 72%. The scale-up stabilization window is 120 seconds. Four consecutive HPA syncs spanning 60 seconds have all computed a desired replica count of 12. Will HPA scale up right now?

No. The stabilization window is 120 seconds, and only 60 seconds of consistent scale-up signals have accumulated. HPA takes the minimum desired value across all results within the window for scale-up, and the window has not elapsed. HPA requires 120 seconds of uninterrupted scale-up signal before acting.

The fifth sync, at approximately T+75s, would need to compute `desiredReplicas >= 12` again. But that alone is still not sufficient. The window requires 120 seconds of consistent signal. The scale-up will not fire until the HPA sync at approximately T+120s, assuming all intervening syncs produce the same or higher desired count. If any sync within the window produces a lower desired count, that lower value becomes the current stabilized result and the 120-second window effectively resets around the new signal.

---

## Source Links

- [Kubernetes HPA documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [HPA algorithm details](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/#algorithm-details)
- [metrics-server](https://github.com/kubernetes-sigs/metrics-server)
- [Prometheus Adapter](https://github.com/kubernetes-sigs/prometheus-adapter)
- [KEDA](https://keda.sh/)
- [Cluster Autoscaler](https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler)

---

## Related Pages

- Parent index: [Opinion & Overview](index.md)
- Related: [The Kubernetes Scheduler: Decision Loop, Plugin Architecture, and Operational Reality](2026-03-14-kubernetes-scheduler-decision-loop.md)
- Related: [How etcd Consistency Guarantees Shape Kubernetes Control Plane Behavior](2026-03-16-etcd-consistency-kubernetes-control-plane.md)
- Related: [Why Kubernetes Scheduling Uses Requests, Not Limits](2026-03-10-kubernetes-scheduling-requests-not-limits.md)
- Evergreen reference: [Kubernetes learning paths](../../learn/index.md)
