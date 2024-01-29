## Static Pods
Static Pods are managed directly by the kubelet on each node and are not controlled by the API server. An attacker with write access to the manifest directory could modify or introduce new static Pods.


## Mitigations
- Enable kubelet static Pod manifest functionality only if required.
- Restrict filesystem access to the static Pod manifest directory.
- Regularly audit and report all access to directories hosting static Pod manifests.



## The kubelet API
The kubelet API is exposed on TCP port 10250 and allows for information disclosure and command execution in containers.


## Mitigations
- Restrict access to sub-resources of the nodes API object using mechanisms like RBAC.
- Restrict access to the kubelet port to trusted IP ranges.
- Ensure kubelet authentication is set to webhook or certificate mode.



## The etcd API
Kubernetes uses etcd as a datastore, and direct access to this API can lead to data disclosure or modification.


## Mitigations
- Control access to the private key for the etcd server certificate.
- Restrict access to the etcd port at a network level.



## Container runtime socket
The container runtime exposes a Unix socket for interaction with containers. An attacker with access to this socket can launch or interact with containers.


## Mitigations
- Control filesystem access to container runtime sockets.
- Isolate the kubelet from other components using mechanisms like Linux kernel namespaces.
- Restrict or forbid the use of hostPath mounts that include the container runtime socket.