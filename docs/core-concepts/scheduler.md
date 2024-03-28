---
icon: material/circle-small
---

- The **Scheduler** is only responsible for deciding which Pods go on which nodes
    - It doesn’t actually place the Pods on the Nodes (the Kubelet does that)
<br><br>

- There are various criteria that the Scheduler uses to determine which Node to place a Pod on:
    - Resource requirements
    - Application requirements
<br><br> 

- The Scheduler uses a ranking system (0-10) to determine which Node is best; taking into account resources, taints, tolerations, affinity, etc.