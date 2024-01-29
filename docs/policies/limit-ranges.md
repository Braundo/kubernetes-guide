## What is a LimitRange?
A LimitRange is a policy that sets constraints on the resource allocations for various object kinds like Pods or PersistentVolumeClaims within a namespace. It can enforce minimum and maximum compute resource usage per Pod or Container, set storage request limits for PersistentVolumeClaims, and even enforce a ratio between resource requests and limits.


## How Does it Work?
1. Default Values: If a Pod or Container doesn't specify compute resource requirements, the LimitRange admission controller will apply default request and limit values.
2. Tracking Usage: The LimitRange ensures that resource usage does not exceed the minimum, maximum, and ratio defined in any LimitRange present in the namespace.
3. Validation: If you try to create or update an object that violates a LimitRange constraint, the API server will reject the request with an `HTTP 403 Forbidden` status.


## Special Considerations
- LimitRange validations occur only at the Pod admission stage, not on running Pods.
- If two or more LimitRange objects exist in a namespace, the default value applied is not deterministic.
- The LimitRange does not check the consistency of the default values it applies. For example, a default limit value could be less than the request value specified for the container, making the Pod unschedulable.
