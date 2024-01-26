## What is Garbage Collection?
- Collective term for mechanisms that clean up cluster resources.
- Targets terminated pods, completed jobs, objects without owner references, unused containers and images, and more.


## Owners and Dependents
- Objects in Kubernetes link to each other through owner references.
- Owner references help the control plane and other API clients clean up related resources before deleting an object.


## Cascading Deletion
Two types: **Foreground** and **Background**.
- **Foreground**: Owner object first enters a "deletion in progress" state, and dependents are deleted before the owner.
- **Background**: Owner object is deleted immediately, and dependents are cleaned up in the background.


## Orphaned Dependents
- Dependents left behind when an owner object is deleted are called orphan objects.
- By default, Kubernetes deletes dependent objects, but this behavior can be overridden.


## Garbage Collection of Unused Containers and Images
- Kubelet performs garbage collection on unused images every five minutes and on unused containers every minute.
- Configurable options include `HighThresholdPercent` and `LowThresholdPercent` for disk usage.


## Container Garbage Collection
- Variables like `MinAge`, `MaxPerPodContainer`, and `MaxContainers` can be defined to control container garbage collection.
- Kubelet adjusts `MaxPerPodContainer` if it conflicts with `MaxContainers`.


## Configuring Garbage Collection
- Options specific to controllers managing resources can be configured for garbage collection.
