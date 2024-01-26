## What is CRI?
- CRI is a plugin interface that allows the kubelet to use various container runtimes.
- It eliminates the need to recompile cluster components for different runtimes.
- A working container runtime is required on each Node for the kubelet to launch Pods and their containers.


## Protocol
- CRI defines the main gRPC protocol for communication between the kubelet and the container runtime.
- The kubelet acts as a client when connecting to the container runtime via gRPC.


## API Feature State
- As of Kubernetes v1.23, CRI is considered stable.
- The kubelet uses command-line flags like `--image-service-endpoint` to configure runtime and image service endpoints.


## CRI Version Support
- For Kubernetes v1.28, the kubelet prefers to use `CRI v1`.
- If a runtime doesn't support v1, the kubelet negotiates an older supported version.
- `CRI v1alpha2` is considered deprecated.


## Upgrading
- During a Kubernetes upgrade, the kubelet tries to automatically select the latest CRI version.
- If that fails, fallback mechanisms are in place.
- If a gRPC re-dial is required due to a container runtime upgrade, the runtime must support the initially selected version, or the re-dial will fail.