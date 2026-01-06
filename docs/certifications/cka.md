---
icon: lucide/badge-info
---

# Certified Kubernetes Administrator (CKA)

The **Certified Kubernetes Administrator (CKA)** exam tests your ability to install, configure, and manage Kubernetes clusters in real-world scenarios. It focuses heavily on system-level operations, cluster components, and day-to-day administrator tasks.

---

## Exam Overview

- **Format**: Hands-on, performance-based lab
- **Duration**: 2 hours
- **Passing score**: 66%
- **Price**: $395 USD (includes one retake)
- **Open book**: Access to [kubernetes.io/docs](https://kubernetes.io/docs) and [GitHub](https://github.com/kubernetes)

---

## Domains & Weights

| Domain                              | Weight |
|-------------------------------------|--------|
| Cluster Architecture, Installation & Configuration | 25%   |
| Workloads & Scheduling              | 15%   |
| Services & Networking               | 20%   |
| Storage                             | 10%   |
| Troubleshooting                     | 30%   |

---

## What You Should Master

### 1. Cluster Architecture & Setup (25%)

- `kubeadm init`, `join`, `reset`
- Control plane components: API server, scheduler, controller manager
- Node components: kubelet, kube-proxy, container runtime
- `kubectl config` + kubeconfig structure
- Certificate management (CA, client certs)
- `etcdctl` backup and restore
- Static Pods and manifests in `/etc/kubernetes/manifests`
- Taints and tolerations

### 2. Workloads & Scheduling (15%)

- Deployments, ReplicaSets, Jobs, CronJobs
- Labels, selectors, and affinity/anti-affinity rules
- Taints, tolerations, and node selectors
- DaemonSets

### 3. Services & Networking (20%)

- ClusterIP, NodePort, LoadBalancer
- CoreDNS troubleshooting
- NetworkPolicies (basic understanding)
- Ingress (YAML-level familiarity)
- Pod-to-Pod communication

### 4. Storage (10%)

- Volumes and volumeMounts
- PersistentVolumes (PV) and PersistentVolumeClaims (PVC)
- StorageClasses
- AccessModes and reclaim policies

### 5. Troubleshooting (30%)

- Pod/container status (`kubectl describe`, logs, events)
- `kubectl exec`, `port-forward`
- CrashLoopBackOff, ImagePullBackOff
- Control plane failure detection (kubelet, etcd, API server)
- Networking and DNS issues
- Resource scheduling issues (taints, affinity, nodeSelector)
- CNI problems

---

## Practice Tips

- Set up a local cluster using `kubeadm` (or use labs like Killer.sh)
- Use `kubectl explain` often to understand object structure
- Use `kubectl -n kube-system get pods` to monitor system health
- Alias these commands:

```bash
alias k=kubectl
alias kgp='kubectl get pods'
alias kaf='kubectl apply -f'
```

- Practice writing manifests quickly with:

```bash
kubectl run nginx --image=nginx --dry-run=client -o yaml
```

- Use `kubectl edit` and `kubectl patch` to modify resources live

---

## Test Environment Tips

- Open multiple terminal tabs (one for docs, one for kubectl)
- Bookmark key doc pages:

    - [Install tools](https://kubernetes.io/docs/setup/tools/)
    - [Tasks → Configure Pods](https://kubernetes.io/docs/tasks/)
    - [Reference](https://kubernetes.io/docs/reference/)
    
- Use `/etc/kubernetes/manifests/` for static Pod edits
- Save `etcd` backup and restore syntax

---

## Recommended Resources

- [Kubernetes Official Docs](https://kubernetes.io/docs/)
- [Killer.sh Simulator (free with CKA)](https://killer.sh)
- [KodeKloud CKA Course](https://kodekloud.com/p/certified-kubernetes-administrator/)
- [Linux Foundation CKA Training](https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/)
- [YouTube: TechWorld with Nana – CKA Series](https://www.youtube.com/watch?v=X48VuDVv0do)

---

## Summary

The CKA exam simulates **real-world cluster admin tasks**. You’ll be troubleshooting, configuring, deploying, and debugging in a live cluster. With good YAML speed and familiarity with `kubectl`, you’ll be ready to pass with confidence.

Start with the fundamentals. Practice under time pressure. Know where to look in the docs.