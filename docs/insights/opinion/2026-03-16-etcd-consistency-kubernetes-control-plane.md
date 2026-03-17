---
title: "How etcd Consistency Guarantees Shape Kubernetes Control Plane Behavior"
date: 2026-03-16
category: insights
description: "etcd is not just a database. It is the linearizable coordination primitive that every Kubernetes controller is built on top of. Understanding its consistency model, watch machinery, and failure modes is essential for diagnosing subtle control plane behavior and knowing what 'stale state' actually means in production."
---

# How etcd Consistency Guarantees Shape Kubernetes Control Plane Behavior

Most engineers describe etcd as "the database where Kubernetes stores things." That framing is technically accurate and operationally dangerous, because it hides the causal relationship that governs everything in the control plane: every controller in Kubernetes is ultimately reacting to etcd state, filtered through the API server's watch machinery. If you do not understand etcd's consistency model, you cannot correctly reason about why controllers behave the way they do, what "stale state" actually means, or why certain failure modes are quiet rather than loud.

---

## Situation

etcd is a linearizable key-value store built on Raft. Linearizable means every read reflects the most recently completed write -- as if all operations happen on a single global timeline, with no possibility of reading from a lagging replica. Kubernetes deliberately exploits this guarantee: the API server's watch stream is not just a notification system, it is an ordered log of every mutation to cluster state, and controllers are log consumers.

This puts etcd's consistency properties at the root of the entire control loop model. Every controller behavior you find surprising -- acting on outdated state, missing a transition, retrying an update -- traces back to this architecture. Engineers who treat etcd as generic storage miss this and end up debugging controller behavior without the conceptual tools to reason about it precisely.

Understanding the consistency model is also directly operational. When etcd write latency climbs, API server latency climbs with it. When etcd loses quorum, the entire control plane stops making progress. When watch ring buffers overflow, controllers relist and spike API server memory. None of these dynamics are visible if your mental model of etcd is "a key-value store that Kubernetes uses."

The right framing: etcd is a coordination primitive. The API server's watch infrastructure and the informer caching layer in client-go are the mechanisms that allow thousands of controllers and clients to consume etcd state efficiently without overwhelming the cluster. All three layers together -- etcd, watch cache, informer -- are what you need to understand to diagnose anything non-trivial in the control plane.

---

## Architecture and Tradeoffs

### The write path and Raft quorum

etcd uses Raft for consensus. A write commits only when a quorum of members -- floor(n/2) + 1 -- acknowledge the log entry. Until quorum is reached, the write does not exist from Kubernetes' perspective. The API server returns no success, and no watch event fires.

The practical sizing implications:

| Members | Tolerated failures |
|---|---|
| 3 | 1 |
| 5 | 2 |
| 4 | 1 |

The 4-member row is not a typo. An even-numbered cluster tolerates no more failures than the odd number below it, while adding a member that must stay in sync. Even-numbered etcd clusters are strictly worse than odd-numbered ones at every size. This is a common misconfiguration.

### Revision as the global sequence number

Every write to etcd increments a cluster-wide monotonic integer called the revision. This is the mechanism behind `resourceVersion` on every Kubernetes object. It is not a timestamp, not a per-object counter, and not scoped to a specific resource type. It is a global sequence number across the entire etcd keyspace.

When you inspect a Pod and see `resourceVersion: "483921"`, that number means: this object's current state was written as part of etcd revision 483921. It says nothing about wall-clock time and nothing about how many times that object specifically has changed.

Why this matters operationally: `resourceVersion` drives optimistic concurrency. When a controller updates an object, it sends the current `resourceVersion` back in the request. If another writer has modified the object since the controller read it, the API server rejects the write with a `409 Conflict`. The controller must re-read and retry. This is not an edge case. It is the standard conflict resolution mechanism for every controller in the system.

### The three-layer propagation chain

The API server opens a long-lived watch on etcd and streams watch events -- `PUT`, `DELETE` -- in revision order. It fans these out to an in-memory reflector cache (`watchCache`) per resource type. This cache stores the current state of all objects of that type and maintains a ring buffer of recent watch events. It serves `LIST` and `WATCH` requests from memory, not from etcd directly.

Controllers do not watch the API server directly either. They use informers -- the shared caching layer in client-go. An informer issues an initial `LIST` to populate its local store, opens a `WATCH` from the `resourceVersion` of that list, applies incoming watch events to its local store, and enqueues changed objects into a work queue for the controller's reconcile loop. The controller reads from the informer's local store -- not the API server, not etcd.

The full propagation chain is:

```
etcd -> API server watchCache -> informer local store -> controller logic
```

Every arrow is asynchronous. Every arrow introduces propagation delay. This is not a bug -- it is the design that allows Kubernetes to scale without overwhelming etcd with direct reads. But it means controllers always operate on state that lags behind reality by some amount. Under normal conditions that lag is milliseconds to low single-digit seconds. Under load or network stress, it grows.

