---
icon: material/text-box-search-outline
---

# Introduction to Kubernetes

Kubernetes, often referred to as K8s, is an open-source platform designed to automate deploying, scaling, and operating application containers. It was originally developed by Google and is now maintained by the Cloud Native Computing Foundation (CNCF). This sections covers the essentials to get you up to speed with Kubernetes, its architecture, and its key features.

## What is Kubernetes?

Kubernetes is a container orchestrator, which means it manages the deployment and operation of containerized applications. Containers are lightweight, portable units that bundle an application and its dependencies, allowing them to run consistently across different environments. Kubernetes automates several tasks:

- **Deployment:** Deploys applications seamlessly.
- **Scaling:** Adjusts the number of application instances based on demand.
- **Self-healing:** Detects and replaces failed instances.
- **Rolling Updates and Rollbacks:** Updates applications without downtime and rolls back if needed.

<h3>Declarative Model</h3>

The declarative nature of Kubernetes is key to understanding the power of it. At a super high level, this is how Kubernetes operates:

1. You *tell* Kubernetes (typically via `kubectl`) how you want your application to look. What image to use, how many replicas, ports to expose, etc.
2. Kubernetes persists this desired state to the cluster store (etcd)
3. A series of background controllers consistently check if current state matches desired state.
4. If current state does not equal desired state (i.e. we desire 3 replicas but only 2 are currently running),
5. Kubernetes kicks off a series of actions to reconcile the two states. In the example above, this would involve spinning up an extra replica.

![](../images/overview.svg)

## Historical Background

Kubernetes was born from Google's internal systems like Borg and Omega, which managed containerized applications like Search and Gmail at massive scale. In 2014, Google open-sourced Kubernetes, and it quickly became the standard for container orchestration.

## Kubernetes Architecture

Kubernetes clusters consist of two types of nodes - control plane nodes and worker nodes:

- **Control Plane Nodes:** These nodes run the Kubernetes control plane, which includes components like the API server, scheduler, and controllers. They manage the overall state of the cluster.
- **Worker Nodes:** These nodes run the applications and report back status to the control plane.

<h3>Components of the Control Plane</h3>

- **API Server:** The front end of Kubernetes that exposes the Kubernetes API. All traffic within, to, and from various Kubernetes components flows through the ARI Server. It is the Grand Central Station or central nervous system of Kubernetes.
- **Cluster Store:** A distributed database (etcd) that stores the entire state of the cluster. When your define your desired application specifications, they are stored here. This is the only *stateful* core component of Kubernetes.
- **Controllers:** Ensure the cluster's desired state matches its observed state by running background watch loops on objects like Deployments, Pods, etc.
- **Scheduler:** Assigns tasks to worker nodes based on resource availability, application requirements and other criteria.

<h3>Components of Worker Nodes</h3>

- **Kubelet:** The agent that communicates with the API server and manages containers on the node. The kubelet also communicates directly with the container runtime on the node, instructing it to pull images, and start/stop containers.
- **Runtime:** Executes container operations like starting and stopping containers. Common runtimes include containerd and CRI-O.
- **Kube-proxy:** Manages networking for containers, including load balancing.

![](../images/arch.svg)

!!! warning "Note"
    The API Server is the **only** component in Kubernetes that interacts directly with etcd.

## Kubernetes in Action

<h3>The Declarative Approach</h3>

Kubernetes operates on a declarative model, where you specify the desired state of the system in YAML or JSON configuration files. The system continuously works to ensure the observed state matches the desired state. This involves three key principles:

1. **Observed State:** The current state of the system.
2. **Desired State:** The state you want the system to achieve.
3. **Reconciliation:** The process of adjusting the observed state to match the desired state.

<h3>Pods and Deployments</h3>

- **Pods:** The smallest deployable units in Kubernetes, which can contain one or more containers. Pods share resources like network and storage.
- **Deployments:** Higher-level controllers that manage Pods, providing features like scaling, rolling updates, and rollbacks.

<h3>Services</h3>

Services provide stable networking endpoints for Pods, enabling reliable communication between different parts of an application. They abstract away the ephemeral nature of Pods, which can be created and destroyed dynamically.

## Advanced Features

<h3>Self-Healing and Scaling</h3>

Kubernetes automatically replaces failed Pods and scales the application up or down based on traffic and load. This ensures high availability and efficient resource utilization.

<h3>Rolling Updates and Rollbacks</h3>

Kubernetes allows you to update your application without downtime by gradually replacing old Pods with new ones. If something goes wrong, Kubernetes can roll back to the previous version.

## Conclusion

Kubernetes is a powerful tool for managing containerized applications, offering automation, scalability, and reliability. By abstracting the underlying infrastructure, it simplifies application deployment and management across various environments. Whether you're running on-premises or in the cloud, Kubernetes provides a consistent and efficient platform for your applications.