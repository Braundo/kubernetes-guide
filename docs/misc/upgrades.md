---
icon: material/circle-small
---

## OS Upgrades on Kubernetes Nodes

**Node Downtime Handling:**

Kubernetes Nodes are given a default grace period of 5 minutes to reboot during updates or maintenance before the system starts evicting Pods. This is crucial to ensure that services remain available even when Nodes are temporarily down.
<br>

**Draining Nodes:**

To minimize disruption during an OS upgrade, it is advisable to proactively drain the Node. This process safely evicts all Pods from the Node and marks it as unschedulable, ensuring that no new Pods are assigned to it during the upgrade:
```bash
kubectl drain <node-name> --ignore-daemonsets
```

**Uncordoning Nodes:**

After the Node reboots and is ready to resume work, you must make it schedulable again by uncordoning it: 
``` bash
kubectl uncordon <node-name>
```

### Cluster Upgrade Process
In a Kubernetes cluster, it's vital to maintain version compatibility among components. The API Server, as the central component accepting and processing all requests, should always be upgraded first and must not be of a lower version than any other cluster components:

- **Controller Manager and Scheduler** can be at most one minor version behind the API Server.
- **Kubelet and Kube Proxy** can lag behind up to two minor versions.
- **Kubectl** (the command line tool) can be one version higher or lower than your cluster, giving some flexibility during the upgrade process.
<br><br>

**Version Skew Policy:**

Kubernetes supports version skew of up to three minor versions between the master and Node components. Always ensure that your upgrade process respects these limits to prevent compatibility issues.
<br><br>

**Recommended Upgrade Strategy:**

The safest approach to upgrading a Kubernetes cluster is to proceed one minor version at a time. This step-wise progression helps in managing dependencies and reducing the risk of significant disruptions:
<br><br>

**Step-by-Step Upgrade Guide Using Kubeadm:**

1. **Plan Your Upgrade:**
Use `kubeadm upgrade plan` to check the available versions and plan the upgrade steps.

2. **Upgrade Kubeadm:**
Update the kubeadm tool itself to the desired version:
```bash
apt-get upgrade -y kubeadm=<new-version>
```

3. **Upgrade the Control Plane Nodes:**
Apply the upgrade to the master Nodes using kubeadm:
``` bash
kubeadm upgrade apply v<new-version>
```

4. **Upgrade Kubelet on Each Node:**
After upgrading the master, upgrade kubelet on each Node:
``` bash
apt-get upgrade -y kubelet=<new-version>
systemctl restart kubelet
```

5. **Update Node Components:**
Complete the Node upgrade by running:
``` bash
kubeadm upgrade node
```

6. **Monitoring Upgrades:**
Always monitor the cluster's status and component health via `kubectl get nodes` to ensure all Nodes are at the correct version and fully operational post-upgrade.