## Phases
A Pod's life begins in `Pending` when it's accepted by the Kubernetes system, but the container images are not yet running. It moves to `Running` when its containers start, but may enter `Succeeded` or `Failed` if it completes its task or encounters an error, respectively. `Unknown` indicates that the cluster cannot determine the Pod's state, often due to communication problems.
  
## Container States
- Containers within a Pod can be in different states:
  - `Waiting`: The container is not yet running its workload, typically because it's pulling its image or waiting for its command to start.
  - `Running`: The container is executing without issues.
  - `Terminated`: The container has stopped, either because it completed its task or due to an error. This state is often accompanied by exit codes and status messages that can be checked using `kubectl`.

## Container Restart Policy
- The `restartPolicy` field within a Pod specification dictates the Kubelet's behavior when handling container terminations:
- `Always`: Automatically restart the container if it stops.
- `OnFailure`: Restart only if the container exits with a non-zero exit status (indicative of failure).
- `Never`: Do not automatically restart the container.

## Pod Conditions
- These are flags set by the Kubelet to provide more granular status than the phase:
    - `PodScheduled`: Indicates if the pod has been scheduled to a node.
    - `ContainersReady`: All containers in the Pod are ready.
    - `Initialized`: All init containers have started successfully.
    - `Ready`: The Pod is able to serve requests and should be added to the load balancing pools of all matching services.

## Custom readiness checks
- Can be configured via `readinessGates` in a Pod's specification, allowing you to define additional conditions to be evaluated before considering a Pod as ready.
- `PodReadyToStartContainers` is a hypothetical condition that could be used to signify network readiness, implying the Pod's network setup is complete and it's ready to start containers.

## Container Probes
- These are diagnostic tools used by the Kubelet to assess the health and readiness of a container:
- `livenessProbe`: Determines if a container is running. If this probe fails, the Kubelet kills the container which may be restarted depending on the pod's `restartPolicy`.
- `readinessProbe`: Determines if a container is ready to respond to requests. Failing this probe means the container gets removed from service endpoints.
- `startupProbe`: Used for containers that take a long time to start. If this probe fails, the Kubelet will not start the liveness or readiness probes, giving the container more time to initialize.

## Using Probes
- **Liveness Probes**: Implement if you need to handle the container's inability to recover from a deadlock or other runtime issues internally.
- **Readiness Probes**: Utilize when your container needs to perform certain actions such as warming a cache or migrating a database before it can serve requests.
- **Startup Probes**: Employ for slow-starting containers to ensure that Kubernetes doesn't kill them before they're up and running.

## Termination of Pods
- Pods are terminated gracefully, allowing for cleanup and shutdown procedures to complete. The Kubelet sends a `SIGTERM` signal to the containers, indicating that they should shut down. You can specify the grace period during which a container should complete its shutdown before being forcibly killed.