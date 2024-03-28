---
icon: material/circle-small
---

## OS Upgrades

- By default, Nodes has 5 minutes to come back up before their Pods are killed
- When performing an OS upgrade, it’s best to `drain` the Node before upgrading, because it may take longer than 5 minutes
    - Use the `--ignore-daemonsets` flag
- Once the Node comes back up, you’ll have to `uncordon` the Node to make it available to schedule Pods again
- The `cordon` command simply marks the Node as un-schedulable (but does not drain the Pods from the Node)

## Cluster Upgrade Process

- It is ***not*** mandatory for all components to have the same version numbers
    - However, no components should have a *higher* version than the API Server
    - Controller Manager can be **one** version lower
    - Scheduler can be **one** version lower
    - Kubelet and Kube Proxy can each be **two** versions lower
    - Kubectl can be **one** version higher *OR* lower


- Kubernetes supports up to the **latest 3 minor versions**

- The recommended approach to upgrade is **one minor version at a time**

- Upgrade master nodes first

- Kubeadm **does not** manage Kubelets, which must be upgraded manually

- The output of `kubectl get nodes` shows the versions of the **Kubelets** on each node

Generalized steps for upgrading:

```bash
# show recommended version to ugprade to
kubeadm upgrade plan

# upgrade the kudeadm tool
apt-get upgrade -y kubeadm=<version>

# on the master node, upgrade control plane services
kubeadm upgrade apply v<version>

# upgrade the kubelet
apt-get upgrade -y kubelet=<version>

# upgrade the node
kubeadm upgrade node

# restart the kubelet
systemctl restart kubelet
```