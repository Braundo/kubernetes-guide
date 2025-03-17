---
icon: material/sitemap
---

Kubernetes Services are essential for ensuring reliable communication between Pods. They abstract the complexities of networking and provide stable endpoints for applications.

## Introduction to Kubernetes Services

<h3>Why Use Services?</h3>

Pods in Kubernetes are ephemeral; they can be created, destroyed, and rescheduled at any time due to various events such as scaling operations, rolling updates, rollbacks, and failures. This makes direct communication with Pods unreliable. Kubernetes Services address this issue by providing a stable endpoint for communication.

## How Services Work

Services in Kubernetes provide a front end (DNS name, IP address, and port) that remains constant regardless of the state of the Pods behind it. They use label selectors to dynamically route traffic to healthy Pods that match the specified criteria.

<h3>Service Discovery</h3>

Kubernetes offers two primary modes of service discovery:

- **Environment Variables:** When a Pod is created, the kubelet adds environment variables for each active Service. These variables are accessible within the Pod and provide the Service's cluster IP and port.
- **DNS:** Kubernetes includes a DNS server that automatically assigns DNS names to Services. Pods can use these DNS names to communicate with Services.

<h3>Endpoint Management</h3>

Services use endpoints to track the IP addresses of the Pods that match their label selector. The kube-proxy component on each node watches for changes to Service and Endpoint objects, updating the iptables rules accordingly to ensure traffic is correctly routed.

<h3>Load Balancing</h3>

Kubernetes Services provide built-in load balancing across the Pods they manage. The kube-proxy component distributes incoming requests to the available Pods based on the chosen load balancing strategy, ensuring even distribution of traffic.

## Types of Kubernetes Services

Kubernetes supports several types of Services, each suited to different use cases:

<h2>ClusterIP</h2>

<div style="text-align: center; width: 100%;">
    <img src="/images/clusterip.svg#only-light" alt="Kubernetes ClusterIP approach" style="width: 170%; max-width: 1000px;" />
    <img src="/images/clusterip.svg#only-dark" alt="Kubernetes ClusterIP approach" style="width: 170%; max-width: 1000px;" />
</div>

<p><strong>Key Points:</strong></p>
<ul>
<li>Internal IP and DNS name are automatically created.</li>
<li>Accessible only from within the cluster (i.e. Pod to Pod).</li>
<li>Ideal for internal applications that do not need external access.</li>
</ul>

!!! tip "Label Selector Behavior"
    When a Service uses label selectors to find Pods (e.g., `project: ab`), Pods must have **ALL** the labels specified in the selector to receive traffic. However, Pods can have additional labels beyond those required by the selector and will still receive traffic. This means that selectors work as an "AND" operation, not an "OR" operation.

<p><strong>Example YAML:</strong></p>

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-clusterip-service
spec:
  selector:
    app: my-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
