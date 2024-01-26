## What are nodes?
- Worker machines in a Kubernetes cluster.
- Run containerized applications managed by the Control Plane.
- Equipped with a Kubelet agent that communicates with the master components.



## Control Plane vs Worker Nodes
- Nodes are managed by master components, primarily the *Control Plane*.
- Operations include adding nodes, updating node software, and decommissioning nodes.
``` mermaid
stateDiagram-v2
    state control_plane {
        kube_apiserver
        kube_apiserver --> etcd: stores data
        kube_apiserver --> kube_controller_manager: watches changes
        kube_apiserver --> scheduler: finds placement
        scheduler --> kube_apiserver: watches for pods needing scheduled
        kube_controller_manager
    }

    state worker_nodes {
        kubelet
        kubelet --> kube_proxy: configures networking
        kubelet --> container_runtime: runs containers
        kube_proxy --> iptables_BPF: manages networking rules
        container_runtime
    }

    control_plane --> worker_nodes: manages
    worker_nodes --> control_plane: reports

```
> Don't worry if some of these components don't make sense - we'll get to them in later sections.

## Node Name Uniqueness
- Each node must have a unique identifier within the cluster.
- Ensures accurate scheduling and task allocation.


## Self-registration of Nodes
- Nodes can automatically register themselves upon joining the cluster.
- Facilitates dynamic scaling and resource allocation.


## Manual Node Administration
- Admins can manually add or remove nodes using the Kubernetes API or CLI tools.
- Useful for fine-grained control over the cluster.


## Node Status
- Provides detailed information about the node, including IP addresses, conditions (`Ready`, `OutOfDisk`, etc.), and resource capacity.
- Updated periodically by the node's Kubelet.


## Node Heartbeats
- Regular signals sent from the Kubelet to the master to indicate the node's health.
- Failure to send a heartbeat within a certain time leads to node eviction.


## Node Controller
- A Control Plane component responsible for monitoring nodes.
- Handles node failures and triggers pod evictions if necessary.


## Rate Limits on Eviction
- Configurable settings that control the speed at which pods are evicted from unhealthy nodes.
- Helps to avoid overwhelming the remaining healthy nodes.


## Resource Capacity Tracking
- Nodes report available resources like CPU, memory, and storage for better scheduling.
- Helps the scheduler in placing pods where resources are available.


## Node Topology
- Information about the physical or virtual layout of nodes in terms of regions, zones, and other cloud-provider specific metadata.
- Used for optimizing workload distribution and high availability.


## Graceful Node Shutdown
- A process that safely evicts pods before shutting down or rebooting a node.
- Ensures minimal impact on running applications and services.


## Pod Priority based Graceful Node Shutdown
- During a graceful shutdown, pods with higher priority are evicted last.
- Ensures that critical applications continue to run for as long as possible.


## Non-graceful Node Shutdown Handling
- In cases of abrupt failures, all pods are immediately terminated.
- Risks include data loss and potential service disruption.


## Swap Memory Management
- Kubernetes allows for the enabling or disabling of swap memory usage on nodes.
- Swap usage can impact application performance and pod scheduling decisions.