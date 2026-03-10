---
title: "True HA in Kubernetes: Why Multi-Zone Alone Isn't Enough"
date: 2026-03-10
category: playbooks
description: "Multi-zone clusters remove the zone-failure risk but create a false sense of security. Real high availability requires coordinating PDBs, topology spread constraints, affinity rules, probes, graceful shutdown, and admission webhook resilience into a coherent strategy."
---

# True HA in Kubernetes: Why Multi-Zone Alone Isn't Enough

Multi-zone clusters are table stakes, but they're not HA. You can run nodes in three zones and still have an outage the first time a rolling deployment drains too many replicas at once, a readiness probe misconfiguration black-holes traffic, or the cluster autoscaler launches replacement nodes into a single zone. Real high availability is an emergent property of many interlocking decisions, most of them made at the workload level, not the infrastructure level.

This playbook covers the full picture: what each layer protects against, what it doesn't, where teams commonly leave gaps, and how to reason about the whole stack together.

---

## Situation

### The Multi-Zone Illusion

When you deploy a Kubernetes cluster across three availability zones, you've solved for one class of failure: an entire zone going dark. That's meaningful. It's also the *easiest* failure to guard against, because it happens infrequently and the mitigation (spread nodes across zones) is set once at the cluster level.

The failures that actually cause outages look like this:

- A Deployment rolls out a bad image and `maxUnavailable: 25%` takes down three of four replicas before health checks catch it
- Maintenance drains two nodes simultaneously; both happen to hold the same stateful pod
- Cluster autoscaler scales down and picks nodes in two different zones, collapsing zone coverage
- An admission webhook (cert-manager, Kyverno, OPA Gatekeeper) loses quorum during a planned upgrade and starts rejecting all pod mutations
- A pod panics on startup, triggers `CrashLoopBackOff`, and traffic keeps routing to it because the readiness probe never toggles it out
- All replicas of a service land on the same node due to scheduler bin-packing; that node's kubelet hangs

These are day-two, day-three, day-N failures. Zone spread doesn't touch any of them.

---

## Architecture and Tradeoffs

### Pod Disruption Budgets: The Availability Floor

A `PodDisruptionBudget` tells the Kubernetes eviction API the minimum number of pods that must remain available during voluntary disruptions, node drains, cluster upgrades, manual evictions. Without a PDB, `kubectl drain` will evict every pod on a node simultaneously, regardless of how many replicas you have.

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-server-pdb
  namespace: production
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: api-server
```

**`minAvailable` vs `maxUnavailable`:** Use `minAvailable` when you know the hard floor (e.g., "we need at least 2 serving replicas"). Use `maxUnavailable` when availability is a fraction of current scale. Avoid using `minAvailable: 100%`, it makes nodes undrain-able and will block cluster upgrades.

**Common mistakes:**

- **Leaving PDBs undefined.** Without one, there's no eviction guardrail. Node drains during upgrades will gut your service.
- **Setting `minAvailable` equal to your replica count.** Same result, nodes can never be drained. `minAvailable: N-1` is a safer pattern for most workloads.
- **PDBs on single-replica deployments.** A PDB with `minAvailable: 1` on a `replicas: 1` deployment makes that pod permanently unevictable. Scale to at least 2 replicas, or accept that maintenance windows require downtime.
- **Forgetting StatefulSets.** StatefulSets need PDBs too. Their ordered rollout semantics don't protect against concurrent voluntary evictions.

**What PDBs don't protect against:** Involuntary disruptions, OOM kills, node hardware failure, kernel panics, spot instance termination. For those, you need replica spread (covered below) and headroom in the cluster autoscaler.

---

### Topology Spread Constraints: Spreading With Intent

`topologySpreadConstraints` is the modern, expressive replacement for the old `podAntiAffinity` spread pattern. It lets you declare a maximum skew, how unbalanced pod distribution can be across topology domains, with fine-grained control over what happens when the constraint can't be satisfied.

```yaml
spec:
  topologySpreadConstraints:
    - maxSkew: 1
      topologyKey: topology.kubernetes.io/zone
      whenUnsatisfiable: DoNotSchedule
      labelSelector:
        matchLabels:
          app: api-server
    - maxSkew: 1
      topologyKey: kubernetes.io/hostname
      whenUnsatisfiable: DoNotSchedule
      labelSelector:
        matchLabels:
          app: api-server
