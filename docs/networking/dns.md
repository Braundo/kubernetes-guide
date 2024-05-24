---
icon: material/circle-small
---

## Service Discovery
As we saw in the previous sections, Kubernetes can be a very busy platform with Pods constantly coming and going. Services help calm some of the storm by providing a stable endpoint for clients to connect to. But *how* do apps find other apps on a cluster? Through Service discovery! There are two main concepts that make up Service discovery as a whole: *Registration* and *Discovery*.

### Service registration
This is the process of an app on Kubernetes providing its connection details to a registry in order for other apps on the cluster to be able to find it. This happens automatically when Services are created.  

As briefly mentioned in the previous section, Kubernetes provides its own DNS service (typically referred to as the *cluster DNS*). It's deployed as a series of Pods managed by a Deployment called `coredns`. These Pods are behind a Service called `kube-dns`. All of these reside within the `kube-system` Namespace.  

Every Service created on a Kubernetes cluster will automatically register itself with the cluster DNS to ensure that all Pods across the cluster can "find" it.

![service](../../images/svc-2.svg)
<br/><br/><br/>
**The high-level flow of Service registration is as follows:**  

1. Post a Service manifest to the API server (via `kubectl`)
1. The Service is given a stable IP address called a **ClusterIP**
1. EndpointSlices are created to maintain the list of healthy Pods which match the Service's label selector
1. The Service's name and IP are registered with the cluster DNS.  

It's worth noting that cluster DNS implements its own controller which constantly watches the API server for new Services being created. When a new one is observed, it automatically creates the DNS records mappings - meaning neither applications nor Services need to perform their own Service registration.  

Every Node's `kube-proxy` also watches the API server for new EndpointSlices and creates local networking rules when one is observed. This helps with redirecting ClusterIP traffic to Pod IPs.

### Service Discovery
The best way to explain discovery is likely through an example. So let's assume we have two applications on the same cluster - `ham` and `eggs`. Each application has their Pods fronted by a Service, which in turn each have their own ClusterIP.

``` shell title="$ kubectl get svc"
NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
ham-svc   ClusterIP     192.168.1.200               443/TCP   5d19h
eggs-svc  ClusterIP     192.168.1.208               443/TCP   5d19h
```

In order for the `ham` application to communicate with the `eggs` application, it needs to know two things:  

1. The *name* of the `eggs` application's Service (`eggs-svc`)
1. How to convert that name to an IP address

In the case of #1, it's the responsibility of the application developers to know which applications they need to communicate with. Kubernetes internal DNS handles point #2.  

As mentioned above, Kubernetes automatically configures each container in the cluster to be able to resolve the IP address of the *cluster DNS Service*. It also appends any relevant search domains to unqualified names. It performs these actions by populating the `/etc/resolv.conf` on every container.  

ClusterIPs exist on their own special Service network, so it takes a bit of work for traffic to get there. One thing to note is that every Node in a cluster has a `kube-proxy` controller that creates IPVS rules any time a new Service is created. The steps that occur after an application attempts to communicate with another application on the cluster is a series of routing steps that can be summarized as follows:

1. The application container's default gateway routes the traffic to the **Node** it is running on.
1. The Node itself does not have a route to the Service network so it routes the traffic to the **node kernel**.
1. The Node kernel recognizes traffic intended for the service network (recall the IPVS rules) and routes the traffic to a healthy Pod that matches the label selector of the Service.  


## Namespaces
A key point in understanding cluster DNS is knowing that Namespaces are able to partition a cluster's address space. Cluster address spaces are typically denoted as `cluster.local` and then have object names prepended to it. For instance, the `ham-svc` Service from above exists in the default Namespace and would have an FQDN of `ham-svc.default.svc.cluster.local`.  

Now imagine you wanted to partition the cluster domain further with `perf` and `qa` Namespaces. For a `ham-svc` Service in each of those Namespaces, the address would look as follows:

- **Perf**: `ham-svc.perf.svc.cluster.local`
- **QA**: `ham-svc.qa.svc.cluster.local`

Objects within the **same Namespace** can connect to each other using short names. However, cross-Namespace communication must use the FQDN. To visualize this, take the following setup where we have a Service in each Namespace fronting a few Pods:

![service](../../images/dns.svg)

For the `salt` Pod to communicate with the `ham-svc` Service, it can simply reference it by it's short name (`ham-svc`) since they are within the *same* `perf` Namespace.  

However, for `salt` to communicate with the `eggs-svc` Service, which resides in the `qa` Namespace, it would have to leverage it's FQDN: `eggs-svc.qa.svc.cluster.local`.

*[IPVS]: IP Virtual Server
*[FQDN]: Fully Qualified Domain Name
