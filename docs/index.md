---
icon: material/home
---

# Kubernetes One Pager

This page is intended to give you a quick, one-page summary of Kubernetes. There will likely be some terms or concepts in the summary below that don't make a ton of sense without full context. Please view relevant documentation sections for a more in-depth explanation of various topics.  

## Background
At a high-level, Kubernetes is responsible for deploying your applications and dynamically responding to changes to keep your applications running how you intended. Kubernetes runs on any cloud or on-premise datacenter, abstracting away all of the underlying infrastructure and letting you focus on application development. All applications running on Kubernetes must be containerized, and those containers must be running inside of a Pod.  

Kubernetes itself was born out of Google's experience running billions of containers at scale and managing them with proprietary systems called Borg and Omega. In 2014 Google donated Kubernetes as an open-source project to the Cloud Native Computing Foundation (CNCF).

## Control Plane
Fundamentally, Kubernetes is a *cluster* - a group of machines, so to speak. These machines are called *nodes* in the Kubernetes world and can be cloud instances, virtual machines, physical servers, your laptop, etc.

A Kubernetes cluster consists of a *control plane* and any number of *worker nodes*. The control plane is the "brain" of Kubernets and handles things such as scheduling workloads to nodes, implenting the API, and watching for changes that need to be responded to. The worker nodes handle the leg-work of actually running applications.

### API Server
Speaking of, the API server is the central component for all communication for all components in Kubernetes.  

Any communication inbound or outbound to/from the Kubernetes cluster must be routed through the API server.

### Cluster Store
The control plane, like many aspects of Kubernetes, exists in a *stateless* manner. However, the *clsuter store* does not - it persistently stores the state of the cluster and other configuration data. As of Kubernetes v1.28, `etcd` is the distributed databse that Kubernetes leverages for it's cluster store.  

`etcd` is installed on every control plane node by default for high-availability. However, it does not tolerate split-brain scenarios and will prevent *updates* to the cluster in such states - but it will still allow applications to run in those scenarios.

### Controller Manager
Kubernetes consists of many different *controllers*, which are essentially background loops that watch for changes to the cluster (and alert when things don't match up so other components can take action). All controllers are managed and implemented by a higher-level component called the *controller manager*. 

The following logic is at the core of what Kubernetes is and how it works:  

``` mermaid
flowchart TD
    A(Obtain desired state) --> B(Observe current state)
    B --> C{desired = current?}
    C -->|Yes| B
    C -->|No| E[Take action]
```

### Scheduler
The scheduler's job is to watch the API server for new tasks (applications) and assign them to a worker node. If you pull back the curtains there is a complex ranking system that Kubernetes uses to filter out unhealthy nodes, nodes with low capacity, etc. - but the end result is that nodes with the highest-ranknig scores are selected to run tasks first.

### Cloud Controller Manager
If your Kubernetes cluster runs in the public cloud, your control plane will have an extra component called the *cloud controller manager*. This component is effectively responsible for interfacing with cloud services such as storage, networking, etc.

## Woker Nodes
Worker nodes are much simpler than control plane nodes. They consist of three main components: the *kubelet*, *container runtime*, and *kube-proxy*.

### Kubelet
This is the main Kubernetes process that runs on every worker node in a cluster. The principal purpose of the kubelet is to watch the API server for new applications needing to be scheduled.  

### Container runtime
The kubelet itself cannot pull images, start, or stop containers. It needs a container runtime to perform all of thse actions. Kubernetes supports a pluggable architecture called the Container Runtime Interface (CRI) that allows third-party container runtimes to by inserted.  

### Kube-proxy
The kube-proxy rnus on every node and handles all local networking. The kube-proxy is responsible for each node getting its own unique IP address and handles routing of traffic.

## DNS
Every Kubernetes cluster has an internal DNS service that it uses for service discovery. This service has a static IP address that is available to every Pod on every node within the cluster. This means that every single app running on the cluster can locate the DNS service and use it for discovering other applications or services on the cluster (no extra application code is needed to make this work).

## Declarative Model
At the core of Kubernetes is the concept of the *declarative model*. You tell Kubernetes how you want your application to look and run (how many replicas, which image to use, network settings, commands to run, how to perform updates, etc.), and it's Kubernetes job to ensure that happens. You "tell" Kubernetes through the use of manifest files written in YAML.  

You take those manifest files and `POST` them to the Kubernetes API server (typically through the use of `kubectl` commands). The API server will then authenticate the request, inspect the manifest for formatting, route the request to the appropriate controller (i.e. if you've defined a manifest file for a Deployment, it will send the request to the Deployments controller), and then it will record your desired state in the cluster store (remember, `etcd`). After this, the relevant controller will get started on performing any tasks necessary to get your application into it's desired state.  

After your application is up and running, controllers begin monitoring it's state in the background and ensuring it matches the desired state in `etcd` (see simple logic diagram above).

## Pods
Pods are the atomic unit of scheduling in Kubernetes. As virtual machines were in the VMware world, so are Pods in the world of Kubernetes. Every container running on Kubernetes must be wrapped up in a Pod. The most simple implementation of this are single-container Pods - one container inside one Pod. However there are instances where multi-container Pods make sense. Those advanced use-cases can be explored in further depth later in the documentation.

It's important to note that when you scale up/down application in Kubernetes, you're not doing so by adding/removing containers directly - you do so by adding/removing Pods.

### Atomic
Pod deployment is atomic in nature - a Pod is only considered **Ready** when *all* of its containers are up and running. Either the entire Pod comes up successfully and is running, or the entire thing doesn't. - there are no partial states.

### Lifecycle
Pods are designed to be ephemeral in nature. Once a Pod dies, it's not meant to be restarted or revived. Instead, the intent to spin up a brand new Pod in the failed ones place (based off of your defined Manifest). Further, Pods are *immutable* and should not be changed once running. If you need to chance your application, you update the configuration via the manifest and deploy a new Pod.

### Deployments

!!! note "Rest of the summary is in progress"


<br/><br/><br/><br/><br/><br/>
> **Legal discalimer**:  
>  
> 
* "Kubernetes", "K8s" and the Kubernetes logo are trademarks or registered trademarks of the Linux Foundation.  
>  
> * Neither myself nor this site are officially associated with the Linux Foundation.  