---
title: "Why Every Pod Gets a Real IP: The Kubernetes Flat Network Model, CNIs, and Ingress Controllers"
date: 2026-03-12
category: playbooks
description: "Kubernetes enforces a simple rule: every Pod can reach every other Pod directly, without NAT. This single constraint drives the entire networking architecture - from CNI plugin selection to ingress controller design. Understanding why this model exists and how it is implemented on EKS and AKS is essential for diagnosing and operating production clusters."
---

# Why Every Pod Gets a Real IP: The Kubernetes Flat Network Model, CNIs, and Ingress Controllers

Kubernetes enforces a deceptively simple networking rule: every Pod gets its own IP address, and every Pod can talk directly to every other Pod without network address translation. That one constraint - no NAT between Pods - determines which CNI plugin you can use, how your subnets must be sized, why security group rules apply the way they do, and where debugging starts when traffic breaks.

This playbook covers the model itself, why it exists, how CNI plugins implement it differently, and how ingress controllers and cloud load balancers sit on top of it to handle external traffic.

---

## Situation

### The Three Networking Guarantees

Kubernetes defines three rules that every conformant cluster must satisfy:

1. Every Pod has its own unique, routable IP address
2. Pods communicate directly using those IPs
3. No NAT occurs between Pods

The practical effect looks like this:

```
Pod A: 10.2.1.5
Pod B: 10.2.3.9

Pod A to Pod B:
  src: 10.2.1.5
  dst: 10.2.3.9
  (no translation)
```

The source IP is preserved end-to-end. Pod B sees the actual IP of Pod A, not a node IP or a gateway IP. This is the flat network model: from the Pod's perspective, the cluster is a single flat network where any Pod can reach any other Pod directly.

### Why This Is Different from Docker Networking

Before Kubernetes became the standard, most container networking used NAT-heavy approaches.

The classic Docker model:

```
Container (172.17.0.4)
  down
Docker bridge
  down
Host NAT (192.168.1.10)
  down
External network
```

Containers were not directly addressable. Traffic required port mappings:

```
192.168.1.10:8080 -> container:80
```

This created operational problems that compound at scale:

- **Service discovery complexity.** You discover the host IP and port, not the container itself. When containers move or restart, port assignments shift.
- **Port conflicts.** Multiple containers sharing a host compete for port space.
- **NAT debugging.** A connection failure anywhere in the chain is difficult to attribute to the correct layer.
- **Source IP loss.** Servers see host IPs in access logs, breaking IP-based access control, rate limiting, and audit trails.

Kubernetes solved these as first-class problems by eliminating intra-cluster NAT entirely.

### Why the No-NAT Guarantee Matters in Practice

The no-NAT model is load-bearing for several Kubernetes features:

**NetworkPolicy.** Policies match on Pod IPs. If NAT existed between Pods, the source IP visible to the destination Pod would be a gateway or node IP, not the originating Pod. Policies would be impossible to enforce accurately.

**Service mesh identity.** Platforms like Istio and Linkerd use Pod IPs as the basis for workload identity. Sidecars intercept traffic between known Pod IPs and apply mTLS, retries, and circuit breaking. NAT would break this identity model.

**Observability.** Metrics and traces that record source and destination IPs produce meaningful topology maps only if those IPs identify actual workloads, not NAT intermediaries.

**Debugging.** When a connection drops in a no-NAT environment, a packet capture at the source or destination shows the real endpoint. With NAT, the same capture shows a translated address, and you need to trace through NAT tables to reconstruct the actual path.

### Pods Are Treated Like Virtual Machines

The mental model Kubernetes uses is not containers. It is virtual machines.

Each Pod receives a unique IP, assigned at creation and stable for the Pod's lifetime, runs inside its own network namespace, and communicates with other Pods exactly as a VM would communicate with another VM on the same network.

Multiple containers inside a single Pod share that Pod's network namespace - they share the IP, can communicate over `localhost`, and see the same network interfaces. They behave like processes inside the same virtual machine.

```
Pod (IP: 10.2.1.5)
  app container       <- port 8080
  sidecar proxy       <- port 15001
  log collector       <- internal only
```

