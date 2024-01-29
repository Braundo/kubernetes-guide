## SchedulingGates
- **What It Is**: `SchedulingGates` is a new field in the Pod specification. It's an array of strings, where each string represents a condition that the Pod must meet before it can be scheduled.

- **Immutability**: Once a Pod is created with `SchedulingGates`, you can't add new gates to it. However, you can remove existing ones to make the Pod schedulable.

- **Use Case**: Imagine you have a multi-stage deployment process where a Pod needs to pass some pre-conditions before it can be scheduled. You can use `SchedulingGates` to ensure that the Pod only gets scheduled after these conditions are met.


## Observability
- **New Metrics Label**: The `scheduler_pending_pods` metric now includes a "gated" label. This helps in monitoring Pods that are intentionally not being scheduled due to `SchedulingGates`.

- **Monitoring**: This feature allows for better observability into why certain Pods are not being scheduled, making it easier to debug issues related to Pod scheduling.


## Mutable Pod Scheduling Directives
- **What It Is**: Starting from Kubernetes v1.27, you can change the scheduling directives of a Pod even if it has `SchedulingGates`.

- **Constraints**: The catch is that you can only "tighten" the scheduling directives. This means you can make them more restrictive, but not more permissive. For example, if a Pod was initially set to be scheduled on nodes with a certain label, you can change it to only be scheduled on nodes with that label and an additional condition.

- **Use Case**: This is useful in scenarios where you might need to adjust the scheduling conditions of a Pod due to changes in cluster state or workload requirements, without having to delete and recreate the Pod.