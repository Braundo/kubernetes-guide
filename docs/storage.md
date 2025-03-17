---
icon: material/database
---

# Mastering Kubernetes Storage

Storing and retrieving data is crucial for most real-world applications. Kubernetes' persistent volume subsystem allows you to connect to enterprise-grade storage systems that provide advanced data management services such as backup and recovery, replication, and snapshots.

## Overview

Kubernetes supports a variety of storage systems, including those from major cloud providers and enterprise-class solutions like EMC and NetApp. This section will cover:

- The big picture of Kubernetes storage
- Various storage providers
- The Container Storage Interface (CSI)
- Kubernetes persistent volume subsystem
- Dynamic provisioning with Storage Classes
- Hands-on examples

## The Big Picture

Kubernetes supports different types of storage, such as block, file, and object storage, from various external systems, either in the cloud or on-premises.

<h3>Types of Storage</h3>

<ul>
<li><strong>Block Storage:</strong> Provides raw storage volumes that can be mounted as disks to Pods. Ideal for databases and applications requiring high-performance storage.</li>
<li><strong>File Storage:</strong> Offers a shared file system that can be mounted by multiple Pods. Suitable for shared data and configuration files.</li>
<li><strong>Object Storage:</strong> Stores data as objects, often used for unstructured data like media files and backups.</li>
</ul>

<h3>High-Level Architecture</h3>

Storage providers connect to Kubernetes through a plugin layer, often using the Container Storage Interface (CSI). This standardized interface simplifies integrating external storage resources with Kubernetes.

<h3>Key Components</h3>

<ul>
<li><strong>Storage Providers:</strong> External systems providing storage services, like EMC, NetApp, or cloud providers.</li>
<li><strong>Plugin Layer:</strong> Connects external storage systems with Kubernetes, typically using CSI plugins.</li>
<li><strong>Kubernetes Persistent Volume Subsystem:</strong> Standardized API objects that allow applications to consume storage easily.</li>
</ul>

## Storage Providers

Kubernetes supports a wide range of external storage systems, each typically providing its own CSI plugin. These plugins are usually installed via Helm charts or YAML installers and run as Pods in the <code>kube-system</code> Namespace.

<h3>Restrictions</h3>

<ul>
<li><strong>Cloud-Specific:</strong> You can't provision and mount GCP volumes if your cluster is on Microsoft Azure.</li>
<li><strong>Locality:</strong> Pods often need to be in the same region or zone as the storage backend.</li>
</ul>

## Container Storage Interface (CSI)

The Container Storage Interface (CSI) is a standard for exposing arbitrary block and file storage systems to containerized workloads on Container Orchestration Systems (COS) like Kubernetes. CSI allows for the consistent configuration and management of storage solutions across various container orchestration systems.

<h3>Benefits of CSI</h3>

<ul>
<li><strong>Standardization:</strong> Provides a consistent interface for storage providers, simplifying integration.</li>
<li><strong>Flexibility:</strong> Supports a wide range of storage solutions and configurations.</li>
<li><strong>Scalability:</strong> Enables dynamic provisioning and management of storage resources.</li>
<li><strong>Decoupled Updates:</strong> CSI plugins can be updated independently of Kubernetes releases.</li>
<li><strong>Broad Compatibility:</strong> CSI plugins work across different orchestration platforms.</li>
</ul>

<h3>Installing CSI Plugins</h3>

Most cloud platforms pre-install CSI plugins for native storage services. Third-party storage systems require manual installation, often available as Helm charts or YAML files.

## Persistent Volumes and Claims

Persistent Volumes (PVs) and Persistent Volume Claims (PVCs) are integral to Kubernetes' storage system, providing a way to manage and consume storage resources.

<h3>Persistent Volumes (PVs)</h3>

PVs are cluster-wide storage resources that are provisioned either statically by an administrator or dynamically using Storage Classes. They represent a piece of storage that has been provisioned by an administrator or dynamically created by Kubernetes.

<ul>
<li><strong>Static Provisioning:</strong> Administrators manually create PVs, defining the storage details and capabilities.</li>
<li><strong>Dynamic Provisioning:</strong> Kubernetes automatically provisions storage based on the Storage Class specified in the PVC.</li>
</ul>

