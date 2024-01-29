## Introduction
- Kubernetes offers built-in APIs for declarative management of workloads.
- Workloads run as containers inside Pods.
- Kubernetes control plane manages Pods based on workload object specifications.


## Deployment and ReplicaSet
- Most common way to run applications on the cluster.
- Good for managing stateless application workloads.
- Pods in a Deployment are interchangeable.
- Replaces the legacy `ReplicationController` API.


## StatefulSet
- Manages one or more Pods running the same application code.
- Pods have a distinct identity, unlike Deployments.
- Commonly used to link Pods with their persistent storage via `PersistentVolume`.
- Replacement Pods connect to the same `PersistentVolume`.


## DaemonSet
- Defines Pods that provide node-specific facilities.
- Useful for running drivers or other node-level services.
- Can run across every node or a subset of nodes in the cluster.


## Job and CronJob
- **Job** represents a one-off task that runs to completion.
- **CronJob** represents tasks that repeat according to a schedule.