```

This example enforces two things simultaneously: pods are spread across zones with at most 1 pod difference between zones, *and* no two pods land on the same node. Both constraints must be satisfiable for scheduling to proceed.

**`whenUnsatisfiable` modes:**

- `DoNotSchedule`, hard constraint. Pod stays Pending if it can't be placed satisfying the constraint. This is what you want for production workloads where placement correctness matters more than fast scheduling.
- `ScheduleAnyway`, soft constraint. The scheduler scores nodes by skew and prefers balanced placement, but doesn't block. Useful for batch workloads or during scale-out when capacity is temporarily constrained.

**`minDomains`:** Available since 1.24 (stable in 1.30), this field tells the scheduler how many topology domains *should* exist. Without it, if you have pods in only one zone (e.g., during initial scale-up), the scheduler may satisfy constraints trivially. Setting `minDomains: 3` for a three-zone cluster forces the spread calculation to account for all three zones.

```yaml
topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: DoNotSchedule
    minDomains: 3
    labelSelector:
      matchLabels:
        app: api-server
```

**Zone vs node spread:** Spread at the zone level protects against zone failure. Spread at the node level protects against a single node taking down multiple replicas simultaneously. Most production services benefit from both, zone spread as the outer constraint, node spread as the inner one.

**Interaction with Cluster Autoscaler:** `DoNotSchedule` constraints on zone topology will cause pending pods if one zone has no available capacity. The Cluster Autoscaler reads these constraints and will provision nodes in the needed zone, but only if that zone has a configured node group. Verify your node group configuration covers all zones your constraints require.

---

### Pod Anti-Affinity: The Older, Heavier Option

Before topology spread constraints existed, `podAntiAffinity` was the standard tool for spread. It still has a role, particularly when you need to co-locate or separate workloads based on business rules rather than pure numeric balance.

```yaml
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
            - key: app
              operator: In
              values:
                - api-server
        topologyKey: kubernetes.io/hostname
```

`requiredDuringSchedulingIgnoredDuringExecution` is a hard rule, no two pods with this label on the same node, ever. `preferredDuringSchedulingIgnoredDuringExecution` is a scored preference.

**The "IgnoredDuringExecution" caveat:** Both variants only apply at scheduling time. If a node's labels change after a pod is placed, the constraint isn't re-evaluated. Pods don't get evicted if the topology shifts. This is usually fine, but worth knowing.

**Prefer topology spread constraints for spread.** Anti-affinity is O(n²) in the scheduler for large clusters and doesn't express balance, it only expresses exclusion. Use it for co-location rules (e.g., "put this sidecar on the same node as the main app") or hard separation rules ("these two services must never share a node"). For spreading replicas, topology spread constraints are faster and more expressive.

---

### Readiness, Liveness, and Startup Probes: Traffic Gate and Process Guardian

Probes are the mechanism by which Kubernetes knows whether a pod should receive traffic (readiness) and whether it should be restarted (liveness). Getting them wrong is one of the most common sources of production incidents.

### Readiness Probes

A pod with a failing readiness probe is removed from Service endpoints. Traffic stops flowing to it. This is the primary mechanism for zero-downtime deployments: new pods only receive traffic after they pass readiness, and old pods drain before termination.

```yaml
readinessProbe:
  httpGet:
    path: /healthz/ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3
  successThreshold: 1
