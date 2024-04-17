---
icon: material/circle-small
---

## Understanding High Availability (HA) in Kubernetes

**Impact of Losing a Master Node:**

In a Kubernetes cluster, the loss of a Master node impacts the control plane's ability to manage workloads. While applications running on worker nodes will continue to operate, there will be no capability to start new Pods, restart failed Pods, or perform rolling updates until the control plane is restored. This limitation underscores the need for a High Availability (HA) configuration to ensure continuous management capabilities.

## High Availability Components
**API Server in Active-Active Mode:**

The API Server, the core component that receives all REST requests for modifications and queries to the cluster state, can operate in an Active-Active configuration across multiple master nodes. This setup enhances availability and load balancing by distributing API requests among several servers.
<br><br>

**Controller Manager and Scheduler:**

These critical components, which observe cluster state changes and make decisions to manage the workload, typically run in an Active-Standby mode to prevent dual operations which could lead to conflicts or duplicated efforts. Kubernetes uses a leader election mechanism to determine which node should be active, ensuring that only one instance of each component makes decisions at any time.


## ETCD High Availability

**ETCD Topologies:**

- **Stacked Topology**: In this configuration, ETCD runs directly on the master nodes, alongside other control plane components. This setup simplifies management but can increase the risk of resource contention.
- **External Topology**: Alternatively, ETCD can operate on dedicated external servers. This arrangement isolates ETCD from the Kubernetes control plane, potentially enhancing performance and reliability by reducing load on the master nodes.
<br><br>

**ETCD Consistency Model:**

ETCD, a key-value store that holds the cluster's state, ensures data consistency across its instances through a leader election process. When write operations occur:

- Only the leader node processes the write initially.
- The leader then replicates the data to follower nodes.
- A write is considered successful only once a majority of nodes have stored the update.

This model helps maintain data integrity and state consistency, even if individual ETCD nodes experience disruptions.

## Configuring a Load Balancer for HA

To achieve HA for the API Servers, it is common practice to place a load balancer in front of the API server endpoints. The load balancer distributes incoming traffic across all available API servers to ensure even load distribution and improve fault tolerance. When configuring your `kubeconfig`, you should point to the load balancer's IP or DNS name instead of individual API servers:
```yaml
clusters:
- cluster:
    certificate-authority: ca.crt
    server: https://<load-balancer-DNS>:6443
  name: kubernetes-cluster
```
This setup ensures that the Kubernetes client (kubectl) and other components always connect through the highly available load balancer.
