---
icon: material/select
---

## Namespaces in Kubernetes

Namespaces are a powerful feature in Kubernetes that allow you to segment your cluster into multiple groups, providing organization, isolation, and management capabilities.

## Understanding Namespaces

<h3>What are Namespaces?</h3>

In Kubernetes, Namespaces provide a way to partition a single Kubernetes cluster into multiple virtual clusters. This is different from kernel namespaces, which isolate resources at the operating system level.

- **Kernel Namespaces:** Isolate operating system resources for containers.
- **Kubernetes Namespaces:** Segment a Kubernetes cluster into separate environments for different teams, projects, or applications.

<h3>Benefits of Using Namespaces</h3>

Namespaces offer several advantages, including:

- **Organizational Segmentation:** Separate environments for development, testing, and production.
- **Resource Management:** Apply different resource quotas and policies to each Namespace.
- **Soft Isolation:** Prevent resource conflicts and organize cluster resources logically.

![](../images/ns.svg)

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

!!! info "Note"
    Instead of typing out **namespace** each time, you can shorten it to **ns** in `kubectl` commands.

To view the existing Namespaces, use:
```sh
kubectl get namespaces
```
This command lists all the Namespaces in the cluster, showing their status and age.

Example output:
```text
NAME                 STATUS   AGE
default              Active   84d
kube-node-lease      Active   84d
kube-public          Active   84d
kube-system          Active   84d
local-path-storage   Active   84d
```

To delete a Namespace:
```sh
kubectl delete ns my-namespace
```
This command deletes the specified Namespace and all the resources within it. Be cautious when deleting Namespaces, as this action is irreversible.

Example output:
```text
namespace "my-namespace" deleted
```

## Creating and Managing Namespaces

<h3>Creating a Namespace</h3>

You can create a Namespace either imperatively or declaratively.

**Imperative Creation:**
```sh
kubectl create ns my-namespace
```
This command immediately creates a Namespace named `my-namespace`. It's a quick and straightforward method for creating Namespaces.

Example output:
```text
namespace/my-namespace created
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
kubectl apply -f namespace.yaml
```
This approach allows you to manage your Namespace as code, making it easier to track changes and automate deployments. The labels can be used for organizational purposes or for applying specific policies.

Example output:
```text
namespace/my-namespace created
```

<h3>Configuring kubectl for a Specific Namespace</h3>

To avoid specifying the Namespace in every command, set your context to a specific Namespace:
```sh
kubectl config set-context --current --namespace=my-namespace
```
This command configures `kubectl` to use `my-namespace` as the default Namespace for the current context. It simplifies your workflow by eliminating the need to repeatedly specify the Namespace.

Example output:
```text
Context "your-current-context" modified.
```

## Deploying Applications in Namespaces

You can deploy resources to a specific Namespace by specifying it in the YAML file or by using the `-n` flag with `kubectl` commands.

**Example YAML for Deployment:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  namespace: my-namespace # specified here
spec:
  containers:
  - name: my-container
    image: nginx
    ports:
    - containerPort: 80
```
This YAML file specifies that the Pod `my-pod` should be deployed in the `my-namespace` Namespace. By including the `namespace` field, you ensure the resource is created in the correct Namespace.

Apply the YAML file:
```sh
kubectl apply -f deployment.yaml
```
This command deploys the resources defined in `deployment.yaml` to the specified Namespace.

Example output:
```text
pod/my-pod created
```

**Using the `-n` Flag:**
```sh
kubectl get pods -n my-namespace
```
The `-n` flag specifies the Namespace for the `kubectl` command. This command lists all Pods in the `my-namespace` Namespace.

Example output:
```text
NAME        READY   STATUS    RESTARTS   AGE
my-pod      1/1     Running   0          1m
```

## Summary

Namespaces in Kubernetes are an effective way to manage resources and organize environments within a cluster. While they provide soft isolation and ease of management, remember that they are not suitable for hard multi-tenancy. By using Namespaces, you can efficiently segment your cluster and apply different policies and resource quotas to each segment.