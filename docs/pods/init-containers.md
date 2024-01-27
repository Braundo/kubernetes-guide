## What are Init Containers?
- Specialized containers that run before the application containers in a Pod. They can contain utilities or setup scripts not present in the application image.
- Init containers always run to completion, and each must complete successfully before the next one starts. If an init container fails, it is restarted until it succeeds, depending on the Pod's `restartPolicy`.



## Configuration
- Init containers are specified in the Pod specification under the `initContainers` field, similar to how application containers are defined.


## Differences from Regular Containers
- Init containers support all the features of application containers but do not support lifecycle hooks or probes like `livenessProbe`, `readinessProbe`, and `startupProbe`.


## esource Handling
- Resource requests and limits for init containers are managed differently than for application containers.


## Sequential Execution
- If multiple init containers are specified, they are run sequentially, and each must succeed before the next can run.


## Use Cases:
- Running utilities or custom code for setup that are not present in the application image.
- Blocking or delaying application container startup until certain preconditions are met.
- Limiting the attack surface by keeping unnecessary tools separate.
- Examples: The documentation provides YAML examples to demonstrate how to define a Pod with init containers.
- Advanced features like `activeDeadlineSeconds` can be used to prevent init containers from failing forever.
- Starting from Kubernetes v1.28, a feature gate named `SidecarContainers` allows specifying a `restartPolicy` for init containers independent of the Pod and other init containers.
- **Resource Sharing**: The highest of any particular resource request or limit defined on all init containers is the effective init request/limit for the Pod.
- **Pod Restart Reasons**: A Pod can restart, causing re-execution of init containers, for various reasons like Pod infrastructure container restart or all containers in a Pod being terminated.