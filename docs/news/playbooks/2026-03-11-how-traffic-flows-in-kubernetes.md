---
title: "How Traffic Actually Flows in Kubernetes: Services, kube-proxy, and Cloud Load Balancers"
date: 2026-03-11
category: playbooks
description: "A Kubernetes Service is not a load balancer - it is a routing abstraction. Understanding the three layers that actually move traffic (node dataplane, cloud load balancer, application connections) explains most real-world networking behavior in EKS and AKS."
---

# How Traffic Actually Flows in Kubernetes: Services, kube-proxy, and Cloud Load Balancers

A common misconception is that Kubernetes Services perform load balancing. They don't. A Service is a stable virtual endpoint - a name, an IP, and a list of backing Pods. The actual packet forwarding happens across three distinct layers: the node-level dataplane (kube-proxy or eBPF), the cloud provider load balancer for external traffic, and the connection behavior of the clients and applications involved.

Platform teams that miss this architecture routinely misdiagnose traffic imbalance, misattribute scaling lag, and design Ingress stacks that create unexpected bottlenecks. This playbook traces each layer in detail.

---

## Situation

### The Load Balancer Misconception

When a developer creates a Kubernetes Service and traffic starts flowing to their Pods, it looks like load balancing is happening. Requests arrive, Pods share the load. The Service must be doing it.

Trace where the packets actually go and the picture changes immediately. The Service IP never hosts a process. No software listens on it. It is a routing target that exists only inside kernel forwarding tables. The entity doing the actual packet selection is kube-proxy (or its eBPF replacement), running a daemon on every node, watching for Service and EndpointSlice changes and rewriting kernel rules accordingly.

This distinction matters in practice when things break. When one Pod is receiving 70% of traffic and two others split the remaining 30%, that is not a Service bug. It is a consequence of connection-level load balancing and persistent client connections. When new Pods come up after a scale event and traffic doesn't rebalance immediately, that is not a cluster health issue. It is the expected behavior of a system that doesn't forcibly terminate existing connections.

Teams that understand the layered model stop chasing phantom Service failures and start diagnosing the right layer.

---

## Architecture and Tradeoffs

### Layer 1: The Service Abstraction

A Kubernetes Service provides three things: a stable virtual IP (ClusterIP), a stable DNS name, and a dynamically maintained list of healthy backend Pods. It does not forward traffic.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: orders
spec:
  selector:
    app: orders
  ports:
  - port: 80
    targetPort: 8080
```

When this Service exists, Kubernetes assigns it a ClusterIP (for example `10.0.15.23`) and continuously reconciles which Pods match the `app: orders` selector. Healthy, ready Pods are included. Unready or terminating Pods are removed.

The Service object is a control plane concept. What makes traffic actually flow is what the node dataplane does with it.

### Endpoints and EndpointSlices

Behind the scenes, Kubernetes maintains the backend Pod list in EndpointSlice objects. Each slice holds a batch of Pod IP and port entries for a given Service. Networking components watch EndpointSlices (not Services directly) to get the current backend list.

```
Service: orders
EndpointSlice:
  - 10.2.1.14:8080
  - 10.2.4.11:8080
  - 10.2.7.9:8080
```

When a Pod becomes ready, its IP is added to the slice. When a Pod enters termination or fails its readiness probe, it is removed. Network components pick up these changes and update their forwarding rules.

### Layer 2: kube-proxy and the Node Dataplane

kube-proxy runs as a DaemonSet on every node. It watches Services and EndpointSlices and installs packet forwarding rules into the node's network stack. When a packet arrives destined for a Service ClusterIP, the node's kernel intercepts it and rewrites the destination to one of the backing Pod IPs before forwarding.

**iptables mode** is the most common historically. kube-proxy writes NAT rules that probabilistically select a backend. The selection is stateless and per-connection: once a connection opens to a particular Pod, all packets in that connection go to the same Pod. New connections are distributed across backends, but the distribution is approximate and depends on how many connections each backend currently holds.

**IPVS mode** replaces iptables NAT chains with a kernel-level virtual server table. It supports multiple scheduling algorithms (round-robin, least-connection, weighted) and handles rule updates more efficiently at scale. Large clusters with thousands of Services benefit noticeably. Most managed clusters still default to iptables, but IPVS is available.

**eBPF dataplanes** (Cilium being the primary example) replace kube-proxy entirely. eBPF programs attached to network interfaces intercept packets before they traverse iptables chains. Selection is done in the eBPF program, packets are sent directly to the chosen Pod, and the overhead of walking long iptables chains disappears. Observability improves because eBPF programs can emit per-connection and per-flow telemetry directly. This is the direction the ecosystem is moving, but iptables remains the default on most managed clusters today.

### Why Traffic Distribution Is Uneven

Because load balancing operates at the connection level, not the request level. A client that opens a persistent HTTP/1.1 connection sends all its requests over that connection. They all land on the same Pod. If one client is significantly busier than others, the Pod handling its connection appears overloaded even though the connection count across Pods is balanced.

```
Client opens persistent connection → Pod A
  Request 1 → Pod A
  Request 2 → Pod A
  Request 3 → Pod A

