
**Prometheus Format**: Kubernetes components emit metrics in Prometheus format, which is structured plain text readable by both humans and machines.
<br/><br/>

**Metrics Endpoint**: Metrics are generally available on the `/metrics` endpoint of the HTTP server. For components that don't expose this endpoint by default, it can be enabled using the `-bind-address` flag.
<br/><br/>

**Components**: Metrics are available for various components like `kube-controller-manager`, `kube-proxy`, `kube-apiserver`, `kube-scheduler`, and `kubelet`.
<br/><br/>

**RBAC Authorization**: If your cluster uses RBAC, reading metrics requires authorization via a user, group, or ServiceAccount with a ClusterRole that allows accessing `/metrics`.
<br/><br/>

**Metric Lifecycle**: Metrics go through different stages Alpha, Stable, Deprecated, Hidden, and Deleted. Each stage has its own set of rules and stability guarantees.
<br/><br/>

**Command-Line Flags**: Admins can enable hidden metrics through a command-line flag on a specific binary, using the flag `show-hidden-metrics-for-version`.
<br/><br/>

**Component Metrics**: Specific metrics are available for the `kube-controller-manager` and `kube-scheduler`, providing insights into the performance and health of these components.
<br/><br/>

**Disabling Metrics**: Metrics can be turned off via the command-line flag `-disabled-metrics` if they are causing performance issues.
<br/><br/>

**Metric Cardinality Enforcement**: To limit resource use, you can use the `-allow-label-value` command-line option to dynamically configure an allow-list of label values for a metric.