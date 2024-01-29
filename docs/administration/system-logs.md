## Klog Library
- Klog is the Kubernetes logging library used to generate log messages for system components.
- Kubernetes is in the process of simplifying logging, and certain klog command-line flags are deprecated starting with Kubernetes v1.23 and will be removed in v1.26.


## Output Redirection
- Output is generally written to `stderr` and is expected to be handled by the component invoking a Kubernetes component.
- For environments where traditional output redirection options are not available, kube-log-runner can be used as a wrapper to redirect output.


## Structured Logging
- Introduced in Kubernetes v1.23 (beta), structured logging allows for a uniform structure in log messages, making it easier to store and process logs.
- The default formatting is backward-compatible with traditional klog.


## Contextual Logging
- Introduced in Kubernetes v1.24 (alpha), contextual logging builds on structured logging and allows developers to add additional information to log entries.
- It is currently gated behind the StructuredLogging feature gate and is disabled by default.


## JSON Log Format
Available since Kubernetes v1.19 (alpha), the `-logging-format=json` flag changes the log format to JSON.


## Log Verbosity Level
Controlled by the `v` flag, increasing the value logs increasingly less severe events.


## Log Location
Logs can be written to `journald` or `.log` files in the `/var/log` directory, depending on whether the system component runs in a container.


## Log Query
Introduced in Kubernetes v1.27 (alpha), this feature allows viewing logs of services running on the node, provided certain feature gates and configuration options are enabled.
