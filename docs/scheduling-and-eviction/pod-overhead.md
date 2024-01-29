## What is Pod Overhead?
Pod Overhead is a feature in Kubernetes that accounts for the resources consumed by the Pod infrastructure on top of the container requests and limits. This is particularly useful when you're running Pods in a runtime that has additional overhead, such as Kata Containers or gVisor.


## How It Works
PodOverhead Field: The `PodOverhead` field is added to the Pod specification under the `spec` section. This field specifies the additional overhead in terms of CPU and memory.

``` yaml
apiVersion: v1
kind: Pod
metadata:
  name: overhead-demo
spec:
  overhead:
    cpu: "200m"
    memory: "120Mi"
```
<br/>


- **Scheduler's Role**: The Kubernetes scheduler takes into account this overhead when scheduling the Pod. This ensures that the Node has enough resources to accommodate not just the containers but also the Pod overhead.

- **Resource Accounting**: The `kubelet` also includes the overhead when calculating the Pod's resource usage. This is reflected in metrics and used in eviction decisions.
<br/><br/>

## Admission Controller

- **RuntimeClass**: You can define the overhead in the `RuntimeClass` if you're using multiple runtimes in your cluster. This makes it easier to manage overhead settings across different types of Pods.

``` yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: kata-fc
handler: kata-fc
overhead:
  podFixed:
    cpu: "250m"
    memory: "160Mi"
```
<br/>

- **Automatic Injection**: When you create a Pod that specifies a RuntimeClass with Pod overhead defined, the overhead settings are automatically injected into the Pod spec.


## Monitoring and Metrics
- **Resource Metrics**: Metrics related to CPU and memory usage will include the overhead, providing a more accurate representation of actual resource utilization.

- **Eviction**: The `kubelet` considers the overhead when making eviction decisions, ensuring that it doesn't evict Pods based on inaccurate resource usage data.