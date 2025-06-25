---
icon: material/gauge
---

<h1>Resource Requests & Limits</h1>

Kubernetes lets you control how much CPU and memory each container is <strong>guaranteed</strong> and <strong>allowed</strong> to use. This is done through <strong>resource requests</strong> and <strong>limits</strong> in the container spec.

---

<h2>Requests vs Limits</h2>

| Term     | Purpose                               | Scheduler Uses? | Enforced at Runtime? |
|----------|----------------------------------------|------------------|----------------------|
| <code>requests</code> | Minimum resources guaranteed to a container | ✅ Yes           | ❌ No               |
| <code>limits</code>   | Maximum resources a container can use       | ❌ No            | ✅ Yes              |

- <strong>Requests</strong> are used during scheduling. Kubernetes places Pods on nodes that can satisfy their requested resources.
- <strong>Limits</strong> prevent a container from exceeding a set threshold.

---

<h2>Example: CPU and Memory Settings</h2>

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

This guarantees the container gets <strong>at least 256Mi and 250 millicores</strong>, but it <strong>cannot exceed 512Mi or 500 millicores</strong>.

---

<h2>Why It Matters</h2>

- <strong>Too low requests</strong> → Your Pod may get scheduled on a crowded node and experience performance issues.
- <strong>No limits</strong> → A container can consume all resources and cause noisy neighbor problems.
- <strong>Too low limits</strong> → Can result in <strong>OOMKills</strong> or throttled CPU.

---

<h2>CPU Behavior</h2>

- If a container exceeds its <strong>CPU limit</strong>, it is throttled - not killed.
- If you don’t set a limit, the container may consume all available CPU.

---

<h2>Memory Behavior</h2>

- If memory <strong>usage exceeds the limit</strong>, the container is killed with an <strong>OOMKill</strong> (Out of Memory).
- Kubernetes does <strong>not restart it</strong> unless it's part of a higher-level controller (like a Deployment).

---

<h2>Best Practices</h2>

- Always set both **requests** and **limits** - especially for memory.
- Set realistic **requests** to ensure proper scheduling.
- Avoid overly restrictive limits unless you're debugging or need to enforce strict control.
- Use <strong>LimitRanges</strong> to enforce defaults and maximums in namespaces.
- Monitor Pod and Node usage to tune your settings.
- Set realistic requests and limits for every container. This keeps your cluster healthy and prevents resource hogs or accidental outages.

---

<h2>Summary</h2>
<ul>
<li><strong>Requests</strong> guarantee a minimum amount of resources for a container.</li>
<li><strong>Limits</strong> cap the maximum resources a container can use.</li>
<li>Always set both for predictable, stable workloads.</li>
</ul>
