---
icon: material/network-outline
---

# Networking in Kubernetes

Networking is a fundamental aspect of Kubernetes, enabling communication between various components within a cluster and with the outside world. This section covers the Container Network Interface (CNI) and popular CNI plugins, as well as network policies for controlling pod communication.

## Container Network Interface (CNI)

<h3>What is CNI?</h3>

The Container Network Interface (CNI) is a specification and a set of libraries for configuring network interfaces in Linux containers. It ensures that when a container is created or deleted, its network resources are allocated and cleaned up properly.

<h3>Role of CNI in Kubernetes</h3>

Kubernetes uses CNI to manage networking for Pods. When a Pod is created, the CNI plugin is responsible for assigning the Pod an IP address, setting up the network interface, and ensuring connectivity both within the cluster and externally.

## Popular CNI Plugins

Several CNI plugins are widely used in Kubernetes environments. Each offers different features and capabilities.

<h3>Calico</h3>

Calico provides secure network connectivity for containers, virtual machines, and native host-based workloads. It supports a range of features, including:

- **Network Policy Enforcement**: Allows you to define and enforce network policies.
- **BGP for Routing**: Uses Border Gateway Protocol (BGP) for high-performance routing.
- **IP-in-IP and VXLAN Encapsulation**: Supports various encapsulation methods for different networking needs.

## Understanding Overlay Networking in Kubernetes

Overlay networking is a fundamental concept in Kubernetes that allows for the seamless communication of pods across different nodes within a cluster. This approach abstracts the underlying network infrastructure, providing a virtual network that connects all pods regardless of their physical location. The diagram below illustrates the high-level architecture of overlay networking in a Kubernetes cluster.

<h3>Key Components of the Overlay Network</h3>

**1. Node Network**:
    - This is the physical network where the Kubernetes nodes (servers) are deployed. Each node in the cluster has a unique IP address within this network.
    - Nodes can communicate with each other through this network, enabling pod-to-pod communication across different nodes.

**2. Pod Network**:
    - Pods are assigned IP addresses from a logically separate, private CIDR block, distinct from the node network.
    - The pod network enables direct communication between pods across different nodes. This network is virtual and managed by Kubernetes through the use of CNI (Container Network Interface) plugins.

**3. Services Network**:
    - Kubernetes services provide stable endpoints for accessing pods. They use cluster-internal IP addresses and DNS names to facilitate communication.
    - Services abstract the underlying pods, allowing for load balancing and failover.

<h3>How Overlay Networking Works</h3>

In overlay networking, each pod receives an IP address from a private CIDR block. This block is logically separate from the network where the nodes are deployed, allowing for greater scalability and simplified network management.

<h4>Intra-Cluster Communication</h4>

- **Pod-to-Pod Communication**: Pods can communicate directly with each other using their assigned IP addresses. The overlay network ensures that these communications are routed correctly, regardless of the pods' physical locations.
- **Service-to-Pod Communication**: Services use label selectors to route traffic to the appropriate pods. The service network provides a stable IP and DNS name for accessing the pods, abstracting the complexity of pod IP management.

<h4>Exiting the Cluster</h4>

- When traffic leaves the cluster, it undergoes Source Network Address Translation (SNAT), which translates the pod's IP address to the node's IP address. This process ensures that external systems see the traffic as coming from the node, not the individual pod.
- Inbound traffic destined for pods is routed through services like load balancers. These services manage the translation and routing of requests to the appropriate pods, hiding the pod IP addresses behind the node's IP address.

<h3>Benefits of Overlay Networking</h3>

- **Scalability**: The separation of pod and node networks allows for easy scaling of the cluster. New pods and nodes can be added without reconfiguring the underlying network infrastructure.
- **Flexibility**: Overlay networks abstract the physical network, providing a consistent and flexible networking environment that can adapt to various underlying infrastructures.
- **Simplicity**: Managing a private CIDR block for pods simplifies IP address management and reduces the complexity of networking configurations.


Overlay networking is a powerful model in Kubernetes, enabling seamless and scalable communication between pods and services. By abstracting the underlying network infrastructure, overlay networking allows for greater flexibility and simplicity in managing Kubernetes clusters. The diagram above encapsulates these concepts, illustrating the relationship between the node network, pod network, and services network in a Kubernetes environment.

![](../images/network-overlay.svg)

**Installation Example:**
```sh
$ kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
```

<h3>Flannel</h3>

Flannel is a simple and easy-to-configure CNI plugin designed to provide basic networking for Kubernetes clusters. It supports various backend options for network traffic encapsulation, including VXLAN and host-gw.

**Key Features:**

