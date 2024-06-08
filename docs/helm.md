---
icon: material/ship-wheel
---

# Helm and Kubernetes Package Management

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

<h3>How Helm Works</h3>

Helm operates with two main components:

1. **Helm Client:** The command-line tool that you use to create, install, and manage Helm charts.
2. **Helm Server (Tiller):** In Helm v2, Tiller runs inside the Kubernetes cluster and manages the deployment of charts. Note that Helm v3 has removed Tiller, and the client communicates directly with the Kubernetes API server.


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

`Chart.yaml` contains metadata about the chart:
```yaml
apiVersion: v2
name: my-chart
description: A Helm chart for Kubernetes
type: application
version: 0.1.0
appVersion: 1.0.0
```

<h4>Example values.yaml</h4>

`values.yaml` contains default configuration values:
```yaml
replicaCount: 3
image:
  repository: myimage
  tag: latest
  pullPolicy: IfNotPresent
service:
  type: ClusterIP
  port: 80
```

<h4>Example Deployment Template</h4>

`templates/deployment.yaml` defines a Kubernetes Deployment:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Chart.Name }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Chart.Name }}
  template:
    metadata:
      labels:
        app: {{ .Chart.Name }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        ports:
        - containerPort: {{ .Values.service.port }}
```

<h3>Using Helm Charts</h3>

<h4>Installing a Chart</h4>

To install a chart, use the following command:
```sh
$ helm install my-release my-chart/
```

This command installs the chart with the release name `my-release`.

<h4>Customizing Values</h4>

Override default values by specifying a custom `values.yaml` file:
```sh
$ helm install my-release -f custom-values.yaml my-chart/
```

Or by using the `--set` flag:
```sh
$ helm install my-release --set replicaCount=5 my-chart/
```

<h4>Upgrading a Release</h4>

To upgrade an existing release with new values or chart versions:
```sh
$ helm upgrade my-release my-chart/
```

<h4>Rolling Back a Release</h4>

To roll back to a previous release:
```sh
$ helm rollback my-release 1
```

<h3>Customizing Helm Charts</h3>

You can customize Helm charts by modifying templates and values. Here are some tips:

<h4>Using Templates</h4>

Helm uses the Go templating language. You can define templates with placeholders for dynamic values. For example:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-{{ .Chart.Name }}
spec:
  replicas: {{ .Values.replicaCount }}
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}-{{ .Chart.Name }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
```

<h4>Template Functions</h4>

Helm templates support functions for advanced customization. For example, you can use the `default` function to provide fallback values:
```yaml
image: "{{ .Values.image.repository | default "nginx" }}"
```

<h4>Conditional Logic</h4>

Use conditional statements to include or exclude resources based on values:
```yaml
{{- if .Values.service.enabled }}
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}-{{ .Chart.Name }}
spec:
  type: {{ .Values.service.type }}
  ports:
  - port: {{ .Values.service.port }}
{{- end }}
```

## Practical Example

<h3>Creating and Deploying a Custom Helm Chart</h3>

1. **Create a new Helm chart:**
   ```sh
   $ helm create custom-chart
   ```

2. **Customize `values.yaml`:**
   ```yaml
   replicaCount: 2
   image:
     repository: nginx
     tag: stable
     pullPolicy: IfNotPresent
   service:
     type: NodePort
     port: 80
   ```

3. **Customize `templates/deployment.yaml`:**
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: {{ .Release.Name }}-{{ .Chart.Name }}
   spec:
     replicas: {{ .Values.replicaCount }}
     selector:
       matchLabels:
         app: {{ .Release.Name }}-{{ .Chart.Name }}
     template:
       metadata:
         labels:
           app: {{ .Release.Name }}-{{ .Chart.Name }}
       spec:
         containers:
         - name: {{ .Chart.Name }}
           image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
           ports:
           - containerPort: {{ .Values.service.port }}
   ```

4. **Deploy the custom chart:**
   ```sh
   $ helm install my-custom-release custom-chart/
   ```

5. **Verify the deployment:**
   ```sh
   $ kubectl get pods
   ```

## Summary

Helm simplifies the management of Kubernetes applications by using charts to package, deploy, and manage resources. By creating and using Helm charts, you can streamline the deployment process, manage configurations, and take advantage of Helm's powerful templating capabilities to customize your applications for different environments.