---
icon: lucide/square-dashed
title: Kubernetes Namespaces Explained (Isolation, Use Cases, and Best Practices)
description: Learn how Kubernetes namespaces work, when to use them, and common patterns for organizing workloads and environments.
hide:
 - footer
---

# Namespaces

Namespaces provide logical partitioning inside a single cluster.

They are useful for separating teams, environments, and policy boundaries without creating separate clusters for everything.

## Built-in Namespaces

| Namespace | Purpose |
| :--- | :--- |
| `default` | Fallback namespace if none is specified |
| `kube-system` | Control-plane and system workloads |
| `kube-public` | Publicly readable metadata use cases |
| `kube-node-lease` | Node heartbeat lease objects |

## Namespaced vs Cluster-Scoped Resources

Namespaced resources:

- Pods
- Deployments
- Services
- ConfigMaps
- Secrets

Cluster-scoped resources:

- Nodes
- StorageClasses
- PersistentVolumes
- ClusterRoles and ClusterRoleBindings

Check scope quickly:

```bash
kubectl api-resources --namespaced=true
kubectl api-resources --namespaced=false
```

## Isolation Boundaries

Namespaces isolate object names and many policies, but they are not a complete security boundary by themselves.

For real multi-tenant separation, combine:

- Namespaces
- RBAC
- NetworkPolicies
- ResourceQuota and LimitRange
- Pod Security Admission labels

## DNS and Cross-Namespace Access

Service discovery format:

- same namespace: `http://my-service`
- cross namespace: `http://my-service.other-namespace.svc.cluster.local`

Cross-namespace traffic is allowed by default unless restricted by policy.

## Resource Governance

### ResourceQuota example

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-a-quota
  namespace: team-a
spec:
  hard:
    pods: "50"
    requests.cpu: "20"
    requests.memory: 40Gi
```

### LimitRange example

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-container-limits
  namespace: team-a
spec:
  limits:
    - type: Container
      default:
        cpu: "500m"
        memory: "512Mi"
      defaultRequest:
        cpu: "100m"
        memory: "128Mi"
```

## Operational Practices

- Use explicit namespaces in CI/CD (`-n` or fully-qualified manifests).
- Use naming conventions (`team-a-dev`, `team-a-prod`).
- Avoid placing application workloads in `kube-system`.
- Audit namespace ownership and RBAC regularly.

## Summary

Namespaces are foundational for cluster organization, but policy controls are what make isolation enforceable in production.
