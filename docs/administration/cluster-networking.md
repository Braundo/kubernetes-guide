## Highly-coupled container-to-container communications
In Kubernetes, tightly coupled application components can be packed into a Pod. Containers in the same Pod share the same network namespace, which means they can communicate with each other via localhost. This makes inter-container communication seamless.


## Pod-to-Pod communications
This is the core focus of the document. In Kubernetes, every Pod gets its own IP address, and there's no need for explicit links between Pods or mapping container ports to host ports. This makes it easier to run services that bind to specific ports without conflicts. The Pod-to-Pod communication is made possible through a networking model that may be implemented differently depending on the network plugin used.


## Pod-to-Service communications
Kubernetes Services are an abstraction that defines a logical set of Pods and enables external traffic exposure, load balancing, and service discovery for those Pods. Services allow Pods to reliably communicate with each other without needing to know the IP address of the Pod they are talking to.


## External-to-Service communications
Kubernetes Services also allow for external traffic to enter the cluster. This is usually done through various types of Service types like ClusterIP, NodePort, and LoadBalancer, each serving a different use-case and environment.

<br/><br/>
Container Network Interface (CNI) plugins are responsible for attaching Pods to the host network, and they come in various flavors. Some offer basic Pod networking, while others offer extended features like network policy enforcement, encryption, and more.

<br/><br/>
There are ongoing efforts to improve networking, led by the Special Interest Group for Networking (SIG-Network). They are actively working on Kubernetes Enhancement Proposals (KEPs) to introduce new features and improvements in networking.
