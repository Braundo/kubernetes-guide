---
icon: material/circle-small
---

* In Kubernetes, a **controller** is a process that continuously monitors the state of various components and works toward bringing the system into its desired state.
<br><br>

* For example, the **Node Controller** is responsible for monitoring Kubernetes Nodes:

    * It receives heartbeats from the Nodes every 5 seconds - via the Kubernetes API Server
    * If it doesn’t receive a heartbeat from a Node, it gives it a 40-second grace period before marking the Node as `Unreachable`
    * Once a node is marked `Unreachable`, it gives the Node 5 minutes to come back online before it evicts Pods from that Node and begins scheduling them on a healthy Node (if part of a ReplicaSet).

<br>

* The **Replication Controller** is in charge of monitoring the state of ReplicaSets. 
<br><br>

- There are many other types of Controllers within Kubernetes (Deployment, Namespace, Endpoint, CronJob, ServiceAccount, Job, StatefulSet, etc…)
<br><br>

* All of these Controllers are packaged into a single process known as the **Kubernetes Controller Manager**.