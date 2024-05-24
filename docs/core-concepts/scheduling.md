---
icon: material/circle-small
---

- Every Pod specification includes an optional `nodeName` field, which is typically left unset. When a Pod is created without a specific `nodeName`, Kubernetes' scheduler automatically assigns the Pod to an appropriate Node, populating the `nodeName` field with the selected Node's name. 
- When the **Scheduler** reviews Pods, it finds Pods that do not have that field set and those are the candidates for scheduling
- It then runs the scheduling algorithm to determine which Node to place the Pod on and populates the `nodeName` field

## Manual Scheduling

- You can manually set the specific Node in your Pod definition:
    
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: nginx
  nodeName: k8s02 # you can specify the Node you want here
```
> The `nodeName` field cannot be updated once the Pod is running. If you want to update the Node a running Pod resides on, you have to create a `Binding` object and send a POST request to the Binding API of the Pod,

## Taints and Tolerations
Taints and tolerations work together to ensure that Pods are not scheduled onto inappropriate Nodes. Taints are applied to Nodes and can repel Pods that do not have a corresponding toleration. 

- **Taints** are markers applied to Nodes that denote special behavior. For example, a Node might have a taint that indicates it should not host any Pods that do not explicitly tolerate the taint. 
- **Tolerations** are applied to Pods and allow them to "ignore" taints on Nodes, thus enabling them to be scheduled onto Nodes with those taints.

Together, taints and tolerations provide a powerful way to ensure that Pods are only scheduled onto suitable Nodes. For instance, you might taint a Node to only allow database Pods that require high I/O performance, ensuring that other workloads do not disrupt database operations. 

- <span style="color: #FF0000">**Taints**</span> are specific to <span style="color: #FF0000">**Nodes**</span>
- <span style="color: #4287f5">**Tolerations**</span> are specific to <span style="color: #4287f5">**Pods**</span>
- <span style="color: #FF0000">**Taints**</span> on a Node say “only these certain Pods can be scheduled here”
- <span style="color: #4287f5">**Tolerations**</span> on a Pod say “you can tolerate a Node that has this given taint”

## Node Selectors

* Node selectors specify which Node you want a Pod to run on based on labels you place on the Node itself
    * i.e. if you label a Pod as `disktype=ssd`, implying it can only be scheduled on Nodes with that label, you can specify in the Pod definition YAML:
    
```yaml
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
  nodeSelector:
    disktype: ssd # label here
```
> Note there are limitations here as you cannot use complex operators like `IS NOT` , `OR` , `EXISTS` , etc.

## Node Affinity
Node affinity is a set of rules that the scheduler uses to determine where a Pod can be placed based on labels on Nodes. Unlike simple Node selectors, Node affinity allows for more complex expressions:

- **Required rules** must be met for a Pod to be scheduled on a Node.
- **Preferred rules** suggest preferences but do not strictly enforce them.

This feature allows you to specify that certain Pods should or should not be placed in specific ways relative to other Pods or based on Node attributes, enhancing the scheduler's ability to distribute workloads optimally. 

- Node affinity ***does*** let you use complex operators
- Node affinity is **a set of rules used by the Scheduler to determine where a Pod can be placed**.
- The rules are defined using custom labels on Nodes and label selectors specified in Pods.
- Node affinity allows a Pod to specify an affinity (or anti-affinity) towards a group of Nodes it can be placed on.
    
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: disktype
            operator: In
            values:
            - ssd
  containers:
  - name: nginx
    image: nginx
```
    

## Resource Requirements

- Among other things, the Scheduler takes into account **the resources required by the Pod** and **the resources available on the Node(s)** when attempting to schedule a Pod
- You can specify how much CPU and memory to *request* for your Pod when defining it
    - This is called a **Resource Request**
    
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: simple-webapp-color
  labels:
    name: simple-webapp-color
spec:
  containers:
  - name: simple-webapp-color
    image: nginx
    ports:
      - containerPort: 8080
    resources:
      requests:
        memory: "4Gi"
        cpu: 2
