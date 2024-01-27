## Feature State
!!! info "This is an alpha feature introduced in Kubernetes verison 1.25"


## Purpose
User namespaces isolate the user running inside the container from the one in the host. This enhances security by limiting the damage a compromised container can do to the host or other pods.


## Linux-only Feature
This feature is specific to Linux and requires support for `idmap` mounts on the filesystems used.


## Container Runtime Support
CRI-O version 1.25 and later support this feature. `Containerd` v1.7 is not compatible with certain Kubernetes versions in terms of user namespace support.


## UID/GID Mapping
The `kubelet` will assign unique host UIDs/GIDs to each pod to ensure no overlap.


## Capabilities
Capabilities granted to a pod are limited to the pod's user namespace and are mostly invalid outside of it.


## Limitations
When using a user namespace, you cannot use other host namespaces like network, IPC, or PID.


## Security
The feature mitigates the impact of certain CVEs by ensuring that UIDs/GIDs used by the host's files and host's processes are in a specific range.