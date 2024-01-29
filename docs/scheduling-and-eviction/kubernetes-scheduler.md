## Scheduling Overview
- **Role of Scheduler**: The scheduler watches for newly created Pods that have no Node assigned and is responsible for finding the best Node for each Pod.
- **Scheduling Principles**: The scheduler takes into account various factors like resource requirements, hardware/software constraints, affinity and anti-affinity rules, etc., to make the scheduling decision.


## kube-scheduler
- **Default Scheduler**: `kube-scheduler` is the default scheduler in Kubernetes and is part of the control plane.
- **Customization**: It's designed to allow you to write your own scheduling component if needed.
- **Feasible Nodes**: Nodes that meet the scheduling requirements for a Pod are called feasible nodes. If no nodes are suitable, the Pod remains unscheduled.
- **Scoring**: After filtering feasible Nodes, the scheduler scores them based on a set of functions and picks the Node with the highest score to run the Pod.


## Node Selection
Two-Step Operation: Node selection is done in two steps: Filtering and Scoring:  

1. **Filtering**: This step finds the set of Nodes where it's feasible to schedule the Pod. For example, it checks if a Node has enough resources to meet the Pod's requirements.
2. **Scoring**: In this step, the scheduler ranks the remaining Nodes based on active scoring rules.


## Configuring the Scheduler
- **Scheduling Policies**: These allow you to configure predicates for filtering and priorities for scoring.
- **Scheduling Profiles**: These allow you to configure plugins that implement different scheduling stages like `QueueSort`, `Filter`, `Score`, `Bind`, `Reserve`, `Permit`, etc.
