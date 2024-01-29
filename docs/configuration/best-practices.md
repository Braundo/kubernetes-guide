## General Configuration Tips
- Always specify the latest stable API version in your configuration files.
- Store configuration files in version control to facilitate quick rollbacks and cluster restoration.
- Prefer YAML over JSON for configuration files as it's more user-friendly.


## "Naked" Pods vs ReplicaSets, Deployments, and Jobs
- Avoid using naked Pods that are not bound to a ReplicaSet or Deployment.
- Use Deployments for almost all scenarios as they ensure the desired number of Pods and specify a strategy for Pod replacement.

## Services
- Create a Service before its corresponding backend workloads (Deployments or ReplicaSets).
- Services provide environment variables to containers, which implies an ordering requirement: Services must be created before the - Pods that need them.


## Using Labels
- Use semantic labels for your application or Deployment.
- Labels can be manipulated for debugging; removing labels will make the Pod invisible to controllers and Services.

## Using kubectl
- Use `kubectl apply -f directory` to apply configurations from all .yaml, .yml, and .json files in a directory.
- Use label selectors for `get` and `delete` operations instead of specific object names.