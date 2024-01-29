A Kubernetes Deployment is a higher-level abstraction designed to manage the desired state of a set of replicated Pods. It allows you to describe an intended state in a Deployment object, and the Deployment controller changes the actual state to the desired state at a controlled rate. Here are some key features and functionalities:  


## Key Features
- **Replica Management**: You can specify the number of Pod replicas you want to run.
- **Updates**: Allows for rolling updates to Pods, ensuring zero downtime.
- **Rollbacks**: If something goes wrong, you can roll back to a previous stable version.
- **Scaling**: You can easily scale your application up or down.
- **Self-healing**: Automatically replaces failed or unhealthy Pods.


## Common Operations
- **Create a Deployment**: Usually done through a YAML file that describes the Deployment.
- **Inspect a Deployment**: Using commands like `kubectl get deployments` or `kubectl describe deployment <deployment-name>`.
- **Update a Deployment**: You can update the image or other fields in the YAML and apply it.
- **Rollback a Deployment**: Using `kubectl rollout undo deployment <deployment-name>`.
- **Scale a Deployment**: Using `kubectl scale deployment <deployment-name> --replicas=number`.


## YAML Example
Here's a simple example of a Deployment YAML file:

``` yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
  ```