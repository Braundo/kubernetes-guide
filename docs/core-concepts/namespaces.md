---
icon: material/circle-small
---

## Overview
Namespaces in Kubernetes are like virtual clusters within a physical cluster. They help partition resources among multiple users and teams, enabling a more organized deployment environment. Namespaces provide a mechanism to scope resource names, simplify resource management, and facilitate the application of specific access controls, resource quotas, and policies at a granular level. 

!!! warning "Namespaces are not intended to be used for secure isolation"
    While namespaces help in organizing and managing access to resources, they do not provide a strong security boundary capable of preventing all forms of resource access or interference between namespaces. For scenarios requiring stringent security isolation, such as multi-tenant environments with strict compliance requirements, the best practice is to use multiple Kubernetes clusters. 

## Common Uses for Namespaces
Namespaces are commonly used to separate environments within a single Kubernetes cluster. This separation helps in managing different deployment stages such as development, testing, staging, and production within the same cluster but without interference. Each environment can have its own set of permissions, limits, and policies, ensuring that resources are not accidentally shared or overwritten across different team functions. 

## Network and Namespace Policies
Network policies in Kubernetes provide an additional layer of security when using namespaces. By default, Pods within a namespace can communicate freely. Network policies allow you to define rules for inbound and outbound traffic between pods across different namespaces, helping to enforce a stricter communication policy and prevent unauthorized access.

For example, you can create a network policy that only allows traffic from the 'development' namespace to the 'testing' namespace, enhancing the security and isolation between different deployment stages.

## Built-in Namespaces
Kubernetes starts with several built-in Namespaces:

- `default`: The space where objects are placed if no other Namespace is specified.
- `kube-system`: For objects created by the Kubernetes system.
- `kube-public`: Usually reserved for resources that should be visible and readable publicly throughout the whole cluster.
- `kube-node-lease`: For lease objects associated with nodes which help the Kubelet in determining node health.  

To view all the namespaces in your cluster and verify their status, you can use the `kubectl get namespaces` command. This command lists all namespaces, providing a quick overview of the operational scope within your cluster: 

``` bash title="$ kubectl get namespaces"
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