---
icon: material/circle-small
---

## Backup Strategies in Kubernetes
One straightforward method to back up Kubernetes objects is to query the API server and export all significant resources to a YAML file. This can be done using the `kubectl` command:
```bash
kubectl get all --all-namespaces -o yaml > all-resources-backup.yaml
```
<br>

For a more comprehensive backup, you can directly back up the etcd database, which holds all state and configuration data of your Kubernetes cluster. etcdctl, the CLI tool for etcd, provides a built-in solution to snapshot the database:
```bash
ETCDCTL_API=3 etcdctl snapshot save /opt/snapshot-pre-boot.db \
--endpoints=https://127.0.0.1:2379 \
--cacert=/etc/kubernetes/pki/etcd/ca.crt \
--cert=/etc/kubernetes/pki/etcd/server.crt \
--key=/etc/kubernetes/pki/etcd/server.key
```
This snapshot includes all Kubernetes states and can be used to restore the entire cluster to the point in time when the snapshot was taken.

You can view the status of a snapshot by running:
```bash
etcdctl snapshot status snapshot.db
```
<br>


## Restore from an etcd Snapshot
Restoring your Kubernetes cluster from an etcd snapshot involves several critical steps:

1. **Stop the Kubernetes API Server:**
   To begin the restoration, you need to stop the API server to prevent any changes to the cluster state during the restore process:
```bash
service kube-apiserver stop
```

2. **Restore the etcd Snapshot:**
Use `etcdctl` to restore the snapshot to a new data directory. This helps prevent corruption of the existing data during the restore process:
``` bash
etcdctl snapshot restore /opt/snapshot-pre-boot.db --data-dir /var/lib/etcd-from-backup
```
3. **Update the etcd Pod Specification:**
Modify the etcd manifest to use the new data directory. This usually involves editing the etcd pod definition in the Kubernetes manifests directory:
```bash
vi /etc/kubernetes/manifests/etcd.yaml
# Change the data directory to /var/lib/etcd-from-backup
```

4. **Restart etcd and Kubernetes API Server:**
Reload the systemd daemon to apply the changes and restart the etcd service:
``` bash
systemctl daemon-reload
service etcd restart
# Wait for etcd to become fully operational
service kube-apiserver start
```

5. **Monitoring the Restoration:**
After restarting the services, monitor the cluster's logs and status to ensure that all components are functioning correctly and the state has been restored as expected.

