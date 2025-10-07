---
icon: material/account-lock-outline
---

<h2>Core Concepts</h2>

RBAC controls <strong>who can do what</strong> in your Kubernetes cluster. It sets permissions for accessing the Kubernetes API and is essential for securing clusters with multiple users or teams. Kubernetes RBAC grants specific actions (verbs) on resources to users or service accounts.

<h3>RBAC Objects</h3>

| Kind           | Purpose                                       |
|----------------|-----------------------------------------------|
| <code>Role</code>         | Grants permissions within a single namespace  |
| <code>ClusterRole</code>  | Grants permissions cluster-wide               |
| <code>RoleBinding</code>  | Assigns a Role to a user/group in a namespace |
| <code>ClusterRoleBinding</code> | Assigns a ClusterRole to a user/group across all namespaces |



---

<h2>Example: Read-Only Role in a Namespace</h2>

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

<h3>Binding the Role</h3>

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

This lets <code>alice</code> read pods in the <code>dev</code> namespace only.

---

<h2>Cluster-Wide Example</h2>

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
- Not scoping permissions - always **follow least privilege**

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