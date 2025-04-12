---
icon: material/account-lock-outline
---

# RBAC (Role-Based Access Control)

RBAC controls **who can do what** in your Kubernetes cluster. It defines **permissions to access the Kubernetes API**, and is critical for securing multi-user environments.

---

## Core Concepts

Kubernetes RBAC works by **granting verbs on resources** to users or service accounts.

### RBAC Objects

| Kind           | Purpose                                       |
|----------------|-----------------------------------------------|
| `Role`         | Grants permissions within a single namespace  |
| `ClusterRole`  | Grants permissions cluster-wide               |
| `RoleBinding`  | Assigns a Role to a user or group in a namespace |
| `ClusterRoleBinding` | Assigns a ClusterRole to a user or group across all namespaces |

---

## Example: Read-Only Role in a Namespace

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: dev
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list"]
```

### Binding the Role

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: dev
subjects:
  - kind: User
    name: alice
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

This lets `alice` **read pods in the `dev` namespace** only.

---

## Cluster-Wide Example

To give a user full access to nodes and persistent volumes across the cluster:

```yaml
kind: ClusterRole
rules:
  - apiGroups: [""]
    resources: ["nodes", "persistentvolumes"]
    verbs: ["get", "list", "watch"]
```

> Bind it using a `ClusterRoleBinding` to apply cluster-wide.

---

## Common Verbs

- `get`, `list`, `watch`: Read operations
- `create`, `update`, `patch`, `delete`: Write operations
- `impersonate`: Required to act as another user/service account

---

## Common RBAC Pitfalls

- Forgetting to bind a Role: RBAC rules do nothing unless bound
- Using `ClusterRole` when `Role` is safer
- Not scoping permissions — always **follow least privilege**

---

## Audit & RBAC

Pair RBAC with audit logging to:

- Detect excessive privileges
- Track unauthorized access attempts
- Ensure least privilege policies are followed

---

## Summary

- RBAC defines access to **Kubernetes API resources**
- Use `Role`/`RoleBinding` for namespaced access, `ClusterRole` for global access
- Grant **least privilege** and bind only what’s necessary
- Essential for securing clusters and enabling multi-team usage