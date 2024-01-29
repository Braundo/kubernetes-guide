## Terminology
- **Edge Router**: A router that enforces the firewall policy for your cluster.
- **Cluster Network**: A set of links, logical or physical, that facilitate communication within a cluster.


## What is Ingress?
- Manages external access to services within a cluster.
- Typically provides HTTP and HTTPS routes.
- Can provide load balancing, SSL termination, and name-based virtual hosting.


## Prerequisites
- Must have an Ingress controller to satisfy an Ingress.
- Basic workflow: Create an Ingress object -> Ingress controller configures the load balancer.


## The Ingress Resource
- Mainly composed of a set of rules based on hostnames and paths.
- API object that manages external access to services.


## Ingress Rules
- Define how to route traffic by hostnames and paths.
- Each rule has one or more HTTP paths, each forwarding to a defined backend.


## DefaultBackend
- An addressable Kubernetes Service to handle all requests not matching any path in the Ingress rules.
- Serves as a catch-all for undefined routes.


## Resource Backends
- A feature to forward traffic to resources other than Kubernetes Services.
- Can be used to route traffic to a custom resource.


## Path Types
- Defines how to match requests based on their paths.
- Types: `Exact`, `Prefix`, and `ImplementationSpecific`.


## Hostname Wildcards
- Allows for the routing of HTTP traffic based on wildcards in hostnames.
- E.g., `.foo.com` routes to a specific service.


## Ingress Class
- Allows you to configure multiple Ingress controllers.
- Each controller is identified by a unique class.


## IngressClass Scope
- Defines the scope of a particular Ingress class.
- Can be either cluster-wide or namespaced.


## Deprecated Annotation
- Annotations for specifying ingress class are deprecated.
- Replaced by the ingressClassName field in the Ingress spec.


## Default IngressClass
- Specifies the ingress class to use when none is defined.
- Configured through a cluster-wide setting.


## Types of Ingress
- **Single Service Ingress**: Simplest kind, routes everything to one Service.
- **Simple fanout**: Routes traffic from a single IP address to more than one Service.
- **Name-based virtual hostin**g: Routes traffic on multiple hostnames to different services.


# Ingress Controllers


## Introduction
- Ingress controllers are essential for the functioning of an Ingress resource in a Kubernetes cluster.
- Unlike other controllers, Ingress controllers are not started automatically and must be set up manually.


## Supported Controllers
- Kubernetes officially supports and maintains AWS, GCE, and nginx ingress controllers.

## Additional Controllers
- Various third-party ingress controllers like AKS Application Gateway, Apache APISIX, Avi Kubernetes Operator, and many others are available.


## Using Multiple Ingress Controllers
- You can deploy multiple ingress controllers in a cluster using ingress class.
- The `.metadata.name` of the ingress class resource is important when creating an Ingress object.


## Default IngressClass
- If an Ingress object doesn't specify an IngressClass and there's exactly one IngressClass marked as default, Kubernetes applies the default IngressClass.
- An IngressClass is marked as default by setting the i`ngressclass.kubernetes.io/is-default-class` annotation to `true`.


## Controller Specifications
- While all ingress controllers should ideally fulfill the Kubernetes specification, they may operate differently.