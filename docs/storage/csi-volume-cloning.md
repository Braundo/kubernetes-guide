## Introduction
The document introduces the concept of cloning existing Container Storage Interface (CSI) Volumes in Kubernetes. The feature allows you to specify existing Persistent Volume Claims (PVCs) in the `dataSource` field to indicate that you want to clone a volume. A clone is essentially a duplicate of an existing Kubernetes volume that behaves like any standard volume. The key difference is that upon provisioning, the backend device creates an exact duplicate of the specified volume instead of a new empty one.


## Implementation
From the Kubernetes API perspective, cloning is implemented by allowing you to specify an existing PVC as a `dataSource` during new PVC creation. The source PVC must be bound and available, meaning it should not be in use.


## User Considerations
- Cloning support is only available for CSI drivers.
- Only dynamic provisioners support cloning.
- CSI drivers may or may not have implemented volume cloning.
- Cloning can only be done within the same namespace for both source and destination PVCs.
- Cloning is supported with different Storage Classes.
- The destination volume can have the same or a different storage class as the source.
- The default storage class can be used, and storageClassName can be omitted in the spec.
- Cloning can only be done between two volumes that use the same `VolumeMode` setting.



## Provisioning
Clones are provisioned like any other PVC, except that a `dataSource` is added that references an existing PVC in the same namespace. The document provides a YAML example for creating a new PVC that is a clone of an existing one.


## Usage
Once the new PVC is available, it can be consumed like any other PVC. It becomes an independent object that can be consumed, cloned, snapshotted, or deleted independently. The source is not linked to the newly created clone in any way, allowing for modifications or deletions without affecting the clone.