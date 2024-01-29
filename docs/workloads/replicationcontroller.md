## Purpose and Functionality
- Ensures a specified number of pod replicas are running at any given time.
- Automatically replaces pods that fail, are deleted, or are terminated.


## How it Works
- If there are too many pods, it terminates the extra ones.
- If there are too few, it starts more.


## Abbreviation
- Often abbreviated to `rc` in discussions and kubectl commands.


## Use Cases
- Can run one instance of a Pod indefinitely.
- Can run several identical replicas of a replicated service, like web servers.


## Configuration Example
- YAML configuration specifies the number of `replicas`, `selector`, and pod `template`.


## Commands
- `kubectl apply -f <config-file>` to apply the configuration.
- `kubectl describe replicationcontrollers/rc-name` to check the status.


## Pod Template
- `.spec.template` is a pod template with the same schema as a Pod.


## Labels and Selectors
- `.spec.selector` is a label selector that manages pods with matching labels.


## Scaling
- `.spec.replicas` specifies the number of pods that should run concurrently.


## Deletion
- kubectl delete scales the ReplicationController to zero and waits for pod deletion.


## Alternatives
- ReplicaSet and Deployment are the next-generation alternatives.


## DaemonSet and Job
- For machine-level functions, use DaemonSet.
- For pods expected to terminate on their own, use Job.