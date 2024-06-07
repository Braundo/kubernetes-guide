---
icon: material/shuffle-variant
---

# Managing Ingress in Kubernetes

Ingress in Kubernetes allows you to manage external access to your services, typically HTTP. It provides features like load balancing, SSL termination, and name-based virtual hosting, enabling multiple services to be accessed through a single load balancer.

## Introduction to Ingress

<h3>Why Use Ingress?</h3>

Ingress offers a way to expose multiple applications through a single load balancer, addressing the limitations of NodePort and LoadBalancer services:

- **NodePort** services use high port numbers and require clients to track node IP addresses.
- **LoadBalancer** services create a one-to-one mapping between internal services and cloud load balancers, which can be costly and limited by cloud provider quotas.

<h3>How Ingress Works</h3>

Ingress is defined in the `networking.k8s.io/v1` API group and operates at Layer 7 of the OSI model, allowing it to inspect HTTP headers and forward traffic based on hostnames and paths. It requires two main constructs:

1. **Ingress Resource:** Defines routing rules.
2. **Ingress Controller:** Implements the routing rules. Unlike other Kubernetes resources, Ingress controllers are not built-in and must be installed separately.

![](../images/ingress.svg)

In this example, the traffic flow is as follows:

1. Client requests <b>eggs.food.com</b> or <b>food.com/eggs</b> and hits the public load-balancer.
2. The request is forwarded to the Ingress controller.
3. HTTP headers are inspected and Ingress rules trigger and route traffic to <b>svc-eggs</b>.
4. The <b>svc-eggs</b> Service forwards the request to a healthy Pod listed in its EndpointSlice.

## Setting Up Ingress

<h3>Installing an Ingress Controller</h3>

To use Ingress, you need an Ingress controller. This example uses the NGINX Ingress controller:

**1. Install the NGINX Ingress Controller:**
   ```sh
   kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.4/deploy/static/provider/cloud/deploy.yaml
   ```

**2. Check the Ingress Controller Pod:**
   ```sh
   kubectl get pods -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
   ```

<h3>Configuring Ingress Class</h3>

Ingress classes allow multiple Ingress controllers to coexist in a single cluster:

**1. List Ingress Classes:**
   ```sh
   kubectl get ingressclass
   ```

**2. Describe Ingress Class:**
   ```sh
   kubectl describe ingressclass nginx
   ```

## Creating and Managing Ingress Resources

<h3>Deploying Sample Applications</h3>

**1. Deploy Apps and Services:**
   ```sh
   kubectl apply -f app.yml
   ```

**app.yml:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: svc-bacon
spec:
  selector:
    app: bacon
  ports:
    - port: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: svc-eggs
spec:
  selector:
    app: eggs
  ports:
    - port: 8080
---
apiVersion: v1
kind: Pod
metadata:
  name: bacon
  labels:
    app: bacon
spec:
  containers:
    - name: bacon
      image: mybaconimage
      ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Pod
metadata:
  name: eggs
  labels:
    app: eggs
spec:
  containers:
    - name: eggs
      image: myeggsimage
      ports:
        - containerPort: 8080
```

<h3>Configuring Ingress Resource</h3>

**2. Deploy Ingress Resource:**
   ```sh
   kubectl apply -f ig-all.yml
   ```

**ig-all.yml:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: breakfast-all
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
    - host: bacon.breakfast.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: svc-bacon
                port:
                  number: 8080
    - host: eggs.breakfast.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: svc-eggs
                port:
                  number: 8080
    - host: breakfast.com
      http:
        paths:
          - path: /bacon
            pathType: Prefix
            backend:
              service:
                name: svc-bacon
                port:
                  number: 8080
          - path: /eggs
            pathType: Prefix
            backend:
              service:
                name: svc-eggs
                port:
                  number: 8080
```

<h3>Verifying Ingress Setup</h3>

**3. Check Ingress Resource:**
   ```sh
   kubectl get ing
   ```

**4. Describe Ingress Resource:**
   ```sh
   kubectl describe ing breakfast-all
   ```

## Configuring DNS for Ingress

To route traffic correctly, configure DNS to point to the Ingress load balancer's IP:

**1. Edit /etc/hosts:**
   ```sh
   212.2.246.150 bacon.breakfast.com
   212.2.246.150 eggs.breakfast.com
   212.2.246.150 breakfast.com
   ```

## Testing Ingress

Open a web browser and try accessing the following URLs:

- `bacon.breakfast.com`
- `eggs.breakfast.com`
- `breakfast.com/bacon`
- `breakfast.com/eggs`

## Advanced Ingress Concepts

<h3>Session Affinity</h3>

Session Affinity ensures that requests from the same client go to the same Pod, which is useful for stateful applications.

**Example YAML:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-affinity-service
spec:
  selector:
    app: my-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  sessionAffinity: ClientIP
```

<h3>External Traffic Policy</h3>

External Traffic Policy specifies whether traffic from outside the cluster is routed only to Pods on the same node or across all nodes.

**Example YAML:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-external-service
spec:
  type: LoadBalancer
  selector:
    app: my-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  externalTrafficPolicy: Local
```

## Troubleshooting Ingress

<h3>Common Issues and Solutions</h3>

**1. Service Not Accessible:**
   - Check Service and Pod status:
     ```sh
     kubectl get svc
     kubectl get pods
     ```
   - Ensure selectors match Pod labels.

**2. DNS Resolution Fails:**
   - Verify cluster DNS is running:
     ```sh
     kubectl get pods -n kube-system -l k8s-app=kube-dns
     ```
   - Check `/etc/resolv.conf` in Pods.

<h3>Practical Tips</h3>

- Use `kubectl logs` to inspect Ingress controller logs.
- Restart Ingress controller Pods if necessary:
  ```sh
  kubectl delete pod -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
  ```

## Summary

Ingress in Kubernetes provides a powerful way to manage external access to your services. By understanding and utilizing Ingress, you can efficiently route traffic to multiple services using a single load balancer, ensuring scalability and ease of management.