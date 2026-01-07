---
icon: lucide/notebook-pen
title: Kubectl Cheat Sheet (Common Kubernetes Commands)
description: A practical kubectl cheat sheet with commonly used commands for inspecting, debugging, and managing Kubernetes resources.
hide:
  - footer
---

# Kubectl Cheatsheat

This isn't just a list of commands; it's a collection of the workflows you use every day.
From switching contexts to debugging crashed pods, this reference cuts through the noise.

-----

## Setup & Configuration

Before you do anything, make sure you are talking to the right cluster.

| Action | Command |
| :--- | :--- |
| **List Contexts** | `kubectl config get-contexts` |
| **Switch Cluster** | `kubectl config use-context <context_name>` |
| **Switch Namespace** | `kubectl config set-context --current --namespace=<ns>` |
| **View Config** | `kubectl config view --minify` |
| **Who Am I?** | `kubectl auth can-i create pods` (Check your own permissions) |

!!! tip "Pro Tip"
    Install `kubectx` and `kubens`. Stop typing long commands. Use these standard tools:

    * `kubectx my-cluster` (Switch cluster)
    * `kubens my-namespace` (Switch namespace)

-----

## Inspection & Observation

The "Read" operations. Most of your day is spent here.

| Object | Command | Notes |
| :--- | :--- | :--- |
| **Pods** | `kubectl get pods -o wide` | Shows Node IP and Pod IP. |
| **All Namespaces** | `kubectl get pods -A` | The "God View" of the cluster. |
| **Watch Live** | `kubectl get pods -w` | Live stream of status changes. |
| **Events** | `kubectl get events --sort-by=.metadata.creationTimestamp` | **Crucial:** Shows errors chronologically. |
| **Labels** | `kubectl get pods --show-labels` | Debug Selector issues. |
| **Resource Usage** | `kubectl top pod --containers` | Requires metrics-server. |

-----

## Debugging (The "Fix It" Phase)

When things go red, run these in order.

| Scenario | Command | Why use it? |
| :--- | :--- | :--- |
| **Why did it die?** | `kubectl describe pod <pod>` | Read the "Events" section at the bottom. |
| **App Logs** | `kubectl logs <pod>` | Standard output of the app. |
| **Previous Logs** | `kubectl logs <pod> --previous` | **Gold.** See logs of the container *before* it crashed. |
| **Specific Container**| `kubectl logs <pod> -c <sidecar>` | For multi-container pods (like Service Mesh). |
| **Shell Access** | `kubectl exec -it <pod> -- /bin/sh` | Jump inside to check files/network. |
| **Distroless Debug** | `kubectl debug -it <pod> --image=busybox --target=<container>` | Attaches a shell to a locked-down pod. |

-----

## Creation & Modification

The "Write" operations.

| Action | Command |
| :--- | :--- |
| **Apply YAML** | `kubectl apply -f my-app.yaml` |
| **Restart App** | `kubectl rollout restart deployment/my-app` (Zero downtime\!) |
| **Scale Up** | `kubectl scale deployment/my-app --replicas=5` |
| **Edit Live** | `kubectl edit svc/my-service` (Opens in VI/Nano) |
| **Force Delete** | `kubectl delete pod <pod> --grace-period=0 --force` (Use responsibly\!) |
| **Quick Job** | `kubectl create job manual-job --image=busybox -- echo "Done"` |

-----

## Power User Tricks (JSONPath)

Stop using `grep`. Use native filtering to get exactly the data you need.

**1. Get only the Pod IPs:**

```bash
kubectl get pods -o jsonpath='{.items[*].status.podIP}'
```

**2. List all images running in the cluster:**

```bash
kubectl get pods -A -o jsonpath='{.items[*].spec.containers[*].image}'
```

**3. Find which node a specific pod is on:**

```bash
kubectl get pod my-pod -o jsonpath='{.spec.nodeName}'
```

**4. Decode a Secret instantly:**

```bash
kubectl get secret my-secret -o jsonpath='{.data.password}' | base64 -d
```

-----

## Housekeeping

Keep your cluster clean.

| Command | Description |
| :--- | :--- |
| `kubectl delete pod --field-selector=status.phase=Failed -A` | Delete all "Evicted" or "Failed" pods. |
| `kubectl api-resources` | List every object type your cluster supports. |
| `kubectl explain pod.spec.containers.livenessProbe` | **Documentation:** Read the manual for any field without leaving the terminal. |

-----

## Shell Aliases (Save Your Fingers)

Add these to your `.bashrc` or `.zshrc`. You will thank yourself later.

```bash
alias k="kubectl"
alias kg="kubectl get"
alias kgp="kubectl get pods"
alias kga="kubectl get pods -A"
alias kd="kubectl describe"
alias kdel="kubectl delete"
alias klogs="kubectl logs"
alias kex="kubectl exec -it"
```

Now you can just type:
`kex my-pod -- bash`