### Why controllers are level-triggered, not edge-triggered

Watch events can be lost. Clients restart. Networks blip. Ring buffers overflow. A controller that depended on receiving every state transition would diverge permanently the moment it missed one. Level-triggered reconciliation -- compare desired state to actual state, act on the difference, repeat -- is the only model that provides correctness guarantees with an unreliable event stream. The informer's periodic resync re-enqueues every object at a configurable interval, even when nothing has changed, enforcing this property mechanically.

### Linearizable vs serializable reads and API server latency

etcd exposes two read modes. Linearizable reads go through Raft quorum -- they are guaranteed to reflect the most recent write, but they incur the latency of a quorum roundtrip. Serializable reads are served from the local member's state and may be slightly behind the leader. Kubernetes uses linearizable reads for anything where correctness matters: leader election, `resourceVersion` conflict detection. The API server uses linearizable by default for most operations, which is why etcd read latency directly translates to API server latency. When API server p99 latency climbs, etcd read latency is the first place to look.

### Why horizontal scaling of controllers is hard

Because controllers use optimistic concurrency and single-threaded work queues, two active instances of the same controller over the same objects will continuously conflict with each other, generating `409`s and discarded work. This is why Kubernetes' own controllers use leader election rather than active-active scaling -- only one replica holds the lease and drives reconciliation; the others wait. Sharding is possible but requires careful partitioning logic.

---

## Failure Modes to Plan For

### etcd leader election latency

When the etcd leader fails, Raft must elect a new one. During that election -- typically 1-3 seconds in a healthy cluster, potentially 10-30 seconds with poor tuning or network stress -- etcd refuses all writes. The API server's watch stream pauses. Controllers stop receiving events. No new Pods can be scheduled, no Secrets updated, no status written.

From the outside this looks like: `kubectl` commands hang, controllers appear frozen, existing workloads continue running (kubelets are node-local and do not require etcd to execute Pod lifecycles), but nothing in cluster state changes. The absence of activity is the signal. Monitor `etcd_server_leader_changes_seen_total` and set alerts on values above 1-2 per hour. Tune `--heartbeat-interval` and `--election-timeout` conservatively; the defaults (100ms/1000ms) are appropriate for most deployments and should not be tightened without profiling actual network RTT between members.

### Watch ring buffer overrun and forced relist

The API server's watch ring buffer is finite. Under high write volume -- dense clusters, frequent status updates from many kubelets, many concurrent controllers -- old events can age out of the buffer before a slow consumer reads them. When this happens, the API server sends the informer a `410 Gone` error on its watch. The informer must relist from scratch: a full `LIST` against the watch cache, re-establishing a new watch from the latest `resourceVersion` and reprocessing every object.

In a large cluster, a single relist of all Pods can transfer megabytes and spike API server memory. If multiple informers relist simultaneously -- say, after a brief API server disruption -- the aggregate load can be significant. Tune `--watch-cache-sizes` based on cluster size and write volume. The level-triggered reconcile model is what prevents dropped events from causing permanent divergence, but relists are expensive and should be treated as a signal of an undersized cache, not an expected steady-state.

### Partial partition and stale member reads

True etcd split-brain should not occur with an odd-numbered cluster and a correct Raft implementation. What does occur in practice is a partial partition: an etcd member that is reachable by the API server but has fallen behind the leader. If the API server routes a linearizable read to this member, it will block until the member catches up or fail with a timeout. Under sustained partition this manifests as elevated API server latency and periodic request failures, even though etcd technically has quorum. Monitor `etcd_server_slow_read_indexes_total` and `etcd_network_peer_round_trip_time_seconds` across all members.

### The restart thundering herd

When the API server restarts, every informer in every controller reconnects and issues a `LIST` simultaneously. The watch cache mitigates it -- clients hit the cache, not etcd directly -- but the cache must warm from etcd on API server startup. The window between API server start and cache fully warm is when reads are slowest and most likely to fail. Self-managed clusters should use rolling API server restarts during upgrades and account for this warmup window in readiness probes and load balancer health checks.

### etcd latency propagation to controller throughput

If etcd write latency spikes from 2ms to 200ms, the API server queues incoming write requests and its request latency climbs. Controllers attempting to update objects see higher round-trip times. Optimistic concurrency retries -- which require a re-read and a re-write -- now each cost roughly 400ms instead of 4ms. Controllers that were completing reconcile loops quickly begin queuing work faster than they complete it. Watch stream event throughput decreases because fewer writes per second complete and enter the stream. The first metric signals are `etcd_request_duration_seconds{operation="put"}` on the etcd side and `apiserver_request_duration_seconds` on the API server side.

