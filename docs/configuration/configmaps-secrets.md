---
icon: lucide/key-round
title: ConfigMaps and Secrets in Kubernetes (Configuration Management Explained)
description: Learn how ConfigMaps and Secrets store and inject configuration data into Pods, and best practices for managing sensitive values.
hide:
 - footer
---

# ConfigMaps and Secrets

Config and code should be separated.

In Kubernetes, ConfigMaps and Secrets are the standard resources for injecting runtime configuration into workloads.

- ConfigMap: non-sensitive configuration.
- Secret: sensitive data such as credentials and keys.

## ConfigMap Basics

Use ConfigMaps for values such as feature flags, endpoints, and app settings.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  LOG_LEVEL: info
  API_BASE_URL: https://api.internal.example
```

## Secret Basics

Use Secrets for credentials, tokens, and certificate material.

Prefer `stringData` for authoring convenience; Kubernetes will encode into `data`.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
stringData:
  DB_USERNAME: app
  DB_PASSWORD: supersecret
```

Base64 encoding is not encryption. Use encryption at rest for etcd and strict RBAC.

## Injection Patterns

### 1) Environment variables

```yaml
envFrom:
  - configMapRef:
      name: app-config
  - secretRef:
      name: db-secret
```

Or individual keys:

```yaml
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: db-secret
        key: DB_PASSWORD
```

### 2) Mounted files

```yaml
volumes:
  - name: config-vol
    configMap:
      name: app-config
containers:
  - name: app
    image: ghcr.io/example/app:1.0.0
    volumeMounts:
      - name: config-vol
        mountPath: /etc/app-config
        readOnly: true
```

Secret mount variant:

```yaml
volumes:
  - name: secret-vol
    secret:
      secretName: db-secret
```

## Update Behavior

- Environment variable injection is evaluated at container start.
- Mounted ConfigMap and Secret volumes can refresh over time.
- Applications may still need explicit reload behavior to pick up new values.

## Security Practices

- Do not store secrets in Git.
- Restrict Secret access with namespace-scoped RBAC.
- Enable etcd encryption at rest.
- Consider external secret managers and sync controllers for high-security environments.
- Use immutable ConfigMaps and Secrets where frequent mutation is not required.

## Operational Tips

```bash
kubectl get configmap app-config -o yaml
kubectl get secret db-secret -o yaml
kubectl describe pod <pod-name>
```

Use `kubectl describe pod` to verify projected env vars and mounted volumes.

## Related Concepts

- [Init Containers](../workloads/init-containers.md)
- [Security Contexts](../security/sec-context.md)
- [Resource Limits and Requests](limits-requests.md)
