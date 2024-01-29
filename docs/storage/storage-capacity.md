## Feature State
- The feature is stable as of Kubernetes v1.24. It helps Kubernetes keep track of storage capacity and aids the scheduler in placing Pods on nodes with sufficient storage.


## Before You Begin
- To utilize storage capacity tracking, you must be running Kubernetes v1.28 or above and use a CSI driver that supports this feature.


## API Extensions
- `CSIStorageCapacity` objects: Created by a CSI driver in its namespace, each object contains capacity information for one storage class and specifies which nodes can access that storage.
- `CSIDriverSpec.StorageCapacity` field: When set to true, the Kubernetes scheduler considers storage capacity for volumes using the CSI driver.



## Scheduling
- The scheduler uses storage capacity information if:
- A Pod uses a yet-to-be-created volume.
- The volume uses a StorageClass that references a CSI driver and uses `WaitForFirstConsumer` volume binding mode.
- The CSIDriver object for the driver has StorageCapacity set to true.
- In this case, the scheduler only considers nodes with enough storage. The check is basic and compares the volume size against the capacity listed in CSIStorageCapacity objects that include the node.


## Rescheduling
- Node selection is tentative until the CSI driver confirms the volume creation. If the volume can't be created due to outdated capacity information, the scheduler retries.


## Limitations
- Scheduling can fail permanently if a Pod uses multiple volumes and one volume consumes all the available capacity in a topology segment.
- The feature increases the chance of successful scheduling but doesn't guarantee it due to potentially outdated information.