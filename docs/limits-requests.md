---
icon: material/gauge
---

# Resource Requests & Limits

Kubernetes lets you control how much CPU and memory each container is **guaranteed** and **allowed** to use. This is done through **resource requests** and **limits** in the container spec.

---

## Requests vs Limits

| Term     | Purpose                               | Scheduler Uses? | Enforced at Runtime? |
|----------|----------------------------------------|------------------|----------------------|
| `requests` | Minimum resources guaranteed to a container | ✅ Yes           | ❌ No               |
| `limits`   | Maximum resources a container can use       | ❌ No            | ✅ Yes              |

- **Requests** are used during scheduling. Kubernetes places Pods on nodes that can satisfy their requested resources.
- **Limits** prevent a container from exceeding a set threshold.

---

## Example: CPU and Memory Settings

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

This guarantees the container gets **at least 256Mi and 250 millicores**, but it **cannot exceed 512Mi or 500 millicores**.

---

## Why It Matters

- **Too low requests** → Your Pod may get scheduled on a crowded node and experience performance issues.
- **No limits** → A container can consume all resources and cause noisy neighbor problems.
- **Too low limits** → Can result in **OOMKills** or throttled CPU.

---

## CPU Behavior

- If a container exceeds its **CPU limit**, it is throttled — not killed.
- If you don’t set a limit, the container may consume all available CPU.

---

## Memory Behavior

- If memory **usage exceeds the limit**, the container is killed with an **OOMKill** (Out of Memory).
- Kubernetes does **not restart it** unless it's part of a higher-level controller (like a Deployment).

---

## Best Practices

- Always set both **requests** and **limits** — especially for memory.
- Set realistic **requests** to ensure proper scheduling.
- Avoid overly restrictive limits unless you're debugging or need to enforce strict control.
- Use **LimitRanges** or **ResourceQuotas** to apply default or max values across a namespace.

---

## Summary

- **Requests** = what your container is guaranteed
- **Limits** = the hard ceiling your container can use
- Kubernetes uses requests for scheduling and limits for enforcement.
- Proper resource settings help with performance, predictability, and cluster stability.