---
icon: material/circle-small
---
**Ingress** aims to bridge the gap that exists with NodePort and LoadBalancer Services. NodePorts are great, but must use a high port number and require you to know the FQDN or IP address of your Nodes. LoadBalancer Services don't require this, but they are limited to one internal Service per load-balancer. So, if you have 50 applications you need exposed to the internet, you'd need 50 of your cloud provider's load-balancers instantiated - which would probably be cost prohibitive in most cases.  

Ingresses come into play here by allowing multiple Services to be "fronted" by a single cloud load-balancer. To accomplish this, Ingress will use a single LoadBalancer Service and use host-based or path-based routing to send traffic to the appropriate underlying Service.  

![service](../../images/ingress-1.svg)

## Routing Examples

#### Host-based Routing
![service](../../images/ingress-2.svg)
<br/><br/><br/><br><br>

#### Path-based Routing
![service](../../images/ingress-3.svg)
<br><br>

!!! warning "Kubernetes does not come with an Ingress controller by default"
<br><br>
## Ingress Controllers

An Ingress controller is deployed as a resource on Kubernetes like any other:
``` yaml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: nginx-ingress-controller
spec:
  replicas: 1
  selector:
    matchLabels:
      name: nginx-ingress
  template:
		metdata:
		  labels:
		    name: nginx-ingress
		spec:
		  containers:
		    - name: nginx-ingress-controller
		      image: quay.io/kubernetes-ingress-controller/nginx-ingress-controller:0.21.0
		  args:
		    - /nginx-ingress-controller
		    - --configmap=$(POD_NAMESPACE)/ngnix-configuration
		  env:
		    - name: POD_NAME
		      valueFrom:
		        fieldRef:
		          fieldPath: metadata.name
		    - name: POD_NAMESPACE
		      valueFrom:
		        fieldRef:
		          fieldPath: metadata.namespace
		  ports:
		    - name: http
		      containerPort: 80
		    - name: https
		      containerPort: 443
```
<br><br>

You’ll also need to create a configuration (ConfigMap) for the Ingress controller:
```yaml
kind: ConfigMap
apiVersion: v1
metadata:
    name: nginx-configuration
```
<br><br>

You’ll also need a Service to expose the Ingress controller:
```yaml
apiVersion: v1
kind: Service
metadata:
    name: nginx-ingress
spec:
    type: NodePort
    ports:
    - port: 80
    targetPort: 80
    protocol: TCP
    name: HTTP
    - port: 443
    targetPort: 443
    protocol: TCP
    name: https
    selector:
    name: nginx-ingress
```
<br><br>

Ingress controllers have intelligence built-in to monitor the Kubernetes cluster for Ingress changes and update the underlying Nginx server when something changes

- To do this, it needs a ServiceAccount with the right set of permissions:
    ``` yaml
    apiVersion: v1
    kind: ServiceAccount
    metadata:
    name: ngninx-ingress-serviceaccount
    ```

## Ingress Resources

An **Ingress Resource** is a set of rules and configurations applied on the Ingress Controller
- i.e. forward all traffic to a single application, route to different applications by URL path, domain, etc.
- It is created as a Kubernetes definition file like all others:    
    ```yaml
    apiVersion: extensions/v1beta1
    kind: Ingress
    metadata:
        name: ingress-eggs
    spec:
        backend:
        serviceName: eggs-service
        servicePort: 80
    ```
<br>
You can set up multiple rules for handling different traffic scenarios

- Within each rule you can handle different paths
<br><br>

You can define the rules in a manifest file definition for the Ingress as well: 
```yaml
apiVersion: v1
kind: Ingress
metadata:
    name: ingress-eggs-ham
spec:
    rules:
    - http:
        paths:
        - path: /eggs
        backend:
            serviceName: eggs-service
            servicePort: 80
        - path: /ham
        backend:
            serviceName: ham-service
            servicePort: 80
```
<br><br>

Here’s an example of how you would write rules based on **domain names**:
``` yaml
apiVersion: v1
kind: Ingress
metadata:
  name: ingress-eggs-ham
spec:
  rules:
  - host: eggs.my-online-store.com
	  http:
	      paths:
	      - backend:
	          serviceName: eggs-service
	          servicePort: 80
  - host: ham.my-online-store.com
	  http:
	      paths:
	      - backend:
	          serviceName: ham-service
	          servicePort: 80
```

## More Information
For a deeper dive into Ingress, refer to [the official Kubernetes documentation](https://kubernetes.io/docs/concepts/services-networking/ingress/).