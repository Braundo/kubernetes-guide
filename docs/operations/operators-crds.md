---
icon: lucide/puzzle
title: Kubernetes Operators and CRDs Explained (Extending Kubernetes)
description: Learn how Custom Resource Definitions and Operators extend Kubernetes with domain-specific automation.
hide:
 - footer
---

# Operators and CRDs

CRDs extend the Kubernetes API. Operators add automation logic for those custom resources.

Together, they let teams model and automate complex domain workflows directly in Kubernetes.

## CRD basics

A CustomResourceDefinition introduces a new API type.

After a CRD is installed, users can create custom objects with normal Kubernetes workflows (`kubectl`, GitOps, admission policies, RBAC).

## Operator basics

An Operator is a controller that watches custom resources and reconciles desired state into concrete Kubernetes objects and operational actions.

Examples of operator-managed actions:

- bootstrapping clustered databases
- performing version-aware upgrades
- backup and restore orchestration
- failover and lifecycle management

## Why Operators are useful

For complex stateful systems, raw Deployments and StatefulSets are not enough to encode day-2 operations safely.

Operators capture domain runbook logic in code so it is repeatable and observable.

## High-level flow

```mermaid
flowchart LR
  A[Custom Resource] --> B[Operator Controller]
  B --> C[StatefulSet, Service, Secret, PVC]
  C --> D[Observed State]
  D --> B
```

## When to choose Helm vs Operator

- choose Helm for packaging and straightforward lifecycle
- choose Operator when continuous domain-specific reconciliation is required

Many platforms use both: Helm to install the operator, operator to manage the application lifecycle.

## Operational checks

```bash
kubectl get crd
kubectl get <custom-resource-plural> -A
kubectl describe <custom-resource-kind> <name> -n <namespace>
kubectl logs deploy/<operator-deployment> -n <operator-namespace>
```

## Governance considerations

- review CRD schema quality before adoption
- constrain operator RBAC to least privilege
- monitor operator upgrades like any control-plane dependency
- validate backup and restore behavior before production reliance

## Summary

CRDs and Operators make Kubernetes extensible and automatable for advanced platforms. Use them when lifecycle logic is too complex for static manifests alone.

## Related Concepts

- [StatefulSets](../workloads/statefulsets.md)
- [Maintenance](maintenance.md)
- [Security Primer](../security/security.md)
