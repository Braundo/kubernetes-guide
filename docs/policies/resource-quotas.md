## What is a Resource Quota?
A Resource Quota is an object in Kubernetes that sets limits on resource usage for each namespace. This is particularly useful when multiple teams or services share a Kubernetes cluster and you want to prevent any single team or service from consuming all the resources.


## How Does It Work?
- **Namespaces**: Different teams usually work in different namespaces. This isolation is often enforced using Role-Based Access Control (RBAC).
- **ResourceQuota Object**: For each namespace, an administrator creates a ResourceQuota object that defines the resource limits.
- **Resource Tracking**: As users create Kubernetes resources like pods and services in a namespace, the quota system keeps track of the usage to ensure it doesn't exceed the limits defined in the ResourceQuota object.
- **Violation & Enforcement**: If a resource request violates a quota, the request will fail with an HTTP 403 FORBIDDEN status, along with a message explaining the violated constraint.



## Types of Resources That Can Be Quota-ed
- **Compute Resources**: CPU and memory can be limited. You can set both "requests" and "limits" for these resources.
- **Storage Resources**: You can limit the storage requested in Persistent Volume Claims (PVCs).
- **Object Count**: You can also limit the number of specific types of objects, like Pods, Services, etc.
- **Extended Resources**: From Kubernetes 1.10 onwards, you can also quota extended resources like GPUs.
- **Priority Class**: You can set quotas based on the priority class of the pods.



## Special Scopes
Resource quotas can also have scopes that further restrict what is measured by the quota. For example, you can set a quota that only counts resources for Pods that are not in a terminal state (i.e., their `.status.phase` is neither `Failed` nor `Succeeded`).


## Enabling Resource Quotas
Resource quotas are usually enabled by default in many Kubernetes distributions. They are activated when the API server has `ResourceQuota` listed in its `--enable-admission-plugins` flag.


## Practical Examples
- **Team Quotas**: In a cluster with 32 GiB RAM and 16 cores, you could let Team A use 20 GiB and 10 cores, Team B use 10 GiB and 4 cores, and keep the rest in reserve.
- **Environment Quotas**: Limit the "testing" namespace to 1 core and 1 GiB RAM, while letting the "production" namespace use any amount.
