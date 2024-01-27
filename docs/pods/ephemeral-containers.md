## Purpose
Ephemeral containers are a special type of container designed for temporary tasks like troubleshooting. They are *not* meant for building applications.

## Immutability
Once a Pod is created, you can't add a container to it. Ephemeral containers offer a way to inspect the state of an existing Pod without altering it.

## Resource Allocation
Ephemeral containers don't have guarantees for resources or execution. They will never be automatically restarted.

## Limitations
Many fields that are available for regular containers are disallowed for ephemeral containers, such as ports and resource allocations.

## Creation Method
These containers are created using a special `ephemeralcontainers` handler in the API, not directly through `pod.spec`.

## Use-Cases
Useful for interactive troubleshooting when `kubectl exec` is insufficient, especially with distroless images that lack debugging utilities.

## Process Namespace Sharing
Enabling this feature is helpful for viewing processes in other containers within the same Pod.