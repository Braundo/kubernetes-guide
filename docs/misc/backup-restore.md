---
icon: material/circle-small
---

- You can save many objects on the cluster by querying the API Server and exporting it to YAML by running:
    
    ```bash
    kubectl get all --all-namespaces -o yaml > all-deploy-services.yaml
    ```
<br>

- Instead of backing up resources, you can back up the etcd server itself - etcd comes with a built-in snapshot solution:

    ```bash
    etcdctl snapshot save /opt/snapshot-pre-boot.db
    --endpoints=https://127.0.0.1:2379 \
    --cacert=/etc/kubernetes/pki/etcd/ca.crt \
    --cert=/etc/kubernetes/pki/etcd/server.crt \
    --key=/etc/kubernetes/pki/etcd/server.key
    ```
<br>

- You can view the status of a snapshot by running:

    ```bash
    etcdctl snapshot status snapshot.db
    ```
<br>

- Here are the generalized steps to restore from etcd from a backup:
    
    ```bash
    # first stop the API Server
    service kube-apiserver stop

    # then restore
    # note the new directory being used by etcd
    etcdctl snapshot restore snapshot.db --data-dir /var/lib/etcd-from-backup

    # edit etcd service to use new directory
    vi /etc/kubernetes/manifests/etcd.yaml

    # restart the etcd service
    systemctl daemon-reload

    # wait 1-2 minutes for pods to come back up
    service etcd restart

    # start API Server
    service kube-apiserver start
    ```
<br>

- An easy way to view etcd servers for a cluster is by inspecting the API Server pod running in the `kube-system` Namespace
    - It will have a field called `--etcd-servers` under the `command` field
<br><br>

- To view details about the etcd server you can also run:
    
    ```bash
    ps -ef | grep etcd
    ```
<br>

- You can edit the etcd service at:
    ``` bash
    vi /etc/systemd/system/etcd.service
    ```