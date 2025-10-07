---
icon: material/ship-wheel
---

<h1>Helm</h1>

Helm is the package manager for Kubernetes. Helm lets you define, install, and upgrade Kubernetes applications using packages called <strong>charts</strong>. It makes deploying and managing complex apps as easy as installing an app on your phone - just use a "chart" and you're off to the races.

---

<h2>Benefits of Using Helm</h2>
<ul>
<li><strong>Simplifies Deployment:</strong> Bundle all your resources in one chart for easy deployment.</li>
<li><strong>Versioning:</strong> Upgrade and roll back apps with a single command.</li>
<li><strong>Reuse:</strong> Share charts across teams and environments.</li>
<li><strong>Customization:</strong> Use templates and values to adapt to any setup.</li>
<li><strong>Dependency Management:</strong> Charts can depend on other charts.</li>
</ul>

---

<h2>Helm Architecture</h2>

- <strong>Helm Client:</strong> Command-line tool for managing charts.
- <strong>Helm Server (Tiller):</strong> Only in Helm v2. In Helm v3+, the client talks directly to the Kubernetes API server (no Tiller).

---

<h2>How Helm Works</h2>
<ul>
<li><strong>Charts:</strong> Collections of files describing Kubernetes resources.</li>
<li><strong>Values Files:</strong> Override default settings for different environments.</li>
<li><strong>Templates:</strong> Dynamically generate manifests.</li>
<li><strong>Releases:</strong> Each deployment of a chart is a release.</li>
<li><strong>Repositories:</strong> Collections of charts you can share and reuse.</li>
</ul>

---

<h2>Creating and Using Helm Charts</h2>

<h3>Creating a Helm Chart</h3>

To create a new Helm chart:

```sh
helm create my-chart
```

This generates:
```
my-chart/
  Chart.yaml          # Chart metadata
  values.yaml         # Default configuration values
  charts/             # Dependency charts
  templates/          # Kubernetes resource templates
```

<h3>Example Chart.yaml</h3>

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
