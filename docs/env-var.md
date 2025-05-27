---
icon: material/cogs
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

## Probes Overview

Kubernetes uses **probes** to check if a container is:

- **Alive** (liveness probe): Whether the app should be restarted
- **Ready** (readiness probe): Whether the app is ready to receive traffic
- **Started** (startup probe): Whether the app has finished starting up

Each probe runs a check (HTTP request, TCP socket, or command) and takes action based on success or failure.

---

## Liveness Probe

Restarts the container if the probe fails repeatedly.

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10
```

---

## Readiness Probe

Used to signal when the container is ready to receive traffic. If the probe fails, the Pod is removed from Service endpoints.

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10
```

---

## Startup Probe

Useful for applications that take a long time to initialize. Prevents premature liveness failures during startup.

```yaml
startupProbe:
  httpGet:
    path: /startup
    port: 8080
  failureThreshold: 30
  periodSeconds: 10
```

---

## Best Practices

- Use **readiness probes** to avoid routing traffic to unready pods.
- Use **liveness probes** for self-healing on deadlocks or hung apps.
- Use **startup probes** for slow-starting applications.
- Avoid setting `initialDelaySeconds` too low — allow the app to start first.
- Prefer HTTP or command probes for rich diagnostics.
- Avoid hardcoding values inside your images. Use environment variables, ConfigMaps, and Secrets for maximum flexibility and security.

---

<h2>Summary</h2>
<ul>
<li><strong>Environment variables</strong> make your containers configurable and portable.</li>
<li>Use ConfigMaps and Secrets for dynamic or sensitive values.</li>
<li>Probes help keep your apps healthy and ready for traffic.</li>
</ul>