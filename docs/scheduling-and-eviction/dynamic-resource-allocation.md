## Key Concepts
- `ResourceClass`: Defines the resource driver and common parameters for a certain kind of resource.
- `ResourceClaim`: Specifies a particular resource instance required by a workload.
- `ResourceClaimTemplate`: Defines the spec for creating ResourceClaims.
- `PodSchedulingContext`: Used internally for coordinating pod scheduling when ResourceClaims need to be allocated.



## Example Configuration
Here's an example configuration for a fictional resource driver:

``` yaml
apiVersion: resource.k8s.io/v1alpha2
kind: ResourceClass
name: resource.example.com
driverName: resource-driver.example.com
---
apiVersion: cats.resource.example.com/v1
kind: ClaimParameters
name: large-black-cat-claim-parameters
spec:
  color: black
  size: large
---
apiVersion: resource.k8s.io/v1alpha2
kind: ResourceClaimTemplate
metadata:
  name: large-black-cat-claim-template
spec:
  spec:
    resourceClassName: resource.example.com
    parametersRef:
      apiGroup: cats.resource.example.com
      kind: ClaimParameters
      name: large-black-cat-claim-parameters
---
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-cats
spec:
  containers:
  - name: container0
    image: ubuntu:20.04
    command: ["sleep", "9999"]
    resources:
      claims:
      - name: cat-0
  - name: container1
    image: ubuntu:20.04
    command: ["sleep", "9999"]
    resources:
      claims:
      - name: cat-1
  resourceClaims:
  - name: cat-0
    source:
      resourceClaimTemplateName: \
      large-black-cat-claim-template
  - name: cat-1
    source:
      resourceClaimTemplateName: \
      large-black-cat-claim-template
```



## Scheduling
Resource drivers are responsible for marking ResourceClaims as "allocated" once resources for them are reserved. This informs the scheduler where in the cluster a ResourceClaim is available.


## Monitoring
The `kubelet` provides a gRPC service for the discovery of dynamic resources of running Pods.


## Enabling the Feature
This is an alpha feature and needs to be enabled explicitly. You also need to install a resource driver for specific resources that are meant to be managed using this API.