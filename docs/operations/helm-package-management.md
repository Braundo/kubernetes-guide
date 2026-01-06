---
icon: lucide/ship-wheel
---

# Helm: The Package Manager

Deploying a single Pod is easy. Deploying a production application - which needs a Deployment, Service, Ingress, ConfigMap, Secret, and HPA - is hard.

Managing that same application across Dev, Staging, and Production (with different replica counts and image tags for each) is a nightmare.

**Helm** solves this. It is the "apt-get" or "npm" for Kubernetes. It allows you to bundle related YAML files into a single package called a **Chart**.

-----

## The "Cookie Cutter" Analogy

Think of your Kubernetes YAML files as "Cookies."

  * **Without Helm:** You hand-craft every single cookie (YAML file). If you need 10 cookies, you write 10 files. If you want to change the flavor, you edit 10 files.
  * **With Helm:** You create a **Mold** (Template).
      * You pour "dough" (Configuration Values) into the mold.
      * Helm presses the button and generates perfect YAML files for you every time.

-----

## Core Concepts

| Term | Definition |
| :--- | :--- |
| **Chart** | The package itself. A directory containing templates and metadata. (The "Mold") |
| **Values** | The configuration settings. (The "Dough"). Defined in `values.yaml`. |
| **Release** | An instance of a Chart running in your cluster. (The "Cookie"). You can install the same chart 5 times to get 5 different releases. |
| **Repository** | A place to store and share Charts (like Docker Hub, but for Helm). |

-----

## Helm Architecture (v3+)

**Forget Tiller.**
In the old days (Helm v2), there was a component called Tiller that ran inside your cluster with full admin rights. It was a massive security hole.

**Helm v3** is client-only.
When you run `helm install`, the Helm binary on your laptop:

1.  Reads your local charts/values.
2.  Generates the final YAML manifests.
3.  Talks directly to the Kubernetes API to apply them.
4.  Stores the "state" of the release in a Kubernetes Secret (in the same namespace).

-----

## The Directory Structure

When you run `helm create my-chart`, you get this standard layout:

```text
my-chart/
  Chart.yaml          # Metadata (Name, Version, Dependencies)
  values.yaml         # Default configuration (The "Variables")
  charts/             # Sub-charts (Dependencies go here)
  templates/          # The Logic
    deployment.yaml   # A Deployment, but with {{ placeholders }}
    service.yaml      # A Service, but with {{ placeholders }}
    _helpers.tpl      # Reusable code snippets
```

-----

## The Templating Engine

Helm uses the **Go Templating** language. This is what makes it powerful.

**1. The Template (`templates/deployment.yaml`)**
Instead of hardcoding "nginx", you use a variable.

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: {{ .Values.replicaCount }}
  containers:
    - name: my-app
      image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
```

**2. The Values (`values.yaml`)**
You define the defaults here.

```yaml
replicaCount: 3
image:
  repository: nginx
  tag: 1.21
```

**3. The Result (Rendered Manifest)**
Helm combines them to create valid Kubernetes YAML.

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 3
  containers:
    - name: my-app
      image: "nginx:1.21"
```

-----

## Daily Commands (Cheat Sheet)

### 1\. Installation

Install a chart from a repo (like Bitnami).

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install my-redis bitnami/redis
```

### 2\. Customizing Values

You almost never use the default values. You override them.

```bash
# Option A: Command line flags (good for quick tests)
helm install my-web ./my-chart --set replicaCount=5

# Option B: Custom values file (Best Practice)
helm install my-web ./my-chart -f values-prod.yaml
```

### 3\. Upgrading (Day 2 Operations)

Changed a value? Just run upgrade. Helm calculates the "diff" and patches the resources.

```bash
helm upgrade my-web ./my-chart -f values-prod.yaml
```

### 4\. Rollbacks (The "Undo" Button)

Did your upgrade break production? Helm keeps a history of every release.

```bash
helm history my-web
# REVISION    UPDATED     STATUS      CHART
# 1           ...         SUPERSEDED  my-chart-1.0
# 2           ...         DEPLOYED    my-chart-1.1

# Rollback to revision 1 immediately
helm rollback my-web 1
```

-----

## Managing Dependencies

In Helm v3, you declare dependencies in `Chart.yaml` (not `requirements.yaml`).

```yaml
# Chart.yaml
dependencies:
  - name: postgresql
    version: 10.x.x
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
```

Then run:

```bash
helm dependency build
```

This downloads the postgres chart into your `charts/` folder automatically.

-----

## Summary

  * **Helm** is the standard for packaging Kubernetes apps.
  * It separates **Configuration** (`values.yaml`) from **Code** (`templates/`).
  * It handles **Dependencies** (installing a database alongside your app).
  * It provides **Revision History** and **Rollbacks** out of the box.
  * **Pro Tip:** Always use `--dry-run --debug` before installing a complex chart to see exactly what YAML will be generated without actually applying it.