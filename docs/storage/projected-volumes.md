## Introduction
- Projected volumes map multiple existing volume sources into a single directory.
- Supported volume sources: `secret`, `downwardAPI`, `configMap`, `serviceAccountToken`.
- All sources must be in the same namespace as the Pod.


## Example Configuration: Secret, DownwardAPI, ConfigMap
- Demonstrates how to combine `secret`, `downwardAPI`, and `configMap` in a single Pod.
- Uses `apiVersion: v1, kind: Pod`, and specifies volume sources under projected.sources.


## Example Configuration: Non-Default Permission Mode
- Shows how to set a non-default permission mode for secrets.
- Uses mode: 511 to set specific permissions for the secret.


## ServiceAccountToken Projected Volumes
- Allows injecting the token for the current service account into a Pod.
- Fields:
    - **audience**: Intended audience of the token (optional).
    - **expirationSeconds**: Token validity duration, at least 10 minutes.
    - **path**: Relative path to the mount point.


## SecurityContext Interactions
### Linux
- Projected files have correct ownership, including container user ownership.

### Windows
- Ownership is not enforced due to virtual SAM database in each container.
- Recommended to place shared files in their own volume mount outside of `C:\\`.
