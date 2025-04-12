---
icon: material/lock-outline
---

# Security Contexts

A **Security Context** defines privilege and access control settings for a **Pod** or **container**. It’s how you harden workloads against privilege escalation, file system abuse, and host access.

---

## Why It Matters

By default, containers can:

- Run as root inside the container
- Access shared volumes with writable access
- Escalate privileges if not blocked

Security contexts **restrict and control** this behavior — without needing to modify your image.

---

## Pod vs Container Security Contexts

- **Pod-level** applies to all containers in the Pod
- **Container-level** overrides the Pod-level settings

---

## Common Fields

| Field                  | Purpose                                          |
|------------------------|--------------------------------------------------|
| `runAsUser`            | Run as specific UID inside the container         |
| `runAsNonRoot`         | Force non-root user                             |
| `readOnlyRootFilesystem` | Prevent writing to root FS                  |
| `allowPrivilegeEscalation` | Block `setuid` or `sudo` actions            |
| `privileged`           | Gives access to host-level features (avoid)     |
| `capabilities`         | Add/drop Linux kernel capabilities              |

---

## Example: Secure Container Context

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
```

This setup:

- Ensures the container isn’t running as root
- Forces read-only filesystem
- Blocks privilege escalation and kernel capabilities

---

## Example: Pod-Level Context

```yaml
spec:
  securityContext:
    fsGroup: 2000
    runAsUser: 1000
```

- `fsGroup`: Sets file group ownership for mounted volumes
- Useful when containers need write access to shared volumes

---

## Avoid Privileged Mode

```yaml
securityContext:
  privileged: true
```

This gives full host access — avoid unless you know exactly what you’re doing (e.g., for a CNI plugin or host-level utility).

---

## Quick Hardening Checklist

- ✅ `runAsNonRoot: true`
- ✅ Drop all capabilities unless needed
- ✅ Use `readOnlyRootFilesystem`
- ✅ Avoid `privileged: true`
- ✅ Explicitly set `runAsUser` and `fsGroup` for file access

---

## Summary

- Security contexts define **runtime privileges** for Pods and containers
- Helps enforce **least privilege** and prevent lateral movement
- Combine with **PodSecurity Admission** and **RBAC** for layered defense