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
kubectl logs <pod> -n <ns> -c <container> -f          # follow live
kubectl exec -it <pod> -n <ns> -- sh
kubectl debug -it <pod> -n <ns> --image=busybox:1.36 --target=<container>
kubectl port-forward pod/<pod> 8080:8080 -n <ns>       # local tunnel to pod
kubectl port-forward svc/<svc> 8080:80 -n <ns>         # local tunnel to service
kubectl cp <pod>:/path/to/file ./local-file -n <ns>    # copy file from pod
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

## Patching resources

```bash
kubectl patch deployment web -n <ns> -p '{"spec":{"replicas":5}}'
kubectl patch node <node> -p '{"spec":{"unschedulable":true}}'
kubectl set image deployment/web web=ghcr.io/example/web:v2.0.0 -n <ns>
kubectl label pod <pod> -n <ns> app=debug --overwrite
kubectl annotate deployment web -n <ns> kubernetes.io/change-cause="v2 rollout"
```

## Cleanup and maintenance

```bash
kubectl delete pod --field-selector=status.phase=Failed -A
kubectl delete pod <pod> -n <ns> --force --grace-period=0   # force-delete stuck pod
kubectl api-resources
kubectl api-resources --namespaced=false                     # cluster-scoped only
kubectl explain deployment.spec.strategy
kubectl cluster-info
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
