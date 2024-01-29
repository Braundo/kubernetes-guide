## kubectl proxy
- Runs on a user's desktop or in a pod.
- Proxies from a localhost address to the Kubernetes API server.
- Uses HTTP for client-to-proxy communication.
- Uses HTTPS for proxy-to-API server communication.
- Locates the API server and adds authentication headers.


## apiserver proxy
- Acts as a bastion built into the API server.
- Connects a user outside of the cluster to cluster IPs that might otherwise be unreachable.
- Runs in the API server processes.
- Uses HTTPS (or HTTP if configured) for client-to-proxy communication.
- Proxy-to-target may use HTTP or HTTPS, depending on available information.
- Can be used to reach a Node, Pod, or Service.
- Performs load balancing when used to reach a Service.


## kube proxy
- Runs on each node.
- Proxies UDP, TCP, and SCTP.
- Does not understand HTTP.
- Provides load balancing.
- Used only to reach services.


## Proxy/Load-balancer in front of API server(s)
- Existence and implementation vary from cluster to cluster (e.g., nginx).
- Sits between all clients and one or more API servers.
- Acts as a load balancer if there are multiple API servers.


## Cloud Load Balancers on external services
- Provided by some cloud providers (e.g., AWS ELB, Google Cloud Load Balancer).
- Created automatically when the Kubernetes service has type LoadBalancer.
- Usually supports UDP/TCP only.
- SCTP support depends on the cloud provider's implementation.

<br/><br/>

!!! note "Proxies have replaced redirect capabilities, which have been deprecated."