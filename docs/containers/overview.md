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
A simple way to think about the relationship of containers and Kubernetes is that each **node** can run multiple **pods**, which in turn each run a single **container** (typically).

``` mermaid
graph TD
    Node[Node] --> Pod1[Pod]
    Node --> Pod2[Pod]
    Node --> Pod3[Pod]
    Node --> Pod4[Pod]

    Pod1 --> Container1[Container]
    Pod2 --> Container2[Container]
    Pod3 --> Container3[Container]
    Pod4 --> Container4[Container]

    style Node fill:#f9f,stroke:#333,stroke-width:4px
    style Pod1 fill:#bbf,stroke:#333,stroke-width:2px
    style Pod2 fill:#bbf,stroke:#333,stroke-width:2px
    style Pod3 fill:#bbf,stroke:#333,stroke-width:2px
    style Pod4 fill:#bbf,stroke:#333,stroke-width:2px
    style Container1 fill:#88f,stroke:#333,stroke-width:1px
    style Container2 fill:#88f,stroke:#333,stroke-width:1px
    style Container3 fill:#88f,stroke:#333,stroke-width:1px
    style Container4 fill:#88f,stroke:#333,stroke-width:1px

```