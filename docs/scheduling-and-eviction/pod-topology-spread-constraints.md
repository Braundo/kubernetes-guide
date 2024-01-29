## Motivation
The primary motivation is to distribute Pods in a way that they are not all scheduled on the same node or same zone, which could be a single point of failure. For example, if you have a service that scales its Pods automatically, you don't want all Pods to be on the same node. As you scale up, you might also want to consider network latency and costs, aiming to distribute Pods across different data centers or zones.


## topologySpreadConstraints Field
This is the field you add to your Pod spec to define the constraints. It has several sub-fields:  
- `maxSkew`: Defines how unevenly Pods may be distributed. A lower number means a more even distribution.
- `topologyKey`: The key for node labels to define a topology (e.g., zone, node, etc.)
- `whenUnsatisfiable`: What to do if the constraint can't be satisfied (DoNotSchedule or ScheduleAnyway).
- `labelSelector`: Used to find Pods that these constraints apply to.
- `minDomains`: (Optional) Minimum number of domains (like zones or nodes) that must be eligible for Pod placement.



## Node Labels
Nodes should be labeled with the topology keys you intend to use, like `zone` or `region`. These labels are used by the scheduler to make decisions.


## Multiple Constraints
You can define multiple `topologySpreadConstraints`. In such cases, all constraints must be satisfied for a Pod to be scheduled.


## Interaction with Node Affinity
If a Pod also has node affinity rules, then the scheduler will consider those rules in conjunction with the topology spread constraints.


## Example 1: Basic Spread Constraints
This example ensures that the Pods are spread across different zones.

``` yaml
apiVersion: v1
kind: Pod
metadata:
  name: mypod
spec:
  topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: zone
    whenUnsatisfiable: DoNotSchedule
    labelSelector:
      matchLabels:
        app: myapp
  containers:
  - name: nginx
    image: nginx
```



## Example 2: Multiple Constraints
This example ensures that the Pods are spread both across zones and nodes.

``` yaml
apiVersion: v1
kind: Pod
metadata:
  name: mypod
spec:
  topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: zone
    whenUnsatisfiable: DoNotSchedule
    labelSelector:
      matchLabels:
        app: myapp
  - maxSkew: 2
    topologyKey: node
    whenUnsatisfiable: ScheduleAnyway
    labelSelector:
      matchLabels:
        app: myapp
  containers:
  - name: nginx
    image: nginx
```



## Example 3: Using minDomains
This example ensures that Pods are spread across at least 2 zones.

``` yaml
apiVersion: v1
kind: Pod
metadata:
  name: mypod
spec:
  topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: zone
    whenUnsatisfiable: DoNotSchedule
    labelSelector:
      matchLabels:
        app: myapp
    minDomains: 2
  containers:
  - name: nginx
    image: nginx
```



## Example 4: Interaction with Node Affinity
This example shows how node affinity can be combined with spread constraints.

``` yaml
apiVersion: v1
kind: Pod
metadata:
  name: mypod
spec:
  affinity:
    nodeAffinity:
      requiredDuringScheduling \
      IgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: hardware
            operator: In
            values:
            - fast-ssd
  topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: zone
    whenUnsatisfiable: DoNotSchedule
    labelSelector:
      matchLabels:
        app: myapp
  containers:
  - name: nginx
    image: nginx
```


## Implicit Conventions
- Only Pods in the same namespace as the incoming Pod are considered as matching candidates.
- Also, any nodes that don't have the `topologyKey` specified in `topologySpreadConstraints` are bypassed.
- This feature is particularly useful for large, distributed, and dynamic clusters where you want to control the Pod distribution for reasons like high availability, data locality, and load balancing.