- **Simple Overlay Network**: Uses a flat network to provide communication between nodes.
- **Multiple Backends**: Supports different backend options like VXLAN, host-gw, and UDP.

**Installation Example:**
```sh
$ kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```

<h3>Weave</h3>

Weave Net is a CNI plugin that creates a virtual network allowing Pods to communicate with each other, regardless of the node they are on. It is designed for simplicity and ease of use.

**Key Features:**

- **Automatic Mesh Network**: Automatically forms a mesh network for all nodes in the cluster.
- **Encryption**: Supports network traffic encryption.
- **Network Policy**: Integrates with Kubernetes Network Policies for traffic control.

**Installation Example:**
```sh
$ kubectl apply -f https://cloud.weave.works/k8s/net?k8s-version=$(kubectl version | base64 | tr -d '\n')
```

## Network Policies

Network policies in Kubernetes provide a way to control the communication between Pods. They use label selectors to define the source and destination Pods and specify the allowed protocols and ports.

<h3>Defining Network Policies</h3>

Network policies are defined using YAML files. Here’s a basic example that allows incoming traffic to Pods with the label `app: my-app` only from Pods with the label `role: frontend`.

**Example Network Policy:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: my-app
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: frontend
    ports:
    - protocol: TCP
      port: 80
```

<h3>Enforcing Network Policies</h3>

To enforce network policies, ensure that your CNI plugin supports them. Most advanced CNI plugins, like Calico and Weave, provide full support for Kubernetes network policies.

**Applying a Network Policy:**
```sh
$ kubectl apply -f networkpolicy.yaml
```

<h3>Key Concepts</h3>

- **PodSelector**: Selects the Pods to which the policy applies.
- **Ingress Rules**: Define the allowed incoming traffic to the selected Pods.
- **Egress Rules**: Define the allowed outgoing traffic from the selected Pods.

<h3>Example Use Cases</h3>

1. **Isolate Development and Production**: Ensure that development Pods cannot communicate with production Pods.
2. **Allow Only Specific Services**: Permit communication only between specific services, enhancing security.
3. **Restrict Traffic by Namespace**: Control traffic between different namespaces for better segmentation and security.

## Introduction to Service Mesh

<h3>Concept and Benefits</h3>

A service mesh abstracts the complexity of service-to-service communication, providing a uniform and consistent way to secure, connect, and monitor microservices. Key benefits include:

- **Traffic Management:** Advanced routing, load balancing, and traffic splitting.
- **Security:** Mutual TLS (mTLS) for secure communication between services.
- **Observability:** Detailed telemetry and monitoring of service interactions.
- **Resilience:** Fault injection, retries, and circuit breaking.

<h3>Setting Up Istio</h3>

Istio is a popular open-source service mesh that provides advanced networking, security, and observability features for microservices.

**Installation:**
1. Download the Istio CLI:
   ```sh
   curl -L https://istio.io/downloadIstio | sh -
   cd istio-<version>
   export PATH=$PWD/bin:$PATH
   ```

2. Install Istio on your cluster:
   ```sh
   istioctl install --set profile=demo -y
   ```

3. Label the namespace for automatic sidecar injection:
   ```sh
   kubectl label namespace default istio-injection=enabled
   ```

<h3>Using Istio</h3>

**Deploy a sample application:**
```sh
kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml
```

**Access the Istio dashboard:**
```sh
kubectl apply -f samples/addons
istioctl dashboard kiali
```

<h3>Using Linkerd</h3>

<h3>Setting Up Linkerd</h3>

Linkerd is a lightweight service mesh that provides essential features like observability, security, and reliability.

**Installation:**
1. Install the Linkerd CLI:
   ```sh
   curl -sL https://run.linkerd.io/install | sh
   export PATH=$PATH:$HOME/.linkerd2/bin
   ```

2. Install Linkerd on your cluster:
   ```sh
   linkerd install | kubectl apply -f -
   linkerd check
   ```

3. Label the namespace for automatic sidecar injection:
   ```sh
   kubectl annotate ns default linkerd.io/inject=enabled
   ```

**Deploy a sample application:**
```sh
kubectl apply -f https://run.linkerd.io/emojivoto.yml
```

**Access the Linkerd dashboard:**
```sh
linkerd viz dashboard &
```

## Summary

Kubernetes networking, facilitated by CNI plugins, is crucial for seamless communication between Pods and external systems. Popular CNI plugins like Calico, Flannel, and Weave offer various features to meet different networking needs. Network policies provide fine-grained control over pod communication, enhancing the security and manageability of your Kubernetes clusters. By understanding and implementing these concepts, you can build a robust and secure networking environment for your applications.