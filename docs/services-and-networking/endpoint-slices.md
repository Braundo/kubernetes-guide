## EndpointSlice API
- Provides a scalable and extensible way to track network endpoints in a Kubernetes cluster.
- Automatically created for any Kubernetes Service with a selector.
- Groups network endpoints by protocol, port number, and Service name.


## Address Types
- Supports IPv4, IPv6, and FQDN (Fully Qualified Domain Name).


## Conditions
- Three conditions: `ready`, `serving`, and `terminating`:
- `ready` maps to a Pod's Ready condition.
- `serving` is for pod readiness during termination.
- `terminating` indicates whether an endpoint is terminating.


## Topology Information
- Includes the location of the endpoint, Node name, and zone.


## Management
- Mostly managed by the control plane's endpoint slice controller.
- Label `endpointslice.kubernetes.io/managed-by` indicates the entity managing an EndpointSlice.


## Ownership
- Owned by the Service they track endpoints for.
- Ownership indicated by an owner reference and a `kubernetes.io/service-name` label.


## EndpointSlice Mirroring
- Mirrors custom Endpoints resources to EndpointSlices unless certain conditions are met.


## Distribution of EndpointSlices
- Tries to fill EndpointSlices as full as possible but does not actively rebalance them.
- Prioritizes limiting EndpointSlice updates over a perfectly full distribution.


## Duplicate Endpoints
- Endpoints may be represented in more than one EndpointSlice due to the nature of EndpointSlice changes.


## Comparison with Endpoints
- EndpointSlices offer better scalability and extensibility compared to the original Endpoints API.
