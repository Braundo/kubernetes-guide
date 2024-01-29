## Resource Management for Pods and Containers
In Kubernetes, each container in a Pod can have its resource requirements specified, such as CPU and memory. The Kubernetes scheduler (`kube-scheduler`) uses these requirements to decide which node is best suited to run the Pod. The `kubelet` on the node then enforces these limits to ensure the container doesn't use more than it's allocated.


## Requests and Limits
"Requests" are the minimum resources that a container will be allocated. For example, if a container requests 500MB of memory, Kubernetes will only schedule it on a node with at least that much free memory. "Limits," on the other hand, are the maximum resources that a container can use. If a container tries to use more than its limit, it may be terminated or throttled depending on the resource type.


## Resource Types
You can specify various types of resources, but CPU and memory are the most common. "Huge pages" are a Linux feature that allows the kernel to manage memory more efficiently for specific workloads.


## Resource Requests and Limits of Pod and Container
In the Pod specification, you can define the resource requests and limits for each container. The Pod's overall resource request and limit are the sum of its containers' individual requests and limits. This aggregated information is used by the scheduler for Pod placement.


## Resource Units in Kubernetes
CPU resources are usually specified in "millicores," where 1000 millicores equal 1 core. Memory is typically specified in bytes, but you can use suffixes like "Mi" or "Gi" for mebibytes or gibibytes, respectively.


## How Pods with Resource Requests are Scheduled
When you create a Pod with resource requests, the scheduler looks for a node that has enough free resources to meet the Pod's requirements. If no such node exists, the Pod remains in a "Pending" state until resources become available.


## How Kubernetes Applies Resource Requests and Limits
Once a Pod is scheduled, the `kubelet` on the node uses Linux features like cgroups to enforce the resource limits. This ensures that each container only uses the CPU and memory it's allocated.


## Monitoring Compute & Memory Resource Usage
Kubernetes provides various metrics and tools to monitor resource usage. You can use built-in commands like `kubectl top` or deploy monitoring solutions like Prometheus to keep track of how much CPU and memory your Pods are using.


## Local Ephemeral Storage
Ephemeral storage is temporary disk space that a Pod can use during its lifecycle. It's local to the node and is deleted when the Pod is removed. You can specify requests and limits for ephemeral storage similar to CPU and memory.


## Extended Resources
These are custom resources that you can define for specialized hardware or software requirements, such as GPUs or licenses. You can register these resources on nodes and then reference them in your Pod specifications.
