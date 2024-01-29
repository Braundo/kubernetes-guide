## Framework Workflow
Scheduling Cycle & Binding Cycle: The scheduling cycle selects a node for the Pod, and the binding cycle applies that decision to the cluster. These cycles can run serially or concurrently.


## Extension Points
The framework offers various extension points where scheduler plugins can register. These include:
- `PreEnqueue`: Called before adding Pods to the internal active queue.
- `QueueSort`: Used to sort Pods in the scheduling queue.
- `PreFilter`: Pre-processes info about the Pod or checks conditions.
- `Filter`: Filters out nodes that cannot run the Pod.
- `PostFilter`: Called when no feasible nodes were found.
- `PreScore`: Performs "pre-scoring" work.
- `Score`: Ranks nodes that have passed the filtering phase.
- `NormalizeScore`: Modifies scores before final ranking.
- `Reserve`: Notifies plugins when resources are being reserved and unreserved.
- `Permit`: Prevents or delays the binding to the candidate node.
- `PreBind`: Performs work required before a Pod is bound.
- `Bind`: Binds a Pod to a Node.
- `PostBind`: Called after a Pod is successfully bound.


## Plugin API
- Plugins must first register and get configured.
- They then use the extension point interfaces, which have a specific form.



## Plugin Configuration
- You can enable or disable plugins in the scheduler configuration.
- Most scheduling plugins are enabled by default in Kubernetes v1.18 or later.
- You can also implement your own scheduling plugins.