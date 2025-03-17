---
icon: material/ship-wheel
---

# Helm

Helm is a powerful tool for managing Kubernetes applications. It simplifies application deployment and management by using packages called "charts." This page will cover an introduction to Helm, its benefits, and how to create and use Helm charts effectively.

## Introduction to Helm

<h3>What is Helm?</h3>

Helm is a package manager for Kubernetes that allows you to define, install, and upgrade complex Kubernetes applications. It uses a packaging format called charts, which are collections of files that describe a related set of Kubernetes resources.

<h3>Benefits of Using Helm</h3>

Helm provides several benefits for managing Kubernetes applications:

- **Simplifies Deployment:** Packages multiple Kubernetes resources into a single unit, making it easier to deploy complex applications.
- **Versioning:** Supports versioning of charts, enabling easy upgrades and rollbacks.
- **Reuse:** Allows you to reuse charts for different environments, reducing duplication.
- **Customization:** Supports customizable templates to adapt to different environments and configurations.
- **Dependency Management:** Manages dependencies between different charts.

<h3>Helm Architecture</h3>

Helm operates with two main components:

1. **Helm Client:** The command-line tool that you use to create, install, and manage Helm charts.
2. **Helm Server (Tiller):** In Helm v2, Tiller runs inside the Kubernetes cluster and manages the deployment of charts. Note that Helm v3 has removed Tiller, and the client communicates directly with the Kubernetes API server.

<h3>How Helm Works</h3>

- **Charts:** Collections of files that describe a related set of Kubernetes resources.
- **Values Files:** Used to customize the deployment by overriding default values.
- **Templates:** Allow dynamic generation of Kubernetes manifests.
- **Releases:** An instance of a chart running in a Kubernetes cluster.
- **Repositories:** Collections of charts that can be shared and reused.

## Creating and Using Helm Charts

<h3>Creating a Helm Chart</h3>

To create a new Helm chart, use the following command:
```sh
$ helm create my-chart
```

This command generates a directory structure with default files:
```
my-chart/
  Chart.yaml          # Chart metadata
  values.yaml         # Default configuration values
  charts/             # Dependency charts
  templates/          # Kubernetes resource templates
```

<h4>Example Chart.yaml</h4>

```yaml
apiVersion: v2
name: my-chart
version: 0.1.0
description: A Helm chart for Kubernetes
```

<h3>Advanced Helm Features</h3>

- **Hooks:** Allow you to run scripts at specific points in a release lifecycle.
- **Lifecycle Management:** Manage the lifecycle of applications with upgrade and rollback capabilities.
- **Managing Dependencies:** Use the `requirements.yaml` file to manage chart dependencies.

<h3>Customizing Helm Charts</h3>

Customize charts for different environments by using values files and templates to override default settings.

## Best Practices

- **Version Control:** Keep your charts in version control for easy tracking and collaboration.
- **Testing:** Test your charts in different environments to ensure compatibility.
- **Security:** Regularly update your charts to include the latest security patches.
- **Documentation:** Provide clear documentation for using and customizing your charts.
