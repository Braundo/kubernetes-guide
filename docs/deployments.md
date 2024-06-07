---
icon: material/refresh
---

## Kubernetes Deployments

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
kubectl apply -f deployment.yaml
```
This command posts the deployment configuration to the Kubernetes API server, which will create the specified number of Pods and manage them according to the defined state.

Example output:
```text
deployment.apps/web-deployment created
```

<h3>Scaling a Deployment</h3>

You can scale a Deployment either imperatively or declaratively.

**Imperative Scaling:**
```sh
kubectl scale deploy web-deployment --replicas=5
```
This command instructs Kubernetes to scale the number of Pods in the `web-deployment` Deployment to 5. Imperative commands are useful for quick changes.

Example output:
```text
deployment.apps/web-deployment scaled
```

**Declarative Scaling:**
Update the `replicas` field in your Deployment YAML file and apply the changes:
```yaml
spec:
  replicas: 5
```
```sh
kubectl apply -f deployment.yaml
```
This method involves updating the YAML file to reflect the desired state and applying it. It aligns with the declarative model, where you describe the desired state and let Kubernetes handle the rest.

Example output:
```text
deployment.apps/web-deployment configured
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
kubectl apply -f deployment.yaml
```
This command updates the deployment with the new image version, triggering a rolling update.

Example output:
```text
deployment.apps/web-deployment configured
```

<h3>Monitoring Rollouts</h3>

You can monitor the status of a rollout using the following command:
```sh
kubectl rollout status deploy web-deployment
```
This command provides real-time feedback on the status of the deployment rollout, allowing you to ensure that the update is proceeding as expected.

Example output:
```text
deployment "web-deployment" successfully rolled out
```

<h3>Pausing and Resuming Rollouts</h3>

If needed, you can pause and resume rollouts:

**Pause:**
```sh
kubectl rollout pause deploy web-deployment
```
Pausing a rollout halts the update process, which can be useful if you need to troubleshoot or make additional changes.

Example output:
```text
deployment.apps/web-deployment paused
```

**Resume:**
```sh
kubectl rollout resume deploy web-deployment
```
Resuming a rollout continues the update process from where it was paused.

Example output:
```text
deployment.apps/web-deployment resumed
```

<h3>Rolling Back a Deployment</h3>

If an update causes issues, you can roll back to a previous version. Kubernetes retains old ReplicaSets for this purpose.

To roll back to the previous version:
```sh
kubectl rollout undo deploy web-deployment
```
This command reverts the deployment to the last stable configuration.

Example output:
```text
deployment.apps/web-deployment rolled back
```

For more control, you can specify a particular revision:
```sh
kubectl rollout undo deploy web-deployment --to-revision=1
```
This command rolls back the deployment to a specified revision, providing finer control over the rollback process.

Example output:
```text
deployment.apps/web-deployment rolled back to revision 1
```

## Advanced Features

<h3>Autoscaling</h3>

Kubernetes supports various autoscalers:

- **Horizontal Pod Autoscaler (HPA):** Adjusts the number of Pods based on CPU/memory usage.
- **Vertical Pod Autoscaler (VPA):** Adjusts resource limits/requests for running Pods.
- **Cluster Autoscaler (CA):** Adjusts the number of nodes in the cluster.

**Example of HPA:**
```sh
kubectl autoscale deploy web-deployment --cpu-percent=50 --min=1 --max=10
```
This command sets up an HPA for the `web-deployment`, adjusting the number of Pods to maintain average CPU usage at 50%, with a minimum of 1 Pod and a maximum of 10 Pods.

Example output:
```text
horizontalpodautoscaler.autoscaling/web-deployment autoscaled
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
kubectl apply -f deployment.yaml
```
This command posts the deployment configuration to the Kubernetes API server, which then ensures the desired state is maintained.

Example output:
```text
deployment.apps/web-deployment created
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
kubectl apply -f sample-deployment.yaml
```
This command creates the sample deployment as specified in the YAML file.

Example output:
```text
deployment.apps/sample-deployment created
```

<h3>Scaling the Application</h3>

Scale the Deployment to 5 replicas:
```sh
kubectl scale deploy sample-deployment --replicas=5
```
This command scales the number of Pods in the `sample-deployment` Deployment to 5.

Example output:
```text
deployment.apps/sample-deployment scaled
```

Verify the scaling:
```sh
kubectl get deploy sample-deployment
```
This command checks the status of the `sample-deployment` Deployment, confirming the number of running replicas.

Example output:
```text
NAME               READY   UP-TO-DATE   AVAILABLE   AGE
sample-deployment  5/5     5            5           5m
```

<h3>Updating the Application</h3>

Update the image version to `nginx:1.16.0` in the YAML file and apply the changes:
```sh
kubectl apply -f sample-deployment.yaml
```
This command updates the deployment with the new image version, triggering a rolling update.

Example output:
```text
deployment.apps/sample-deployment configured
```

Monitor the rollout:
```sh
kubectl rollout status deploy sample-deployment
```
This command provides real-time feedback on the status of

 the deployment rollout, ensuring that the update is proceeding as expected.

Example output:
```text
deployment "sample-deployment" successfully rolled out
```

<h3>Rolling Back the Application</h3>

Rollback to the previous version:
```sh
kubectl rollout undo deploy sample-deployment
```
This command reverts the deployment to the last stable configuration.

Example output:
```text
deployment.apps/sample-deployment rolled back
```

## Summary

Deployments in Kubernetes offer a robust mechanism for managing stateless applications. By leveraging features like self-healing, scaling, rolling updates, and rollbacks, you can ensure your applications are resilient, scalable, and easy to maintain. Embracing the declarative model simplifies management and aligns with Kubernetes' principles of infrastructure as code.