---
icon: material/select
---

# Namespaces

Namespaces in Kubernetes allow you to divide cluster resources between multiple users or teams. They provide **logical isolation** and help with **multi-tenancy**, access control, and resource management.

---

## When to Use Namespaces

Namespaces are useful when:

- You need to **isolate environments** (e.g., `dev`, `staging`, `prod`)
- You want to enforce **resource quotas and limits**
- You want to implement **RBAC per team or application**

> For most small or single-team clusters, the `default` namespace is sufficient.

---

## Viewing Namespaces

```shell
kubectl get namespaces
```

Or with shorthand:

```shell
kubectl get ns
```

---

## Creating a Namespace

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

## Using Namespaces with kubectl

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

## Cleanup

To delete a namespace and everything inside it:

```shell
kubectl delete namespace dev-team
```

---

## Summary

- Namespaces are key to **organizing**, **isolating**, and **managing** Kubernetes resources.
- Use them for multi-tenancy, RBAC, and resource quotas.
- Know which resources are namespaced vs. cluster-scoped.