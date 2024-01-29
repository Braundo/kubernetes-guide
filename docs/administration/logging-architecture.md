## Application Logs
Standard Output and Standard Error Streams: Applications in Kubernetes should write logs to the standard output (stdout) and standard error (stderr) streams. This allows Kubernetes to capture these logs regardless of the logging library or format used by the application.


## Cluster-level Logging
- **Separate Storage**: Logs should be stored in a dedicated storage system separate from nodes, pods, or containers. This ensures that logs are retained even if the associated Kubernetes objects are deleted.
- **No Native Solution**: Kubernetes itself doesn't offer a built-in log storage solution, but you can integrate third-party tools like Elasticsearch, Logstash, and Kibana (ELK stack) or other logging solutions.


## Pod and Container Logs
**Log Capture**: Kubernetes captures logs for each container within a running Pod. These logs are available through the `kubectl logs` command.


## How Nodes Handle Container Logs
**Container Runtimes**: Container runtimes like Docker or containerd capture the standard output and standard error streams and redirect them to a logging driver, which is usually configured to write to a file on disk.


## Log Rotation
**Kubelet Configuration**: The `kubelet`, running on each node, can be configured to automatically rotate logs to prevent filling up storage space. This is particularly useful for long-running Pods or high-verbosity logging.


## System Component Logs
- **Running in Containers**: Some system components may run in containers and write logs to the standard output and standard error streams.
- **Directly Running**: Some components may run directly on the node and write logs to files in specific directories.


## Log Locations
**OS Dependent**: The locations where logs are stored depend on the operating system. For example, in a system using `systemd`, you might find logs in `/var/log`.


## Cluster-level Logging Architectures
- **Node-level Logging Agent**: An agent running on each node can be responsible for capturing logs and sending them to a centralized logging solution.
- **Dedicated Sidecar Container**: A sidecar container within each Pod can capture and forward logs.
- **Direct Push to Backend**: Applications can be configured to push logs directly to a logging backend, bypassing the need for a separate logging agent.