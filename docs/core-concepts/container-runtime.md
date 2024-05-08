---
icon: material/circle-small
---

## History

Initially, Docker was the predominant container runtime, integral to Kubernetes' orchestration capabilities. To accommodate a broader range of container technologies, Kubernetes later introduced the Container Runtime Interface (CRI), facilitating integration with any runtime conforming to the Open Container Initiative (OCI) standards, notably the `imagespec` for building images and the `runtimespec` for developing runtimes.
<br>

Despite its popularity, Docker did not initially support CRI, as it predated the standard. To bridge this gap, Docker developed the Docker Shim—a provisional solution for integrating Docker with Kubernetes without full CRI compliance. Docker's ecosystem also includes `containerd`, an OCI-compliant runtime capable of operating independently of Docker.
<br>

Starting with Kubernetes version 1.24, support for Docker Shim was phased out in favor of `containerd`, which became the default runtime. Nonetheless, Docker images remain compatible with Kubernetes due to their adherence to the `imagespec` OCI standard, ensuring seamless operation with `containerd`.
<br>

When Kubernetes introduced the [Container Runtime Interface](https://kubernetes.io/docs/concepts/architecture/cri/) (CRI) it allowed any runtime to be used as long as they adhered to the [Open Container Initiative](https://opencontainers.org/) (OCI). There are two main specs to be aware of: 
- **`imagespec`** - how an image should be built
- **`runtimespec`** - how a container runtime should be developed  
<br>

## containerd

`containerd` has achieved graduated status within the CNCF, highlighting its maturity and stability as a container runtime. It can be installed independently of Docker, providing a streamlined, Docker-free deployment option. While `containerd` includes a command-line tool called `ctr`, this tool is primarily intended for debugging purposes and may not be as user-friendly for general usage. 
<br>


*[OCI]: Open Container Initiative
*[CRI]: Container Runtime Interface