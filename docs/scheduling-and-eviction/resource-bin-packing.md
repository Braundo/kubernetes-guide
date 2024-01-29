## MostAllocated Strategy
This strategy scores nodes based on resource utilization, favoring nodes with higher allocation. You can set weights for each resource type to influence the node score. Here's an example configuration:

``` yaml
apiVersion: kubescheduler.config\
.k8s.io/v1beta3
kind: KubeSchedulerConfiguration
profiles:
- pluginConfig:
  - args:
      scoringStrategy:
        resources:
        - name: cpu
          weight: 1
        - name: memory
          weight: 1
        - name: intel.com/foo
          weight: 3
        - name: intel.com/bar
          weight: 3
        type: MostAllocated
    name: NodeResourcesFit
```


## RequestedToCapacityRatio Strategy
This strategy allows users to specify resources and their weights to score nodes based on the request-to-capacity ratio. It's particularly useful for bin packing extended resources. Here's an example configuration:  

``` yaml
apiVersion: kubescheduler.config\
.k8s.io/v1beta3
kind: KubeSchedulerConfiguration
profiles:
- pluginConfig:
  - args:
      scoringStrategy:
        resources:
        - name: intel.com/foo
          weight: 3
        - name: intel.com/bar
          weight: 3
        requestedToCapacityRatio:
          shape:
          - utilization: 0
            score: 0
          - utilization: 100
            score: 10
        type: RequestedToCapacityRatio
    name: NodeResourcesFit
```


## Tuning the Score Function

``` yaml
shape:
  - utilization: 0
    score: 0
  - utilization: 100
    score: 10
```
