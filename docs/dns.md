---
icon: material/dns
---

## Service Discovery
As we saw in the previous section, Kubernetes can be a very busy platform with Pods constantly coming and going. Services help calm some of the storm by providing a stable endpoint for clients to connect to. But *how* do apps find other apps on a cluster? Through Service discovery! There are two main concepts that make up Service discovery as a whole: *Registration* and *Discovery*.

### Service registration
This is the process of an app on Kubernetes providing its connection details to a registry in order for other apps on the cluster to be able to find it. This happens automatically when Services are created.  

As briefly mentioned in the previous section, Kubernetes provides its own DNS service (typically referred to as the *cluster DNS*). It's deployed as a series of Pods managed by a Deployment called `coredns`. These pods are behind a Service called `kube-dns`. All of these reside within the `kube-system` Namespace.  

Every Service created on a Kubernetes cluster will automatically register itself with the cluster DNS to ensure that all Pods across the cluster can "find" it.

``` mermaid
flowchart LR
    SVC[<b>Service</b><br><tt>foo-svc<br>10.0.0.8]
    SVC --> |1. Register Service| REG[<b>Service registry</b><br><tt>foo-svc: 10.0.0.8]
    CON[<tt>app] --> |2. Discover Service| REG
    CON --> |3. Consume Service| SVC
```
<br/><br/><br/>
**The high-level flow of Service registration is as follows:**  

1. Post a Service manifest to the API server (via `kubectl`)
1. The Service is given a stable IP address called a **ClusterIP**
1. EndpointSlices are created to maintain the list of healthy Pods which match the Service's label selector
1. The Service's name and IP are registered with the cluster DNS.  

It's worth noting that cluster DNS implements its own controller which constantly watches the API server for new Services being created. When a new one is observed, it automatically creates the DNS records mappings - meaning neither applications nor Services need to perform their own service registration.  

Every node's `kube-proxy` also watches the API server for new EndpointSlices and creates local networking rules when one is observed. This helps with redirecting ClusterIP traffic to Pod IPs.

### Service Discovery

To be populated...