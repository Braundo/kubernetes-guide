## The Two Sorts of Pod Isolation
1. **Namespace isolation**: Isolating whole namespaces from one another.
2. **Pod isolation**: More granular control, isolating individual pods.


## The NetworkPolicy Resource
- Defines how pods are allowed to communicate with each other and other network endpoints.
- PodSelector targets Pods to apply the policy.
- PolicyTypes specifies what types of traffic are affected.


## Behavior of to and from Selectors
- ingress and egress rules can be set.
- Rules can be as specific as "allow traffic from these IPs" or "allow traffic from Pods with these labels."


## Default Policies
- Policies that apply when no other policies do.


## Default Deny All Ingress Traffic
- Blocks all incoming traffic to Pods unless it matches a NetworkPolicy.


## Allow All Ingress Traffic
- Allows all incoming traffic to Pods.


## Default Deny All Egress Traffic
- Blocks all outgoing traffic from Pods unless it matches a NetworkPolicy.


## Allow All Egress Traffic
- Allows all outgoing traffic from Pods.


## Default Deny All Ingress and All Egress Traffic
- Blocks both incoming and outgoing traffic unless they match a NetworkPolicy.


## SCTP Support
- SCTP (Stream Control Transmission Protocol) is supported as a protocol alongside TCP and UDP.


## Targeting a Range of Ports
- NetworkPolicy can target a range of ports instead of a single port.


## Targeting Multiple Namespaces by Label
- NetworkPolicy can target multiple namespaces using namespace labels.


## Targeting a Namespace by its Name
- Specific namespaces can be targeted by their name.


## What You Can't Do with Network Policies (at least, not yet)
- Limitations like not being able to enforce egress based on DNS names, or not being able to limit access based on the protocol's fields.
