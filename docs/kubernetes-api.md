---
icon: material/api
---

# Mastering the Kubernetes API

Understanding the Kubernetes API is essential for mastering Kubernetes. It serves as the backbone of the platform, allowing you to manage resources programmatically and automate cluster operations.

## Overview of the Kubernetes API

<h3>The Big Picture</h3>

Kubernetes is an API-centric platform. All resources, such as Pods, Services, and StatefulSets, are defined through the API and managed by the API server. Administrators and clients interact with the cluster by sending requests to create, read, update, and delete these resources. Most interactions are done using `kubectl`, but they can also be crafted in code or generated through API development tools.

!!! warning "Note"
    The API Server is the **only** component in Kubernetes that interacts directly with etcd.

<h3>Key Concepts</h3>

- **API Server:** The central component that exposes the API and handles requests.
- **Resources and Objects:** Resources like Pods and Services are defined in the API. When deployed to a cluster, these resources are often called objects.
- **Serialization:** The process of converting an object into a string or stream of bytes for transmission or storage. Kubernetes supports JSON and Protobuf for serialization.

<h3>How the API Works</h3>

The Kubernetes API server is the central hub through which all interactions in the cluster are routed, functioning as the front-end interface for Kubernetes' API. Picture it as the Grand Central Station of Kubernetes — every command, status update, and inter-service communication passes through the API server via RESTful calls over HTTPS. Here's a snapshot of how it operates:  

- `kubectl` commands are directed to the API server, whether it's for creating, retrieving, updating, or deleting Kubernetes objects.
- Node Kubelets keep an eye on the API server, picking up new tasks and sending back their statuses.
- The control plane services don't chat amongst themselves directly; they communicate through the API server.  

## Understanding Serialization

Serialization is essential for transmitting and storing objects. Kubernetes typically uses JSON for communication with external clients and Protobuf for internal cluster traffic due to its efficiency.

<h3>Example: Serialization in Action</h3>

When a client like `kubectl` posts a request, it serializes the object as JSON. The API server then processes this request and sends back a serialized response.

## The API Server

<h3>Role and Function</h3>

The API server is the front-end to the Kubernetes API, handling all RESTful HTTPS requests. It manages all interactions between internal components and external clients.

<h3>Components</h3>

- **Control Plane Service:** Runs as a set of Pods in the `kube-system` Namespace.
- **TLS and Authentication:** Ensures secure communication and validates requests.
- **RESTful Interface:** Supports CRUD operations via standard HTTP methods (POST, GET, PUT, PATCH, DELETE).

<h3>Example: Using the API</h3>

A typical `kubectl` command translates into a REST request:
```sh
$ kubectl get pods --namespace eggs
```
This command converts to:
```
GET /api/v1/namespaces/eggs/pods
```

## Hands-On with the API

<h3>Exploring the API</h3>

1. **Start a Proxy Session:**
   ```sh
   $ kubectl proxy --port 9000 &
   ```

2. **Using `curl` to Interact with the API:**
   ```sh
   $ curl -X GET http://localhost:9000/api/v1/namespaces/eggs/pods
   ```

<h3>Creating Resources</h3>

1. **Define a Namespace:**
   **ns.json:**
   ```json
   {
     "kind": "Namespace",
     "apiVersion": "v1",
     "metadata": {
       "name": "eggs",
       "labels": {
         "chapter": "api"
       }
     }
   }
   ```

2. **Post the Namespace:**
   ```sh
   $ curl -X POST -H "Content-Type: application/json" \
   --data-binary @ns.json http://localhost:9000/api/v1/namespaces
   ```

3. **Verify Creation:**
   ```sh
   $ kubectl get namespaces
   ```

4. **Delete the Namespace:**
   ```sh
   $ curl -X DELETE -H "Content-Type: application/json" \
   http://localhost:9000/api/v1/namespaces/eggs
   ```

## Inspecting the API

<h3>Useful Commands</h3>

1. **List All API Resources:**
   ```sh
   $ kubectl api-resources
   ```

2. **List Supported API Versions:**
   ```sh
   $ kubectl api-versions
   ```

3. **Inspect Specific Resources:**
   ```sh
   $ kubectl explain pods
   ```

4. **Using `curl` to Explore:**
   ```sh
   $ curl http://localhost:9000/apis
   ```

## Extending the API

<h3>Custom Resources</h3>

Kubernetes allows you to extend the API with CustomResourceDefinitions (CRDs). These custom resources behave like native Kubernetes resources, enabling you to manage new types of objects within your cluster.

<h3>Example CRD</h3>

**crd.yml:**
```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: eggs.breakfast.com
spec:
  group: breakfast.com
  scope: Cluster
  names:
    plural: recipes
    singular: recipe
    kind: Recipe
    shortNames:
    - rp
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                bookTitle:
                  type: string
                topic:
                  type: string
                edition:
                  type: integer
```

<h3>Deploying the CRD</h3>

1. **Apply the CRD:**
   ```sh
   $ kubectl apply -f crd.yml
   ```

2. **Create an Instance:**
   **eggs.yml:**
   ```yaml
   apiVersion: breakfast.com/v1
   kind: Recipe
   metadata:
     name: scrambled
   spec:
     topic: Eggs
     edition: 1
   ```

3. **Apply the Instance:**
   ```sh
   $ kubectl apply -f eggs.yml
   ```

4. **Verify Creation:**
   ```sh
   $ kubectl get rp
   ```

## Conclusion

The Kubernetes API is a powerful tool for managing your cluster. By understanding its structure and capabilities, you can leverage it to automate and streamline your operations. From creating resources to extending the API with custom definitions, mastering the API is key to unlocking Kubernetes' full potential.