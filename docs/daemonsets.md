---
icon: material/content-copy
---

<h1>Managing DaemonSets in Kubernetes</h1>

DaemonSets ensure that all (or some) nodes run a copy of a Pod. They are used for deploying system-level applications like log collectors, monitoring agents, and other node-specific services.

<h2>Introduction to DaemonSets</h2>

DaemonSets are designed to manage the deployment of Pods across all nodes in a cluster. They ensure that a specific Pod is running on each node, making them ideal for system-level applications.


<h3>Use Cases for DaemonSets</h3>

DaemonSets are commonly used for:

- **Log Collection:** Deploying log collection agents on each node.
- **Monitoring:** Running monitoring agents to collect metrics from nodes.
- **Networking:** Managing network services like DNS or proxy servers.

<h3>Key Features</h3>


- **Automatic Updates:** Automatically adds Pods to new nodes when they are added to the cluster.
- **Selective Deployment:** Can be configured to deploy Pods only to specific nodes using node selectors.
- **Rolling Updates:** Supports rolling updates to update Pods without downtime.

<h3>Managing DaemonSets</h3>

DaemonSets can be managed using various Kubernetes features:

- **Node Selectors:** Control which nodes a DaemonSet's Pods are scheduled on.
- **Tolerations:** Allow DaemonSet Pods to run on nodes with specific taints.
- **Update Strategy:** Configure rolling updates to minimize disruption.

<h3>Example YAML for DaemonSet</h3>

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
spec:
  selector:
    matchLabels:
      name: fluentd
  template:
    metadata:
      labels:
        name: fluentd
    spec:
      containers:
      - name: fluentd
        image: fluent/fluentd:v1.11
        resources:
          limits:
            memory: 200Mi
            cpu: 100m
      tolerations:
      - key: "node-role.kubernetes.io/master"
        operator: "Exists"
        effect: "NoSchedule"

---

<h2>Summary</h2>
<ul>
<li><strong>DaemonSets</strong> ensure a Pod runs on every (or selected) node in your cluster.</li>
<li>They’re perfect for log collection, monitoring, and node-specific services.</li>
<li>Rolling updates and node selectors give you fine-grained control.</li>
</ul>

> <strong>Best Practice:</strong> Use DaemonSets for system-level workloads that must run everywhere. For app workloads, use Deployments or StatefulSets.
```

## Best Practices

- **Resource Management:** Define resource requests and limits to ensure efficient use of node resources.
- **Node Affinity:** Use node affinity to control where Pods are scheduled.
- **Monitor DaemonSet Health:** Regularly check the status and health of DaemonSets to ensure they are running as expected.
- **Scaling Considerations:** Plan for scaling by understanding the resource requirements of DaemonSet Pods.
