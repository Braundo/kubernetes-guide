## Overview
- Dynamic volume provisioning allows for the on-demand creation of storage volumes. This eliminates the need for cluster administrators to manually create storage volumes and their corresponding PersistentVolume objects in Kubernetes. The feature is based on the API object `StorageClass` from the API group `storage.k8s.io`.


## Background
- A cluster administrator can define multiple `StorageClass` objects, each specifying a volume plugin (provisioner) and the parameters to pass to that provisioner. This allows for the exposure of multiple types of storage within a cluster, each with custom parameters. This design abstracts the complexity of storage provisioning from end-users, allowing them to choose from multiple storage options.


## Enabling Dynamic Provisioning
- To enable this feature, a cluster administrator must pre-create one or more `StorageClass` objects. These objects define which provisioner should be used and what parameters should be passed when dynamic provisioning is invoked. For example, a storage class named "slow" might provision standard disk-like persistent disks, while a storage class named "fast" might provision SSD-like persistent disks.


## Using Dynamic Provisioning
- Users can request dynamically provisioned storage by including a storage class in their `PersistentVolumeClaim`. The `storageClassName` field of the `PersistentVolumeClaim` object must match the name of a `StorageClass` configured by the administrator. For instance, to select the "fast" storage class, a user would specify `storageClassName: fast` in their claim.


## Defaulting Behavior
- Dynamic provisioning can be enabled such that all claims are dynamically provisioned if no storage class is specified. This is achieved by marking one `StorageClass` object as the default and ensuring that the `DefaultStorageClass` admission controller is enabled on the API server.


## Topology Awareness
- In Multi-Zone clusters, it's important that storage backends are provisioned in the Zones where Pods are scheduled. This ensures that Pods can be spread across Zones in a Region while still having access to the appropriate storage.