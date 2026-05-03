---
icon: lucide/brick-wall-shield
title: Kubernetes Security Context Explained (Privileges, Users, and Capabilities)
description: Learn how Kubernetes security contexts control container privileges, user IDs, and Linux capabilities.
hide:
 - footer
---

# Security Context

Security context defines runtime hardening controls for pods and containers.

If RBAC protects API actions, security context protects the process behavior of running containers.

## Pod-level vs container-level settings

- pod-level settings apply to all containers by default
- container-level settings can override pod defaults

Common pod-level fields:

- `runAsUser`
- `runAsGroup`
- `fsGroup`

Common container-level fields:

- `allowPrivilegeEscalation`
- `readOnlyRootFilesystem`
- `capabilities`
- `seccompProfile`

## Hardened example

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hardened-app
spec:
  securityContext:
    runAsUser: 10001
    runAsGroup: 10001
    fsGroup: 10001
  containers:
    - name: app
      image: ghcr.io/example/app:v1.9.0
      securityContext:
        runAsNonRoot: true
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        seccompProfile:
          type: RuntimeDefault
        capabilities:
          drop:
            - ALL
      volumeMounts:
        - name: tmp
          mountPath: /tmp
  volumes:
    - name: tmp
      emptyDir: {}
```

## What each control helps prevent

- `runAsNonRoot`: blocks root process launch by default.
- `allowPrivilegeEscalation: false`: prevents setuid-based escalation paths (e.g. `sudo`, `su`).
- `capabilities.drop: [ALL]`: removes excess Linux privileges -- Linux grants ~40 capabilities to root processes by default; dropping all then adding back only what's needed is the correct approach.
- `readOnlyRootFilesystem`: reduces persistence options for attackers who gain code execution.
- `seccompProfile: RuntimeDefault`: constrains the system call surface to a safe default profile; reduces kernel attack surface.

## Privileged mode

`privileged: true` gives the container nearly all Linux capabilities and removes almost all kernel isolation between the container and the host. It should never be used in production workloads.

```yaml
# DANGEROUS - avoid unless absolutely required by node-level tooling
securityContext:
  privileged: true
```

If a tool claims it needs `privileged: true`, investigate whether it actually requires specific capabilities (`NET_ADMIN`, `SYS_PTRACE`, etc.) that can be added selectively instead.

## AppArmor

AppArmor profiles restrict what system resources a container process can access (files, network, capabilities). Supported on nodes where AppArmor is installed:

```yaml
securityContext:
  appArmorProfile:
    type: RuntimeDefault  # uses the container runtime's default profile
```

Use `Localhost` to apply a specific named profile installed on the node. AppArmor works in tandem with seccomp to provide layered kernel hardening.

## Practical adoption tips

- standardize a secure default snippet for all teams
- add exceptions only with explicit review
- pair with Pod Security Admission so policy is enforceable
- test stateful workloads that need writable paths and tune mounts accordingly

## Summary

Security context is one of the highest impact workload hardening tools in Kubernetes. Apply strict defaults and make privilege escalation an explicit exception path.

## Related Security Concepts

- [Pod Security](psa.md)
- [RBAC](rbac.md)
- [Workloads](../workloads/pods-deployments.md)
