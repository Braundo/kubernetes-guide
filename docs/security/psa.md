---
icon: lucide/file-lock
title: Kubernetes Pod Security Standards Explained (Restricted, Baseline, Privileged)
description: Learn how Kubernetes Pod Security Standards work and how to enforce secure workload configurations.
hide:
 - footer
---

# Pod Security

Pod Security Admission enforces Pod Security Standards at the namespace level.

It is the built-in replacement for the removed PodSecurityPolicy mechanism.

## Standard policy levels

- Privileged: minimal restrictions, for trusted system workloads only
- Baseline: blocks common privilege escalation patterns
- Restricted: strong hardening baseline for most production apps

## Admission modes

Namespace labels can set three behaviors:

- enforce: block non-compliant pods
- warn: allow but emit warnings to API clients
- audit: allow but record violations in audit logs

## Namespace labeling example

```bash
kubectl label ns payments \
  pod-security.kubernetes.io/enforce=baseline \
  pod-security.kubernetes.io/warn=restricted \
  pod-security.kubernetes.io/audit=restricted
```

This pattern is useful for staged migration: enforce baseline while surfacing restricted gaps.

## Version pinning

Pin policy versions to avoid unexpected behavior drift during control plane upgrades.

```bash
kubectl label ns payments \
  pod-security.kubernetes.io/enforce-version=v<cluster-minor> \
  pod-security.kubernetes.io/warn-version=v<cluster-minor> \
  --overwrite
```

Use your cluster's current minor version and update deliberately after validation.

## Typical restricted requirements

Workloads commonly need these settings to pass restricted policy:

- `runAsNonRoot: true`
- `allowPrivilegeEscalation: false`
- `seccompProfile.type: RuntimeDefault`
- capabilities dropped (`ALL` then selective add if needed)

## Operational rollout pattern

1. apply `warn` and `audit` for target level
2. fix violating workloads
3. switch `enforce` to target level
4. monitor admission failures and deployment pipelines

## Summary

Pod Security Admission gives a clear, native baseline for workload hardening. Use staged rollout and version pinning to avoid production surprises.

## Related Security Concepts

- [Security Context](sec-context.md)
- [RBAC](rbac.md)
- [Security Primer](security.md)