All three containers share `10.2.1.5`. The sidecar and the app communicate over `localhost`. From outside the Pod, traffic reaches `10.2.1.5:8080` and the Pod's internal networking handles the rest.

### Kubernetes Does Not Implement Networking

A critical architectural point: Kubernetes itself does not implement the flat network model. It specifies what the model must guarantee and delegates implementation entirely to a pluggable system called the Container Network Interface (CNI).

When a Pod is scheduled and the kubelet starts the Pod sandbox, it calls the configured CNI plugin. The CNI is responsible for creating a network interface inside the Pod's namespace, assigning an IP, configuring routing rules so the Pod is reachable, and ensuring the Pod can reach other Pods across nodes.

```
Pod scheduled
  down
kubelet starts Pod sandbox
  down
CNI plugin invoked
  down
veth pair created
  down
IP assigned
  down
routes configured on node
  down
Pod is reachable
```

Different CNI plugins satisfy this contract in fundamentally different ways. Choosing a CNI is one of the most consequential infrastructure decisions when building a cluster.

---

## Architecture and Tradeoffs

### CNI Architectural Models

There are three major architectures for satisfying the Kubernetes networking contract.

#### Overlay Networking

Overlay CNIs create a virtual network on top of the existing node network. Pod traffic is encapsulated in an outer packet before leaving the node and decapsulated on arrival at the destination node.

```
Pod A (10.2.1.5)
  down
veth interface on node
  down
VXLAN encapsulation
  inner: 10.2.1.5 to 10.2.3.9
  outer: node1 to node2
  down
Physical node network
  down
VXLAN decapsulation
  down
Pod B (10.2.3.9)
```

Common encapsulation methods are VXLAN and IP-in-IP. The Pod-level IPs are preserved in the inner packet, satisfying the no-NAT requirement, while the outer packet uses node IPs to traverse the underlying network.

**Examples:** Flannel, Calico (overlay mode), older Weave deployments.

**Advantages:**
- Works on any infrastructure, cloud or bare metal
- Does not require changes to the underlying network
- Pod IP range is independent of the node network

**Disadvantages:**
- Encapsulation adds CPU overhead and increases packet size
- Effective MTU is reduced by the encapsulation header
- Troubleshooting requires understanding both the outer and inner packet headers

Overlay networking was the dominant approach in early Kubernetes clusters and remains common where infrastructure flexibility is required.

#### Native Cloud Networking

Cloud-native CNIs eliminate the overlay entirely. Pods receive real IP addresses from the cloud provider's network - actual VPC or VNet IPs - and traffic flows directly through cloud routing infrastructure.

```
Pod A (10.0.1.23)
  down
ENI on the node
  down
VPC routing table
  down
Pod B (10.0.14.8)
```

No encapsulation. The cloud network knows about the Pod IPs and routes to them natively.

**Advantages:**
- No encapsulation overhead
- Pod IPs are visible inside the cloud VPC; security groups and flow logs apply directly
- Simpler packet path and simpler troubleshooting
- Integration with cloud-native security tooling

**Disadvantages:**
- IP exhaustion - subnets must accommodate both node IPs and all Pod IPs
- Pod density per node is constrained by ENI and IP-per-ENI limits
- Less portable across environments

#### eBPF Networking

The newest generation of CNIs uses eBPF programs running in the Linux kernel to handle packet routing without relying on iptables or encapsulation.

```
Service IP
  down
eBPF program (attached at network interface)
  down
direct socket redirect to Pod
```

eBPF programs intercept packets before they traverse the traditional network stack. They make routing decisions at wire speed, emit detailed telemetry per connection and per flow, and replace kube-proxy entirely.

**Primary example:** Cilium.

**Advantages:**
- Significantly lower latency than iptables-based approaches
- Scales without the rule chain length problems iptables encounters above a few thousand Services
- Rich built-in observability via Hubble (connection-level flow data, DNS tracking, HTTP visibility)
- Advanced policy capabilities including Layer 7 enforcement

**Disadvantages:**
- Requires a relatively modern Linux kernel
- eBPF debugging is specialized
- Cilium has a steeper learning curve than simpler CNIs

### EKS: AWS VPC CNI

EKS defaults to the AWS VPC CNI, a native routing CNI maintained by AWS.

