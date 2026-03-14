---
icon: lucide/share-2
title: Kubernetes Networking Explained (Pod-to-Pod, Service, and Cluster Networking)
description: Understand Kubernetes networking fundamentals, including pod communication, service networking, and cluster-level traffic flow.
hide:
 - footer
---

# Networking Concepts

Kubernetes networking is built on a simple model with strict expectations for connectivity and service discovery.

## Core Model

1. Every pod gets its own IP address.
2. Pods can communicate with other pods without user-managed NAT between pods.
3. Services provide stable virtual endpoints in front of changing pod backends.

Containers in the same pod share one network namespace and communicate over `localhost`.

## Data Plane Components

Networking behavior depends on your implementation stack:

- CNI plugin: pod network and IP routing.
- kube-proxy or eBPF service implementation: service VIP translation and load balancing.
- CoreDNS: in-cluster DNS.

## Traffic Types

- East-west: traffic between workloads inside the cluster.
- North-south: traffic entering or leaving the cluster.

East-west usually uses Services and DNS.
North-south usually uses Ingress or Gateway API on top of Service backends.

## Service Discovery

Service DNS format:

```text
<service>.<namespace>.svc.cluster.local
```

Example:

```bash
nslookup api.backend.svc.cluster.local
```

## Security and Segmentation

By default, many CNIs allow broad pod-to-pod communication.

Use NetworkPolicies to explicitly control allowed ingress and egress paths between workloads.

## Practical Troubleshooting Checks

```bash
kubectl get pods -A -o wide
kubectl get svc -A
kubectl get endpointslices -A
kubectl get netpol -A
```

If DNS fails, check CoreDNS pods in `kube-system`.

## Related Networking Topics

- [Kubernetes Services](services-networking.md)
- [Ingress and HTTP Routing](ingress.md)
- [Network Policies](netpol.md)
- [Gateway API](gateway-api.md)
