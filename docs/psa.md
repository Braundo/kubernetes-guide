---
icon: material/lock
---

**Pod Security Admission (PSA)** is the built-in mechanism in Kubernetes for enforcing security standards on Pods at the API level. Introduced in Kubernetes v1.22 and stable in v1.25, it replaced the deprecated PodSecurityPolicy (PSP) feature.

PSA evaluates Pod specifications during creation or update and applies policy controls based on predefined security profiles.

---

## Key Concepts

PSA is implemented as an **admission controller** that checks incoming Pod specs and enforces or audits their compliance with a chosen security profile.

There are **three policy levels**, each defining a different set of security requirements:

| Level     | Description                                                                |
|-----------|----------------------------------------------------------------------------|
| `privileged` | No restrictions — full access to host features                         |
| `baseline`   | Minimally restrictive, prevents known high-risk settings               |
| `restricted` | Highly restrictive, follows best practices for multi-tenant hardening  |

Each namespace can have policies assigned in one of three **modes**:

| Mode     | Description                                                     |
|----------|-----------------------------------------------------------------|
| `enforce` | Reject non-compliant Pods                                     |
| `audit`   | Log violations but allow the Pod                              |
| `warn`    | Send warnings to the user, but allow the Pod                  |

---

## Configuring PSA

PSA is enabled by default in modern Kubernetes clusters. You can configure policy levels on a **per-namespace** basis using labels.

### Example: Apply `restricted` policy with all modes

```bash
kubectl label namespace secure-ns \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/enforce-version=latest \
  pod-security.kubernetes.io/audit=restricted \
  pod-security.kubernetes.io/audit-version=latest \
  pod-security.kubernetes.io/warn=restricted \
  pod-security.kubernetes.io/warn-version=latest
```

This enforces, audits, and warns against any pod that doesn’t meet the `restricted` policy level.

---

## Policy Examples

Here are a few settings disallowed at each level:

| Setting                  | baseline | restricted |
|--------------------------|----------|------------|
| `hostNetwork: true`      | ❌       | ❌         |
| `privileged: true`       | ❌       | ❌         |
| `runAsNonRoot: false`    | ✅       | ❌         |
| `allowPrivilegeEscalation: true` | ✅  | ❌         |
| `capabilities.add: ["ALL"]` | ❌    | ❌         |

For full definitions, refer to the Kubernetes Pod Security Standards.

---

## When to Use Each Profile

| Use Case                        | Recommended Level |
|----------------------------------|--------------------|
| Development namespace           | baseline           |
| CI/CD pipelines                 | baseline           |
| Multi-tenant cluster workloads  | restricted         |
| System workloads or privileged apps | privileged     |

---

## Best Practices

- Apply PSA labels early in your cluster setup.
- Use `audit` and `warn` modes first to test compliance before enforcing.
- Combine PSA with RBAC and admission webhooks for layered security.
- Use `kubectl run` and `kubectl apply` in secure ways to avoid bypassing policy checks.
- Regularly review and adjust policy levels as your workloads evolve.

---

## Summary

Pod Security Admission (PSA) provides a native, stable way to enforce pod-level security standards in Kubernetes. By labeling namespaces with the appropriate levels and modes, you can create secure boundaries around workloads and minimize exposure to unsafe configurations.