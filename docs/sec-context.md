---
icon: material/lock-outline
---

<h1>Security Contexts</h1>

A <strong>Security Context</strong> defines privilege and access control settings for a <strong>Pod</strong> or <strong>container</strong>. It’s how you harden workloads against privilege escalation, file system abuse, and host access.

---

<h2>Why It Matters</h2>

By default, containers can:

- Run as root inside the container
- Access shared volumes with writable access
- Escalate privileges if not blocked

Security contexts <strong>restrict and control</strong> this behavior — without needing to modify your image.

---

<h2>Pod vs Container Security Contexts</h2>

- <strong>Pod-level</strong> applies to all containers in the Pod
- <strong>Container-level</strong> overrides the Pod-level settings

---

<h2>Common Fields</h2>

| Field                  | Purpose                                          |
|------------------------|--------------------------------------------------|
| <code>runAsUser</code>            | Run as specific UID inside the container         |
| <code>runAsNonRoot</code>         | Force non-root user                             |
| <code>readOnlyRootFilesystem</code> | Prevent writing to root FS                  |
| <code>allowPrivilegeEscalation</code> | Block <code>setuid</code> or <code>sudo</code> actions            |
| <code>privileged</code>           | Gives access to host-level features (avoid)     |
| <code>capabilities</code>         | Add/drop Linux kernel capabilities              |

---

<h2>Example: Secure Container Context</h2>

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

<h2>Best Practices</h2>

 
- Always run containers as a non-root user (<code>runAsNonRoot: true</code>).
- Use <code>readOnlyRootFilesystem: true</code> for immutable containers.
- Drop all unnecessary Linux capabilities.
- Avoid privileged mode unless absolutely necessary.
- Use Pod-level security context for shared settings.
- Always review and lock down security contexts in production workloads.
- Start with the most restrictive settings and loosen only as needed.

---

<h2>Summary</h2>

 
- <strong>Security contexts</strong> are critical for hardening workloads.
- Use them to restrict privileges, enforce non-root, and block escalation.
- Combine with PodSecurityAdmission and RBAC for a defense-in-depth approach.

