---
icon: material/vector-selection
---
## Overview
Namespaces are used to partition Kubernetes clusters and provide easy ways to apply policies and quotas at a more granular level.  

!!! warning "Namespaces are not intended to be used for secure isolation"
    If you need secure isolation, the best practice is to use multiple clusters.

Namespaces can be a useful construct for partitioning a single cluster among various environments for teams. For instance, the a single cluster might have development and production environments partitioned by Namespace.  

Kubernetes comes with a number of Namspaces already created. You can run the following command to view all namespaces on a cluster:  

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
When deploying objects on Kubernetes you can specify the target Namespace imperatively by adding the `-n <Namespace>` flag to your command, or declaratively by specifying the Namespace in your YAML file.  

!!! info "If you don't explicitly define a Namespace, objects will be deployed to the `default` Namespace."