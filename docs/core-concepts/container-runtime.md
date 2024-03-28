---
icon: material/circle-small
---

## History

- Originally, Docker was the most popular and thus defacto container runtime that Kubernetes was built to orchestrate
<br><br>

- As Kubernetes grew in popularity, Kubernetes introduced the [Container Runtime Interface](https://kubernetes.io/docs/concepts/architecture/cri/) (CRI) which allowed any runtime to be used as long as they adhered to the [Open Container Initiative](https://opencontainers.org/) (OCI). There are two main specs to be aware of: 
    - **`imagespec`** - how an image should be built
    - **`runtimespec`** - how a container runtime should be developed  
<br>

- Docker did not support CRI because it was built before the CRI standard was developed<br><br>
- Docker introduced the Docker Shim, which was a “hacky” way to support Docker on Kubernetes without using the CRI<br><br>
- Docker also includes a lot of other features - but notably includes containerd, which *is* OCI compliant and can be run without Docker<br><br>


- As of Kubernetes version `1.24`, Docker Shim support was removed completely, and containerd was used as the default
    - However, all Docker *images* do follow the **`imagespec`** OCI standard, so they can continue to be used on Kubernetes with the containerd runtime

## containerd

- Graduated status member of CNCF that can be installed without Docker itself
- Comes with a CLI tool called `ctr` which is not very user-friendly and mainly used for debugging containerd


*[OCI]: Open Container Initiative
*[CRI]: Container Runtime Interface