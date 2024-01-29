## Motivation
- Designed for multi-zone environments.
- Aims to keep network traffic within the originating zone for reliability, performance, and cost.


## Enabling Topology Aware Routing
- Enabled by setting the `service.kubernetes.io/topology-mode` annotation to `Auto`.
- EndpointSlices will have Topology Hints populated to allocate endpoints to specific zones.


## When it works best
- Even distribution of incoming traffic.
- Service has 3 or more endpoints per zone.


## How It Works
- "Auto" heuristic proportionally allocates endpoints to each zone.
- EndpointSlice controller sets hints based on allocatable CPU cores in each zone.


## EndpointSlice controller
- Responsible for setting hints on EndpointSlices.
- Allocates endpoints based on the allocatable CPU cores for nodes in each zone.


## kube-proxy
- Filters endpoints based on hints set by the EndpointSlice controller.
- Sometimes allocates endpoints from different zones for even distribution.


## Safeguards
- Several rules to ensure safe use of Topology Aware Hints.
- If rules aren't met, `kube-proxy` selects endpoints from anywhere in the cluster.


## Constraints
- Not used when `internalTrafficPolicy` is set to `Local`.
- Does not work well for Services with traffic originating from a subset of zones.
- Does not account for unready nodes or nodes with specific labels.


## Custom heuristics
- Allows for custom heuristics if the built-in ones don't meet specific use cases.