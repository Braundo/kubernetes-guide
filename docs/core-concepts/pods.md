---
icon: material/circle-small
---

Pods are the atomic unit of scheduling in Kubernetes. As virtual machines were in the VMware world, so are Pods in the world of Kubernetes. Every container running on Kubernetes must be wrapped up in a Pod. Think of a Pod as a wrapper for your application’s container(s), similar to how a virtual machine encapsulates an entire operating system and its applications.  

The most simple implementation of this are single-container Pods - one container inside one Pod. However there are certain instances where multi-container Pods make sense.

It's important to note that when you scale up/down applications in Kubernetes, you're not doing so by adding/removing containers directly - you do so by adding/removing Pods.

## Atomic
Pods are atomic units in the sense that they are deployed, scaled, and terminated together. This makes them a fundamental component for deploying applications in Kubernetes:

- **Single-container Pods**: The simplest form, containing only one container.
- **Multi-container Pods**: These contain multiple containers that need to work closely together.

## Lifecycle
Pods are designed to be ephemeral in nature. Once a Pod dies, it's not meant to be restarted or revived. Instead, the intent is to spin up a brand new Pod in the failed ones place (based off of your defined manifest). Further, Pods are *immutable* and should not be changed once running. If you need to change your application, you update the configuration via the manifest and deploy a new Pod.  

Pods also follow a defined restart policy in order to handle container failures:  

- `Always`: The container is restarted even if it exits successfully.
- `OnFailure`: The container is only restarted if it exits with an error.
- `Never`: The container is never restarted, regardless of the exit status.

## Shared Resources and Communication
Containers within a Pod share networking and volumes:

- **Networking**: Containers in a Pod share the same IP address and port space.
- **Volumes**: Allows sharing of storage between containers within a Pod.

## Multi-container Pods
As mentioned above, the simplest way to run an app on Kubernetes is to run a single container inside of a single Pod. However, in situations where you need to tightly couple two or more functions you can co-locate multiple containers inside of the same pod. One such example would be leveraging the sidecar pattern for logging wherein the main container dumps logs to a supporting container that can sanitize and format the logs for consumption. This frees up the main container from having to worry about formatting logs.  

## Affinity and Anti-affinity
Kubernetes offers ways to control where Pods are placed relative to other Pods or to specific nodes. Pod affinity rules attract Pods to nodes with specific labels, while anti-affinity rules repel them, ensuring high availability and optimal resource utilization.

## Resource Requests and Limits
Pods can specify the amount of CPU and memory required (requests) and the maximum that can be consumed (limits). This helps Kubernetes make better scheduling decisions and manage system resources efficiently.

## Probes: Readiness and Liveness
Kubernetes uses probes to manage the lifecycle of containers within Pods:

- **Readiness Probes**: Ensure traffic is not sent to a Pod until it is ready to handle it.
- **Liveness Probes**: Help to keep applications healthy by restarting containers that fail the defined checks.

## Init Containers
Init containers run before the application containers and are used to perform setup tasks or wait for some condition before the app starts. They run to completion and must exit before the main application containers start.

## Quality of Service (QoS) Classes
Pods are assigned QoS classes based on their resource requests and limits:

- `Guaranteed`: Pods with defined and equal requests and limits, ensuring the highest priority.
- `Burstable`: Pods with defined requests lower than limits, giving some flexibility.
- `BestEffort`: Pods with no requests or limits, receiving the lowest priority.

## Pod Disruption Budgets
Pod Disruption Budgets (PDBs) allow you to ensure that a minimum number of Pods are always available during voluntary disruptions, such as node maintenance, safeguarding against outages.

## Annotations and Labels
Labels are key/value pairs for organizing and selecting groups of Pods, while annotations provide a way to store additional metadata to help manage applications.

## Service Accounts
Pods use service accounts to authenticate to the Kubernetes API, which is crucial for Pods that need to interact with the API for automation and orchestration.

## Summary
Pods are the building blocks of a Kubernetes application. They ensure that containers run in a controlled, isolated, and secure environment with all the necessary configurations and resources. While Pods are inherently transient, their patterns and behaviors are foundational to how applications are designed and managed in Kubernetes. For more granular control and advanced features, refer to the official Kubernetes documentation.

*[sidecar]: A Kubernetes side container is an additional container that runs alongside a primary application container within a Pod.
*[ephemeral]: Lasting for a very short time.
*[atomic]: All or nothing.