The core mechanism is Elastic Network Interfaces (ENIs). Each node is provisioned with one primary ENI (holding the node IP) and can attach secondary ENIs, each capable of holding multiple secondary IP addresses. The CNI assigns these secondary IPs to Pods.

```
Node (10.0.1.10)
  Primary ENI:  10.0.1.10
  Secondary ENI:
    10.0.1.23  <- Pod
    10.0.1.24  <- Pod
    10.0.1.25  <- Pod
```

All Pod IPs are real VPC IPs. Traffic flows through normal VPC routing with no encapsulation.

**Security groups on Pods.** Because Pod IPs are real ENI IPs, AWS security groups can be applied directly to Pods - not just nodes. This enables pod-level network access control using native AWS tooling rather than Kubernetes NetworkPolicy alone.

**VPC flow logs capture Pod traffic.** Flow logs show actual Pod IPs, making network audit and forensics straightforward.

**IP exhaustion is a real constraint.** Every Pod consumes a VPC IP from the subnet. A `/24` subnet holds 251 usable IPs. If a node runs 30 Pods, it consumes 31 IPs. Large clusters need careful subnet planning or IPv6 adoption.

**Pod density is capped by instance type.** The number of ENIs a node can attach, and the number of IPs per ENI, are determined by the instance type. A `t3.medium` can host roughly 17 Pod IPs. A `m5.xlarge` can host 58. Cluster autoscaling decisions should account for this.

### AKS: Azure CNI and Azure CNI Overlay

AKS supports multiple CNI modes, reflecting the evolution of the IP exhaustion problem.

**Azure CNI** is the original native routing option. Pods receive real Azure VNet IP addresses.

```
Node: 10.240.0.4
Pod:  10.240.0.12
Pod:  10.240.0.13
```

Traffic routes directly across the VNet. The advantages and constraints mirror AWS VPC CNI - good performance and observability, but significant IP consumption. In Azure, this constraint is more visible because VNet address spaces are often shared with other resources and teams.

**Azure CNI Overlay** was introduced specifically to address IP exhaustion. Nodes remain in the VNet with real VNet IPs, but Pods receive overlay addresses from a separate range.

```
Node: 10.240.0.4 (VNet IP)
Pod:  192.168.1.5 (overlay IP)
Pod:  192.168.1.6 (overlay IP)
```

VNet IP consumption drops dramatically. Pod-to-Pod traffic that crosses nodes goes through an overlay encapsulation step, reintroducing some overhead. Pod IPs are not visible in VNet flow logs, and security groups cannot be applied to overlay Pod IPs directly. The right choice depends on VNet address space availability, observability requirements, and performance sensitivity.

**Cilium on AKS** is increasingly the recommended path for teams that need Layer 7 network policies or detailed flow telemetry. Azure CNI handles IP assignment while Cilium's eBPF programs handle policy enforcement and provide Hubble observability.

### Ingress Controllers: Handling External Traffic

CNI plugins solve Pod-to-Pod networking inside the cluster. They do not solve the problem of getting traffic into the cluster from outside. That is the role of ingress controllers and cloud load balancers.

Without an ingress controller, external traffic can only reach the cluster via NodePort or LoadBalancer Services. Neither handles HTTP routing, TLS termination, or host/path-based rules. Most production applications need all three.

The full external traffic path:

```
Internet
  down
Cloud Load Balancer (L4 or L7)
  down
Ingress Controller (running as Pods in the cluster)
  down
ClusterIP Service
  down
kube-proxy / eBPF dataplane
  down
Pod IP (via CNI)
```

Each layer has a distinct responsibility:

| Layer | Responsibility |
|---|---|
| Cloud Load Balancer | Distribute traffic across nodes; optional TLS offload |
| Ingress Controller | HTTP routing, host/path rules, TLS termination, header manipulation |
| Service | Stable virtual endpoint; dynamic backend Pod list |
| CNI dataplane | Actual packet routing to the destination Pod IP |

**NGINX Ingress** is the historically dominant option - mature, widely documented, and flexible. Configuration complexity grows with the number of routes, and NGINX reload cycles can cause brief disruption at scale.

