## Concepts
- **Taints**: These are applied to nodes to mark them as unsuitable for certain pods. For example, `kubectl taint nodes node1 key1=value1:NoSchedule` adds a taint to `node1`.

- **Tolerations**: These are applied to pods and allow them to be scheduled on nodes with matching taints.

For example, a toleration could look like this:

``` yaml
tolerations:
- key: "key1"
  operator: "Equal"
  value: "value1"
  effect: "NoSchedule"
```



## Effects
- `NoExecute`: Affects already running pods. Pods that do not tolerate the taint are evicted immediately.

- `NoSchedule`: No new pods will be scheduled on the tainted node unless they have a matching toleration.

- `PreferNoSchedule`: A softer version of `NoSchedule`. Kubernetes will try to avoid placing a pod that does not tolerate the taint on the node, but it's not guaranteed.


## Use Cases
- **Dedicated Nodes**: For exclusive use by a particular set of users.

- **Nodes with Special Hardware**: For example, nodes with GPUs.

- **Taint-based Evictions**: Automatically taints a node when certain conditions are true, like `node.kubernetes.io/not-ready`.


## Example
Here's an example of a pod that uses tolerations:

``` yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
  labels:
    env: test
spec:
  containers:
  - name: nginx
    image: nginx
    imagePullPolicy: IfNotPresent
  tolerations:
  - key: "example-key"
    operator: "Exists"
    effect: "NoSchedule"
```