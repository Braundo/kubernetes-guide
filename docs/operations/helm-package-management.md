---
icon: lucide/ship-wheel
title: Helm and Package Management in Kubernetes Explained
description: Learn how Helm works, how charts are structured, and how Helm simplifies application deployment in Kubernetes.
hide:
 - footer
---

# Helm

Helm is the standard package manager for Kubernetes applications.

It lets you template manifests, manage configuration per environment, and track release history for upgrade and rollback workflows.

## Core concepts

- Chart: package containing templates and metadata
- Values: input configuration for template rendering
- Release: deployed instance of a chart in a namespace
- Repository: distribution source for charts

## Typical chart structure

```text
my-chart/
  Chart.yaml
  values.yaml
  templates/
  charts/
```

## Install and upgrade workflow

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install redis bitnami/redis -n platform --create-namespace
helm upgrade redis bitnami/redis -n platform -f values-prod.yaml
```

## Safe change practices

Before applying upgrades:

```bash
helm lint ./my-chart
helm template my-app ./my-chart -f values-prod.yaml
helm upgrade my-app ./my-chart -f values-prod.yaml --dry-run --debug
```

After upgrade:

```bash
helm history my-app -n platform
helm rollback my-app 3 -n platform
```

## Values management guidance

- keep a base values file plus environment overlays
- avoid committing plaintext secrets in values files
- prefer immutable image tags for release reproducibility
- document required values and defaults for platform consumers

## Hooks

Helm hooks execute Jobs at defined lifecycle points: `pre-install`, `post-install`, `pre-upgrade`, `post-upgrade`, `pre-delete`, `post-delete`, and `pre-rollback`.

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migrate
  annotations:
    "helm.sh/hook": pre-upgrade
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": before-hook-creation
```

Hooks are commonly used for database migrations (`pre-upgrade`), smoke tests (`post-install`), and cleanup jobs (`post-delete`). Set `hook-delete-policy: before-hook-creation` to prevent accumulating old hook Jobs across releases.

## Dependency management

Declare chart dependencies in `Chart.yaml` and build them during CI or packaging.

```bash
helm dependency build ./my-chart
```

## Common operational mistakes

- changing chart templates and values simultaneously without test rendering
- treating Helm as imperative only, with no Git review process
- skipping rollback rehearsal for critical services

## Summary

Helm improves repeatability and release safety when combined with linting, templating checks, and disciplined values management.

## Related Concepts

- [Troubleshooting](troubleshooting.md)
- [Maintenance](maintenance.md)
- [Operators and CRDs](operators-crds.md)
