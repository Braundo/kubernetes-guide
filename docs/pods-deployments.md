---
icon: material/cube-outline
---

# Pods & Deployments

In Kubernetes, **Pods** are the foundational execution units—everything runs in a Pod. But on their own, Pods aren't typically used directly in production environments. Instead, **Deployments** manage Pods to provide automation, self-healing, and declarative updates.

---

## What is a Pod?

A **Pod** is the smallest deployable unit in Kubernetes. It represents one or more containers that share:

- The same **network namespace** (IP address and port space).
- A shared **storage volume** (if defined).
- The same **lifecycle** (they are scheduled and managed together).

Typically, a Pod contains a **single container**, but multi-container Pods are used when tightly coupled containers need to share resources, such as a sidecar pattern.

**Key traits of Pods**:

- Pods are ephemeral and disposable.
- Pods do not self-heal if they crash or are evicted.
- Pods are bound to a specific Node until terminated.

![Multi-container Diagram](images/multicontainer-light.png#only-light)
![Multi-container Diagram](images/multicontainer-dark.png#only-dark)

```mermaid
flowchart TD 
    subgraph "Pod"
        subgraph "container"
        H["application"]
        end
    end
```

---

## What is a Deployment?

A **Deployment** is a higher-level Kubernetes resource that manages a ReplicaSet, which in turn manages the lifecycle of multiple identical Pods.

With Deployments, you get:

- Declarative management of Pod replicas
- Rolling updates and rollbacks
- Auto-replacement of failed Pods
- Declarative versioning of your app

You define the desired state in a `Deployment` YAML file, and the Kubernetes control plane ensures that the running state matches it.

---

## Relationship Between Pods and Deployments

Think of a **Pod** like a coffee machine in a busy café. It makes drinks, does its job, and eventually wears out or breaks.

Now imagine the **Deployment** as the café manager:

- They make sure there are always enough coffee machines running.
- If one breaks, they replace it.
- If demand increases, they bring in more.
- If an update to the machine model is needed, they roll them out gradually and safely.

So while a **Pod** is the worker, the **Deployment** manages the workforce and ensures consistency, scalability, and resiliency over time.

**A Deployment always manages Pods**—you typically never run a Deployment without Pods.

When you apply a Deployment spec:

1. Kubernetes creates a **ReplicaSet**.
2. The ReplicaSet creates the desired number of **Pods**.
3. If any Pod dies, the ReplicaSet spawns a replacement.

---

## When to Use What?

**Use Pods directly**:

  - In static dev/test environments.
  - For one-off jobs (though `Job` is preferred).
  - For simple single-Pod debugging.

**Use Deployments**:

  - Always, for production services.
  - When you need replication, availability, and self-healing.
  - If you plan to roll out updates with zero downtime.