```

**Design your `/ready` endpoint carefully.** It should check that the process can actually serve requests, database connections established, caches warm, dependent upstream healthy. A readiness endpoint that always returns 200 is worse than useless; it lets sick pods receive traffic.

**Don't check external dependencies you don't control.** If your readiness probe checks a third-party API and that API is degraded, you'll mark all your pods unready and take yourself down. Check *your* ability to serve (e.g., your local DB connection pool), not the world.

### Liveness Probes

A pod with a failing liveness probe is restarted. This is a self-healing mechanism for processes that are alive but stuck, deadlocked, OOM-spinning, or corrupted in memory.

```yaml
livenessProbe:
  httpGet:
    path: /healthz/live
    port: 8080
  initialDelaySeconds: 15
  periodSeconds: 10
  failureThreshold: 3
```

**Liveness probes should be minimal.** They should only check "is this process able to respond at all", not dependent services, not data validity. An overzealous liveness probe that checks downstream systems will restart healthy pods during transient upstream failures, turning a dependency outage into a cascading restart storm across your fleet.

**Use `startupProbe` for slow-starting containers.** Rather than setting a high `initialDelaySeconds` on your liveness probe (which delays detection of post-startup hangs), use a `startupProbe` that succeeds once during initialization, then hands off to the normal liveness probe.

```yaml
startupProbe:
  httpGet:
    path: /healthz/live
    port: 8080
  failureThreshold: 30
  periodSeconds: 5
```

This gives the container up to 150 seconds to start (30 × 5s) before the liveness probe kicks in, without blinding the liveness check after startup.

---

### Graceful Shutdown: The Other Half of Zero-Downtime

Rolling deployments are only zero-downtime if terminating pods actually drain their in-flight requests before dying. The Kubernetes pod termination sequence is:

1. Pod is marked `Terminating`; removed from Service endpoints (async)
2. `preStop` hook executes (if defined)
3. SIGTERM is sent to PID 1
4. `terminationGracePeriodSeconds` countdown starts (default: 30s)
5. SIGKILL is sent if process hasn't exited

**The endpoint removal race:** Steps 1 and 2 are asynchronous. kube-proxy and cloud load balancers take time to propagate the endpoint removal. If your process exits immediately on SIGTERM, requests that were still being routed to it will get connection resets. The fix:

```yaml
lifecycle:
  preStop:
    exec:
      command: ["/bin/sh", "-c", "sleep 5"]
```

A 5-second `preStop` sleep gives the network stack time to stop routing new connections to the pod before your process starts shutting down. This is not a hack, it's the recommended pattern.

**`terminationGracePeriodSeconds`:** Set this higher than your longest expected in-flight request plus your drain time. For most HTTP services, 60 seconds is a reasonable floor. For services with long-lived connections (WebSocket, gRPC streaming), increase it to cover your actual drain window.

**Signal handling in your application:** If your container runs a shell script as PID 1, SIGTERM often doesn't propagate to child processes. Use `exec` to replace the shell with your process, or use a proper init system like `tini`. An application that can't catch SIGTERM will always be force-killed after the grace period, regardless of what Kubernetes is configured to wait.

---

### Deployment Rollout Strategy: Controlling the Blast Radius

`maxUnavailable` and `maxSurge` in a Deployment's rolling update strategy control how aggressively Kubernetes replaces pods during rollouts.

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 0
    maxSurge: 1
```

`maxUnavailable: 0, maxSurge: 1` is the safest configuration: never take down a running pod until a replacement is healthy and passing readiness. It requires capacity for one extra pod per rolling step, but it guarantees your running replica count never drops during the rollout. For services where any capacity drop is unacceptable, this is the right default.

`maxUnavailable: 25%` (the Kubernetes default) means a quarter of your pods can be unavailable simultaneously during a rollout. For a 4-replica deployment, that's one pod. For a 40-replica deployment, that's ten. Understand the math before accepting the default.

**`minReadySeconds`:** This underused field tells the Deployment controller to wait N seconds after a pod passes readiness before considering it "available" and moving to the next rollout step. Without it, the controller advances immediately after the first readiness check passes, before sustained health is confirmed.

