``` mermaid
graph TB
    subgraph Kubernetes Control Plane
        cm[Cloud Controller Manager]
        api[API Server]
        etcd[(ETCD)]
        cm -->|interacts with| api
        api --> etcd
    end

    subgraph Cloud Infrastructure
        nodeController[Node Controller]
        routeController[Route Controller]
        serviceController[Service Controller]
        cloudResources[Cloud Resources]
        nodeController --> cloudResources
        routeController --> cloudResources
        serviceController --> cloudResources
    end

    cm -->|manages| nodeController
    cm -->|manages| routeController
    cm -->|manages| serviceController

    classDef k8s fill:#326ce5,stroke:#fff,stroke-width:2px;
    class cm,nodeController,routeController,serviceController k8s;

```

## Cloud Controller Manager
- A Kubernetes control plane component that embeds cloud-specific control logic.
- Decouples the interoperability logic between Kubernetes and underlying cloud infrastructure.
- Allows cloud providers to release features at a different pace compared to the main Kubernetes project.


## Design
- Runs in the control plane as a replicated set of processes, usually as containers in Pods.
- Implements multiple controllers in a single process.


## Node Controller
- Updates Node objects when new servers are created in the cloud infrastructure.
- Annotates and labels the Node object with cloud-specific information.
- Verifies the node's health and deletes the Node object if the server has been deleted from the cloud.


## Route Controller
- Configures routes in the cloud so that containers on different nodes can communicate.
- May also allocate blocks of IP addresses for the Pod network.


## Service Controller
- Integrates with cloud infrastructure components like managed load balancers and IP addresses.
- Sets up load balancers and other infrastructure when a Service resource requires them.


## API Object Access
- Requires specific access levels to various API objects like Node, Service, and Endpoints.
- For example, full access to read and modify Node objects, and list and watch access to Service objects.


## RBAC ClusterRole
- Defines the permissions required for the cloud controller manager, such as creating events and service accounts.
