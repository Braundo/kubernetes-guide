## Kubernetes Default Limits
- Amazon Elastic Block Store (EBS): 39 volumes per Node
- Google Persistent Disk: 16 volumes per Node
- Microsoft Azure Disk Storage: 16 volumes per Node



## Custom Limits
You can customize these limits by setting the value of the `KUBE_MAX_PD_VOLS` environment variable and then restarting the scheduler. For CSI drivers, you may need to consult their specific documentation for customization procedures.


## Dynamic Volume Limits
As of Kubernetes v1.17, dynamic volume limits are supported for Amazon EBS, Google Persistent Disk, Azure Disk, and CSI. Kubernetes automatically determines the Node type and enforces the appropriate maximum number of volumes for that node. For example:
- On Google Compute Engine, up to 127 volumes can be attached, depending on the node type.
- For Amazon EBS disks on M5, C5, R5, T3, and Z1D instance types, only 25 volumes can be attached.
- On Azure, up to 64 disks can be attached, depending on the node type.



## CSI Driver Limits
If a CSI storage driver advertises a maximum number of volumes for a Node, the kube-scheduler will honor that limit.
