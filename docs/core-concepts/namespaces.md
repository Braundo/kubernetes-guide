---
icon: material/circle-small
---

## Overview
Namespaces are used to partition Kubernetes clusters and provide an easy way to apply policies and quotas at a more granular level.  

!!! warning "Namespaces are not intended to be used for secure isolation"
    If you need secure isolation, the best practice is to use multiple clusters.

## Common Uses for Namespaces
Namespaces are frequently used to separate environments within a cluster, such as differentiating between development, staging, and production. They can also be used for resource management, applying specific policies or quotas to a subset of the cluster.

## Built-in Namespaces
Kubernetes starts with several built-in Namespaces:

- `default`: The space where objects are placed if no other Namespace is specified.
- `kube-system`: For objects created by the Kubernetes system.
- `kube-public`: Usually reserved for resources that should be visible and readable publicly throughout the whole cluster.
- `kube-node-lease`: For lease objects associated with nodes which help the Kubelet in determining node health.  

You can run the following command to view all Namespaces on a cluster:  

``` bash
$ kubectl get namespaces
    NAME              STATUS   AGE
    default           Active   22h
    gmp-public        Active   22h
    gmp-system        Active   22h
    kube-node-lease   Active   22h
    kube-public       Active   22h
    kube-system       Active   22h
```
> Your output will vary based on your environment.  

## Deploying Objects to Namespaces
When deploying objects on Kubernetes you can specify the target Namespace imperatively by adding the `-n <Namespace>` flag to your command, or declaratively by specifying the Namespace in your YAML file:  

``` yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  namespace: my-namespace
...
```

## Namespace Creation
Creating a new Namespace is as simple as applying a new YAML file:

``` yaml
apiVersion: v1
kind: Namespace
metadata:
  name: my-new-namespace
```  

You can also create a Namespace with the kubectl command:

``` shell
kubectl create namespace my-new-namespace
```