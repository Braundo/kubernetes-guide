---
icon: material/circle-small
---
We'll dive into many of these topics in greater detail later on, but for now here is a primer on Kubernetes to get you started.  


## History
Kubernetes itself was born out of Google's experience running billions of containers at scale and managing them with proprietary systems called Borg and Omega. In 2014 Google donated Kubernetes as an open-source project to the Cloud Native Computing Foundation (CNCF).

## 20K-foot View
At a high-level, Kubernetes is responsible for deploying your applications and dynamically responding to changes to keep your applications running how you intended. Kubernetes runs on any cloud or on-premise datacenter, abstracting away all of the underlying infrastructure and letting you focus on application development. All applications running on Kubernetes must be containerized, and those containers must be running inside of a Pod.  

Fundamentally, Kubernetes is a **cluster** - a group of machines, so to speak. These machines are called **nodes** in the Kubernetes world and can be cloud instances, virtual machines, physical servers, your laptop, etc.  Cluster nodes can be lumped into one of two categories: **Control Plane** or **worker nodes**.

<h3>Control Plane and Worker Nodes</h3>

The **Control Plane** is the brain of the Kubernetes cluster. It makes global decisions about the cluster (e.g., scheduling), detects and responds to cluster events. The main components of the Control Plane include:

- **API Server**: The hub for all communication.
- **Scheduler**: Assigns your apps to run on various nodes.
- **Controller Manager**: Oversees a number of smaller controllers that perform actions like replicating pods and handling node operations.

**Worker nodes** are the "muscles" of the cluster where your applications actually run. Each worker node has the following components installed:

- **Kubelet**: Ensures that containers are running in a Pod.
- **Kube-proxy**: Maintains network rules.

![overview](../../images/overview.svg)

Understanding these components and their interactions is crucial for effectively managing and troubleshooting a Kubernetes cluster.


## API Server
Speaking of, the API Server is the central component for all communication for all components in Kubernetes.  

Any communication inbound or outbound to/from the Kubernetes cluster must be routed through the API Server.

## etcd
The Control Plane, like many aspects of Kubernetes, exists in a *stateless* manner. However, **etcd** does not - it persistently stores the state of the cluster and other configuration data.  
<br>

**etcd** plays a critical role in Kubernetes by persistently storing the state of the cluster and other configuration data.
<br>

**etcd** is not merely installed on every control plane node; it is commonly configured externally or runs in a clustered mode across several nodes. This configuration helps avoid single points of failure and ensures that the cluster remains operational even if one or more **etcd** instances fail. It's important to note that while **etcd** can handle network partitions or "split-brain" scenarios by preventing state updates, it will still allow the running applications to operate, thus ensuring service continuity.
<br>

Every result you see when you a run `kubectl get` command is actually data returned from **etcd** (via the API Server).

## Controllers
In Kubernetes, **controllers** are fundamental components that act as watchful guardians of the cluster's desired state. They are essentially background loops monitoring for deviations in the cluster and invoking corrective measures. These controllers include:

- **ReplicationController**: Ensures the specified number of pod replicas are running at any given time.
- **DeploymentController**: Manages the deployment process by updating applications and rolling out new versions seamlessly and safely.

All these controllers are orchestrated by a higher-level component known as the **Controller Manager**. This manager oversees various controllers' activities, ensuring that if the current state doesn't match the desired state, appropriate actions are taken to reconcile the two.


The following logic is at the core of what Kubernetes is and how it works:  

![control-loops](../../images/control-loops.svg)

## Declarative Model
Key to truly mastering Kubernetes is the concept of the *declarative model*. You tell Kubernetes how you want your application to look and run (how many replicas, which image to use, network settings, commands to run, how to perform updates, etc.), and it's Kubernetes job to ensure that happens. You "tell" Kubernetes through the use of manifest files written in YAML.  

You take those manifest files and `POST` them to the Kubernetes API Server (typically through the use of `kubectl` commands). The API Server will then authenticate the request, inspect the manifest for formatting, route the request to the appropriate controller (i.e. if you've defined a manifest file for a Deployment, it will send the request to the Deployments controller), and then it will record your desired state in the cluster store (remember, **etcd**). After this, the relevant controller will get started on performing any tasks necessary to get your application into its desired state.  

After your application is up and running, controllers begin monitoring its state in the background and ensuring it matches the desired state in **etcd** (see simple logic diagram above).