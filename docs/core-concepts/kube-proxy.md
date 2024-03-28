---
icon: material/circle-small
---

- Every Pod can reach every other Pod in a Kubernetes cluster
    - This is done by implementing a Pod network
<br><br>

- A Pod network is a virtual network that spans all Nodes in the cluster
<br><br>

- Services cannot join Pod networks because they are not running processes with any interfaces
<br><br>
- Kube Proxy is a process that runs on each Node in the cluster
    - It searches for any new Services on the cluster and creates local IP rules on each Node when a new Service is found
    - It then forwards any traffic inbound to a given Service to the IP of the Pod(s)