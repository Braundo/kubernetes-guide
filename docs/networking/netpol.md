---
icon: lucide/shield-check
title: Kubernetes Network Policies Explained (Traffic Control and Security)
description: Learn how Kubernetes Network Policies control traffic between Pods and namespaces to improve security and isolation.
hide:
 - footer
---

# Network Policies

NetworkPolicy controls pod-to-pod traffic at Layer 3 and Layer 4.

By default, many clusters allow broad lateral traffic. NetworkPolicy lets you move to explicit allow rules.

## Prerequisite

Your CNI must implement NetworkPolicy. If it does not, policy objects may apply successfully but have no effect.

## Default-deny foundation

Start sensitive namespaces with default-deny, then add explicit allow rules.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: payments
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

## Allow app-to-app ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-web-to-api
  namespace: payments
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: web
      ports:
        - protocol: TCP
          port: 8080
```

## Cross-namespace allow

Use `namespaceSelector` when source pods live in another namespace.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-monitoring-scrape
  namespace: payments
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: monitoring
      ports:
        - protocol: TCP
          port: 9090
```

## Egress and DNS

When egress restrictions are enabled, allow DNS explicitly or service discovery will break.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-egress
  namespace: payments
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
```

## Troubleshooting

```bash
kubectl get netpol -A
kubectl describe netpol allow-web-to-api -n payments
kubectl get pods -A --show-labels
```

Also validate policy behavior with test pods and explicit connectivity checks (`curl`, `nc`, or purpose-built policy tests).

## Design guidance

- define namespace trust boundaries first
- apply default-deny early in new namespaces
- make allow rules specific by label and port
- keep policy manifests version-controlled and reviewed

## Summary

NetworkPolicy is a core Kubernetes security control for lateral movement reduction. It should be standard in production clusters, especially in multi-team environments.

## Related Concepts

- [Networking Overview](networking.md)
- [Ingress](ingress.md)
- [Security Primer](../security/security.md)
- [RBAC](../security/rbac.md)
