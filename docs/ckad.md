---
icon: material/code-tags
---

# Certified Kubernetes Application Developer (CKAD)

The **CKAD** certification tests your ability to design, build, and run applications in Kubernetes. It's focused on **real-world usage of Kubernetes primitives** - deployments, configs, probes, volumes, and services - from a **developer's perspective**.

---

## 🧠 Exam Overview

- **Format**: Hands-on, browser-based lab
- **Duration**: 2 hours
- **Passing score**: 66%
- **Price**: $395 USD (includes one retake)
- **Open book**: Access to [kubernetes.io/docs](https://kubernetes.io/docs)

---

## 📋 Domains & Weights

| Domain                         | Weight |
|--------------------------------|--------|
| Core Concepts                  | 13%   |
| Configuration                  | 18%   |
| Multi-Container Pods           | 10%   |
| Observability                  | 18%   |
| Pod Design                     | 20%   |
| Services & Networking          | 13%   |
| State Persistence              | 8%    |

---

## ✅ What You Should Master

### 1. Core Concepts (13%)

- Pod lifecycle and restart policies
- YAML basics: `kind`, `metadata`, `spec`
- `kubectl explain`, `run`, `logs`, `exec`

---

### 2. Configuration (18%)

- ConfigMaps & Secrets (env and volumes)
- `env`, `envFrom`, `valueFrom`
- Probes: liveness, readiness, startup
- Resource `requests` and `limits`
- `initContainers`

---

### 3. Pod Design (20%)

- Deployments, ReplicaSets, Jobs, CronJobs
- Multi-container Pods (sidecar pattern)
- Labels & selectors
- Rolling updates & rollbacks

---

### 4. Multi-Container Pods (10%)

- Sharing volumes, network namespace
- Common patterns:
  - Sidecar (logging, proxy)
  - Adapter (log converter, translator)
  - Ambassador (external traffic entrypoint)

---

### 5. Observability (18%)

- `kubectl logs`, `describe`, `top`
- Events and debugging Pods
- Container exit codes and status
- Custom probes for health checks
- Monitoring concepts (but not setup)

---

### 6. Services & Networking (13%)

- ClusterIP, NodePort (no LoadBalancer config needed)
- Headless Services
- DNS-based Pod discovery
- Understanding service selectors

---

### 7. State Persistence (8%)

- Volumes and volumeMounts
- PersistentVolumeClaims (PVCs)
- AccessModes: `ReadWriteOnce`, `ReadOnlyMany`
- EmptyDir (for temporary scratch space)

---

## ⚙️ Practice Tips

- Alias often-used commands:

```bash
alias k=kubectl
alias kgp='kubectl get pods'
alias kaf='kubectl apply -f'
```

- Use dry-run + output:

```bash
kubectl run nginx --image=nginx --dry-run=client -o yaml
```

- Practice common configs:
  - YAML for Pods with ConfigMap/Secret env vars
  - Liveness and readiness probes
  - Multi-container Pod with shared volume

---

## 🧪 Test Environment Tips

- Open docs in one tab, terminal in another
- Bookmark these:
  - [Tasks](https://kubernetes.io/docs/tasks/)
  - [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
  - [Workloads Overview](https://kubernetes.io/docs/concepts/workloads/)
- Use `kubectl explain` to recall spec fields quickly
- Copy/paste manifest scaffolds from the docs to save time

---

## 📚 Recommended Resources

- [Kubernetes Official Docs](https://kubernetes.io/docs/)
- [Killer.sh Simulator](https://killer.sh)
- [KodeKloud CKAD Course](https://kodekloud.com/p/kubernetes-for-developers/)
- [Linux Foundation CKAD Training](https://training.linuxfoundation.org/certification/certified-kubernetes-application-developer-ckad/)
- [YouTube: TechWorld with Nana – CKAD Series](https://www.youtube.com/watch?v=d6WC5n9G_sM)

---

## Summary

The CKAD exam tests your **Kubernetes fluency as a developer**. You’ll create and configure Pods, manage configs and secrets, debug issues, and expose applications.

If you’re confident writing manifests and using `kubectl` with speed, you’re ready to pass.