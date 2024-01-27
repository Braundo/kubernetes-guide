## What are Containers?
- Technology for packaging an application along with its runtime dependencies.
- Containers are repeatable and standardized, ensuring the same behavior wherever you run them.
- They decouple applications from the underlying host infrastructure, making deployment easier across different cloud or OS environments.
- In a Kubernetes cluster, each node runs the containers that form the Pods assigned to that node.


## Container Images
- A container image is a ready-to-run software package.
- It contains everything needed to run an application: the code, runtime, application and system libraries, and default settings.
- Containers are intended to be stateless and immutable. Changes should be made by building a new image and recreating the container.


## Container Runtimes
- A fundamental component in Kubernetes for running containers effectively.
- Manages the execution and lifecycle of containers within the Kubernetes environment.
- Kubernetes supports container runtimes like containerd, CRI-O, and any other implementation of the Kubernetes CRI (Container Runtime Interface).
- You can allow your cluster to pick the default container runtime for a Pod or specify the RuntimeClass for different settings.

<br/><br/>

``` mermaid
graph TD
    subgraph Host_Infrastructure["Host Infrastructure"]
        OS[Operating System]
        Hardware[Hardware]
    end

    subgraph Kubernetes_Node["Kubernetes Node"]
        Node[Node]
    end

    subgraph Pod["Pod"]
        Container[Container]
    end

    Kubernetes_Node -->|runs on| OS
    OS --> Hardware
    Node --> Pod
    Pod --> Container

    classDef k8s fill:#326ce5,stroke:#fff,stroke-width:2px;
    class OS,Hardware,Node,Pod,Container k8s;


```