## Introduction
In Kubernetes, a VolumeSnapshot represents a snapshot of a volume on a storage system. The document assumes familiarity with Kubernetes persistent volumes. VolumeSnapshotContent and VolumeSnapshot API resources are provided to create volume snapshots. A VolumeSnapshotContent is a snapshot taken from a volume in the cluster, provisioned by an administrator. It is a resource in the cluster, similar to a PersistentVolume.


## API Objects and Support
VolumeSnapshot, VolumeSnapshotContent, and VolumeSnapshotClass are Custom Resource Definitions (CRDs), not part of the core API. VolumeSnapshot support is only available for CSI drivers. A snapshot controller and a sidecar helper container called csi-snapshotter are deployed as part of the VolumeSnapshot deployment process. The snapshot controller watches VolumeSnapshot and VolumeSnapshotContent objects and is responsible for their creation and deletion.


## Lifecycle
VolumeSnapshotContents are resources in the cluster, while VolumeSnapshots are requests for those resources. Snapshots can be provisioned in two ways: pre-provisioned or dynamically provisioned. In pre-provisioned, a cluster administrator creates VolumeSnapshotContents with details of the real volume snapshot on the storage system. In dynamic provisioning, a snapshot is taken from a PersistentVolumeClaim.


## Binding
The snapshot controller handles the binding of a VolumeSnapshot object with an appropriate VolumeSnapshotContent object. The binding is a one-to-one mapping.


## Protection
While taking a snapshot of a PersistentVolumeClaim, that PersistentVolumeClaim is in-use. Deletion of the PersistentVolumeClaim object is postponed until the snapshot is readyToUse or aborted.


## Deletion
Deletion is triggered by deleting the VolumeSnapshot object, and the DeletionPolicy will be followed. If the DeletionPolicy is Delete, then the underlying storage snapshot will be deleted along with the VolumeSnapshotContent object.


## VolumeSnapshots and VolumeSnapshotContents Specs
Each VolumeSnapshot contains a spec and a status. For dynamically provisioning a snapshot, `volumeHandle` is the unique identifier of the volume created on the storage backend. For pre-provisioned snapshots, `snapshotHandle` is the unique identifier of the volume snapshot created on the storage backend.


## Converting Volume Mode
If the VolumeSnapshots API supports the `sourceVolumeMode` field, then it has the capability to prevent unauthorized users from converting the mode of a volume.


## Provisioning Volumes from Snapshots
You can provision a new volume, pre-populated with data from a snapshot, by using the `dataSource` field in the PersistentVolumeClaim object.