Pod A → 70% of traffic
Pod B → 20%
Pod C → 10%
```

This is expected behavior, not a bug. HTTP/2 multiplexing makes it worse because a single connection can carry hundreds of concurrent streams. Addressing it requires either application-level load balancing (a service mesh or a client that opens multiple connections) or switching to a short-lived connection model.

### Layer 3: Cloud Load Balancers for External Traffic

For traffic entering the cluster from outside, a cloud load balancer sits in front of the node layer.

```
Internet
  ↓
Cloud Load Balancer (AWS NLB / Azure Standard LB)
  ↓
Node IP
  ↓
NodePort
  ↓
kube-proxy rules
  ↓
Pod
```

When a Service of `type: LoadBalancer` is created, the cloud controller manager requests a load balancer from the cloud provider and configures it to forward traffic to each node's NodePort for that Service. The cloud LB routes to nodes, not to Pods. It cannot track individual Pods because Pods are created and deleted continuously across nodes and have cluster-internal IPs that are not reachable from outside the VPC without additional configuration.

The NodePort is the node-level entry point. Every node in the cluster listens on the same NodePort, regardless of whether it currently hosts a Pod for that Service. A request arriving at a node that has no local backing Pod is forwarded internally to a node that does.

### Ingress Controllers: A Fourth Layer in Practice

Most production platforms insert an Ingress controller between the cloud load balancer and the Service.

```
Internet
  ↓
Cloud Load Balancer
  ↓
Ingress Controller (NGINX / AWS LBC / Azure App Gateway / Istio)
  ↓
ClusterIP Service
  ↓
kube-proxy / eBPF
  ↓
Pod
```

The Ingress controller handles TLS termination, host and path-based routing, header manipulation, and rate limiting. It is itself a workload running in the cluster, behind a Service of its own. The cloud LB routes to the Ingress controller nodes; the controller routes internally to backend Services.

This is where the full load balancing picture comes together: the cloud LB distributes across nodes, the Ingress controller distributes across Ingress controller replicas, and kube-proxy distributes connections to backend Pods.

---

## Failure Modes to Plan For

### Persistent Connection Imbalance

A new Pod starts. EndpointSlice is updated. kube-proxy adds the new Pod to its backend pool. But existing connections are not interrupted. The new Pod receives only new connections. If client connection turnover is slow (long-lived gRPC streams, keep-alive HTTP connections), the new Pod may sit underloaded for minutes while existing Pods remain overloaded.

**Signal:** New Pod in a Deployment showing much lower request rate than siblings immediately after start. Connection count visible in `ss -s` or netstat on the node showing imbalance across Pods.

**Mitigation:** Set `MaxConnectionAge` on gRPC servers to force periodic connection cycling. Use shorter keep-alive timeouts on HTTP servers. A service mesh with per-request load balancing (Istio, Linkerd) addresses this at the protocol level.

### Endpoint Propagation Lag

When a Pod becomes ready, there is a brief window before kube-proxy on all nodes has updated its rules. During this window, traffic can be sent to an endpoint that is not yet configured locally, causing connection errors. The same applies in reverse during termination: kube-proxy may remove the endpoint before the Pod has drained its in-flight connections.

**Signal:** Transient connection resets or 502s during rollouts even when health probes are correctly configured.

**Mitigation:** Add a `preStop` sleep hook to delay the SIGTERM signal until endpoint removal has propagated. A value of 5-15 seconds covers most kube-proxy propagation windows.

```yaml
lifecycle:
  preStop:
    exec:
      command: ["sleep", "10"]
```

### NodePort Traffic Cross-Node Hops

A cloud LB routes a request to Node A. Node A has no local Pod for that Service. kube-proxy on Node A forwards the packet to a Pod on Node B. This cross-node hop adds latency and consumes bandwidth. At scale, a significant fraction of requests take this path.

**Signal:** Higher-than-expected east-west traffic between nodes. Latency that scales with the number of nodes rather than the number of Pods.

**Mitigation:** Enable `externalTrafficPolicy: Local` on the LoadBalancer Service. This restricts each node to only forwarding traffic to local Pods. Nodes without a local Pod are excluded from the cloud LB target group. This eliminates the cross-node hop but requires the cloud LB to be aware of which nodes are valid targets, which the cloud controller manager handles automatically on EKS and AKS.

```yaml
spec:
  type: LoadBalancer
  externalTrafficPolicy: Local
