---
icon: material/database
---

## Overview
Arguably the most important aspect of any application is the ability to persist and retrieve data. Thankfully, Kubernetes supports a wide variety of storage back-ends and also integrates with many third-party systems that provide things such as replication, snapshots, backup and more.  

Kubernetes can also support different types of storage - anything from objects to files or blocks. However, regardless of the type of storage or where it's located (on-premise, cloud, etc.), Kubernetes will treat it as a **volume**.  

Kubernetes is able to support so many different storage types and services by leveraging the **Container Storage Interface (CSI)**. The CSI is an established standard that provides a straightforward interface for Kubernetes.

``` mermaid
flowchart LR
    subgraph external storage
        netapp[(NetApp)]
        azureblock[(Azure)]
        etc[(etc)]
    end
    netapp --> CSI
    azureblock --> CSI
    etc --> CSI
    subgraph Kubernetes cluster
    CSI -->
    subsystem["<b>Persistent Volume subsystem</b><br><tt>pv, pvc, sc"]
    end
```

The only thing required for an external storage provider to be surfaced as a volume in Kubernetes is for it to have a CSI plugin. On the right side of the diagram you'll also notice three Kubernetes API objects:  

- **Persistent Volumes (PV)**: map to external storage objects
- **Persistent Volume Claims (PVC)**: akin to "tickets" that authorize Pods to be able to use the relevant PV
- **Storage Classes (SC)**: wrap the previous two in some automation

Take an example below where our cluster is running on GKE and we have a 2TB block of storage called `gce-pd`. We then create a PV called `k8s-vol` that will map to the `gce-pd` with the `pd.csi.storage.gke.io` CSI plugin. Here's how that might look visually:  

``` mermaid
flowchart LR
    storage[(<tt>gce-pd)] --- |pd.csi.storage.gke.io|k8s["Kubernetes cluster"]
    pv["<b>k8s-vol</b><br><tt>pv"]
    k8s --- pv
    pv -.- storage
    pv --- pvc["pvc fa:fa-ticket"]
    pvc --- pod
```

!!! warning "Multiple Pods cannot access the same volume."
!!! warning "You cannot map an external storage volume to multiple PVs."

## Container Storage Interface (CSI)
The CSI is [an open-source project](https://github.com/container-storage-interface/spec/blob/master/spec.md) that defines interfaces in a clear manner so that storage can be leveraged across Kubernetes (and other container orchestrators).

While CSI is a critical piece of getting storage working in Kubernetes, unless you explicitly work on writing storage plugins you'll likely never interact with it. Most of your interaction with CSI will simply be referencing your relevant CSI plugin in YAML files.  

## Persistent Volumes
At a high level, PVs are the way external storage objects are represented in Kubernetes.

## Storage Classes
StorageClasses (SCs) allow you to define different types of storage. How they are defined depends on the type of storage you're using. For example, if you're using Google Cloud Storage you have classes such as Standard, Nearline, Coldline, and Archive. You may also have simpler/more straightforward classes at your disposal such as SSD and HDD. When you create a SC you map both of those definitions so Pods in your cluster can use either or.

| External Type | K8s StorageClass |
| ------| ------ |
| SSD | sc-fast |
| HDD | sc-slow |

Below is an example of how a StorageClass YAML definition may look for leveraging Google Cloud Storage:  

``` yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ssd
provisioner: pd.csi.storage.gke.io  # Google Cloud CSI plugin
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
parameters:
  type: pd-ssd  # Google Cloud SSD drives
  provisioned-iops-on-create: '10000'
```

!!! info "StorageClass objects are immutable. You cannot modify them after they are deployed."

Below is the high-level flow for creating and using StorageClasses:

1. Ensure you have a storage back-end (cloud, on-prem, etc.)
1. Have a running Kubernetes cluster
1. Install and setup the CSI storage plugin to connect to Kubernetes
1. Create at least one StorageClass on Kubernetes
1. Deploy Pods with PVCs that reference those Storage classes

Below is an example YAML file that ties SC, PVC, and Pods together so you can see how they all interact:

``` yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ssd  # this will be referenced by the PVC below
provisioner: pd.csi.storage.gke.io
parameters:
  type: pd-ssd
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
    name: mypvc  # this will be referenced by the Pod below
spec:
    accessModes:
    - ReadWriteOnce
    resources:
        requests:
            storage: 256Gi
    storageClassName: ssd  # matches the name of the SC above
---
apiVersion: v1
kind: Pod
metadata:
    name: mypod
spec:
    volumes:
    - name: data
    persistentVolumeClaim:
        claimName: mypvc  # matches the name of the PVC above
...
```
> This YAML is only partially complete - it's mainly for showing the relationships between these objects via metadata.

#### Access Mode
Kubernetes StorageClasses support three different types of volume access modes:

1. **ReadWriteOnce(RWO)**: PV can only be bound as read/write by a single PVC (or Pod)
1. **ReadWriteMany**: PV can be bound as read/write by multiple PVCs (or Pods)
1. **ReadOnlyMany**: PV can be bound as read-only by multiple PVCs (or Pods)

#### Reclaim Policy
When you define a **reclaim policy** on a volume, you tell Kubernetes how it should deal with a PV after the relevant PVC is released. There are two options that can be selected:  

1. **Delete**: Default option that will delete the PV and any underlying storage resources on the external system itself once the PVC is released.
1. **Retain**: This will keep the PV object as well as any underlying data on the external system. However, no PVCs can use it going forward. 


*[PV]: PersistentVolume
*[PVC]: PersistentVolumeClaim
*[SC]: StorageClass
*[GKE]: Google Kubernetes Engine