## Assigning Pods to Nodes
Automatic Scheduling: By default, Kubernetes automatically schedules Pods to Nodes based on available resources. However, you can override this behavior for specific use-cases.


## Methods for Manual Scheduling
- `nodeSelector`: Simplest form, matches node labels.
- `Affinity and Anti-affinity`: More expressive than nodeSelector.
- `nodeName`: Directly specify the node.
- `Pod Topology Spread Constraints`: Control how Pods are spread across your cluster.



## Node Labels
- Nodes can have labels that you manually attach or that Kubernetes automatically populates.
- Labels can be used for node isolation and security.



## NodeSelector
A field in the Pod spec that specifies node labels to match.



## Affinity and Anti-affinity
- `Node Affinity`: Similar to nodeSelector but more expressive.
- `requiredDuringSchedulingIgnoredDuringExecution`: Hard requirement.
- `preferredDuringSchedulingIgnoredDuringExecution`: Soft requirement.
- `Inter-pod Affinity/Anti-affinity`: Allows you to specify rules based on labels of other Pods, not just node labels.



## Node Affinity Weight
You can assign weights to preferred rules. The scheduler uses these to score nodes.



## Inter-pod Affinity and Anti-affinity
Allows you to specify rules based on labels of other Pods that are already running on the node.



## Practical Use-cases
Useful when used with higher-level objects like ReplicaSets, StatefulSets, and Deployments.



## Example: Redis Cache Deployment
An example is given for a Redis cache where `podAntiAffinity` is used to ensure that no two replicas with the label `app=store` are scheduled on the same node.