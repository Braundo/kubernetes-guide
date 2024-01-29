## Introduction
- The concept of VolumeSnapshotClass in Kubernetes is similar to that of StorageClass. While StorageClass allows administrators to define "classes" of storage for provisioning volumes, VolumeSnapshotClass serves the same purpose but for provisioning volume snapshots.

## The VolumeSnapshotClass Resource
- A VolumeSnapshotClass contains three main fields:
1. **Driver**: Specifies the CSI volume plugin used for provisioning VolumeSnapshots.
2. **DeletionPolicy**: Configures what happens to a VolumeSnapshotContent when the associated VolumeSnapshot is deleted. It can be either `Retain` or `Delete`.
3. **Parameters**: Describes additional configurations for volume snapshots belonging to this class.

The name of the VolumeSnapshotClass object is significant as it is used by users to request a particular class. Once created, these objects cannot be updated. Here's an example YAML configuration:

``` yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-hostpath-snapclass
driver: hostpath.csi.k8s.io
deletionPolicy: Delete
parameters:
```


## Default VolumeSnapshotClass
- Administrators can specify a default VolumeSnapshotClass for those VolumeSnapshots that don't request any particular class. This is done by adding an annotation `snapshot.storage.kubernetes.io/is-default-class: "true"`.

Example:
``` yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-hostpath-snapclass
  annotations:
    snapshot.storage.kubernetes.io/is-default-class: "true"
driver: hostpath.csi.k8s.io
deletionPolicy: Delete
parameters:
```


## Deletion Policy
- The `deletionPolicy` can be either `Retain` or `Delete`:
- `Retain`: The underlying snapshot and VolumeSnapshotContent remain even if the VolumeSnapshot is deleted.
- `Delete`: Both the underlying storage snapshot and the VolumeSnapshotContent object are deleted when the VolumeSnapshot is deleted.