```

### Source IP Loss with externalTrafficPolicy: Cluster

The default `externalTrafficPolicy: Cluster` performs SNAT when forwarding to a Pod on another node. The Pod sees the node IP as the source, not the client IP. This breaks access logs, IP-based rate limiting, and geo-routing logic.

**Signal:** All Pod access logs showing node IPs rather than client IPs.

**Mitigation:** Use `externalTrafficPolicy: Local` (see above), which preserves the source IP because no SNAT is needed. Alternatively, configure the Ingress controller to pass the original IP via `X-Forwarded-For` and have the application trust that header.

### Ingress Controller as Single Point of Distribution

An Ingress controller with two replicas and no topology spread constraints may both land on the same node or zone. The cloud LB then routes all traffic through a single node, eliminating the distribution benefit and creating a single point of failure.

**Signal:** Ingress controller Pods co-located on the same node. All Ingress traffic passing through a single node visible in node-level bandwidth metrics.

**Mitigation:** Apply topology spread constraints and a PodDisruptionBudget to the Ingress controller Deployment, the same as any other traffic-critical workload.

---

## Practical Implementation Path

### Step 1: Understand Your Current Traffic Path

Before optimizing anything, trace the actual path traffic takes from the cloud LB to a Pod.

```bash
# Find the NodePort for a LoadBalancer service
kubectl get svc my-service -o jsonpath='{.spec.ports[*].nodePort}'

# Check kube-proxy mode
kubectl get cm kube-proxy -n kube-system -o yaml | grep mode

# List EndpointSlices for a service
kubectl get endpointslices -l kubernetes.io/service-name=my-service

# Check whether externalTrafficPolicy is set
kubectl get svc my-service -o jsonpath='{.spec.externalTrafficPolicy}'
```

### Step 2: Set externalTrafficPolicy: Local for External Services

For any Service of `type: LoadBalancer` that handles external traffic, evaluate whether `externalTrafficPolicy: Local` is appropriate. It is the right choice for most HTTP/HTTPS workloads because it preserves source IP and eliminates cross-node hops.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: orders
spec:
  type: LoadBalancer
  externalTrafficPolicy: Local
  selector:
    app: orders
  ports:
  - port: 80
    targetPort: 8080
```

Ensure the Deployment has sufficient replicas spread across nodes so no node is without a local Pod backend. Use topology spread constraints to enforce the spread.

### Step 3: Add preStop Hooks to Production Pods

All production Pods that receive traffic should have a `preStop` sleep to cover endpoint propagation lag during rolling updates and scale-in events.

```yaml
spec:
  containers:
  - name: app
    lifecycle:
      preStop:
        exec:
          command: ["sleep", "10"]
  terminationGracePeriodSeconds: 60
```

### Step 4: Spread Your Ingress Controller

Treat the Ingress controller as a traffic-critical workload with the same spread and disruption requirements as your most important services.

```yaml
# On the Ingress controller Deployment
spec:
  replicas: 3
  template:
    spec:
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: ingress-nginx
      - maxSkew: 1
        topologyKey: kubernetes.io/hostname
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: ingress-nginx
```

### Step 5: Address Long-Lived Connection Imbalance

For gRPC services or any service where clients maintain long-lived connections, configure the server to cycle connections periodically. For gRPC in Go:

```go
grpc.NewServer(
  grpc.KeepaliveParams(keepalive.ServerParameters{
    MaxConnectionAge: 30 * time.Second,
    MaxConnectionAgeGrace: 5 * time.Second,
  }),
)
```

For services where a service mesh is in use, delegate connection-level load balancing to the mesh. Istio and Linkerd both handle per-request distribution at the sidecar level, bypassing the connection-affinity problem entirely.

### Step 6: Evaluate eBPF if You're Running CNI Plugins That Support It

If your cluster runs Cilium or another eBPF-capable CNI, investigate replacing kube-proxy with the eBPF dataplane. On EKS, this is supported with the Cilium CNI. On AKS, the Cilium dataplane is available as a network policy option. The primary gains are lower latency, faster rule propagation at scale, and better per-flow observability via Hubble.

This is not urgent for most clusters but becomes relevant above a few hundred Services where iptables rule chain length starts affecting performance.

---

## Source Links

- [Services networking](https://kubernetes.io/docs/concepts/services-networking/service/)
- [EndpointSlices](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/)
- [Virtual IPs and Service proxies](https://kubernetes.io/docs/reference/networking/virtual-ips/)
- [Using source IP](https://kubernetes.io/docs/tutorials/services/source-ip/)
- [Ingress controllers](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/)
- [Cilium eBPF dataplane](https://docs.cilium.io/en/stable/network/ebpf/)
- [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller/)
- [Azure Application Gateway Ingress Controller](https://learn.microsoft.com/en-us/azure/application-gateway/ingress-controller-overview)

---

## Related Pages

- Parent index: [Playbooks](index.md)
- Related: [Networking Overview](../../networking/networking.md)
- Related: [Services and Networking](../../networking/services-networking.md)
- Related: [Ingress](../../networking/ingress.md)
- Related: [Gateway API](../../networking/gateway-api.md)
- Related: [Network Policies](../../networking/netpol.md)
