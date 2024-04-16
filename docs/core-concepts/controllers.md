---
icon: material/circle-small
---

### Understanding Kubernetes Controllers

In Kubernetes, a **controller** is a background process that constantly monitors the state of various components within the cluster. Its primary function is to reconcile the current state of the cluster with the desired state specified by the user.

<h4>Key Controllers in Kubernetes</h4>

- **Node Controller**: Monitors the health of nodes by checking 'heartbeats' received through the Kubernetes API server every 5 seconds. If a heartbeat is missed, the node is given a 40-second grace period before being marked as 'Unreachable'. If the node remains unreachable for 5 minutes, it is considered down, and its Pods are evicted and rescheduled to available nodes, ensuring continued availability and resilience of applications.

- **Replication Controller**: Ensures that the number of replicas for a Pod matches the desired state defined in a ReplicaSet. If there are too few Pods, it creates more; if there are too many, it removes the excess.

<h4>Other Essential Controllers</h4>

- **Deployment Controller**: Manages the life cycle of deployments by updating Pods and ReplicaSets.
- **Namespace Controller**: Handles namespace creation, updating, and deletion.
- **Endpoint Controller**: Populates the Endpoints object (that is, joins Services & Pods).
- **CronJob Controller**: Manages time-based jobs, ensuring they run at specified times.
- **ServiceAccount Controller**: Manages Service Accounts, automating token creations.
- **Job Controller**: Oversees tasks that run to completion.
- **StatefulSet Controller**: Manages applications that require persistent state or unique identities.

<h4>Kubernetes Controller Manager</h4>

All these controllers are consolidated into a single binary — the **Kubernetes Controller Manager**. This component optimizes cluster management by centralizing the control mechanisms required to manage various cluster states effectively.

By understanding and leveraging these controllers, operators can ensure their Kubernetes clusters operate smoothly and resiliently, automatically handling failures and changes in the environment.

### Extending Controller Functionality

Kubernetes is also extensible, allowing developers to create custom controllers that introduce new behaviors or manage third-party resources, further enhancing the ecosystem's capabilities.
