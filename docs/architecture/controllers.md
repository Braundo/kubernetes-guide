## Control Loop
- A non-terminating loop that regulates the state of a system.
- Example: A thermostat in a room that adjusts the temperature to reach the desired state.


## Controller Pattern
- Tracks at least one Kubernetes resource type.
- Responsible for making the current state align with the desired state specified in the resource's spec field.


## Control via API Server
- Controllers interact with the cluster API server to manage state.
- Example: The Job controller creates or removes Pods via the API server to complete a task.


## Direct Control
- Some controllers interact with external systems to achieve the desired state.
- Example: A controller that scales the number of nodes in a cluster by interacting with cloud provider APIs.


## Desired vs. Current State
- Kubernetes aims for a cloud-native approach, handling constant change.
- Controllers work to bring the current state closer to the desired state, even if the cluster is never in a stable state.


## Design Principles
- Kubernetes uses multiple controllers for different aspects of cluster state.
- Allows for resilience, as one controller can take over if another fails.


## Ways of Running Controllers
- Built-in controllers run inside the kube-controller-manager.
- Custom controllers can run either inside or outside the Kubernetes cluster.
