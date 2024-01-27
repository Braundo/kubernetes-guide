*Pods are the smallest deployable units of computing in Kubernetes*. A Pod is a group of one or more containers with shared storage and network resources. They are always co-located and co-scheduled, running in a shared context. Pods model an application-specific "logical host" and can contain one or more application containers that are tightly coupled.



## Key Concepts:
- **What is a Pod?**: A Pod is similar to a set of containers with shared namespaces and shared filesystem volumes.

- **Using Pods**: Pods are generally not created directly but are created using workload resources like Deployment or Job.

- **Workload Resources**: These are resources that manage one or more Pods for you. Examples include Deployment, StatefulSet, and DaemonSet.

- **Pod Templates**: These are specifications for creating Pods and are included in workload resources.

- Pod Update and Replacement: When the Pod template for a workload resource is changed, new Pods are created based on the updated template.

- **Resource Sharing and Communication**: Pods enable data sharing and communication among their constituent containers.

- **Storage in Pods**: A Pod can specify a set of shared storage volumes that all containers in the Pod can access.

- **Pod Networking**: Each Pod is assigned a unique IP address. Containers in a Pod share the network namespace, including the IP address and network ports.

- **Privileged Mode for Containers**: Any container in a Pod can run in privileged mode to use operating system administrative capabilities.

- **Static Pods**: These are managed directly by the `kubelet` daemon on a specific node, without the API server observing them.

- **Container Probes**: These are diagnostics performed periodically by the `kubelet` on a container.
