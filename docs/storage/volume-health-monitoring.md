## Feature State
The feature is in alpha state as of Kubernetes v1.21.


## Overview
Volume Health Monitoring in Kubernetes is part of the Container Storage Interface (CSI). It allows CSI Drivers to detect abnormal conditions in the underlying storage systems and report them as events on Persistent Volume Claims (PVCs) or Pods.


## Components
The feature is implemented in two main components:
1. **External Health Monitor Controller**: This controller watches for abnormal volume conditions and reports them on the related PVC.
2. **Kubelet**: It also plays a role in volume health monitoring.



## Controller-Side Monitoring
If a CSI Driver supports this feature from the controller side, an event will be reported on the related PVC when an abnormal volume condition is detected. The External Health Monitor controller also watches for node failure events. You can enable node failure monitoring by setting the `enable-node-watcher` flag to true. When a node failure is detected, an event is reported on the PVC to indicate that pods using this PVC are on a failed node.


## Node-Side Monitoring
If a CSI Driver supports this feature from the node side, an event will be reported on every Pod using the PVC when an abnormal volume condition is detected.


## Metrics
Volume Health information is also exposed as Kubelet VolumeStats metrics. A new metric `kubelet_volume_stats_health_status_abnormal` is added, which includes two labels: `namespace` and `persistentvolumeclaim`. The count is either 1 or 0, where 1 indicates the volume is unhealthy and 0 indicates the volume is healthy.