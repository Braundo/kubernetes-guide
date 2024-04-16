---
icon: material/circle-small
---

### Kubernetes Scheduler Overview

The **Scheduler** in Kubernetes is a critical component responsible for assigning Pods to Nodes in the cluster. While the Scheduler decides the placement of Pods, it is the Kubelet on each node that actually places the Pod onto the Node.

<h4>Responsibilities of the Scheduler</h4>

The primary function of the Scheduler is to:
- Evaluate the resource requirements of each Pod.
- Assess the current availability and conditions of the Nodes.
- Assign the Pod to a Node that best meets the Pod’s needs.

<h4>Decision-Making Criteria</h4>

The Scheduler uses a variety of criteria to determine the most suitable Node for a Pod, including:

- **Resource Requirements**: Checks if nodes have the CPU, memory, and storage to meet the Pod's requirements.
- **Application Requirements**: Considers specific demands such as GPU needs or data locality.
- **Quality of Service (QoS)**: Prioritizes Pods based on their QoS class (Guaranteed, Burstable, BestEffort).

<h4>Scheduling Algorithm</h4>

The Scheduler employs a two-phase process consisting of filtering and scoring:

1. **Filtering Phase**: The Scheduler filters out nodes that do not satisfy the Pod’s requirements. Factors considered include:
   - Node capacity.
   - Resource availability.
   - Taints and tolerations.
   - Affinity and anti-affinity specifications.

2. **Scoring Phase**: Nodes that pass the filtering phase are scored on a scale from 0 to 10 based on how well they meet the requirements. The Scheduler considers:
   - Resource utilization and availability.
   - Affinity rules specified in the Pod configuration.
   - Other custom policies that may be configured.

The node with the highest score is selected for the Pod placement. If multiple nodes have the same score, the Scheduler selects one at random.

<h4>Advanced Scheduling</h4>

Advanced scheduling features allow for more complex decision-making:

- **Node Affinity/Anti-Affinity**: Allows specifying rules that a node must or must not meet to host a Pod.
- **Pod Affinity/Anti-Affinity**: Enables placing Pods in proximity to other Pods to meet various operational requirements.
- **Taints and Tolerations**: Nodes can be "tainted" to repel Pods unless they "tolerate" the taint.

### Practical Example: Using Node Affinity

To leverage node affinity, define it in your Pod spec. For instance, to schedule a Pod on a node with a specific feature (like SSDs), your Pod spec might include:

```yaml
...
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - key: kubernetes.io/ebs-volume
              operator: In
              values:
                - ssd
```