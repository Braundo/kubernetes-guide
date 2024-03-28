---
icon: material/circle-small
---

## Configuring HA
- If you lose a Master node, your applications will remain running on worker nodes and users can still access those applications
    - However, Pods won’t restart or update as part of Deployment because there will be no controllers
<br><br>

- The **API Server** can be run in an `Active`-`Active` mode on multiple masters because they process one request at a time and simply pass information to other services which take action
    - With multiple masters you can point your Kubeconfig to a loadbalancer on port 6443 in front of the masters to distribute traffic between the underlying API Servers
<br><br>

- The **Controller Manager** and **Scheduler** watch the cluster for changes and taking necessary actions
    - These must be run in an `Active`-`Standby` mode to ensure that actions are duplicated
    - Leader election process picks the `Active` one

## ETCD in HA
- **ETCD** can be configured in two topologies:
    - **Stacked Topology:** running on Kubernetes master nodes
    - **External Topology:** running on dedicated servers external to the cluster
    - Remember the API Server is the only component that talks to ETCD
        - And must be configured to point to the servers, if hosted externally
<br><br>

How does **ETCD** stay consistent when it allows you to read or write from any instance?

- With *reads*, the same data is available across all nodes so it’s straight forward
- With *writes*, **etcd** ensures that only one instance is responsible for ***PROCESSING*** the writes via leader election
    - The leader then ensures the followers are sent a copy of the data
- Writes that come in to an instance other than the leader, they are forwarded to the leader
- A write is only considered complete once the data has been copied to a ***majority of the instances***
    - If an instance goes offline during a write, but the majority copy it - the data will be copied over to the node if/when it comes back online