**AWS Load Balancer Controller** (EKS) translates Kubernetes Ingress resources directly into ALBs. Traffic from the ALB goes directly to Pod IPs when `target-type: ip` is used, bypassing the kube-proxy hop entirely. The tradeoff is cost - every Ingress creates a separate ALB.

**Azure Application Gateway Ingress Controller** (AKS) maps Ingress resources to Azure Application Gateway rules. It provides WAF integration and TLS certificate management via Azure Key Vault, but Application Gateway is a dedicated resource with non-trivial cost and AGIC is more complex to operate than NGINX.

**Service mesh gateways** (Istio Gateway, Linkerd Gateway) integrate ingress routing with the mesh. This eliminates the conceptual gap between internal and external traffic - both flow through the same dataplane, with consistent telemetry and policy.

**Gateway API** is the Kubernetes community's replacement for the Ingress API, providing a richer and more role-aware model. The core objects - GatewayClass, Gateway, HTTPRoute - separate infrastructure concerns from application routing rules. Most modern controllers are moving toward Gateway API. New clusters should prefer it over the legacy Ingress resource.

---

## Failure Modes to Plan For

### IP Exhaustion on Native CNIs

On EKS and AKS with native routing, running out of subnet IPs is an operational event, not just a capacity concern. The CNI cannot assign IPs it does not have. New Pods will fail to start with IP assignment errors. Existing Pods are not affected, which makes the failure mode confusing - the cluster appears healthy until a new Pod attempts to schedule.

**Signal:** Events on Pods showing `Failed to allocate IP` or CNI errors. Node status showing IP pool exhaustion in CNI-specific status annotations.

**Mitigation:** Plan subnet sizes to accommodate peak Pod count plus headroom for rolling updates, which temporarily double the Pod count for a Deployment. On EKS, consider IPv6 mode which eliminates IPv4 exhaustion. On AKS, evaluate Azure CNI Overlay if VNet space is constrained.

### Pod CIDR vs Node CIDR Overlap

On clusters with custom CIDR configuration, a common misconfiguration is a Pod CIDR range that overlaps with the node CIDR or with on-premises network ranges. This causes routing ambiguity - packets intended for a Pod IP are routed to a non-cluster destination instead.

**Signal:** Pod-to-Pod connectivity works within a node but fails between nodes. Node-to-Pod connectivity fails in one direction. On-premises services are unreachable from Pods in specific IP ranges.

**Mitigation:** Audit IP ranges before cluster creation. The Pod CIDR, node CIDR, Service CIDR, and any routable on-premises ranges must not overlap.

### Ingress Controller as Traffic Bottleneck

An ingress controller with two or three replicas, no topology spread, and no resource limits becomes the most impactful single point of failure in the cluster. A memory leak or traffic spike that exhausts one replica cascades to the remaining replicas, triggering a failure mode where increased traffic causes further failures.

**Signal:** Ingress controller Pods restarting or OOMKilled during traffic spikes. High latency or error rates on all services simultaneously (as opposed to a single service).

**Mitigation:** Apply CPU and memory limits and requests. Enable HPA with CPU and custom request-rate metrics. Apply topology spread constraints across zones and nodes. Set a PodDisruptionBudget to prevent simultaneous disruption during node maintenance.

### Overlay MTU Misconfiguration

Overlay CNIs reduce the effective MTU because encapsulation adds header bytes. If the underlying network MTU and the overlay MTU are not correctly configured, large packets get silently dropped or fragmented. The failure mode looks like intermittent partial connectivity - small requests succeed, large responses fail.

**Signal:** HTTP requests complete for small payloads but time out or fail for large payloads. File uploads fail partway through. gRPC streams work for small messages but break for large ones.

**Mitigation:** Verify the CNI's MTU configuration matches the underlying network minus encapsulation overhead. For VXLAN, subtract 50 bytes. For IP-in-IP, subtract 20 bytes.

---

## Practical Implementation Path

### Step 1: Know Your CNI and Its Constraints

Before debugging any networking issue, establish what CNI you are running and what architectural model it uses.

```bash
# Check what CNI is installed
kubectl get pods -n kube-system | grep -E 'cni|flannel|calico|cilium|aws-node|azure'

# On EKS: check VPC CNI version
kubectl describe daemonset aws-node -n kube-system | grep Image

# Check Pod CIDR per node
kubectl get nodes -o jsonpath='{.items[*].spec.podCIDR}'

# Check available IPs on a node
kubectl describe node <node-name> | grep -A5 'Allocatable'
```

