## Why PID Limiting?
- PIDs are a fundamental resource on nodes.
- It's easy to hit the task limit without hitting other resource limits, causing instability.
- Cluster administrators need mechanisms to prevent PID exhaustion that could affect host daemons like `kubelet` or `kube-proxy`.



## How to Configure PID Limiting
- **Node-Level PID Limits**: You can reserve a number of PIDs for system use and Kubernetes system daemons using the -system-reserved and `-kube-reserved` command-line options for the `kubelet`.
- **Pod-Level PID Limits**: The number of PIDs can be limited at the node level for each Pod. This is configured using the `-pod-max-pids` command-line parameter to the `kubelet` or by setting `PodPidsLimit` in the `kubelet` configuration file.



## PID-Based Eviction
- `Kubelet` can terminate a Pod if it's consuming an abnormal number of PIDs.
- You can configure soft and hard eviction policies.
- The eviction signal value is calculated periodically and does not enforce the limit.



## Limitations
- Per-Pod PID limiting protects one Pod from another but doesn't protect node agents from PID exhaustion.
- Pod-defined PID limits are not currently supported.