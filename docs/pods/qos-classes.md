## Scheduler Behavior
The `kube-scheduler` does not consider QoS class when selecting which Pods to preempt.


## Resource Management
The resource request of a Pod is the sum of the resource requests of its containers, and similarly for the resource limit.


# Behavior Independent of QoS Class
Any container exceeding a resource limit will be killed and restarted, and Pods exceeding resource requests become candidates for eviction.


# Memory QoS with cgroup v2
This feature, in alpha stage as of Kubernetes v1.22, uses the memory controller of cgroup v2 to guarantee memory resources.


## Types of QoS Classes
- **Guaranteed**: These Pods have strict resource limits and are least likely to be evicted.
- **Burstable**: These Pods have some lower-bound resource guarantees but do not require a specific limit.
- **BestEffort**: These Pods can use any available node resources and are the first to be evicted under resource pressure.