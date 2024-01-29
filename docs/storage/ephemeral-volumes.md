## Introduction
- Ephemeral volumes are designed for temporary storage needs.
- They follow the Pod's lifetime and are created and deleted along with the Pod.
- Useful for caching services and read-only input data like configuration or secret keys.


## Types of Ephemeral Volumes
- `emptyDir`: Empty at Pod startup, storage from kubelet base directory or RAM.
- `configMap`, `downwardAPI`, `secret`: Inject Kubernetes data into a Pod.
- `CSI ephemeral` volumes: Provided by special CSI drivers.
- Generic ephemeral volumes: Can be provided by any storage driver that supports dynamic provisioning.


## CSI Ephemeral Volumes
- Managed locally on each node.
- Created after a Pod has been scheduled onto a node.
- No concept of rescheduling Pods.
- Not covered by storage resource usage limits of a Pod.


## Generic Ephemeral Volumes
- Similar to emptyDir but may have additional features like fixed size, initial data, etc.
- Supports typical volume operations like snapshotting, cloning, resizing, and storage capacity tracking.


## Lifecycle and PersistentVolumeClaim
- PVC parameters are allowed inside a volume source of the Pod.
- When the Pod is created, an actual PVC object is created and deleted along with the Pod.
- PVCs can be used like any other PVCs, including as data sources in volume cloning or snapshotting.


## Security Considerations
- Allows users to create PVCs indirectly.
- Normal namespace quota for PVCs still applies.