---

## Practical Implementation Path

### Right-size and stabilize etcd first

Run a 3-member etcd cluster for most deployments; move to 5 members when you need to tolerate 2 simultaneous failures. Never run even-numbered clusters. Place members in separate failure domains (zones or racks) but keep network RTT between members below 10ms -- etcd is sensitive to inter-member latency in a way that storage is not. Use dedicated local SSDs for the etcd data directory; shared network storage introduces the fsync latency variance that causes leader instability.

Benchmark your disk with `fio` before deploying etcd in production. A WAL fsync p99 above 10ms is a red flag. The metric to watch is `etcd_disk_wal_fsync_duration_seconds`. Most etcd stability problems in production trace back to disk I/O contention, not network issues.

### Tune the API server watch cache to your cluster size

The default watch cache size is tuned for moderate-sized clusters. For clusters with thousands of Pods, Nodes, or Endpoints, set explicit sizes via `--watch-cache-sizes`. A rough starting point: 1000 entries per resource type for every 500 nodes. Monitor `apiserver_watch_cache_events_dispatched_total` and `apiserver_watch_events_dropped_total`; elevated drop counts indicate the ring buffer is undersized and informers are being forced to relist.

### Treat 409 Conflict rates as a health signal

Every `409 Conflict` on a write means two controllers raced on the same object and one had to retry. A low baseline rate is normal and expected. A climbing rate on a specific resource type -- especially Pod status or Deployment status -- indicates either a controller bug, runaway reconciliation, or a design that has multiple writers competing unnecessarily. Use status subresources to isolate spec writes from status writes. Track `apiserver_request_total{code="409"}` broken down by resource and verb.

### Use leader election for all custom controllers

Any controller you write that manages Kubernetes objects should use leader election, not active-active replicas. The `controller-runtime` library provides this out of the box via `manager.Options.LeaderElection`. Running two active replicas of the same controller is not a reliability improvement; it is a conflict generator. The correct high-availability model is one active instance plus one or more standby instances that take over on lease expiry.

### Set informer resync periods deliberately

The informer resync period determines how frequently the controller re-enqueues all objects even without watch events. The default in client-go is 10-30 minutes depending on the resource. For controllers that manage resources with significant external state (e.g., cloud load balancers), shorter resync periods provide a safety net for missed events but increase reconcile throughput requirements. For controllers managing purely in-cluster state, longer resync periods reduce unnecessary work. Set the period explicitly rather than accepting defaults, and verify that your reconcile loop is idempotent before shortening it.

---

## Mastery Check

If etcd write latency spikes from 2ms to 200ms, what happens to controller behavior and why? What is the first signal you would look for in metrics, and which component emits it?

The write path through the API server now takes roughly 100x longer per mutation. The API server queues incoming write requests and its request latency climbs. Controllers attempting to update objects see higher round-trip times on their write calls. Optimistic concurrency retries -- which require a re-read and a re-write -- now each cost 400ms instead of 4ms. Controllers that were previously completing reconcile loops quickly begin queuing work faster than they complete it.

The first metric signal is `etcd_disk_wal_fsync_duration_seconds` or `etcd_request_duration_seconds{operation="put"}` on the etcd side, and `apiserver_request_duration_seconds` on the API server side. The etcd metric tells you the write latency at the source. The API server metric confirms the propagation. If both are elevated together, the bottleneck is etcd. If API server latency is elevated but etcd write latency is normal, the bottleneck is in the API server itself -- admission webhooks, authorization, or request queuing.

Watch stream propagation is not directly slowed by write latency, but event delivery throughput decreases because fewer writes per second complete and enter the watch stream. Under sustained high latency, controller work queues grow, reconcile loop throughput drops, and the time-to-convergence for any cluster state change increases proportionally.

---

## Source Links

- [etcd documentation: runtime configuration](https://etcd.io/docs/latest/op-guide/runtime-configuration/)
- [Kubernetes API machinery: watch cache internals](https://github.com/kubernetes/kubernetes/tree/master/staging/src/k8s.io/apiserver/pkg/storage/caches)
- [client-go informers and shared informer factory](https://github.com/kubernetes/client-go/tree/master/informers)
- [Raft consensus algorithm](https://raft.github.io/)
- [etcd performance benchmarking guide](https://etcd.io/docs/latest/op-guide/performance/)

---

## Related Pages

- Parent index: [Opinion & Overview](index.md)
- Related: [The Kubernetes Scheduler: Decision Loop, Plugin Architecture, and Operational Reality](2026-03-14-kubernetes-scheduler-decision-loop.md)
- Related: [How Traffic Actually Flows in Kubernetes](2026-03-11-how-traffic-flows-in-kubernetes.md)
- Evergreen reference: [Kubernetes learning paths](../../learn/index.md)
