---
icon: material/speedometer
---

In Kubernetes, **Resource Requests and Limits** allow you to control how much CPU and memory a container is guaranteed to receive, and how much it is allowed to consume at maximum. This is critical for achieving stability, performance, and fairness in shared clusters.

Resource requests and limits are specified for each container inside a Pod and are supported for the following resources:

- `cpu`
- `memory` (RAM)

---

## Resource Requests

A **request** defines the **minimum amount** of a resource that a container is guaranteed. The Kubernetes scheduler uses this value to decide **which node** to place the Pod on, ensuring the node has enough available capacity.

If a node does not have the requested amount of resources available, the Pod will not be scheduled on that node.

### Example:

```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "250m"
```

This container requests 128Mi of RAM and 250 millicores (0.25 cores) of CPU.

---

## Resource Limits

A **limit** defines the **maximum amount** of a resource that a container can use.

- For **CPU**: If a container tries to use more than the limit, it is throttled.
- For **memory**: If usage exceeds the limit, the container is **terminated (OOMKilled)** and may be restarted.

### Example:

```yaml
resources:
  limits:
    memory: "256Mi"
    cpu: "500m"
```

This restricts the container to a maximum of 256Mi RAM and 0.5 CPU cores.

---

## Full Example

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: resource-demo
spec:
  containers:
  - name: app
    image: nginx
    resources:
      requests:
        memory: "128Mi"
        cpu: "250m"
      limits:
        memory: "256Mi"
        cpu: "500m"
```

---

## Why It Matters

| Benefit                        | Description                                                                 |
|-------------------------------|-----------------------------------------------------------------------------|
| Stable Scheduling             | Requests ensure pods land on nodes with adequate resources                  |
| Fair Resource Distribution    | Limits prevent one pod from starving others                                 |
| Cost Efficiency               | Enables autoscaling and bin-packing of workloads                            |
| Cluster Health                | Prevents runaway containers from overloading nodes                          |
| Predictable Performance       | Ensures each container has access to enough CPU and memory                  |

---

## Best Practices

- Always define both **requests** and **limits** — don't leave them blank.
- Requests should match expected steady-state usage.
- Limits should reflect maximum acceptable burst usage.
- Use **Vertical Pod Autoscaler (VPA)** in dynamic environments.
- Monitor actual usage with tools like `kubectl top`, Prometheus, or metrics server.

---

## Summary

Defining CPU and memory **requests** and **limits** is essential for building reliable and performant Kubernetes applications. It ensures your containers are scheduled properly, prevents noisy neighbor problems, and keeps your cluster healthy and efficient.