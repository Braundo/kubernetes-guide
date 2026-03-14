---
icon: lucide/shield-user
title: Kubernetes RBAC Explained (Roles, RoleBindings, and Best Practices)
description: Learn Kubernetes RBAC concepts, how Roles and RoleBindings work, and best practices for least-privilege access with examples.
hide:
 - footer
---

# RBAC

RBAC governs what authenticated identities can do in Kubernetes.

Authentication answers who the caller is. Authorization with RBAC answers what that caller is allowed to do.

## Core RBAC objects

- Role: namespaced permissions
- ClusterRole: cluster-scoped or reusable permissions
- RoleBinding: binds Role or ClusterRole within one namespace
- ClusterRoleBinding: binds ClusterRole cluster-wide

## Scope and reuse model

A common pattern is to define reusable ClusterRoles and bind them per namespace with RoleBindings.

This gives consistency without giving global access.

## Role example

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: app-reader
  namespace: team-a
rules:
  - apiGroups: [""]
    resources: ["pods", "services", "configmaps"]
    verbs: ["get", "list", "watch"]
```

## RoleBinding example

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: app-reader-binding
  namespace: team-a
subjects:
  - kind: Group
    name: team-a-developers
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: app-reader
  apiGroup: rbac.authorization.k8s.io
```

## Service account access

Workloads should use dedicated service accounts, not the namespace default account.

Pair each service account with only the minimal verbs and resources it needs.

## Validation and troubleshooting

```bash
kubectl auth can-i list pods -n team-a
kubectl auth can-i create deployments --as=system:serviceaccount:team-a:deployer -n team-a
kubectl get role,rolebinding -n team-a
kubectl get clusterrole,clusterrolebinding
```

## Hardening guidance

- avoid broad wildcard rules unless explicitly justified
- tightly control `secrets`, `pods/exec`, and `impersonate` permissions
- minimize use of `cluster-admin`
- review bindings on a fixed cadence and remove stale access

## Summary

RBAC is a primary control plane security boundary. Keep permissions explicit, minimal, and auditable.

## Related Security Concepts

- [Security Primer](security.md)
- [Pod Security](psa.md)
- [Audit and Logging](audit-logging.md)
