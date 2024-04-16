---
icon: material/circle-small
---

## Overview
The Kubernetes API serves as the central nervous system of the platform, orchestrating all interactions within the system. Every operation within Kubernetes, from creating and reading to updating and deleting resources such as Pods and Services, is conducted through requests to the API, which are then processed by the API server. 

While `kubectl` is the go-to command-line tool for sending these requests, they can also be composed programmatically or via specialized API development tools. Regardless of how they're formulated, all requests are funneled to the API server, where they undergo authentication and authorization checks. Once verified, these requests are actioned within the cluster. For instance, a request to create a resource results in its deployment to the cluster, and the object's configuration is then stored in the cluster's datastore. This API-centric design ensures a consistent and secure method for managing the cluster's state and operations.  

``` mermaid
---
title: API request flow
---
flowchart LR
    client["<b>client"] -->
    id1{{"API server<br>auth"}} -->
    api{{"<tt>API"}} -->
    sched{{"<tt>Scheduler"}} -->
    etcd{{"<tt>Cluster<br>store"}}
```  

Communication within Kubernetes relies on serialization, the process of converting objects like Pods and Services into JSON strings for HTTP transmission. This conversion is bidirectional: clients, including kubectl, serialize objects into JSON to make requests, and the API server does likewise when responding. Moreover, Kubernetes stores these serialized states in persistent storage, typically etcd, ensuring the cluster’s state is both maintained and recoverable. 
<br>

Serialization in Kubernetes isn't limited to JSON; it also embraces Protobuf, a schema known for its speed and efficiency, outpacing JSON in performance and scalability. However, Protobuf's complexity makes it less accessible for direct inspection and debugging, which is why it's primarily utilized for internal communications within the cluster, while JSON remains the go-to format for external client interactions.  

To smooth out the serialization process, clients specify their supported formats using the Content-Type header in their HTTP requests. For instance, a client that only understands JSON will declare `Content-Type: application/json`, prompting Kubernetes to respond with data serialized in JSON, adhering to the client's capabilities and preferences.  

Kubernetes is a world of API-defined objects, ranging from the familiar Pods and Services to the traffic-managing Ingresses. All these elements are accessible via the API server, which acts as the gateway for interaction with the cluster. You typically use `kubectl`, the command-line interface, to make requests for these objects. The beauty of Kubernetes extends to its extensibility, allowing third parties to define custom resources that are just as accessible through `kubectl` and the API server.  

When you make a request for an object, the API server springs into action, creating that object within your cluster. But it doesn't just stop there; the API server provides a watch functionality, letting you observe the object as it comes to life. Once the object is up and running, Kubernetes maintains a vigilant watch over it, with the API server offering real-time insight into its current state. Whether you're scaling up with more objects or pruning with deletions, these interactions are all routed through the central hub of the API server.  

``` mermaid
sequenceDiagram
    participant user
    participant kubectl
    participant api-server
    participant etcd

    user->>kubectl: Request Object Creation
    kubectl->>api-server: Create Object
    api-server->>etcd: Serialize and Persist Object
    etcd-->>api-server: Confirm Object Stored
    api-server-->>kubectl: Object Creation Watch
    kubectl-->>user: Object Status Updates
    Note over user,etcd: Object is now ready for use

    user->>kubectl: Query Object State
    kubectl->>api-server: Get Object State
    api-server->>etcd: Retrieve Object Data
    etcd-->>api-server: Object Data
    api-server-->>kubectl: Object State
    kubectl-->>user: Object State Response
```

## API Server
The Kubernetes API server is the central hub through which all interactions in the cluster are routed, functioning as the front-end interface for Kubernetes' API. Picture it as the Grand Central Station of Kubernetes — every command, status update, and inter-service communication passes through the API server via RESTful calls over HTTPS. Here's a snapshot of how it operates:  

- `kubectl` commands are directed to the API server, whether it's for creating, retrieving, updating, or deleting Kubernetes objects.
- Node Kubelets keep an eye on the API server, picking up new tasks and sending back their statuses.
- The control plane services don't chat amongst themselves directly; they communicate through the API server.  

