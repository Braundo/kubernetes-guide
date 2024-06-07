---
icon: material/code-tags
---

# Kubernetes API and Custom Resource Definitions (CRDs)

Kubernetes is highly extensible, allowing you to add custom resources to the API through Custom Resource Definitions (CRDs). This flexibility enables you to manage any kind of application-specific or domain-specific data and operations.

## Extending Kubernetes API

<h3>Introduction to CRDs</h3>

Custom Resource Definitions (CRDs) allow you to define custom resources within the Kubernetes API. These custom resources can represent any type of data or application-specific configuration, extending Kubernetes' capabilities beyond its built-in resource types.

<h3>Benefits of Using CRDs</h3>

- **Custom Resources:** Define custom resources tailored to your application's needs.
- **Declarative Management:** Manage custom resources using Kubernetes' declarative API.
- **Integration:** Integrate seamlessly with existing Kubernetes tools like `kubectl`, controllers, and operators.

<h3>Creating a CRD</h3>

To create a CRD, define it in a YAML file and apply it to your cluster.

**Example CRD Definition:**
```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: widgets.example.com
spec:
  group: example.com
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
                size:
                  type: string
                color:
                  type: string
  scope: Namespaced
  names:
    plural: widgets
    singular: widget
    kind: Widget
    shortNames:
    - wg
```

Apply the CRD to the cluster:
```sh
$ kubectl apply -f widget-crd.yaml
```

<h3>Using Custom Resources</h3>

Once the CRD is defined, you can create and manage instances of the custom resource.

**Example Custom Resource:**
```yaml
apiVersion: example.com/v1
kind: Widget
metadata:
  name: my-widget
spec:
  size: large
  color: blue
```

Apply the custom resource:
```sh
$ kubectl apply -f my-widget.yaml
```

## Using Kubebuilder

<h3>Introduction to Kubebuilder</h3>

Kubebuilder is a framework for building Kubernetes APIs using CRDs. It simplifies the process of creating, managing, and extending Kubernetes resources by providing tools and libraries to generate boilerplate code and handle common tasks.

<h3>Benefits of Using Kubebuilder</h3>

- **Code Generation:** Automatically generates boilerplate code for CRDs and controllers.
- **Best Practices:** Follows Kubernetes best practices for API development.
- **Scaffolding:** Provides scaffolding for custom resources and controllers, reducing development time.

<h3>Installing Kubebuilder</h3>

Install Kubebuilder by following the official installation guide from the [Kubebuilder website](https://kubebuilder.io/).

For Linux/macOS:
```sh
$ curl -L https://github.com/kubernetes-sigs/kubebuilder/releases/download/v2.3.1/kubebuilder_2.3.1_$(uname -s)_$(uname -m).tar.gz | tar -xz -C /usr/local/
$ export PATH=$PATH:/usr/local/kubebuilder/bin
```

<h3>Creating a New Project</h3>

Initialize a new Kubebuilder project:
```sh
$ mkdir widget-operator
$ cd widget-operator
$ kubebuilder init --domain example.com --repo github.com/example/widget-operator
```

<h3>Creating a New API</h3>

Create a new API for the custom resource:
```sh
$ kubebuilder create api --group apps --version v1 --kind Widget
```

This command generates boilerplate code for the custom resource and its controller.

<h3>Defining the Custom Resource</h3>

Edit the generated files to define the schema and behavior of the custom resource.

**Edit `api/v1/widget_types.go`:**
```go
type WidgetSpec struct {
  Size  string `json:"size,omitempty"`
  Color string `json:"color,omitempty"`
}

type WidgetStatus struct {
  // Define observed state of the resource
}

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
type Widget struct {
  metav1.TypeMeta   `json:",inline"`
  metav1.ObjectMeta `json:"metadata,omitempty"`

  Spec   WidgetSpec   `json:"spec,omitempty"`
  Status WidgetStatus `json:"status,omitempty"`
}

// +kubebuilder:object:root=true
type WidgetList struct {
  metav1.TypeMeta `json:",inline"`
  metav1.ListMeta `json:"metadata,omitempty"`
  Items           []Widget `json:"items"`
}
```

<h3>Implementing the Controller</h3>

Edit the generated controller file to define the reconciliation logic.

**Edit `controllers/widget_controller.go`:**
```go
func (r *WidgetReconciler) Reconcile(req ctrl.Request) (ctrl.Result, error) {
  ctx := context.Background()
  log := r.Log.WithValues("widget", req.NamespacedName)

  // Fetch the Widget instance
  var widget appsv1.Widget
  if err := r.Get(ctx, req.NamespacedName, &widget); err != nil {
    log.Error(err, "unable to fetch Widget")
    return ctrl.Result{}, client.IgnoreNotFound(err)
  }

  // TODO: Add application management logic here

  return ctrl.Result{}, nil
}
```

<h3>Deploying the Operator</h3>

Build and push the Operator image:
```sh
$ make docker-build docker-push IMG=<your-image-registry>/widget-operator:v0.1.0
```

Deploy the Operator to the cluster:
```sh
$ make deploy IMG=<your-image-registry>/widget-operator:v0.1.0
```

<h3>Using the Operator</h3>

Create and manage custom resources using the Operator.

**Apply the CRD:**
```sh
$ kubectl apply -f config/crd/bases/example.com_widgets.yaml
```

**Create a Custom Resource:**
```yaml
apiVersion: apps.example.com/v1
kind: Widget
metadata:
  name: my-widget
spec:
  size: large
  color: blue
```

Apply the custom resource:
```sh
$ kubectl apply -f my-widget.yaml
```

## Summary

Kubernetes CRDs and Kubebuilder provide powerful tools for extending the Kubernetes API and managing custom resources. By leveraging these tools, you can create, manage, and automate complex application-specific logic within your Kubernetes cluster. Kubebuilder simplifies the process of building Kubernetes APIs, allowing you to focus on the business logic of your applications.