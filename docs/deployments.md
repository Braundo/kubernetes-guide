---
icon: material/checkbox-multiple-blank-outline
---

# Kubernetes Deployments

Deployments in Kubernetes provide powerful capabilities for managing stateless applications. They enable features like self-healing, scaling, rolling updates, and versioned rollbacks, making it easier to maintain robust and scalable applications.

## Key Concepts of Deployments

<h3>What is a Deployment?</h3>

A Deployment in Kubernetes is a resource that manages a set of identical Pods, ensuring they are up and running as specified. Deployments provide a declarative way to manage updates and scaling of applications.

<h3>Why Use Deployments?</h3>

Deployments add several benefits to managing applications:

- **Self-Healing:** Automatically replaces failed Pods.
- **Scaling:** Adjusts the number of running Pods based on demand.
- **Rolling Updates:** Updates Pods without downtime.
- **Rollbacks:** Easily revert to previous versions if something goes wrong.

## Deployment Architecture

<h3>Components</h3>

Deployments consist of two main components:

- **Deployment Resource:** Defines the desired state and configuration.
- **Deployment Controller:** Monitors the Deployment and ensures the current state matches the desired state through reconciliation.

<h3>Deployment and ReplicaSets</h3>

Deployments manage Pods indirectly through ReplicaSets. A ReplicaSet ensures a specified number of Pod replicas are running at any given time. The Deployment controller creates and manages ReplicaSets as needed to fulfill the Deployment's desired state.

![](../images/deploy.svg)

That diagram may look overly complex and bloated with all of the layers of abstraction, but each layer provides powerful value-adds.

## Creating and Managing Deployments

<h3>Creating a Deployment</h3>

You can create a Deployment using a YAML file that specifies the configuration.

**Example YAML for Deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web-container
        image: nginx:1.14.2
        ports:
        - containerPort: 80
```

To apply this configuration, use the following command:
```sh
$ kubectl apply -f deployment.yaml
```

<h3>Scaling a Deployment</h3>

You can scale a Deployment either imperatively or declaratively.

**Imperative Scaling:**
```sh
$ kubectl scale deploy web-deployment --replicas=5
```

**Declarative Scaling:**
Update the `replicas` field in your Deployment YAML file and apply the changes:
```yaml
spec:
  replicas: 5
```
```sh
$ kubectl apply -f deployment.yaml
```

<h3>Rolling Updates</h3>

Rolling updates allow you to update your application without downtime. Kubernetes gradually replaces old Pods with new ones.

To update the image version in your Deployment, modify the YAML file:
```yaml
spec:
  template:
    spec:
      containers:
      - name: web-container
        image: nginx:1.16.0
```
Apply the updated YAML file:
```sh
$ kubectl apply -f deployment.yaml
```

<h3>Monitoring Rollouts</h3>

You can monitor the status of a rollout using the following command:
```sh
$ kubectl rollout status deploy web-deployment
```

<h3>Pausing and Resuming Rollouts</h3>

If needed, you can pause and resume rollouts:

**Pause:**
```sh
$ kubectl rollout pause deploy web-deployment
```
**Resume:**
```sh
$ kubectl rollout resume deploy web-deployment
```

<h3>Rolling Back a Deployment</h3>

If an update causes issues, you can roll back to a previous version. Kubernetes retains old ReplicaSets for this purpose.

To roll back to the previous version:
```sh
$ kubectl rollout undo deploy web-deployment
```

For more control, you can specify a particular revision:
```sh
$ kubectl rollout undo deploy web-deployment --to-revision=1
```

## Advanced Features

<h3>Autoscaling</h3>

Kubernetes supports various autoscalers:

- **Horizontal Pod Autoscaler (HPA):** Adjusts the number of Pods based on CPU/memory usage.
- **Vertical Pod Autoscaler (VPA):** Adjusts resource limits/requests for running Pods.
- **Cluster Autoscaler (CA):** Adjusts the number of nodes in the cluster.

**Example of HPA:**
```sh
$ kubectl autoscale deploy web-deployment --cpu-percent=50 --min=1 --max=10
```

<h3>Declarative vs. Imperative Management</h3>

Kubernetes prefers a declarative approach, where you define the desired state in YAML files, and Kubernetes manages the steps to achieve that state. This contrasts with the imperative approach, where you issue commands to achieve the desired state.

**Declarative Example:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web-container
        image: nginx:1.14.2
        ports:
        - containerPort: 80
```

Apply the file with:
```sh
$ kubectl apply -f deployment.yaml
```

## Practical Exercise

<h3>Deploying a Sample Application</h3>

Create a YAML file (`sample-deployment.yaml`) with the following content:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sample-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sample
  template:
    metadata:
      labels:
        app: sample
    spec:
      containers:
      - name: sample-container
        image: nginx:1.14.2
        ports:
        - containerPort: 80
```

Deploy it:
```sh
$ kubectl apply -f sample-deployment.yaml
```

<h3>Scaling the Application</h3>

Scale the Deployment to 5 replicas:
```sh
$ kubectl scale deploy sample-deployment --replicas=5
```

Verify the scaling:
```sh
$ kubectl get deploy sample-deployment
```

<h3>Updating the Application</h3>

Update the image version to `nginx:1.16.0` in the YAML file and apply the changes:
```sh
$ kubectl apply -f sample-deployment.yaml
```

Monitor the rollout:
```sh
$ kubectl rollout status deploy sample-deployment
```

<h3>Rolling Back the Application</h3>

Rollback to the previous version:
```sh
$ kubectl rollout undo deploy sample-deployment
```

## Conclusion

Deployments in Kubernetes offer a robust mechanism for managing stateless applications. By leveraging features like self-healing, scaling, rolling updates, and rollbacks, you can ensure your applications are resilient, scalable, and easy to maintain. Embracing the declarative model simplifies management and aligns with Kubernetes' principles of infrastructure as code.