Zooming in on the API server itself, it's part of the Kubernetes control plane services, often running as a Pod set within the kube-system Namespace on the control plane nodes. For those managing their own Kubernetes clusters, ensuring the high availability and robust performance of the control plane is crucial to keep the API server operational. In contrast, for hosted Kubernetes services, these details are abstracted away from the user.  

At its core, the API server's role is to make the Kubernetes API accessible, both to clients within the cluster and to those outside. It secures client connections with TLS encryption and applies various authentication and authorization protocols to vet and process only legitimate requests. All requests, no matter their origin, are subject to the same stringent auth checks.  

The "RESTful" part of the API means it adheres to a modern web API structure that deals with CRUD-style (Create, Read, Update, Delete) requests via standard HTTP methods like `POST`, `GET`, `PUT`, `PATCH`, and `DELETE`.  

Typically, the API server is available on ports 443 or 6443, although these can be configured to suit specific needs. The flexibility of the API server ensures that it can cater to different environments while maintaining strict security and reliable service.  

The following command will show you the address and port your Kubernetes cluster is exposed on:  
``` shell title="$ kubectl cluster-info"
    Kubernetes control plane is running at https://192.168.1.105:6443
    CoreDNS is running at https://192.168.1.105:6443/api/v1/namespaces/...
    Metrics-server is running at https://192.168.1.105:6443/api/v1/namespaces/...
```  

In essence, the Kubernetes API server serves as the gateway to the cluster, offering a secure, RESTful interface for interacting with the cluster's state. Operating from the control plane, it necessitates robust availability and performance to ensure swift and reliable handling of requests, embodying the critical link between the user's commands and the cluster's operational response.

!!! warning "Note"
    The API Server is the **only** component in Kubernetes that interacts directly with etcd.

If you're unfamiliar with REST, [AWS has a great one-pager](https://aws.amazon.com/what-is/restful-api/) to get you up to speed.  


## API
The Kubernetes API is expansive and RESTful, structured to define all Kubernetes resources. Initially, the API was a single, monolithic entity, but as Kubernetes evolved, it transitioned into a more modular form for better manageability, distinguishing between the core group and named groups of API resources.  

**Core API Group:** This group houses the original, fundamental resources such as Pods, Nodes, and Services, accessible under `/api/v1`. These objects, crucial from the early Kubernetes days, have paths that may vary based on whether they are namespaced (e.g., Pods within a specific namespace) or cluster-wide (e.g., Nodes).  

**Named Groups:** Representing the evolution and expansion of the Kubernetes API, named groups contain newer resources organized by functionality. For instance, the "apps" group includes workload-related resources like Deployments and StatefulSets, while "networking.k8s.io" focuses on network aspects such as Ingresses. Unlike the core group, resources in named groups are found under `/apis/{group-name}/{version}/`, reflecting their categorization and versioning.  

This division enhances the API's scalability and navigability, facilitating the introduction of new resources. To explore available resources and their groupings, `kubectl api-resources` provides a comprehensive overview, indicating whether resources are namespaced or cluster-scoped, alongside their shortnames and API group affiliations. This command is instrumental in understanding the API's layout and the scope of resources within a Kubernetes cluster.  

#### Core Group
| Resource | REST Path |
| ----- | ----- |
| Pods | `/api/v1/namespaces{namespace}/pods/` |
| Services | `/api/v1/namespaces/{namespace}services` |
| Nodes | `/api/v1/nodes/` |
| Namespaces | `/api/v1/namespaces` |

#### Named Groups
| Resource | REST Path |
| ----- | ----- |	
| Ingress | `/apis/networking.k8s.io/v1/namespaces/{namespace}/ingresses/` |
| RoleBinding | `/apis/rbac.authorization.k8s.io/v1/namespaces/{namespace}/rolebindings/` |
| ClusterRole | `/apis/rbac.authorization.k8s.io/v1/clusterroles/` |
| StorageClass | `/apis/storage.k8s.io/v1/storageclasses/` |

