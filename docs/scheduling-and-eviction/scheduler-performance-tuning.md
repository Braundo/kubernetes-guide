## Key Points
- **Balancing Latency and Accuracy**: In large clusters, you can balance the scheduler's behavior between latency (quick placement of new Pods) and accuracy (making fewer poor placement decisions).

- **Setting the Threshold**: The `percentageOfNodesToScore` option in the `KubeSchedulerConfiguration` setting determines a threshold for scheduling nodes. It accepts values between 0 and 100. A value of 0 indicates that the scheduler should use its default setting.

- **Node Scoring Threshold**: To improve performance, the scheduler can stop looking for feasible nodes once it has found enough. You specify a threshold as a percentage of all nodes in your cluster.

- **Default Threshold**: If you don't specify a threshold, Kubernetes calculates a figure using a linear formula. The lower bound for the automatic value is 5%.

## Example Configuration

``` yaml
apiVersion: kubescheduler.config.\
k8s.io/v1alpha1
kind: KubeSchedulerConfiguration
algorithmSource:
  provider: DefaultProvider
...
percentageOfNodesToScore: 50
```


## Internal Details
The scheduler iterates over the nodes in a round-robin fashion and also considers nodes from different zones to ensure fairness.

