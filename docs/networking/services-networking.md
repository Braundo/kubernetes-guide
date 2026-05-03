---
icon: lucide/network
title: Kubernetes Services Explained (ClusterIP, NodePort, LoadBalancer)
description: Learn how Kubernetes Services work, how traffic flows to Pods, and when to use ClusterIP, NodePort, and LoadBalancer with real examples.
hide:
 - footer
---

# Services and Traffic Routing

Pods are ephemeral. Their IPs can change as they are recreated.

A Service gives clients a stable destination while Kubernetes updates backend pod endpoints behind the scenes.

## How a Service Works

A Service typically includes:

- selector: chooses backend pods by label.
- virtual IP (ClusterIP): stable in-cluster address.
- DNS name: stable service discovery name.
- port mapping: client-facing port to container-facing target port.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 8080
```

## Service Types

## 1) ClusterIP (default)

Internal-only virtual IP for in-cluster access.

Use when workloads communicate inside the cluster.

![ClusterIP Diagram](../images/clusterip-light.png#only-light)
![ClusterIP Diagram](../images/clusterip-dark.png#only-dark)

## 2) NodePort

Exposes service on each node IP and a static port (default range `30000-32767`).

Use for basic external testing or on-prem setups without a cloud load balancer.

```yaml
spec:
  type: NodePort
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080
```

![NodePort Diagram](../images/nodeport-light.png#only-light)
![NodePort Diagram](../images/nodeport-dark.png#only-dark)

## 3) LoadBalancer

Requests an external load balancer from your infrastructure provider (cloud or compatible on-prem implementation).

```yaml
spec:
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 8080
```

![LoadBalancer Diagram](../images/loadbalancer-light.png#only-light)
![LoadBalancer Diagram](../images/loadbalancer-dark.png#only-dark)

## 4) ExternalName

Maps a Service to an external DNS name, without pod backends.

```yaml
spec:
  type: ExternalName
  externalName: db.example.com
```

This type returns a CNAME record rather than a ClusterIP. No proxying occurs.

## Headless Services

Setting `clusterIP: None` creates a headless Service that returns pod IPs directly from DNS instead of a virtual IP. This is how StatefulSets provide stable per-pod DNS names.

```yaml
spec:
  clusterIP: None
  selector:
    app: web
```

DNS for a headless service returns `A` records for each ready pod IP directly, rather than a single ClusterIP. Clients get all pod addresses and choose themselves.

## EndpointSlices

Kubernetes stores service backend endpoint data in EndpointSlice objects.

This improves scalability compared to the older Endpoints object for large services.

Check backend resolution:

```bash
kubectl get svc web
kubectl get endpointslices -l kubernetes.io/service-name=web
```

## externalTrafficPolicy

For `NodePort` and `LoadBalancer` services, `externalTrafficPolicy` controls whether external traffic is routed cluster-wide or only to pods on the receiving node.

- `Cluster` (default): traffic can be forwarded to any node that has a ready pod. Source IP is NAT'd, so the pod sees the node IP rather than the client IP.
- `Local`: traffic is only sent to pods on the node that received it. Preserves the client source IP but causes uneven load distribution if pods are not evenly spread across nodes.

Use `Local` when your app needs the real client IP (e.g. for rate limiting or geo routing) and you accept the tradeoff.

## Session Affinity

By default, each connection is independently load-balanced across pod endpoints. To route repeated connections from the same client to the same pod, use session affinity:

```yaml
spec:
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800
```

This is based on the source IP as seen by the Service, not the original client IP (use `externalTrafficPolicy: Local` if you need the real client IP to drive affinity).

## Common Pitfalls

- Selector mismatch: Service has no endpoints.
- Wrong `targetPort`: traffic reaches pod IP but wrong container port.
- Readiness probe failures: endpoints removed because pods are not ready.
- Using `sessionAffinity` with `Cluster` externalTrafficPolicy and expecting it to track real client IPs.

## Summary Table

| Type | Visibility | Typical use |
| :--- | :--- | :--- |
| `ClusterIP` | Internal | Service-to-service traffic |
| `NodePort` | External via node IP | Basic external exposure |
| `LoadBalancer` | External LB IP/hostname | Public or private ingress point |
| `ExternalName` | DNS alias | External dependency abstraction |

## Related Concepts

- [Networking Overview](networking.md)
- [Ingress](ingress.md)
- [Gateway API](gateway-api.md)
- [Pods and Deployments](../workloads/pods-deployments.md)
