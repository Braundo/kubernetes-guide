## IPv4/IPv6 dual-stack networking
- Enables the allocation of both IPv4 and IPv6 addresses to Pods and Services.
- Enabled by default for Kubernetes clusters starting in version 1.21.


## Supported Features
- Dual-stack Pod networking
- IPv4 and IPv6 enabled Services
- Pod off-cluster egress routing via both IPv4 and IPv6 interfaces


## Prerequisites
- Kubernetes 1.20 or later
- Provider support for dual-stack networking
- A network plugin that supports dual-stack networking


## Configure IPv4/IPv6 dual-stack
- Various flags for kube-apiserver, kube-controller-manager, kube-proxy, and kubelet to set dual-stack cluster network assignments.


## Services
- Can use IPv4, IPv6, or both.
- `.spec.ipFamilyPolicy` can be set to `SingleStack`, `PreferDualStack`, or `RequireDualStack`.
- `.spec.ipFamilies` can be set to define the order of IP families for dual-stack.


## Dual-stack Service configuration scenarios
- Examples provided for various dual-stack Service configurations.


## Dual-stack defaults on existing Services
- Existing Services are configured by the control plane to set `.spec.ipFamilyPolicy` to `SingleStack`.


## Service type LoadBalancer
- To provision a dual-stack load balancer, set `.spec.type` to `LoadBalancer` and `.spec.ipFamilyPolicy` to `PreferDualStack` or `RequireDualSactk`.


## Egress traffic
- Enable egress traffic for Pods using non-publicly routable IPv6 addresses through mechanisms like transparent proxying or IP masquerading.


## Windows support
- Dual-stack IPv4/IPv6 networking is supported for pods and nodes with single-family services on Windows.
