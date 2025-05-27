---
icon: material/lock
---

**Pod Security Admission (PSA)** is the built-in mechanism in Kubernetes for enforcing security standards on Pods at the API level. Introduced in Kubernetes v1.22 and stable in v1.25, it replaced the deprecated PodSecurityPolicy (PSP) feature.

PSA evaluates Pod specifications during creation or update and applies policy controls based on predefined security profiles.

---

<h2>Key Concepts</h2>

PSA is implemented as an <strong>admission controller</strong> that checks incoming Pod specs and enforces or audits their compliance with a chosen security profile.

There are <strong>three policy levels</strong>, each defining a different set of security requirements:

| Level     | Description                                                                |
|-----------|----------------------------------------------------------------------------|
| <code>privileged</code> | No restrictions — full access to host features                         |
| <code>baseline</code>   | Minimally restrictive, prevents known high-risk settings               |
| <code>restricted</code> | Highly restrictive, follows best practices for multi-tenant hardening  |

Each namespace can have policies assigned in one of three <strong>modes</strong>:

| Mode     | Description                                                     |
|----------|-----------------------------------------------------------------|
| <code>enforce</code> | Reject non-compliant Pods                                     |
| <code>audit</code>   | Log violations but allow the Pod                              |
| <code>warn</code>    | Send warnings to the user, but allow the Pod                  |

---

<h2>Configuring PSA</h2>

PSA is enabled by default in modern Kubernetes clusters. You can configure policy levels on a <strong>per-namespace</strong> basis using labels.

<h3>Example: Apply <code>restricted</code> policy with all modes</h3>

```bash
kubectl label namespace secure-ns \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/enforce-version=latest \
  pod-security.kubernetes.io/audit=restricted \
  pod-security.kubernetes.io/audit-version=latest \
  pod-security.kubernetes.io/warn=restricted \
  pod-security.kubernetes.io/warn-version=latest
```

This enforces, audits, and warns against any pod that doesn’t meet the <code>restricted</code> policy level.

---

<h2>Policy Examples</h2>

Here are a few settings disallowed at each level:

| Setting                  | baseline | restricted |
|--------------------------|----------|------------|
| <code>hostNetwork: true</code>      | ❌       | ❌         |
| <code>privileged: true</code>       | ❌       | ❌         |
| <code>runAsNonRoot: false</code>    | ✅       | ❌         |
| `allowPrivilegeEscalation: true` | ✅  | ❌         |
| `capabilities.add: ["ALL"]` | ❌    | ❌         |

---

<h2>Summary</h2>

- <strong>Pod Security Admission (PSA)</strong> enforces security standards for Pods at the API level.
- Use PSA to prevent risky Pod configurations and enforce best practices per namespace.
- Choose the right policy level and mode for your environment.

!!! tip
    Start with <code>baseline</code> or <code>restricted</code> in new namespaces, and use <code>audit</code> and <code>warn</code> modes to monitor for violations before enforcing.

---

## When to Use Each Profile

| Use Case                        | Recommended Level |
|----------------------------------|--------------------|
| Development namespace           | baseline           |
| CI/CD pipelines                 | baseline           |
| Multi-tenant cluster workloads  | restricted         |
| System workloads or privileged apps | privileged     |

