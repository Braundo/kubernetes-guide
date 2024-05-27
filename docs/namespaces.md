---
icon: material/select-group
---

# Namespaces in Kubernetes

Namespaces are a powerful feature in Kubernetes that allow you to segment your cluster into multiple virtual clusters, providing organization, isolation, and management capabilities.

## Understanding Namespaces

<h3>What are Namespaces?</h3>

In Kubernetes, Namespaces provide a way to partition a single Kubernetes cluster into multiple virtual clusters. This is different from kernel namespaces, which isolate resources at the operating system level.

**Kernel Namespaces:** Isolate operating system resources for containers.
**Kubernetes Namespaces:** Segment a Kubernetes cluster into separate environments for different teams, projects, or applications.

<h3>Benefits of Using Namespaces</h3>

Namespaces offer several advantages, including:

- **Organizational Segmentation:** Separate environments for development, testing, and production.
- **Resource Management:** Apply different resource quotas and policies to each Namespace.
- **Soft Isolation:** Prevent resource conflicts and organize cluster resources logically.

## Practical Use Cases for Namespaces

Namespaces are ideal for managing environments within a single organization, such as:

- **Development Environments:** Separate Namespaces for dev, test, and production environments.
- **Team-Based Separation:** Different teams (e.g., finance, HR, operations) each have their own Namespace.
- **Project-Based Isolation:** Isolate projects within the same cluster to avoid resource conflicts.

<h3>Limitations of Namespaces</h3>

Namespaces provide soft isolation, meaning they help organize resources but do not offer strong security isolation. For stronger isolation, consider using separate clusters.

## Working with Default Namespaces

Every Kubernetes cluster comes with some pre-defined Namespaces:

- **default:** The default Namespace for objects with no specified Namespace.
- **kube-system:** Contains system components like DNS and metrics server.
- **kube-public:** For resources that should be publicly accessible.
- **kube-node-lease:** Manages Node heartbeat and leases.

To view the existing Namespaces, use:
```sh
$ kubectl get namespaces
```

To delete a Namespace:
```sh
$ kubectl delete ns my-namespace
```

## Creating and Managing Namespaces

<h3>Creating a Namespace</h3>

You can create a Namespace either imperatively or declaratively.

**Imperative Creation:**
```sh
$ kubectl create ns my-namespace
```

**Declarative Creation:**
Create a YAML file (`namespace.yaml`):
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: my-namespace
  labels:
    environment: dev
```
Apply the YAML file:
```sh
$ kubectl apply -f namespace.yaml
```

<h3>Configuring kubectl for a Specific Namespace</h3>

To avoid specifying the Namespace in every command, set your context to a specific Namespace:
```sh
$ kubectl config set-context --current --namespace=my-namespace
```

## Deploying Applications in Namespaces

You can deploy resources to a specific Namespace by specifying it in the YAML file or by using the `-n` flag with `kubectl` commands.

**Example YAML for Deployment:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  namespace: my-namespace
spec:
  containers:
  - name: my-container
    image: nginx
    ports:
    - containerPort: 80
```

Apply the YAML file:
```sh
$ kubectl apply -f deployment.yaml
```

**Using the `-n` Flag:**
```sh
$ kubectl get pods -n my-namespace
```

## Conclusion

Namespaces in Kubernetes are an effective way to manage resources and organize environments within a cluster. While they provide soft isolation and ease of management, remember that they are not suitable for hard multi-tenancy. By using Namespaces, you can efficiently segment your cluster and apply different policies and resource quotas to each segment.