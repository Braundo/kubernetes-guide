---
icon: material/api
---

## Mastering the Kubernetes API

Understanding the Kubernetes API is essential for mastering Kubernetes. It serves as the backbone of the platform, allowing you to manage resources programmatically and automate cluster operations.

## Overview of the Kubernetes API

<h3>The Big Picture</h3>

Kubernetes is an API-centric platform. All resources, such as Pods, Services, and StatefulSets, are defined through the API and managed by the API server. Administrators and clients interact with the cluster by sending requests to create, read, update, and delete these resources. Most interactions are done using `kubectl`, but they can also be crafted in code or generated through API development tools.

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
kubectl get pods --namespace eggs
```
This command converts to:
```text
GET /api/v1/namespaces/eggs/pods
```

## Hands-On with the API

<h3>Exploring the API</h3>

**1. Start a Proxy Session:**
   ```sh
   kubectl proxy --port 9000 &
   ```
   This command starts a local proxy to the Kubernetes API server, allowing you to interact with the API using `curl` or other HTTP clients on `http://localhost:9000`.

**2. Using `curl` to Interact with the API:**
   ```sh
   curl -X GET http://localhost:9000/api/v1/namespaces/eggs/pods
   ```
   This command sends a GET request to the API server to retrieve information about Pods in the `eggs` Namespace.

Example output:
```json
{
  "kind": "PodList",
  "apiVersion": "v1",
  "items": []
}
```

<h3>Creating Resources</h3>

**1. Define a Namespace:**
   Create a JSON file (`ns.json`):
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

**2. Post the Namespace:**
   ```sh
   curl -X POST -H "Content-Type: application/json" --data-binary @ns.json http://localhost:9000/api/v1/namespaces
   ```
   This command posts the JSON data to the API server, creating a new Namespace called `eggs`.

Example output:
```json
{
  "kind": "Namespace",
  "apiVersion": "v1",
  "metadata": {
    "name": "eggs",
    "selfLink": "/api/v1/namespaces/eggs",
    "uid": "abcd1234-5678-90ef-ghij-klmnopqrstuv",
    "resourceVersion": "123456",
    "creationTimestamp": "2024-06-07T12:34:56Z",
    "labels": {
      "chapter": "api"
    }
  }
}
```

**3. Verify Creation:**
   ```sh
   kubectl get namespaces
   ```
   This command lists all Namespaces in the cluster, allowing you to verify the creation of the `eggs` Namespace.

Example output:
```text
NAME          STATUS   AGE
default       Active   84d
kube-system   Active   84d
eggs          Active   1m
```

**4. Delete the Namespace:**
   ```sh
   curl -X DELETE http://localhost:9000/api/v1/namespaces/eggs
   ```
   This command deletes the `eggs` Namespace.

Example output:
```json
{
  "kind": "Namespace",
  "apiVersion": "v1",
  "metadata": {
    "name": "eggs",
    "deletionTimestamp": "2024-06-07T12:36:00Z"
  },
  "status": {
    "phase": "Terminating"
  }
}
```

## Inspecting the API

<h3>Useful Commands</h3>

**1. List All API Resources:**
   ```sh
   kubectl api-resources
   ```
   This command lists all available API resources in the cluster.

Example output:
```text
NAME                  SHORTNAMES   APIGROUP                       NAMESPACED   KIND
pods                  po                                        true          Pod
services              svc                                       true          Service
deployments           deploy        apps                        true          Deployment
...
```

**2. List Supported API Versions:**
   ```sh
   kubectl api-versions
   ```
   This command lists all API versions supported by the cluster.

Example output:
```text
v1
apps/v1
batch/v1
extensions/v1beta1
...
```

**3. Inspect Specific Resources:**
   ```sh
   kubectl explain pods
   ```
   This command provides detailed information about the `Pod` resource, including its fields and their descriptions.

Example output:
```yaml
KIND:     Pod
VERSION:  v1

DESCRIPTION:
     Pod is a collection of containers that can run on a host. This resource
     is created by clients and scheduled onto hosts.

FIELDS:
   apiVersion   <string>
   kind         <string>
   metadata     <Object>
   spec         <Object>
   status       <Object>
```

**4. Using `curl` to Explore:**
   ```sh
   curl http://localhost:9000/apis
   ```
   This command lists all API groups and their versions available in the cluster.

Example output:
```json
{
  "kind": "APIGroupList",
  "apiVersion": "v1",
  "groups": [
    {
      "name": "apps",
      "versions": [
        {
          "groupVersion": "apps/v1",
          "version": "v1"
        }
      ],
      "preferredVersion": {
        "groupVersion": "apps/v1",
        "version": "v1"
      }
    },
    ...
  ]
}
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
  name: recipes.breakfast.com
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

**1. Apply the CRD:**
   ```sh
   kubectl apply -f crd.yml
   ```
   This command creates the custom resource definition in the cluster.

Example output:
```text
customresourcedefinition.apiextensions.k8s.io/recipes.breakfast.com created
```

**2. Create an Instance:**
   Create a YAML file (`eggs.yml`) for the custom resource:
   ```yaml
   apiVersion:

 breakfast.com/v1
   kind: Recipe
   metadata:
     name: scrambled
   spec:
     bookTitle: "Breakfast Recipes"
     topic: Eggs
     edition: 1
   ```

**3. Apply the Instance:**
   ```sh
   kubectl apply -f eggs.yml
   ```
   This command creates an instance of the custom resource.

Example output:
```text
recipe.breakfast.com/scrambled created
```

**4. Verify Creation:**
   ```sh
   kubectl get rp
   ```
   This command lists all instances of the custom resource.

Example output:
```text
NAME        AGE
scrambled   1m
```

## Summary

The Kubernetes API is a powerful tool for managing your cluster. By understanding its structure and capabilities, you can leverage it to automate and streamline your operations. From creating resources to extending the API with custom definitions, mastering the API is key to unlocking Kubernetes' full potential.