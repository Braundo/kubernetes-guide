---
icon: material/robot-outline
---

# Kubernetes Operators

Kubernetes Operators extend the functionality of Kubernetes by automating the management of complex applications. They provide a powerful way to manage application-specific logic and stateful workloads.

## What are Operators?

<h3>Introduction to Operators</h3>

Kubernetes Operators are software extensions that use custom resources to manage applications and their components. They follow Kubernetes principles, notably the control loop, to automate tasks beyond the capabilities of standard Kubernetes resources.

<h3>Purpose of Operators</h3>

Operators are designed to automate the entire lifecycle of complex applications, including:

- **Installation:** Deploying and configuring applications.
- **Management:** Managing the application's runtime configuration.
- **Scaling:** Adjusting resources in response to changing workloads.
- **Healing:** Detecting and recovering from failures.
- **Upgrades:** Updating the application to new versions.

<h3>Key Concepts</h3>

Operators extend Kubernetes using the following components:

- **Custom Resource Definitions (CRDs):** Define new types of resources to represent the application and its components.
- **Custom Controllers:** Monitor the state of custom resources and take action to reconcile the actual state with the desired state.

## Detailed Workflow

![](../images/operator.svg)

#### **User Modification**
   - **Action:** A user modifies the custom resource to define or update the desired state of the application.
   - **Example:** The user could be updating the version of the application or changing configuration parameters.

   ```sh
   # Example command to apply a change to a custom resource
   kubectl apply -f custom-resource.yaml
   ```

#### **API Server Interaction**
   - **Action:** The Kubernetes API server receives the modification request and processes it.
   - **Purpose:** The API server validates and stores the new state of the custom resource.

#### **Operator Watches Custom Resource**
   - **Action:** The Operator, running as a controller within the cluster, continuously watches for changes to the custom resources.
   - **Purpose:** The Operator detects the change event and identifies that an action is needed to reconcile the desired state with the actual state.

#### **Operator Takes Action**
   - **Action:** The Operator performs the necessary operations to adjust the state of the application to match the desired state defined in the custom resource.
   - **Examples:** This could include creating, updating, or deleting resources such as Pods, Services, or ConfigMaps. The Operator might also perform application-specific actions like running a database migration or initiating a backup.

#### **State Adjustment**
   - **Action:** The Operator adjusts the state of the application.
   - **Purpose:** Ensures the actual state of the cluster matches the desired state defined in the custom resource.

#### **Continuous Monitoring and Reconciliation**
   - **Action:** The Operator continuously monitors the application and custom resources.
   - **Purpose:** Automatically reconciles any discrepancies between the desired state and the actual state, ensuring the application runs as intended over time.

## Building and Using Operators

<h3>Building an Operator</h3>

Building a Kubernetes Operator typically involves the following steps:

1. **Define a Custom Resource Definition (CRD):** The CRD defines the schema for the custom resource that represents the application.
2. **Implement a Custom Controller:** The controller monitors the custom resource and implements the logic to manage the application.

<h4>Example CRD</h4>

Define a CRD for a sample application (`sample-crd.yaml`):
```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: samples.apps.example.com
spec:
  group: apps.example.com
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
              replicas:
                type: integer
  scope: Namespaced
  names:
    plural: samples
    singular: sample
    kind: Sample
    shortNames:
    - smpl
```

<h4>Example Custom Resource</h4>

Define a custom resource that uses the CRD (`sample-cr.yaml`):
```yaml
apiVersion: apps.example.com/v1
kind: Sample
metadata:
  name: my-sample
spec:
  replicas: 3
```

<h4>Implementing the Controller</h4>

The controller is implemented using a programming language like Go. The [Operator SDK](https://sdk.operatorframework.io/) provides tools and libraries to simplify this process.

<h4>Install Operator SDK</h4>

Install the Operator SDK CLI:
```sh
$ curl -LO https://github.com/operator-framework/operator-sdk/releases/download/v1.16.0/operator-sdk_linux_amd64
$ chmod +x operator-sdk_linux_amd64
$ sudo mv operator-sdk_linux_amd64 /usr/local/bin/operator-sdk
```

<h4>Create a New Operator Project</h4>

Create a new project using the Operator SDK:
```sh
$ operator-sdk init --domain example.com --repo github.com/example/my-operator
$ operator-sdk create api --group apps --version v1 --kind Sample --resource --controller
```

<h4>Implement Reconciliation Logic</h4>

In the generated controller, implement the reconciliation logic to manage the custom resource:
```go
func (r *SampleReconciler) Reconcile(req ctrl.Request) (ctrl.Result, error) {
    ctx := context.Background()
    log := r.Log.WithValues("sample", req.NamespacedName)

    // Fetch the Sample instance
    var sample appsV1.Sample
    if err := r.Get(ctx, req.NamespacedName, &sample); err != nil {
        log.Error(err, "unable to fetch Sample")
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // TODO: Add application management logic here

    return ctrl.Result{}, nil
}
```

<h3>Deploying an Operator</h3>

<h4>Build and Push the Operator Image</h4>

Build the Operator image and push it to a container registry:
```sh
$ make docker-build docker-push IMG=<your-image-registry>/my-operator:v0.1.0
```

<h4>Deploy the Operator</h4>

Deploy the Operator to the Kubernetes cluster:
```sh
$ make deploy IMG=<your-image-registry>/my-operator:v0.1.0
```

<h3>Using the Operator</h3>

Create and manage custom resources using the Operator:

1. **Apply the CRD:**
   ```sh
   $ kubectl apply -f sample-crd.yaml
   ```

2. **Create a Custom Resource:**
   ```sh
   $ kubectl apply -f sample-cr.yaml
   ```

3. **Check the Status:**
   ```sh
   $ kubectl get samples.apps.example.com
   ```

<h3>Advanced Operator Features</h3>

Operators can include advanced features such as:

- **Leader Election:** Ensures only one instance of the Operator is active at a time.
- **Metrics and Monitoring:** Collect and expose metrics for monitoring the Operator's performance.
- **Webhooks:** Implement validation and mutating webhooks to enforce policies.

## Summary

Kubernetes Operators provide a powerful way to manage complex applications by extending Kubernetes with custom resources and controllers. By building and using Operators, you can automate the entire lifecycle of applications, ensuring they are deployed, managed, and scaled efficiently. Operators are a key component in managing stateful and complex workloads in a Kubernetes-native way.