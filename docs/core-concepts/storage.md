---
icon: material/circle-small
---
## Overview
Arguably the most important aspect of any application is the ability to persist and retrieve data. Kubernetes supports a diverse array of storage back-ends, ranging from local storage on Nodes to network-attached storage (NAS) and cloud-based storage solutions. It integrates seamlessly with many third-party systems to offer features like replication, snapshots, and backups, enhancing data durability and availability.   

Kubernetes can also support different types of storage - anything from objects to files or blocks. However, regardless of the type of storage or where it's located (on-premise, cloud, etc.), Kubernetes will treat it as a **volume**.  

Kubernetes is able to support so many different storage types and services by leveraging the [**Container Storage Interface (CSI)**](https://github.com/container-storage-interface/spec/blob/master/spec.md). The CSI is an established standard that provides a straightforward interface for Kubernetes.

![service](../../images/storage-1.svg)

The only thing required for an external storage provider to be surfaced as a volume in Kubernetes is for it to have a CSI plugin. On the right side of the diagram you'll also notice the PV subsystem, which encompasses three Kubernetes API objects:  

- **Persistent Volumes (PV)**: map to external storage objects
- **Persistent Volume Claims (PVC)**: akin to "tickets" that authorize Pods to be able to use the relevant PV
- **Storage Classes (SC)**: wrap the previous two in some automation

Take an example below where our cluster is running on GKE and we have a 2TB block of storage called `gce-pd`. We then create a PV called `k8s-vol` that will map to the `gce-pd` with the `pd.csi.storage.gke.io` CSI plugin.

!!! warning "Multiple Pods cannot access the same volume."
!!! warning "You cannot map an external storage volume to multiple PVs."

## Container Storage Interface (CSI)
The [Container Storage Interface](https://github.com/container-storage-interface/spec/blob/master/spec.md) (CSI) is a standard for exposing arbitrary block and file storage systems to containerized workloads on Container Orchestration Systems (COS) like Kubernetes. CSI allows for the consistent configuration and management of storage solutions across various container orchestration systems. 

CSI enables storage providers to develop a standardized plugin once and have it work across a multitude of container orchestration systems without requiring changes. This simplifies the process of adding new storage capabilities to Kubernetes clusters and ensures compatibility and extendibility.

While CSI is a critical piece of getting storage working in Kubernetes, unless you explicitly work on writing storage plugins you'll likely never interact with it directly. Most of your interaction with CSI will simply be referencing your relevant CSI plugin in YAML files.  

## Persistent Volumes
At a high level, PVs are the way external storage objects are represented in Kubernetes.

## Storage Classes
StorageClasses (SCs) allow you to define different types of storage. How they are defined depends on the type of storage you're using. For example, if you're using Google Cloud Storage you have classes such as Standard, Nearline, Coldline, and Archive. You may also have simpler/more straightforward classes at your disposal such as SSD and HDD. When you create a SC you map both of those definitions so Pods in your cluster can use either or.

| External Type | K8s StorageClass |
| ------| ------ |
| SSD | sc-fast |
| HDD | sc-slow |

Below is an example of how a StorageClass YAML definition may look for leveraging SSDs with Google Cloud Storage:  

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

#### Dynamic Provisioning
StorageClasses in Kubernetes abstract the details of how storage is provided from how it is consumed. They enable dynamic provisioning of storage resources as needed, which is particularly useful in cloud environments where storage can be requested and scaled programmatically.

For example, a StorageClass can define the type of storage (e.g., standard, high-speed SSD, etc.), the replication factor, and the region. When a PVC that references this StorageClass is created, Kubernetes automatically provisions the required storage according to the specifications and binds it to the PVC.

Here's an example YAML definition of a StorageClass that uses a Google Cloud persistent disk with high-performance SSD:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-storage
provisioner: kubernetes.io/gce-pd
parameters:
  type: pd-ssd
  replication-type: none
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

*[PV]: PersistentVolume
*[PVC]: PersistentVolumeClaim
*[SC]: StorageClass
*[GKE]: Google Kubernetes Engine
*[CSI]: Container Storage Interface