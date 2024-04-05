---
icon: material/circle-small
---

- Kubelets are initially responsible for registering a Node with the cluster
<br><br>

- When the Scheduler determines a Node to place a Pod on, it informs the Kubelet on the Node (via the API Server)
    - The Kubelet then instructs the container runtime to pull the image and run the instance
    - The Kubelet will then continually monitor the Pod and report status to the API Server
