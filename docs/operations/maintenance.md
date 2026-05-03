---
icon: lucide/circle-fading-arrow-up
title: Kubernetes Cluster Maintenance Explained (Upgrades, Drains, and Care)
description: Learn how to perform Kubernetes cluster maintenance tasks safely, including node draining, upgrades, and lifecycle management.
hide:
 - footer
---

# Cluster Maintenance

Cluster maintenance should be repeatable, staged, and reversible.

This page focuses on safe day-2 operations for upgrades, node work, and certificate hygiene.

## 1) Backup and Recovery Readiness

Before control-plane changes, verify your recovery path.

For kubeadm-managed control planes, etcd snapshot workflow:

```bash
ETCDCTL_API=3 etcdctl snapshot save snapshot.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

ETCDCTL_API=3 etcdctl snapshot status snapshot.db
```

Also validate restore procedure in a non-production environment.

## 2) Upgrade Sequencing

Follow Kubernetes version skew policy and vendor guidance.

Typical order:

1. Upgrade control plane components (kube-apiserver, controller-manager, scheduler).
2. Upgrade worker nodes in controlled batches.
3. Validate workload health between phases.

**Version skew rules (Kubernetes 1.28+):**

- `kubelet` may be up to **3 minor versions** behind the API server (e.g. apiserver at 1.30, kubelet at 1.27 is supported).
- `kube-proxy` must match the kubelet version on its node.
- `kubectl` should be within one minor version of the API server.

Never run kubelet **newer** than the API server -- this is unsupported and will cause unpredictable behavior.

## 3) Node Maintenance Workflow

When patching or upgrading a node:

1. Cordon the node.
2. Drain workloads safely.
3. Perform maintenance.
4. Validate node health.
5. Uncordon node.

```bash
kubectl cordon node-01
kubectl drain node-01 --ignore-daemonsets --delete-emptydir-data
# perform maintenance
kubectl uncordon node-01
```

Use PodDisruptionBudgets (PDBs) to protect workloads during drains. A PDB specifies how many replicas must remain available:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: web
```

Without a PDB, `kubectl drain` may evict all pods of a deployment simultaneously. With one, drain waits until the PDB constraint can be satisfied before proceeding. This is essential for stateful workloads and services where zero downtime matters.

## 4) kubeadm Node Upgrade Pattern

Use target versions explicitly rather than hardcoded tutorial versions.

```bash
# control plane and worker workflows differ; follow kubeadm docs for your target version
sudo apt-get update
sudo apt-get install -y kubeadm=<target-version>
sudo kubeadm upgrade node
sudo apt-get install -y kubelet=<target-version> kubectl=<target-version>
sudo systemctl restart kubelet
```

On RPM-based systems, use equivalent package manager commands.

## 5) Certificate Lifecycle

On kubeadm clusters, many internal certificates default to one-year validity.

Check regularly:

```bash
kubeadm certs check-expiration
```

Renew as needed and restart affected components per kubeadm guidance:

```bash
kubeadm certs renew all
```

## 6) OS and Kernel Patching

- Avoid unmanaged fleet-wide auto reboots.
- Reboot in waves.
- Use maintenance automation (for example, Kured) with disruption controls.

## 7) Post-Maintenance Validation

```bash
kubectl get nodes
kubectl get pods -A
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

Validate:

- node readiness
- control-plane stability
- workload SLO indicators
- ingress and core service paths

## Summary

- Maintenance is an operational workflow, not a one-off command.
- Backups and restore drills are part of upgrade safety.
- Respect version skew and execute upgrades in stages.
- Use cordon/drain/uncordon consistently.
- Keep certificate and OS patch routines scheduled and observable.