<h3>Persistent Volume Claims (PVCs)</h3>

PVCs are requests for storage by users. They consume PV resources and specify the desired storage size and access modes (e.g., ReadWriteOnce, ReadOnlyMany, ReadWriteMany).

<ul>
<li><strong>Binding Process:</strong> When a PVC is created, Kubernetes matches it to an available PV based on size and access mode.</li>
<li><strong>Lifecycle Management:</strong> PVCs allow users to request storage resources without knowing the underlying infrastructure details.</li>
</ul>

<h3>Example YAML for PV and PVC</h3>

**Persistent Volume (PV):**

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: my-pv
spec:
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: standard
  hostPath:
    path: "/mnt/data"
```

**Persistent Volume Claim (PVC):**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  storageClassName: standard
```

## Kubernetes Persistent Volume Subsystem

The Persistent Volume Subsystem in Kubernetes abstracts the underlying storage details, providing a consistent API for users to request and consume storage resources.

<h3>Key Features</h3>

<ul>
<li><strong>Abstraction:</strong> Decouples storage from Pods, allowing for flexible storage management.</li>
<li><strong>Reclaim Policies:</strong> Defines what happens to a PV when it is released by a PVC (e.g., Retain, Recycle, Delete).</li>
<li><strong>Access Modes:</strong> Specifies how the volume can be mounted by Pods (e.g., ReadWriteOnce, ReadOnlyMany, ReadWriteMany).</li>
</ul>

<h3>Dynamic Provisioning with Storage Classes</h3>

Storage Classes provide a way to define different classes of storage, enabling dynamic provisioning of storage resources based on predefined parameters.

<ul>
<li><strong>Provisioners:</strong> Specify the type of storage backend (e.g., aws-ebs, gce-pd).</li>
<li><strong>Parameters:</strong> Define specific configurations for the storage backend (e.g., volume type, IOPS).</li>
</ul>

<h3>Example YAML for Storage Class</h3>

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp2
```

## Best Practices

<ul>
<li><strong>Choose the Right Storage Type:</strong> Select block, file, or object storage based on application needs.</li>
<li><strong>Use Storage Classes:</strong> Leverage dynamic provisioning to simplify storage management.</li>
<li><strong>Monitor Storage Usage:</strong> Regularly check storage utilization and adjust resources as needed.</li>
<li><strong>Backup and Recovery:</strong> Implement backup strategies to protect data and ensure recovery.</li>
</ul>

## Example

**Example YAML:**
Below is the high-level flow for creating and using StorageClasses:

1. Ensure you have a storage back-end (cloud, on-prem, etc.)
2. Have a running Kubernetes cluster
3. Install and setup the CSI storage plugin to connect to Kubernetes
4. Create at least one StorageClass on Kubernetes
5. Deploy Pods with PVCs that reference those Storage classes

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mypod
spec:
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: mypvc
  containers:
  - name: my-container
    image: myimage
    volumeMounts:
    - name: data
      mountPath: /data
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mypvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
  storageClassName: fast
---
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: fast
provisioner: pd.csi.storage.gke.io
parameters:
  type: pd-ssd
```

## Additional Volume Settings

<h3>Access Modes</h3>

<ul>
<li><strong>ReadWriteOnce (RWO):</strong> Single PVC can bind to a volume in read-write mode.</li>
<li><strong>ReadWriteMany (RWM):</strong> Multiple PVCs can bind to a volume in read-write mode.</li>
<li><strong>ReadOnlyMany (ROM):</strong> Multiple PVCs can bind to a volume in read-only mode.</li>
</ul>

<h3>Reclaim Policy</h3>

<ul>
<li><strong>Delete:</strong> Deletes PV and external storage when PVC is released.</li>
<li><strong>Retain:</strong> Keeps PV and external storage when PVC is deleted, requiring manual cleanup.</li>
</ul>

## Summary

Kubernetes provides a robust storage subsystem that allows applications to dynamically provision and manage storage from various external systems. By leveraging CSI plugins and StorageClasses, you can create flexible and scalable storage solutions tailored to your application's needs.