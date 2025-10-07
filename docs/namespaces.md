---
icon: material/select
---

<h1>Namespaces</h1>

Namespaces in Kubernetes allow you to divide cluster resources between multiple users or teams. They provide <strong>logical isolation</strong> and help with <strong>multi-tenancy</strong>, access control, and resource management.

---

<h2>When to Use Namespaces</h2>

Namespaces are useful when:

- You need to **isolate environments** (e.g., `dev`, `staging`, `prod`)
- You want to enforce **resource quotas and limits**
- You want to implement **RBAC per team or application**

!!! tip
    For most small or single-team clusters, the `default` namespace is sufficient.

---

<h2>Viewing Namespaces</h2>

```shell
kubectl get namespaces
```

Or with shorthand:

```shell
kubectl get ns
```

---

<h2>Creating a Namespace</h2>

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: dev-team
```

Apply it:

```shell
kubectl apply -f namespace.yaml
```

---

<h2>Using Namespaces with kubectl</h2>

```shell
kubectl get pods -n dev-team
kubectl create deployment nginx --image=nginx -n dev-team
```

To temporarily switch namespace context:

```shell
kubectl config set-context --current --namespace=dev-team
```

---

## Default Namespaces

| Namespace     | Purpose                                               |
|---------------|--------------------------------------------------------|
| `default`     | Used when no other namespace is specified              |
| `kube-system` | Kubernetes control plane components (DNS, scheduler)   |
| `kube-public` | Readable by all users, often used for public bootstrap |
| `kube-node-lease` | Heartbeats for node status                         |

---

## Namespaced vs Cluster-Scoped Resources

Some resources **must** live in a namespace, others are **cluster-scoped**.

| Namespaced             | Cluster-Scoped            |
|------------------------|---------------------------|
| Pods, Deployments, PVCs| Nodes, PersistentVolumes  |
| ConfigMaps, Secrets    | Namespaces, CRDs          |
| Services               | StorageClasses, RBAC Roles|

---

## Resource Quotas and Limits

You can **enforce limits** on namespaces using:

- `ResourceQuota`: caps total resources in the namespace
- `LimitRange`: sets default limits per Pod/container

Example:

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: dev
spec:
  hard:
    requests.cpu: "2"
    limits.memory: 4Gi
```

---

<h2>Summary</h2>

- <strong>Namespaces</strong> provide logical isolation for teams, environments, or applications.
- Use namespaces to set resource quotas, apply RBAC, and organize your cluster.
- For small/simple clusters, the <code>default</code> namespace is fine; use more as you scale.

!!! tip
    Name namespaces clearly (e.g., `dev`, `prod`, `team-a`) and use them to enforce security and resource policies.

<br>