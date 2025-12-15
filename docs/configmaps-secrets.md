---
icon: material/key-outline
---

<h1>ConfigMaps & Secrets</h1>

Kubernetes lets you separate your app’s configuration from your container images using two special resources:

- <strong>ConfigMaps</strong> for non-sensitive data (like settings, URLs, etc.)
- <strong>Secrets</strong> for sensitive data (like passwords, tokens, certificates)

This makes your apps more secure, portable, and easier to manage.

---

<h2>ConfigMaps (Non-Sensitive Configuration)</h2>

A <strong>ConfigMap</strong> is a key-value store for plain-text configuration. Use it for:

- Environment settings (like <code>LOG_LEVEL</code>, <code>API_BASE_URL</code>)
- Hostnames, ports, feature flags
- Complete config files or CLI arguments

<h3>Example</h3>

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

<h2>Secrets (Sensitive Data)</h2>

<strong>Secrets</strong> are also key-value stores - but for private data:

- Passwords, tokens, API keys
- SSH keys or TLS certs
- Docker registry credentials

Kubernetes encodes all Secret values in <strong>base64</strong> (for transport, not real security).

<h3>Example</h3>

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  DB_PASSWORD: c3VwZXJzZWNyZXQ=
```

!!! tip
    Decode with `echo c3VwZXJzZWNyZXQ= | base64 -d`. Use `stringData:` if you want Kubernetes to handle encoding for you.

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

Kubernetes allows you to configure runtime behavior of containers using **environment variables**, and to monitor their health using **liveness** and **readiness probes**. These features are essential for building reliable, configurable, and observable applications in the cluster.

---

<h2>Environment Variables</h2>

You can pass key-value pairs into containers using environment variables. These can be hardcoded, referenced from ConfigMaps, Secrets, or even dynamically derived from field references.


### Static Environment Variables

```yaml
env:
  - name: LOG_LEVEL
    value: "debug"
```

### From ConfigMap

```yaml
envFrom:
  - configMapRef:
      name: app-config
```

Or individual keys:

```yaml
env:
  - name: APP_PORT
    valueFrom:
      configMapKeyRef:
        name: app-config
        key: port
```

### From Secret

```yaml
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: db-secret
        key: password
```

### From Pod Metadata

```yaml
env:
  - name: POD_NAME
    valueFrom:
      fieldRef:
        fieldPath: metadata.name
```

---



<h2>Using ConfigMaps & Secrets</h2>

You can mount ConfigMaps and Secrets as environment variables or files inside your Pods. This keeps your app configuration flexible and secure.

---

<h2>Best Practices</h2>
<ul>
<li><strong>Never store sensitive data in ConfigMaps.</strong> Use Secrets for anything private.</li>
<li><strong>Restrict access</strong> to Secrets using RBAC.</li>
<li><strong>Avoid hardcoding values</strong> in your manifests. Reference ConfigMaps and Secrets instead.</li>
<li><strong>Use external secret managers</strong> (like AWS Secrets Manager, HashiCorp Vault) for extra-sensitive data.</li>
</ul>

---

<h2>Summary</h2>
<ul>
<li><strong>ConfigMaps</strong>: For non-sensitive, environment-specific configuration.</li>
<li><strong>Secrets</strong>: For sensitive data, encoded for transport.</li>
<li>Both improve security, portability, and flexibility in your Kubernetes apps.</li>
</ul>
