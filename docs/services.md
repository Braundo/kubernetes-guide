---
icon: material/sitemap
---

## Overview
As mentioned in the [Deployments section](./deployments.md), Pods will likely be spinning up and down *a lot* in your environment throughout the course of updates, rollbacks, failures, etc. As such, it's never a good idea for any client to connect directly to a Pod. Pods are there one minute, gone the next - awfully unreliable in and of themselves.  

This is where Services come in. Services provide stable, long-lived connection points for clients to connect to. They also maintain a list of Pods to route to and provide basic load-balancing capabilities. With Services, the underlying Pods can come and go, but any client should be able to maintain open communication with the application as the Service provides the logic to know which Pods are healthy and where to route traffic.  

``` mermaid
flowchart LR
    client --> SVC[Service]
    SVC --> Pod1[Pod]
    SVC --> Pod2[Pod]
    SVC --> Pod3[Pod]
    SVC --> Pod4[Pod]

    subgraph Deployment
        Pod1
        Pod2
        Pod3
        Pod4
    end
```

## Labels and Selectors
So how does that work? How do Services know which Pods they should be sending traffic to? The short answer is **labels** and **selectors**. In essence, when you define a Service, you specify labels and selectors that - when matched with the same ones on Pods - will route traffic to them.  

As an example, image you want to put a stable Service in front of series of Pods that make up your shopping application. When you defined the Deployment of the application you listed the following labels and selectors for the Pods: `env=prod` and `app=shop`. Now, when you set up this new Service, you used those same labels in it's YAML definition. The new Service will find all Pods on the cluster with those same labels and is now in charge of routing traffic to them.  

Similar to other Kubernetes objects, the Services controller will continually monitor new Pods labels and continually update it's "list" (more on that list later) of Pods to route to.  

``` mermaid
flowchart LR
    SVC[<b>Service</b><tt><br>env=prod<br>app=shop] --> Pod1[<b>Pod</b><tt><br>env=prod<br>app=shop]
    SVC --> Pod2[<b>Pod</b><tt><br>env=prod<br>app=shop]
    SVC --> Pod3[<b>Pod</b><tt><br>env=prod<br>app=shop]
    SVC -.- |X|Pod4[<b>Pod</b><tt><br>env=dev<br>app=shop]
```

One thing to note is that Pods *can* have extra labels and still be managed by the Service if it's other labels still match. As a concrete example, both of the Pods below will still have traffic routed to them, even though one of them has a label that the Service does not.

``` mermaid
flowchart LR
    SVC[<b>Service</b><tt><br>env=prod<br>app=shop] --> Pod1[<b>Pod</b><tt><br>env=prod<br>app=shop<br>cur=usd]
    SVC --> Pod2[<b>Pod</b><tt><br>env=prod<br>app=shop]
```

## EndpointSlices
As mentioned above, as Pods are spinning up and down, the Service will keep an updated list of Pods with the given labels and selectors. How it does this is through the use of **EndpointSlices**, which are effectively just dynamic lists of healthy Pods that match a given label selector.  

Any new pods that are created on the cluster that match a Service's label selector will automatically be added to the given Service's EndpointSlice object. When a Pod disappears (fails, node goes down, etc.) it will be removed from the EndpointSlice. The net result is that the Service's EndpointSlice should always be up to date with a list of healthy pods that the Service can route to.  

## Service Types
#### ClusterIP
Kubernetes supports different types of Services, but the default type is **ClusterIP**, which is only accessible from *inside* the cluster. Any time you create a Service in Kubernetes it will automatically get a ClusterIP that's registered in the cluster's internal DNS service (more on the DNS service in a different section). Every single Pod on a cluster leverages the cluster's DNS service - which results in all Pods being able to resolve Service names to ClusterIPs.  

#### NodePort
Another type of Service that Kubernetes supports is called **NodePort**. This is very similar to ClusterIP but adds the ability for external access on a dedicated port on every node in the cluster. NodePort intentionally uses high-numbered ports (30000 - 32767) to avoid clashing with common ports. To access a NodePort Service from an external client, you simply direct traffic to the IP address of *any node* in the cluster on the given port. The Service will then route the request to the appropriate Pod based on it's list of healthy ones in it's EndpointSlice object.

#### LoadBalancer
If you're running your Kubernetes cluster on a public cloud environment you can leverage a **LoadBalancer** Service. This will provision an internet-facing load-balancer that you can leverage to send traffic to your Service. For more specifics on this type of Service, refer to [the official Kubernetes documentation](https://kubernetes.io/docs/concepts/services-networking/service/#loadbalancer).