---
icon: material/package-variant-closed
---

Pods are the atomic unit of scheduling in Kubernetes. As virtual machines were in the VMware world, so are Pods in the world of Kubernetes. Every container running on Kubernetes must be wrapped up in a Pod. The most simple implementation of this are single-container Pods - one container inside one Pod. However there are certain instances where multi-container Pods make sense.

It's important to note that when you scale up/down applications in Kubernetes, you're not doing so by adding/removing containers directly - you do so by adding/removing Pods.

## Atomic
Pod deployment is atomic in nature - a Pod is only considered **Ready** when *all* of its containers are up and running. Either the entire Pod comes up successfully and is running, or the entire thing doesn't - there are no partial states.

## Lifecycle
Pods are designed to be ephemeral in nature. Once a Pod dies, it's not meant to be restarted or revived. Instead, the intent to spin up a brand new Pod in the failed ones place (based off of your defined manifest). Further, Pods are *immutable* and should not be changed once running. If you need to chance your application, you update the configuration via the manifest and deploy a new Pod.

## Multi-container Pods
As mentioend above, the simplest way to run an app on Kubernetes is to run a single container inside of a single Pod. However, in situations where you need to tightly couple two or more functions you can co-locate multiple containers inside of the same pod. One such example would be leveraging the sidecar pattern for logging wherein the main container dumps logs to a supporting container that can sanitize and format the logs for consumption. This frees up the main container from having to worry about formatting logs.

*[sidecar]: A Kubernetes side container is an additional container that runs alongside a primary application container within a Pod.
*[ephemeral]: Lasting for a very short time.
*[atomic]: All or nothing.