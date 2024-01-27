## Image Pull Operations
- Several methods to provide credentials, including node configuration and `imagePullSecrets`.
- Requires keys for access.


## Private Registries
- Automatically set based on conditions like whether a tag or digest is specified.


## Default Image Pull Policies
- `Never`: Never pulls image; uses local if available.
- `Always`: Always pulls image.
- `IfNotPresent`: Pulls image only if not present.
- By default, the pull policy is set to `IfNotPresent`, meaning the image is pulled only if not already present locally.


## Updating Images
- Tags can be added to identify versions.
- They can include a registry hostname and port number.


## Image Names
- They are pushed to a registry and then referred to in a Pod.
- Container images encapsulate an application and its dependencies.