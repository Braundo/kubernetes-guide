---
icon: material/kubernetes
---

## History
Kubernetes itself was born out of Google's experience running billions of containers at scale and managing them with proprietary systems called Borg and Omega. In 2014 Google donated Kubernetes as an open-source project to the Cloud Native Computing Foundation (CNCF).

## 20K-foot View
At a high-level, Kubernetes is responsible for deploying your applications and dynamically responding to changes to keep your applications running how you intended. Kubernetes runs on any cloud or on-premise datacenter, abstracting away all of the underlying infrastructure and letting you focus on application development. All applications running on Kubernetes must be containerized, and those containers must be running inside of a Pod.  

Fundamentally, Kubernetes is a **cluster** - a group of machines, so to speak. These machines are called **nodes** in the Kubernetes world and can be cloud instances, virtual machines, physical servers, your laptop, etc.  

A Kubernetes cluster consists of a **control plane** and any number of **worker nodes**. The control plane is the "brain" of Kubernetes and handles things such as scheduling workloads to nodes, implementing the API, and watching for changes that need to be responded to. The worker nodes handle the leg-work of actually running applications.

## API Server
Speaking of, the API server is the central component for all communication for all components in Kubernetes.  

Any communication inbound or outbound to/from the Kubernetes cluster must be routed through the API server.

## Cluster Store
The control plane, like many aspects of Kubernetes, exists in a *stateless* manner. However, the *clsuter store* does not - it persistently stores the state of the cluster and other configuration data. As of Kubernetes v1.28, `etcd` is the distributed databse that Kubernetes leverages for it's cluster store.  

`etcd` is installed on every control plane node by default for high-availability. However, it does not tolerate split-brain scenarios and will prevent *updates* to the cluster in such states - but it will still allow applications to run in those scenarios.

## Controllers
Kubernetes consists of many different *controllers*, which are essentially background loops that watch for changes to the cluster (and alert when things don't match up so other components can take action). All controllers are managed and implemented by a higher-level component called the *controller manager*. 

The following logic is at the core of what Kubernetes is and how it works:  

``` mermaid
flowchart TD
    A(Obtain desired state) --> B(Observe current state)
    B --> C{current = desired?}
    C -->|Yes| B
    C -->|No| E[Take action]
```

## Declarative Model
Key to truly mastering Kubernetes is the concept of the *declarative model*. You tell Kubernetes how you want your application to look and run (how many replicas, which image to use, network settings, commands to run, how to perform updates, etc.), and it's Kubernetes job to ensure that happens. You "tell" Kubernetes through the use of manifest files written in YAML.  

You take those manifest files and `POST` them to the Kubernetes API server (typically through the use of `kubectl` commands). The API server will then authenticate the request, inspect the manifest for formatting, route the request to the appropriate controller (i.e. if you've defined a manifest file for a Deployment, it will send the request to the Deployments controller), and then it will record your desired state in the cluster store (remember, `etcd`). After this, the relevant controller will get started on performing any tasks necessary to get your application into it's desired state.  

After your application is up and running, controllers begin monitoring it's state in the background and ensuring it matches the desired state in `etcd` (see simple logic diagram above).