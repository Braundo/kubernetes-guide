---
icon: material/cube-outline
---

## Introduction to Kubernetes Pods

In Kubernetes, every application runs inside a Pod. Understanding how to work with Pods is crucial for deploying, scaling, and managing applications effectively.

## Pod Fundamentals

Pods are the smallest deployable units in Kubernetes and serve as an abstraction layer, allowing various types of workloads to run seamlessly. They enable resource sharing, advanced scheduling, health monitoring, and more.

<h3>Abstraction and Benefits</h3>

Pods abstract the complexities of different workload types, enabling Kubernetes to manage them without needing to understand the specifics of each workload. This abstraction allows for uniform deployment and management across heterogeneous environments.

![](../images/pod-abstract.svg)

In the image above, all four of those apps are vastly different but once containerized and wrapped in a Pod, Kubernetes treats them all the same and doesn't have to worry about the details of how each application is written or works.

<h3>Enhancements and Capabilities</h3>

Pods offer several enhancements for containers, including:

- **Resource Sharing:** Shared filesystem, network stack, memory, process tree, and hostname.
- **Advanced Scheduling:** Features like nodeSelectors, affinity rules, topology spread constraints, resource requests, and limits.
- **Health Monitoring and Restart Policies:** Probes for application health and policies for container restarts.
- **Security and Termination Control:** Enhanced security measures and graceful shutdown processes.
- **Volumes:** Shared storage among containers within a Pod.

## Efficient Resource Utilization

<h3>Resource Sharing in Pods</h3>

Pods allow containers to share resources within the same execution environment:

- **Filesystem and Volumes:** Shared through the `mnt` Linux namespace.
- **Network Stack:** Shared via the `net` Linux namespace.
- **Memory and Process Tree:** Shared using the `ipc` and `pid` Linux namespaces.
- **Hostname:** Shared using the `uts` Linux namespace.

<h3>Scheduling Strategies</h3>

Kubernetes handles scheduling Pods to Nodes based on several different criteria. For multi-container Pods, Kubernetes ensures all containers *within the same Pod* are scheduled on the same Node. Kubernetes comes with sensible defaults for scheduling Pods, but some advanced scheduling techniques are available such as:

- **nodeSelectors:** Labels specifying Node requirements.
- **Affinity Rules:** Attract or repel Pods based on Node or Pod labels.
- **Topology Spread Constraints:** Distribute Pods across zones for high availability.
- **Resource Requests and Limits:** Define minimum and maximum resource requirements for Pods.

## Lifecycle and Management

<h3>Deploying and Managing Pods</h3>

Deploying a Pod involves several steps:

1. **Define the Pod in a YAML manifest:** A YAML file specifying the desired state of the Pod, including containers, volumes, and other resources.
2. **Post the manifest to the API server:** Using `kubectl apply -f <filename>.yaml`, the manifest is sent to the Kubernetes API server.
3. **API server authentication and authorization:** The API server checks if the request is allowed.
4. **API server validation:** The API server validates the Pod specification against the cluster's policies and configurations.
5. **Scheduler assigns the Pod to a Node:** The scheduler determines the most suitable node based on resource availability and scheduling policies.
6. **Kubelet starts and monitors the Pod:** The kubelet on the assigned node starts the containers and continuously monitors their status.

<h3>Pod Lifecycle and Immutability</h3>

Pods are designed to be ephemeral and immutable:

- **Ephemeral:** Pods are created, executed, and terminated without restarting. Pods are deleted upon completion or failure and are not intended to last forever.
- **Immutable:** Once deployed, Pods cannot be modified. To update, a new Pod must be created to replace the old one.

<h3>Restart Policies</h3>

Restart policies apply to individual *containers* within a Pod:

- **Always:** Always restart containers.
- **Never:** Never restart containers.
- **OnFailure:** Restart containers only if they fail.

Again, those are policies for containers within the Pod - Pods themselves do not restart.

## Multi-Container Pods

Multi-container Pods follow the single responsibility principle, where each container performs a distinct role. Some example use cases for this pattern include:

- **Init Containers:** Prepare the environment before application containers start.
- **Sidecar Containers:** Provide auxiliary services alongside the main application container.

