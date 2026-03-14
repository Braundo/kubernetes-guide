---
icon: lucide/logs
title: Kubernetes Audit Logging Explained (Tracking and Investigating Activity)
description: Learn how Kubernetes audit logs work and how they help detect, investigate, and respond to security events.
hide:
 - footer
---

# Audit and Logging

Operational logging and API audit logging serve different goals. You need both.

- audit logs: who changed cluster state and when
- workload logs: what applications and components are doing at runtime

## Kubernetes API audit logging

Audit logs are produced by the API server according to an audit policy.

Common levels:

- `None`: skip
- `Metadata`: request metadata only
- `Request`: metadata plus request body
- `RequestResponse`: metadata plus request and response body

For most production systems, `Metadata` is the default and selected `Request` logging is added for high-value resources.

## Policy example

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
  - level: None
    users: ["system:kube-proxy"]
    verbs: ["watch"]
  - level: Request
    resources:
      - group: ""
        resources: ["configmaps"]
  - level: Metadata
```

Use caution with request and response body logging for sensitive resources such as secrets.

## Workload logging pipeline

Kubernetes does not persist logs for you. Container logs must be collected and shipped to durable storage.

Typical architecture:

- app logs to stdout and stderr
- node-level collector (DaemonSet) tails container logs
- central backend stores and indexes logs
- dashboards and alerts consume centralized data

## Incident response value

Audit plus workload logs provide full investigation context:

- who changed policy or deployment
- what changed in workload behavior
- when an issue started and how it propagated

## Practical controls

- set retention by data class and compliance requirements
- sanitize logs to avoid leaking credentials or tokens
- alert on sensitive action patterns, such as repeated secret access denial
- keep clock synchronization healthy across nodes for timeline accuracy

## Summary

Without audit logging, control plane actions are hard to reconstruct. Without workload logging, runtime failures are hard to explain. Production Kubernetes needs both pipelines running continuously.

## Related Security Concepts

- [RBAC](rbac.md)
- [Pod Security](psa.md)
- [Troubleshooting](../operations/troubleshooting.md)
