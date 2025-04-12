---
icon: material/key-outline
---

# ConfigMaps & Secrets

Kubernetes lets you decouple application configuration from container images using two key resources:

- **ConfigMaps** for non-sensitive data (settings, URLs, etc.)
- **Secrets** for sensitive data (passwords, tokens, certificates)

These resources allow you to define environment-specific values once and reuse them across multiple workloads — improving security, consistency, and portability.

---

## ConfigMaps (Non-Sensitive Configuration)

A **ConfigMap** is a key-value store for plain-text configuration. Use it for:

- Environment-specific settings (`LOG_LEVEL`, `API_BASE_URL`)
- Hostnames, ports, feature flags
- Complete config files or CLI arguments

### Example

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  LOG_LEVEL: debug
  DB_HOST: db.default.svc.cluster.local
```

---

## Secrets (Sensitive Data)

**Secrets** are also key-value stores — but intended for private data such as:

- Passwords, tokens, and API keys
- SSH keys or TLS certs
- Docker registry credentials

Kubernetes encodes all Secret values in **base64**. Note: this is for transport, not security.

### Example

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  DB_PASSWORD: c3VwZXJzZWNyZXQ=
```

> ⓘ Decode with: `echo c3VwZXJzZWNyZXQ= | base64 -d`  
> Use `stringData:` if you want Kubernetes to handle the encoding automatically.

---

## Ways to Use ConfigMaps and Secrets

There are three main ways to expose values inside your Pods:

---

### 1. Environment Variables

Inject all key-value pairs from a ConfigMap or Secret:

```yaml
envFrom:
  - configMapRef:
      name: app-config
  - secretRef:
      name: db-secret
```

Or reference individual keys:

```yaml
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: db-secret
        key: DB_PASSWORD
```

---

### 2. Mounted Volumes

Map each key to a file inside the container:

```yaml
volumes:
  - name: config-vol
    configMap:
      name: app-config
containers:
  - name: app
    volumeMounts:
      - name: config-vol
        mountPath: /etc/config
```

In the container, this results in:

```
/etc/config/LOG_LEVEL
/etc/config/DB_HOST
```

You can do the same for Secrets:

```yaml
volumes:
  - name: creds
    secret:
      secretName: db-secret
```

> ⚠️ Secrets mounted as files on disk are **only base64-decoded**. They are **not encrypted** unless you've enabled encryption at rest.

---

### 3. CLI Arguments or Command Overrides

```yaml
containers:
  - name: app
    image: myapp
    args:
      - "--log-level=$(LOG_LEVEL)"
    env:
      - name: LOG_LEVEL
        valueFrom:
          configMapKeyRef:
            name: app-config
            key: LOG_LEVEL
```

---

## Best Practices

- Use **ConfigMaps** for plain-text configuration and **Secrets** for anything private.
- Use **RBAC** to control access to Secrets.
- Enable **encryption at rest** for Secret resources (`EncryptionConfiguration`).
- Avoid committing secrets to Git — even in base64 form.
- Use tools like **Sealed Secrets**, **Vault**, or **external-secrets** to integrate with cloud-native secrets managers.

---

## Summary

- **ConfigMaps** store non-sensitive values like app settings and hostnames.
- **Secrets** store sensitive data like passwords and certificates — encoded, but not encrypted by default.
- Both can be used via environment variables, mounted volumes, or command overrides.
- Combine with proper RBAC and encryption settings for production use.