> Note: This is not all-inclusive, just a few examples.

The `kubectl api-resources` command is a great way to see which API resources are available on your cluster, as well as useful information about them:  

``` shell title="$ kubectl api-resources"
NAME                              SHORTNAMES   APIVERSION     NAMESPACED
bindings                                       v1             true
componentstatuses                 cs           v1             false
ComponentStatus
configmaps                        cm           v1             true
ConfigMap
endpoints                         ep           v1             true
Endpoints
events                            ev           v1             true
limitranges                       limits       v1             true
LimitRange
namespaces                        ns           v1             false
Namespace
nodes                             no           v1             false
persistentvolumeclaims            pvc          v1             true
PersistentVolumeClaim
persistentvolumes                 pv           v1             false
PersistentVolume
```
> Truncated for brevity

In Kubernetes discussions, you might hear "resources," "objects," and "primitives" used as if they're the same. While common usage often blends these terms together, there's a technical distinction worth noting: Kubernetes fundamentally operates on a resource-based API model.  

**What this means:** At its core, the Kubernetes API deals with "resources." These resources are predominantly "objects" like Pods, Services, and Ingresses. Yet, the API isn't limited to objects alone; it also encompasses lists and a select few operations. Given that the bulk of resources are indeed objects, the terms "resource" and "object" are frequently used interchangeably without causing confusion.  

**Scope of Resources:** Kubernetes differentiates between namespaced and cluster-scoped resources. Namespaced resources must reside within a specific Namespace, tailoring their scope and impact to that Namespace. For instance, Pods and Services require a Namespace to exist. Conversely, cluster-scoped resources either span multiple Namespaces or operate outside the Namespace system altogether. Nodes, for example, are cluster-scoped resources existing beyond Namespace boundaries, while ClusterRoles can be tied to specific Namespaces through RoleBindings to apply permissions across the cluster.  

To get a grip on the resources available in your cluster and their scope, `kubectl api-resources` is an invaluable command. It provides a snapshot of all resources, highlighting whether they are namespaced or cluster-scoped, thereby offering insight into how Kubernetes structures and manages its diverse set of resources.  

## Extending the API
Kubernetes offers a powerful framework for managing and automating containerized applications, largely through its predefined set of resources and controllers that observe and manage the state of objects within the cluster. Yet, one of Kubernetes' most compelling features is its extensibility, allowing you to tailor the system to your specific needs by introducing custom resources and controllers.  

**Extending Kubernetes with Custom Resources and Controllers**  
A vivid example of such extensibility can be observed in the storage domain, where third-party vendors integrate advanced functionalities—like snapshot scheduling—directly into Kubernetes through custom resources. While Kubernetes natively supports storage operations through StorageClasses and PersistentVolumeClaims, these custom resources enable the exposure of vendor-specific features within the same Kubernetes ecosystem.

**The Extension Blueprint**  
Extending the Kubernetes API usually involves:

1. **Creating a Custom Controller**: Develop a controller that uses your custom logic to monitor changes to your resources, ensuring the cluster achieves and maintains the desired state.

2. **Defining a Custom Resource**: Utilize Kubernetes' CustomResourceDefinition (CRD) API object to create new resource types. CRDs integrate seamlessly with the Kubernetes API and include their own RESTful paths. Once established, manage these resources with kubectl as you would with standard resources, thus maintaining a consistent Kubernetes experience.


This approach not only enriches the Kubernetes ecosystem with new functionalities but also maintains the uniformity and coherence of the Kubernetes API, ensuring that custom resources are as accessible and manageable as the built-in ones. Through CRDs, Kubernetes embraces an extendable architecture, empowering developers to innovate and expand the platform's capabilities to meet their unique operational requirements.  

!!! info
    Creating a custom resource doesn't do a whole lot unless you create a custom controller to accompany it. If you're interested in digging into those details, I recommend reading [the official Kubernetes documentation on custom controllers](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/#custom-controllers).  

*[Protobuf]: cross-platform data format used to serialize structured data
*[Serialization]: the process of converting a data object into a byte stream