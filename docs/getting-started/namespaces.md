---
icon: lucide/square-dashed
title: Kubernetes Namespaces Explained (Isolation, Use Cases, and Best Practices)
description: Learn how Kubernetes namespaces work, when to use them, and common patterns for organizing workloads and environments.
hide:
  - footer
---

# Namespaces

If a Kubernetes cluster is a physical building, **Namespaces** are the separate offices (or apartments) inside it.

Everyone shares the same electricity (CPU) and plumbing (Memory), but they have their own keys, their own furniture, and they can't see what's happening in the office next door unless they are explicitly invited.

Namespaces provide **Logical Isolation**. They allow you to host "Dev", "Staging", and "Prod" on the same cluster without them accidentally overwriting each other's configurations.

-----

## The "Default" Namespaces

When you start a fresh cluster, Kubernetes isn't empty. It comes with four built-in namespaces:

| Namespace | Purpose |
| :--- | :--- |
| **`default`** | Where your work goes if you don't specify a namespace. |
| **`kube-system`** | The "Engine Room." Contains the API Server, Scheduler, and DNS. **Do not touch this unless you know what you are doing.** |
| **`kube-public`** | Readable by everyone (even unauthenticated users). Rarely used, mostly for cluster bootstrapping. |
| **`kube-node-lease`** | A technical namespace used by Kubelets to send "heartbeats" to the master. |

-----

## Scoping: Who lives where?

Not everything fits in a namespace. This is a crucial concept for administrators.

  * **Namespaced Resources:** These live *inside* a room. (e.g., Pods, Deployments, Services, ConfigMaps). Two different namespaces can both have a Deployment named "my-app".
  * **Cluster-Scoped Resources:** These are the *building itself*. They exist globally. (e.g., Nodes, PersistentVolumes, StorageClasses). You cannot have two Nodes with the same name, ever.

**How to check?**
Run this command to see which resources are namespaced:

```bash
kubectl api-resources --namespaced=true
```

-----

## Cross-Namespace Communication (DNS)

Beginners often ask: *"Can a Pod in Dev talk to a Service in Prod?"*
**Yes.** (Unless blocked by a NetworkPolicy).

By default, namespaces are **not** network firewalls. They are just organizational folders. However, the **DNS name** changes.

  * **Same Namespace:** You can just call the service name.
      * `curl http://my-database`
  * **Different Namespace:** You must use the Fully Qualified Domain Name (FQDN).
      * `curl http://my-database.production.svc.cluster.local`

-----

## Best Practices for Organization

### 1\. Environments vs. Teams

How should you slice your cluster?

  * **Small Company:** `dev`, `staging`, `prod`.
  * **Large Enterprise:** `team-a-dev`, `team-a-prod`, `team-b-dev`.

### 2\. Resource Quotas (The Budget)

You can assign a "Budget" to a namespace to prevent one team from using all the cluster's RAM.

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: dev
spec:
  hard:
    pods: "10"             # Max 10 pods allowed
    requests.cpu: "4"      # Max 4 CPU cores total
    requests.memory: 2Gi   # Max 2GB RAM total
```

### 3\. LimitRanges (The Rules)

You can force every Pod in a namespace to have a default size, so users don't have to guess.

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-mem-limit
  namespace: dev
spec:
  limits:
  - default:
      memory: 512Mi
    type: Container
```

-----

## Managing Context (The `kubens` Tool)

Typing `-n my-long-namespace-name` on every command is painful.

**The Hard Way:**

```bash
kubectl config set-context --current --namespace=my-team-dev
```

**The Pro Way:**
Install a tool called `kubens` (part of the `kubectx` package).

```bash
kubens my-team-dev
```

Now all your future `kubectl` commands automatically run in that namespace until you switch back.

-----

## Summary

  * **Namespaces** allow you to partition a single cluster into virtual sub-clusters.
  * They are ideal for **multi-tenancy** (separating teams or environments).
  * Resources like **Nodes** and **PVs** are global; Pods and Services are namespaced.
  * Services in different namespaces **can** talk to each other using their full DNS name (FQDN).
  * Use **ResourceQuotas** to prevent a single namespace from hogging all the cluster resources.