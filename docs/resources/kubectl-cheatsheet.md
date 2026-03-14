---
icon: lucide/notebook-pen
title: Kubectl Cheat Sheet (Common Kubernetes Commands)
description: A practical kubectl cheat sheet with commonly used commands for inspecting, debugging, and managing Kubernetes resources.
hide:
 - footer
---

# Kubectl Cheat Sheet

A practical command reference for day-1 and day-2 Kubernetes operations.

## Context and namespace safety

```bash
kubectl config get-contexts
kubectl config current-context
kubectl config use-context <context>
kubectl config set-context --current --namespace=<namespace>
```

Check your active target before write operations.

## Core read commands

```bash
kubectl get pods -A -o wide
kubectl get deploy,sts,ds -A
kubectl get svc -A
kubectl get events -A --sort-by=.metadata.creationTimestamp
kubectl top nodes
kubectl top pods -A
```

## Debugging commands

```bash
kubectl describe pod <pod> -n <ns>
kubectl logs <pod> -n <ns> --all-containers
kubectl logs <pod> -n <ns> --all-containers --previous
kubectl exec -it <pod> -n <ns> -- sh
kubectl debug -it <pod> -n <ns> --image=busybox:1.36 --target=<container>
```

## Deployment operations

```bash
kubectl apply -f app.yaml
kubectl rollout status deploy/<name> -n <ns>
kubectl rollout history deploy/<name> -n <ns>
kubectl rollout undo deploy/<name> -n <ns>
kubectl scale deploy/<name> --replicas=<count> -n <ns>
```

## Service and network checks

```bash
kubectl get svc -n <ns>
kubectl get endpointslices -n <ns>
kubectl exec -it <pod> -n <ns> -- nslookup <service>
kubectl exec -it <pod> -n <ns> -- wget -qO- http://<service>:<port>
```

## RBAC and access checks

```bash
kubectl auth can-i get pods -n <ns>
kubectl auth can-i create deployments --as=<identity> -n <ns>
kubectl get role,rolebinding -n <ns>
kubectl get clusterrole,clusterrolebinding
```

## JSONPath quick lookups

```bash
kubectl get pods -A -o jsonpath='{.items[*].spec.nodeName}'
kubectl get pod <pod> -n <ns> -o jsonpath='{.status.podIP}'
kubectl get pods -A -o jsonpath='{.items[*].spec.containers[*].image}'
```

## Cleanup and maintenance

```bash
kubectl delete pod --field-selector=status.phase=Failed -A
kubectl api-resources
kubectl explain deployment.spec.strategy
```

## Suggested local aliases

```bash
alias k='kubectl'
alias kg='kubectl get'
alias kga='kubectl get all -A'
alias kd='kubectl describe'
alias kl='kubectl logs'
```

## Related Concepts

- [Troubleshooting](../operations/troubleshooting.md)
- [Maintenance](../operations/maintenance.md)
- [RBAC](../security/rbac.md)