```

<h2>NodePort</h2>

<div style="text-align: center; width: 100%;">
    <img src="/images/nodeport.svg#only-light" alt="Kubernetes NodePort approach" style="width: 170%; max-width: 1000px;" />
    <img src="/images/nodeport.svg#only-dark" alt="Kubernetes NodePort approach" style="width: 170%; max-width: 1000px;" />
</div>

1. External client hits node on NodePort.
2. Node forwards request to the ClusterIP of the Service.
3. The Service picks a Pod from the list of healthy Pods in the EndpointSlice.
4. The Pod receives the request.

<br>

<p><strong>Key Points:</strong></p>
<ul>
<li>Allocates a port from a configurable range (default: 30000-32767).</li>
<li>Accessible externally via <code>&lt;NodeIP&gt;:&lt;NodePort&gt;</code>.</li>
<li>Useful for exposing applications for development and testing purposes.</li>
</ul>

!!! info "Important NodePort Behavior"
    When you access a NodePort service, you can connect to **any** node in the cluster on the NodePort, even if the target Pod is not running on that specific node. Kubernetes will automatically route the traffic to the appropriate Pod, regardless of which node it's running on.

<h2>LoadBalancer</h2>

<div style="text-align: center; width: 100%;">
    <img src="/images/loadbalancer.svg#only-light" alt="Kubernetes LoadBalancer approach" style="width: 170%; max-width: 1000px;" />
    <img src="/images/loadbalancer.svg#only-dark" alt="Kubernetes LoadBalancer approach" style="width: 170%; max-width: 1000px;" />
</div>

1. External client hits LoadBalancer Service on friendly DNS name.
2. LoadBalancer forwards request to a NodePort.
3. Node forwards request to the ClusterIP of the Service.
4. The Service picks a Pod from the EndpointSlice.
5. Forwards request to the selected Pod.

<p><strong>Key Points:</strong></p>
<ul>
<li>Automatically provisions an external load balancer.</li>
<li>Provides a single IP address for external access.</li>
<li>Suitable for production environments where high availability is required.</li>
</ul>

<h2>ExternalName</h2>

<p><strong>Key Points:</strong></p>
<ul>
<li>Does not use kube-proxy.</li>
<li>Maps Service to an external DNS name.</li>
<li>Useful for integrating external services into a cluster.</li>
</ul>

<h3>Comparison of Service Types</h3>

| Service Type   | Internal Access | External Access | Use Case                                    |
|----------------|-----------------|-----------------|---------------------------------------------|
| ClusterIP      | Yes             | No              | Internal applications                       |
| NodePort       | Yes             | Yes (via NodeIP)| Development and testing                     |
| LoadBalancer   | Yes             | Yes             | Production environments with high availability |
| ExternalName   | No              | Yes (via DNS)   | Integrating external services               |


## Service Discovery

In terms of how an application then discovers other applications behind a Service, the flow looks like this:

1. The new Service is registered with the cluster DNS (Service Registry).
2. Your application wants to know the IP address of the Service so it provides the name to the cluster DNS for lookup.
3. The cluster DNS returns the IP address of the Service.
4. Your application now knows where to direct its request.

<h3>Practical Example of Service Discovery</h3>

Assume we have two applications on the same cluster - `ham` and `eggs`. Each application has their Pods fronted by a Service, which in turn each have their own ClusterIP.

```bash
kubectl get svc
```

Example output:
```text
NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
ham-svc      ClusterIP   192.168.1.200               443/TCP   5d19h
eggs-svc     ClusterIP   192.168.1.208               443/TCP   5d19h
```

For `ham` to communicate with `eggs`, it needs to know two things:

1. The name of the `eggs` application's Service (eggs-svc).
2. How to convert that name to an IP address.

<h3>Steps for Service Discovery:</h3>

1. The application container's default gateway routes the traffic to the Node it is running on.
2. The Node itself does not have a route to the Service network so it routes the traffic to the node kernel.
3. The Node kernel recognizes traffic intended for the service network and routes the traffic to a healthy Pod that matches the label selector of the Service.


## Networking in Kubernetes

Networking is a fundamental aspect of Kubernetes, enabling communication between various components within a cluster and with the outside world. This section covers the Container Network Interface (CNI) and popular CNI plugins, as well as network policies for controlling pod communication.

<h3>Container Network Interface (CNI)</h3>

<h4>What is CNI?</h4>

The Container Network Interface (CNI) is a specification and a set of libraries for configuring network interfaces in Linux containers. It ensures that when a container is created or deleted, its network resources are allocated and cleaned up properly.

<h4>Role of CNI in Kubernetes</h4>

Kubernetes uses CNI to manage networking for Pods. When a Pod is created, the CNI plugin is responsible for assigning the Pod an IP address, setting up the network interface, and ensuring connectivity both within the cluster and externally.

<h3>Popular CNI Plugins</h3>

Several CNI plugins are widely used in Kubernetes environments. Each offers different features and capabilities.

<h4>Calico</h4>

Calico provides secure network connectivity for containers, virtual machines, and native host-based workloads. It supports a range of features, including:

- **Network Policy Enforcement**: Allows you to define and enforce network policies.
- **BGP for Routing**: Uses Border Gateway Protocol (BGP) for high-performance routing.
- **IP-in-IP and VXLAN Encapsulation**: Supports various encapsulation methods for different networking needs.

<h4>Flannel</h4>

Flannel is a simple and easy way to configure a layer 3 network fabric designed for Kubernetes. It creates an overlay network that allows Pods on different nodes to communicate with each other.

<h4>Weave Net</h4>

Weave Net provides a simple and secure network for Kubernetes clusters. It supports automatic encryption of Pod traffic and can be used to create a flat network topology.

<h3>Understanding Overlay Networking in Kubernetes</h3>

Overlay networking is a fundamental concept in Kubernetes that allows for the seamless communication of pods across different nodes within a cluster. This approach abstracts the underlying network infrastructure, providing a virtual network that connects all pods regardless of their physical location.

<h4>Key Components of the Overlay Network</h4>

- **Node Network**: The physical network where the Kubernetes nodes are deployed.
- **Pod Network**: A logically separate, private CIDR block distinct from the node network.

<h3>Network Policies</h3>

Network Policies allow you to control the communication between Pods. They define rules that specify what traffic is allowed to and from Pods.

<h4>Creating Network Policies</h4>

Network Policies are created using YAML configuration files that specify the allowed traffic.

**Example YAML for Network Policy:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend
spec:
  podSelector:
    matchLabels:
      role: frontend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: backend
```

This configuration allows ingress traffic to Pods with the label "role: frontend" from Pods with the label "role: backend."

## Ingress

<h3>Understanding Ingress</h3>

Ingress allows external HTTP and HTTPS traffic to access services within the cluster. It provides a single entry point for multiple services and can manage SSL termination, load balancing, and name-based virtual hosting.

<h3>Configuring Ingress</h3>

1. **Create an Ingress Resource:** Define rules for routing traffic to services.

2. **Use an Ingress Controller:** Deploy an Ingress controller to manage traffic according to the rules.

3. **TLS Configuration:** Secure traffic using TLS by specifying certificates in the Ingress resource.

<h3>Example Ingress Resource</h3>

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: example-service
            port:
              number: 80

```

<h3>Advanced Ingress Configuration</h3>

Ingress can be configured for advanced use cases, such as:

- **Path-Based Routing:** Direct traffic based on URL paths to different services.
- **Name-Based Virtual Hosting:** Host multiple domains on the same IP address.
- **Load Balancing:** Distribute traffic across multiple backend services.

<h3>Example: Path-Based Routing</h3>

Here's how to configure path-based routing with Ingress:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: path-example
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /service1
        pathType: Prefix
        backend:
          service:
            name: service1
            port:
              number: 80
      - path: /service2
        pathType: Prefix
        backend:
          service:
            name: service2
            port:
              number: 80
```

This configuration routes traffic to `service1` and `service2` based on the URL path.