```yaml
spec:
  minReadySeconds: 10
```

Even 10 seconds of sustained readiness before advancing provides meaningful protection against flapping pods that pass readiness on first check and fail seconds later.

---

### Resource Requests and Limits: Scheduler Correctness and Node Stability

Resource `requests` drive scheduling. The scheduler uses them to find nodes with sufficient available capacity. If your pods have no requests, the scheduler can pack unlimited pods onto a single node, guaranteeing resource contention and OOM kills under load.

```yaml
resources:
  requests:
    cpu: 250m
    memory: 256Mi
  limits:
    cpu: 1000m
    memory: 512Mi
```

**Set memory limits near requests for predictability.** When memory limits are far above requests, many pods may be scheduled to a node that collectively OOM it. Burstable QoS is fine, but unbounded memory limits on memory-hungry services create latent capacity bombs.

**CPU limits are more nuanced.** CPU throttling under cgroups v1 is aggressive, a pod can be CPU-throttled even when the node has idle CPU, simply because it hit its limit within a 100ms window. For latency-sensitive services, consider setting CPU requests correctly and leaving CPU limits unset (BestEffort for CPU, Guaranteed for memory). Monitor `container_cpu_cfs_throttled_seconds_total` to understand actual throttling impact.

**LimitRanges for namespace-level guardrails:** Add a `LimitRange` to each namespace to enforce default requests and limits for pods that don't set their own. This prevents unguarded deployments from degrading node stability.

---

### Priority Classes: Shedding the Right Load

When a cluster is under pressure and the scheduler can't place pods, it will preempt lower-priority pods to make room for higher-priority ones. Without explicit priority classes, all your workloads compete equally, including system-critical components.

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: production-critical
value: 1000000
globalDefault: false
description: "Production-critical services that must not be preempted"
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: production-standard
value: 100000
globalDefault: true
description: "Default priority for production workloads"
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: batch-background
value: 1000
globalDefault: false
description: "Background batch jobs, acceptable to preempt"
```

Assign `production-critical` to revenue-generating services, ingress controllers, and critical monitoring. Assign `batch-background` to CI jobs, data pipelines, and anything with a retry loop. Under node pressure, Kubernetes will shed the right workloads first.

**System priority classes:** The built-in `system-cluster-critical` and `system-node-critical` classes (values ~2B) protect components like CoreDNS and kube-proxy. Never assign these to application workloads.

---

### Admission Webhook Resilience: The Hidden Single Point of Failure

Admission webhooks, used by cert-manager, Kyverno, OPA Gatekeeper, Istio, and most GitOps security tooling, sit in the critical path of every pod creation and mutation. If the webhook service is unavailable when the API server calls it, the behavior depends on `failurePolicy`.

```yaml
webhooks:
  - name: validate.example.com
    failurePolicy: Fail  # API server rejects the request if webhook is unreachable
    # vs.
    failurePolicy: Ignore  # API server allows the request if webhook is unreachable
```

`failurePolicy: Fail` is the secure default, you don't want policy enforcement to silently stop working. But it means your webhook pods are now in the blast radius of every deployment and cluster operation.

**Rules for production webhook deployments:**

1. **Run 2+ replicas across different nodes.** A single-replica admission webhook is a cluster-wide single point of failure.
2. **Set a PDB.** Ensure at least one webhook replica survives node drains.
3. **Apply topology spread constraints.** Spread across zones so a zone failure doesn't kill all webhook capacity.
4. **Set appropriate `timeoutSeconds`.** The default is 10 seconds. If your webhook pod is slow to respond (cold start, GC pause), the API server will time out and apply the failure policy. Tune this, and make your webhook fast.
5. **Use `namespaceSelector` to exclude the webhook's own namespace.** A webhook that validates pods in its own namespace can deadlock during rollouts, it needs to create a pod to respond, but responding is blocked on the pod being created.

```yaml
webhooks:
  - name: validate.example.com
    namespaceSelector:
      matchExpressions:
        - key: kubernetes.io/metadata.name
          operator: NotIn
          values:
            - kyverno  # exclude the webhook's own namespace