One common example is to use a multi-container Pod for service meshes. In these scenarios, a sidecar container acts as an SSL termination point for all traffic coming into the main Pod.

![](../images/sidecar.svg)

As mentioned above, multiple containers within a Pod share the same IP address, network stack, and filesystem. As such, to communicate with specific containers within a multi-container Pod, you have to leverage port addresses. The containers themselves, however, will be able to communicate with each other via localhost.

![](../images/sidecar-net.svg)

## Using kubectl for Pod Management

<h3>kubectl Basics</h3>

`kubectl` is the command-line tool for interacting with Kubernetes clusters. Key operations include:

**Find Running Pods:**
  ```text
  $ kubectl get pods
  NAME        READY   STATUS    RESTARTS   AGE
  nginx-pod   1/1     Running   0          10s
  ```

**View more details on a Pod using `describe`:**
  ```text
  $ kubectl describe pod nginx-pod
  Name:             nginx-pod
  Namespace:        default
  Priority:         0
  Service Account:  default
  Node:             kind-worker/172.18.0.3
  Start Time:       Thu, 06 Jun 2024 19:06:38 -0500
  Labels:           run=nginx-pod
  Annotations:      <none>
  Status:           Running
  IP:               10.244.2.2
  IPs:
    IP:  10.244.2.2
  Containers:
    nginx-pod:
      Container ID:   containerd://92b7e2ac608fc5ad75c7196f69ae8695c93a9b9d5b9f1039b911e5ad65199b08
      Image:          nginx
      Image ID:       docker.io/library/nginx@sha256:0f04e4f646a3f14bf31d8bc8d885b6c951fdcf42589d06845f64d18aec6a3c4d
      Port:           <none>
      Host Port:      <none>
      State:          Running
        Started:      Thu, 06 Jun 2024 19:06:46 -0500
      Ready:          True
      Restart Count:  0
  <-- Rest of output trimmed -->
  ```

**View Pod Logs:**
  ```text
  $ kubectl logs nginx-pod
  /docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration
  /docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
  /docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
  10-listen-on-ipv6-by-default.sh: info: Getting the checksum of /etc/nginx/conf.d/default.conf
  10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf
  /docker-entrypoint.sh: Sourcing /docker-entrypoint.d/15-local-resolvers.envsh
  /docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh
  /docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh
  /docker-entrypoint.sh: Configuration complete; ready for start up
  2024/06/07 00:06:46 [notice] 1#1: using the "epoll" event method
  2024/06/07 00:06:46 [notice] 1#1: nginx/1.27.0
  2024/06/07 00:06:46 [notice] 1#1: built by gcc 12.2.0 (Debian 12.2.0-14)
  2024/06/07 00:06:46 [notice] 1#1: OS: Linux 6.6.26-linuxkit
  2024/06/07 00:06:46 [notice] 1#1: getrlimit(RLIMIT_NOFILE): 1048576:1048576
  2024/06/07 00:06:46 [notice] 1#1: start worker processes
  2024/06/07 00:06:46 [notice] 1#1: start worker process 32
  ```

<h3>Monitoring and Debugging</h3>

Use `kubectl` to monitor and debug Pods effectively:

**Detailed Pod Info:**
  ```text
  $ kubectl get pods -o wide
  NAME        READY   STATUS    RESTARTS   AGE    IP           NODE          NOMINATED NODE   READINESS GATES
  nginx-pod   1/1     Running   0          5m7s   10.244.2.2   kind-worker   <none>           <none>
  ```

**Running a specific command in a running container:**
  ```

sh
  $ kubectl exec nginx-pod -- hostname
  nginx-pod
  ```

**Interactive Shell Session:**
  ```text
  $ kubectl exec -it nginx-pod -- sh
  # hostname
  nginx-pod
  # echo "I am running this from the nginx-pod Pod!"
  I am running this from the nginx-pod Pod!
  ```

## Summary

Pods are the foundational units in Kubernetes, encapsulating applications and providing a robust execution environment. By leveraging Pods effectively, you can take full advantage of Kubernetes' capabilities for deploying, scaling, and managing applications.