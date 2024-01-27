## Container Environment
- The Kubernetes Container environment provides several important resources to Containers:
    - **Filesystem**: A combination of an image and one or more volumes.
    - **Container Information**: Information about the Container itself.
    - **Cluster Information**: Information about other objects in the cluster.


## Container Information
- The hostname of a Container is the name of the Pod in which the Container is running. This can be accessed through the hostname command or the gethostname function call in `libc`.
- The Pod name and namespace are available as environment variables through the downward API.
- User-defined environment variables from the Pod definition are also available to the Container, as are any environment variables specified statically in the container image.


## Cluster Information
- A list of all services running when a Container was created is available to that Container as environment variables.
- This list is limited to services within the same namespace as the new Container's Pod and Kubernetes control plane services.
- For a service named `foo` that maps to a Container named `bar`, variables like `FOO_SERVICE_HOST` and `FOO_SERVICE_PORT` are defined.
- Services have dedicated IP addresses and are available to the Container via DNS if the DNS addon is enabled.