```

---

### Cluster Autoscaler and Node Group Configuration

The Cluster Autoscaler (CA) provisions and removes nodes based on pending pod pressure and underutilization. Its zone awareness matters for HA.

**Per-zone node groups:** Configure separate node groups per zone rather than a single multi-zone group. This gives the autoscaler finer control when topology constraints require capacity in a specific zone. With a single cross-zone group, the autoscaler may not be able to target the right zone.

**`--balance-similar-node-groups`:** Enable this flag so the autoscaler tries to maintain even node counts across similarly configured groups. Without it, scale-out may pile nodes into one zone.

**Scale-down and PDBs:** The autoscaler respects PDBs during scale-down. Nodes that would violate a PDB by draining won't be removed. This is the intended interaction, PDBs are your availability contract, and the autoscaler honors it.

**`--skip-nodes-with-system-pods`:** This flag (enabled by default) prevents scale-down of nodes running `kube-system` pods. Combined with topology spread constraints that spread system pods across zones, this prevents the autoscaler from inadvertently draining an entire zone's system coverage.

**Headroom pods:** The CA only provisions nodes when pods are Pending. This means there's always a provisioning delay between a failure and replacement capacity coming online. For latency-sensitive workloads, consider running low-priority "pause" pods (using `priorityClassName: batch-background`) that hold capacity in reserve. Real workloads preempt them instantly; the CA sees the released headroom and doesn't scale down.

---

### Storage: The HA Constraint Nobody Wants to Talk About

Persistent volumes with `volumeBindingMode: WaitForFirstConsumer` are provisioned in the zone where the pod is scheduled. Once provisioned, the volume is zone-pinned. If the pod moves to a different zone (node failure, rescheduling), it can't mount the volume.

**This fundamentally constrains stateful workload HA.** StatefulSets with zone-pinned PVs cannot fail over to another zone without a storage-layer solution. Options:

- **Cloud-native replicated storage** (AWS EBS Multi-Attach for specific use cases, GCP Regional Persistent Disk): Replicates data across zones synchronously. Supports failover without data loss. Limited to specific volume types and use cases.
- **Distributed storage operators** (Rook/Ceph, Longhorn, OpenEBS): Run storage replicas as pods across zones. Volumes are replicated and zone-local access is handled by a consistent hashing or affinity layer. More complex to operate.
- **Application-level replication**: For databases, run a primary-replica setup (Postgres streaming replication, MySQL Group Replication, Redis Sentinel) where each replica is in a different zone. Accept zone failover at the database level. This is often the most operationally mature path.
- **Accept the constraint**: For truly stateless tiers, move state out of Kubernetes into managed cloud services (RDS, CloudSQL, ElastiCache) that handle their own HA. This is often the right answer.

The worst pattern is pretending zone-pinned PVs are highly available because they're in a multi-zone cluster. They're not.

---

### Horizontal Pod Autoscaler and Scaling Lag

The HPA scales replicas in response to metrics (CPU, memory, custom). It doesn't react instantly, by default it collects metrics every 15 seconds and scales up with a 3-minute stabilization window.

For workloads with spiky traffic, this lag can mean serving at insufficient capacity for 3-5 minutes after a traffic spike begins. Mitigations:

- **Scale earlier.** Set HPA `targetAverageUtilization` lower (e.g., 50% CPU rather than 80%). Accept running at lower utilization in exchange for more scaling headroom before saturation.
- **Set a reasonable minimum.** `minReplicas: 1` is almost never right for production services. Your minimum should cover baseline traffic with headroom, typically at least 2 for HA (spread across zones), often more.
- **KEDA for event-driven scaling.** If your traffic is driven by queue depth, request rate, or external events, KEDA can scale on those signals with lower latency than CPU-based HPA. It also supports scale-to-zero for batch workloads.
- **VPA for right-sizing requests.** If pod resource requests are wildly wrong, HPA CPU percentages are meaningless. Vertical Pod Autoscaler in recommendation mode can surface right-sized requests without automatically changing them.

---

## Failure Modes to Plan For

### Testing Your Resilience

Configuration that's never been exercised is configuration you don't trust. Regularly validate your HA posture:

**Drain a node.** Run `kubectl drain <node> --ignore-daemonsets` and watch what happens. Did any services lose all their endpoints? Did PDBs block the drain (correctly or incorrectly)? Did pods reschedule into balanced zones?

**Delete pods.** `kubectl delete pod -l app=api-server` during traffic. Watch your SLO dashboards. If deleting pods causes visible errors, your readiness probe configuration, PDB, or replica count is insufficient.

**Simulate a zone failure.** Apply a taint to all nodes in one zone with `NoSchedule` and `NoExecute`. Watch pods reschedule. Confirm your topology spread constraints hold up with reduced domain count.

**Chaos engineering tools.** Chaos Mesh, Litmus, and AWS Fault Injection Simulator allow structured fault injection, pod kills, network partitions, CPU stress, node termination. Build game day exercises around specific failure hypotheses, not random chaos.

**Admission webhook disruption.** Scale your webhook deployment to 0 and confirm your workloads can still be updated (or confirm they correctly block, depending on your intent).

---

## Practical Implementation Path

### The Full Checklist

For each production workload, verify:

| Concern | Mechanism | Minimum |
|---|---|---|
| Voluntary disruption | PodDisruptionBudget | minAvailable ≥ 1, replicas ≥ 2 |
| Zone spread | topologySpreadConstraints (zone) | maxSkew: 1, DoNotSchedule |
| Node spread | topologySpreadConstraints (host) | maxSkew: 1, DoNotSchedule |
| Traffic gate | readinessProbe | Meaningful /ready check |
| Process recovery | livenessProbe | Minimal /live check |
| Slow start | startupProbe | For slow-starting containers |
| Graceful drain | preStop sleep + terminationGracePeriodSeconds | ≥ 60s for HTTP services |
| Rollout safety | maxUnavailable: 0, maxSurge: 1, minReadySeconds: 10 | For traffic-sensitive services |
| Scheduler correctness | resource requests | Set on all containers |
| Load shedding | PriorityClass | 3-tier minimum: critical/standard/batch |
| Webhook HA | replicas, PDB, topology spread | Same as application workloads |
| Scaling headroom | HPA minReplicas | ≥ 2 for HA, sized for baseline |
| Storage failover | Volume strategy | Match workload's zone-failover requirements |

---

### Closing Thoughts

High availability in Kubernetes is not a feature you enable. It's a property you compose from many small decisions, each of which closes a specific failure mode. The infrastructure gives you the raw material, multi-zone nodes, elastic compute, managed control planes. The workload configuration is where availability is actually won or lost.

The teams that handle incidents well aren't the ones with the fanciest infrastructure. They're the ones who've thought through each failure mode, configured the appropriate guardrail, and tested it. PDBs, topology spread, proper probes, graceful shutdown, and admission webhook resilience aren't advanced topics, they're foundational. Build them in from the start, and your multi-zone cluster will actually behave like one.

---

## Source Links

- [Pod disruption budgets](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/)
- [Topology spread constraints](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/)
- [Pod lifecycle and termination behavior](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-termination)
- [Configure liveness, readiness, and startup probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Assign priority class to pods](https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/)

---

## Related Pages

- Parent index: [Playbooks](index.md)
- Related: [Pods and Deployments](../../workloads/pods-deployments.md)
- Related: [Operations and Maintenance](../../operations/maintenance.md)
- Related: [Security news](../security/index.md)
- Newsletter: [This Week in Kubernetes](../../index.md#weekly-newsletter)