### Step 2: Verify the Flat Network Is Actually Flat

If you suspect a CNI misconfiguration or networking regression, validate the core guarantee directly.

```bash
# Deploy a debug Pod and test connectivity to another Pod by IP
kubectl run debug-a --image=nicolaka/netshoot --rm -it -- bash

# From inside debug-a:
ping <pod-b-ip>
curl http://<pod-b-ip>:<port>
```

A failure here is a CNI problem, not a Service or Ingress problem. Keep the diagnostic layers separate.

### Step 3: Size Subnets for Native CNI Deployments

If you are running AWS VPC CNI or Azure CNI (non-overlay), calculate your IP budget before deployment.

```
Per node IP consumption:
  1 (node IP)
  + N (max Pods per node, by instance type)
  = total IPs per node

For EKS, check instance ENI limits:
  aws ec2 describe-instance-types \
    --instance-types m5.xlarge \
    --query 'InstanceTypes[].NetworkInfo.{MaxENIs:MaximumNetworkInterfaces,IPsPerENI:Ipv4AddressesPerInterface}'
```

Subnet size should accommodate peak node count times IPs per node, with 30% headroom for rolling updates and node replacement.

### Step 4: Choose Your Ingress Strategy Deliberately

| Scenario | Recommended Approach |
|---|---|
| EKS, need WAF and native AWS integration | AWS Load Balancer Controller (ALB mode) |
| EKS, need flexible L7 routing at low cost | NGINX Ingress |
| AKS, need WAF and Azure integration | AGIC with Application Gateway |
| AKS, need flexible routing | NGINX Ingress |
| Either cloud, running Istio or Linkerd | Mesh Gateway |
| Either cloud, new cluster | Gateway API-compatible controller |

### Step 5: Harden Your Ingress Controller

Treat the ingress controller as critical infrastructure with the same spread and disruption requirements as your most important services.

```yaml
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
      resources:
        requests:
          cpu: 200m
          memory: 256Mi
        limits:
          memory: 512Mi
```

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: ingress-nginx-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: ingress-nginx
```

### Step 6: Evaluate eBPF for Scale or Observability

For clusters above a few hundred Services, or any cluster where detailed network telemetry has operational value, evaluate Cilium. On EKS, Cilium can replace the VPC CNI entirely or run in chained mode. On AKS, Cilium is available as the network policy engine alongside Azure CNI.

The operational investment is higher than simpler CNIs, but the observability return is significant. Hubble provides per-connection flow telemetry, DNS request tracking, and HTTP-level visibility without additional instrumentation.

---

## Source Links

- [Kubernetes networking model](https://kubernetes.io/docs/concepts/cluster-administration/networking/)
- [Container Network Interface specification](https://github.com/containernetworking/cni)
- [AWS VPC CNI documentation](https://docs.aws.amazon.com/eks/latest/userguide/managing-vpc-cni.html)
- [EKS instance type ENI limits](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-eni.html#AvailableIpPerENI)
- [Azure CNI overview](https://learn.microsoft.com/en-us/azure/aks/concepts-network-cni-overview)
- [Azure CNI Overlay](https://learn.microsoft.com/en-us/azure/aks/azure-cni-overlay)
- [Cilium architecture](https://docs.cilium.io/en/stable/overview/intro/)
- [Kubernetes Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)
- [Gateway API](https://gateway-api.sigs.k8s.io/)
- [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller/)
- [Azure Application Gateway Ingress Controller](https://learn.microsoft.com/en-us/azure/application-gateway/ingress-controller-overview)

---

## Related Pages

- Parent index: [Playbooks](index.md)
- Related: [How Traffic Flows in Kubernetes](2026-03-11-how-traffic-flows-in-kubernetes.md)
- Related: [Networking Overview](../../networking/networking.md)
- Related: [Services and Networking](../../networking/services-networking.md)
- Related: [Network Policies](../../networking/netpol.md)
- Related: [Ingress](../../networking/ingress.md)
- Related: [Gateway API](../../networking/gateway-api.md)