```
    

- By default, a Pod **has no limits on the amount of resources it can consume from a Node**
- You can also specify a *limit* on how many resources your Pod can consume when defining it
    
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: simple-webapp-color
  labels:
    name: simple-webapp-color
spec:
  containers:
  - name: simple-webapp-color
    image: nginx
    ports:
      - containerPort: 8080
    resources:
      requests:
        memory: "2Gi"
        cpu: 4
      limits:
        memory: "8Gi"
        cpu: 10
```
    

- When a Pod tries to go beyond the CPU limit, the Node will throttle the CPU usage of the Pod
- A Pod ***can*** use more memory than it’s limit however and will throw an OOM (Out of Memory) error if it happens frequently

- To ensure all Pods have some sort of limit set, you can introduce a **LimitRange**, which ensures all created Pods *within a Namespace* have certain default values without having to set them at the Pod definition-level
    
```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: cpu-resource-constraint
spec:
  limits:
  - default: # limit
      cpu: 500m
    defaultRequest: # request
      cpu: 500m
    max: # limit
      cpu: "1"
    min: # request
      cpu: 100m
    type: Container
```


```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: memory-resource-constraint
spec:
  limits:
  - default: # limit
    memory: 1Gi
  defaultRequest: # request
    memory: 1Gi
  max: # limit
    memory: 1Gi
  min: # request
    memory: 500Mi
  type: Container
```
!!! warning "Changing a LimitRange will not affect running Pods - only newly created ones"

- To set limits at a Namespace-level, you use **Resource Quotas**
    
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: my-resource-quota
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 4Gi
    limits.cpu: "10"
    limits.memory: 10Gi
```
    

## DaemonSets

- DaemonSets run a single copy of each Pod on every Node of the cluster
    - If a new Node is added to the cluster, a new Pod is put onto the new Node

- Use cases might be:
    - Monitoring agent
    - Logging agent
    - Networking solutions which require an agent on every Node

- The `kube-proxy` is actually a DaemonSet as well

- DaemonSets ensure a Pod runs on every single Node in the cluster by using Node Affinity rules

```yaml
apiVersion: apps/v1
kind: DaemonSet
metdata:
  name: monitoring-daemon
spec:
  selector:
    matchLabels:
      app: monitoring-agent
  template:
    metadata:
      labels:
        app: monitoring-agent
     spec:
       containers:
       - name: monitoring-agent-container
         image: monitoring-agent-software
```

## Multiple Schedulers
Kubernetes allows the deployment of multiple scheduler instances to handle Pod placement according to various customized scheduling policies. You can specify which scheduler to use for each Pod if you have special scheduling needs that the default scheduler does not support.

For example, you might deploy a custom scheduler that optimizes for GPU-intensive applications and use it alongside the default Kubernetes scheduler. 

- You can write your own Scheduler program and deploy it as the default scheduler or as a supplemental scheduler
- When defining and deploying a Pod, you can instruct it to leverage a specific Scheduler
    
```yaml
apiVersion: kubescheduler.config.k8s.io/v1
kind: KubeSchedulerConfiguration
profiles:
- schedulerName: my-scheduler
leaderElection: # if running multiple masters
  leaderElect: true
  resourceNamespace: kube-system
  resourceName: lock-object-my-scheduler
```
    

- You can deploy an additional Scheduler as a Pod
    
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-custom-scheduler
  namespace: kube-system
spec:
  containers:
  - command:
    - kube-scheduler
    - --address=127.0.0.1
    - --kubeconfig=/etc/kubernetes/scheduler.conf
    - --config=/etc/kubernetes/my-scheduler-config.yaml

    image: k8s.grc.io/kube-scheduler-amd64:v1.11.3
    name: kube-scheduler
```
    

- You can also deploy it as a Deployment

- To configure a Pod to use a custom Scheduler, we define it in the Pod definition:
    
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  containers:
  - image: nginx
    name: nginx-container
  schedulerName: my-custom-scheduler
```
    

- To view which Scheduler was used for Pods you can look at events by running `kubectl get events -o wide`

