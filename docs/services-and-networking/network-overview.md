## The Kubernetes Network Model
- Every Pod gets a unique cluster-wide IP address.
- Pods can communicate with all other pods on any node without NAT.
- Agents on a node can communicate with all pods on that node.
- "IP-per-pod" model: Containers within a Pod share their network namespaces, including their IP and MAC addresses.


## Kubernetes Networking Concerns
- Containers within a Pod communicate via loopback.
- Cluster networking enables communication between different Pods.
- The Service API exposes applications running in Pods to be reachable from outside the cluster.
- Ingress provides extra functionality for exposing HTTP applications, websites, and APIs.


# Service
- Exposes an application running in the cluster behind a single outward-facing endpoint.


## Ingress
- Makes HTTP (or HTTPS) network service available using a protocol-aware configuration mechanism.


## Ingress Controllers
- Required for an Ingress to work in the cluster.


## EndpointSlices
- Allows the Service to scale to handle large numbers of backends.


## Network Policies
- Controls traffic flow at the IP address or port level.


## DNS for Services and Pods
- Workloads can discover Services within the cluster using DNS.


## IPv4/IPv6 dual-stack
- Supports single-stack IPv4, single-stack IPv6, or dual-stack networking.


## Topology Aware Routing
- Helps keep network traffic within the zone where it originated.


## Service Internal Traffic Policy
- Keeps network traffic within the node if two Pods in the cluster are running on the same node.
