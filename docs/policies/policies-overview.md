## API Objects as Policies
- **NetworkPolicies**: Restrict ingress and egress traffic for workloads.
- **LimitRanges**: Manage resource allocation constraints across different object kinds.
- **ResourceQuotas**: Limit resource consumption for a namespace.


## Admission Controllers
- These run in the API server and can validate or mutate API requests.
- Example: The `AlwaysPullImages` admission controller modifies a new Pod to set the image pull policy to `Always`.
- Kubernetes has several built-in admission controllers that are configurable via the API server `-enable-admission-plugins` flag.


## ValidatingAdmissionPolicy
- Allows configurable validation checks to be executed in the API server using the Common Expression Language (CEL).
- Can be used to block, audit, and warn users about non-compliant configurations.


## Dynamic Admission Control
- These controllers run outside the API server as separate applications.
- They can perform complex checks, including those that require retrieval of other cluster resources and external data.
- Example: An image verification check can look up data from OCI registries to validate container image signatures and attestations.


## Kubelet Configurations
- Some Kubelet configurations act as policies, such as Process ID limits and reservations, and Node Resource Managers.


## Implementation
- Dynamic Admission Controllers that act as flexible policy engines are being developed in the Kubernetes ecosystem. Some examples are Kubewarden, Kyverno, OPA Gatekeeper, and Polaris.