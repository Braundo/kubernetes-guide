## Node-Pressure Eviction
- **Purpose**: To proactively terminate pods to reclaim resources on nodes.
- **Monitored Resources**: Memory, disk space, filesystem inodes.
- **Eviction Phases**: Sets the phase for selected pods to `Failed` and terminates them.
- **Constraints**: Doesn't respect `PodDisruptionBudget` or `terminationGracePeriodSeconds`.


## Self-Healing Behavior
- **Workload Management**: If pods are managed by objects like StatefulSet or Deployment, new pods replace the evicted ones.
- **Static Pods**: `Kubelet` tries to create a replacement for evicted static pods.


## Eviction Signals and Thresholds
- E**viction Signals**: Current state of a particular resource.
- **Eviction Thresholds**: Minimum amount of the resource that should be available.
- **Monitoring Intervals**: Evaluated based on housekeeping-interval, default is 10s.


## Types of Eviction Thresholds
- **Soft Eviction Thresholds**: Have a grace period.
- **Hard Eviction Thresholds**: No grace period, immediate termination.


## Pod Selection for Eviction
- **Criteria**: Resource usage, Pod Priority, and resource usage relative to requests.
- **Eviction Order**: BestEffort or Burstable pods where usage exceeds requests are evicted first.


## Node Conditions
`MemoryPressure`, `DiskPressure`, `PIDPressure`: Reflect that the node is under pressure.


## Known Issues
- **Memory Pressure Observation**: `Kubelet` may not observe memory pressure immediately.
- **Active File Memory**: Not considered as available memory.


## Good Practices
- **Schedulable Resources**: Make sure the scheduler doesn't schedule pods that will trigger eviction.
- **DaemonSets**: Give high enough priority to avoid eviction.


## Flags and Configuration
Various flags like `-eviction-hard`, `-system-reserved`, `-eviction-minimum-reclaim` etc. are used for fine-tuning.

