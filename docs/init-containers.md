---
icon: octicons/container-16
---

Init Containers are specialized containers in Kubernetes that run **before** the main application containers in a Pod. They are designed for initialization logic that must complete successfully before the main container starts.

They are defined alongside normal containers in a Pod spec and are run sequentially. If any Init Container fails, Kubernetes restarts the entire Pod until all Init Containers succeed.

---

## Why Use Init Containers?

Init Containers allow you to separate **startup logic** from your main application container. This makes application containers cleaner, more reusable, and easier to test.

### Common Use Cases:
- Waiting for a service or database to become available
- Initializing config files or downloading data
- Setting up permissions or configuration for shared volumes
- Performing preflight checks or migrations

---

## How Init Containers Work

- Defined under `.spec.initContainers` in a Pod or Deployment spec
- Run **before** any containers in `.spec.containers`
- Run **sequentially**, not in parallel
- Each must complete successfully before the next one runs
- The main containers start only after all Init Containers have finished

---

## Example: Waiting for a Service

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: init-demo
spec:
  initContainers:
  - name: wait-for-db
    image: busybox
    command: ['sh', '-c', 'until nc -z my-db 5432; do echo waiting for db; sleep 2; done']
  containers:
  - name: app
    image: my-app:latest
    ports:
    - containerPort: 8080
```

This Init Container waits until `my-db:5432` is reachable before starting the application container.

---

## Sharing Data with Main Containers

Init Containers can write data to **shared volumes** (e.g., `emptyDir`) that are also mounted by the main containers. This allows them to prepare data or configuration at runtime.

### Example: Write config to a shared volume

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: init-volume-demo
spec:
  volumes:
  - name: shared-data
    emptyDir: {}
  initContainers:
  - name: init
    image: busybox
    command: ['sh', '-c', 'echo hello > /data/message']
    volumeMounts:
    - name: shared-data
      mountPath: /data
  containers:
  - name: app
    image: busybox
    command: ['cat', '/data/message']
    volumeMounts:
    - name: shared-data
      mountPath: /data
```

The Init Container writes a message to a file in a shared volume. The main container reads that file.

---

## Key Points and Best Practices

- Keep Init Containers small and focused
- Use separate images for Init Containers if needed
- Prefer using Init Containers over startup logic inside your app code
- Use retry logic or exponential backoff for dependencies that may take time to become ready

---

## Summary

Init Containers are ideal for separating initialization logic from application logic. They improve modularity, reusability, and clarity of your Pod specifications. You can use them for dependency checks, environment setup, or preparing data for main containers.