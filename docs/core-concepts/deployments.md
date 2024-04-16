---
icon: material/circle-small
---

## Overview
The main idea behind Deployments is that you tell Kubernetes the *desired* state of your application while a looping controller watches your app and continuously attempts to reconcile the *actual* state of your app with the *desired* state you previously defined.

## Deployment Spec
The way you *tell* Kubernetes how you want your application to look is through the use of a YAML file (Deployment spec). When you POST the Deployment spec (via `kubectl`) to the API server, Kubernetes goes through the process of deploying your application to match the desired state and leverages a **Deployment controller** to continuously watch your application state.  

It should be noted that while each Deployment object is configured primarily around a single Pod template, it can manage multiple replicas of that Pod. This means one Deployment can handle scaling of identical Pods horizontally to meet demand.

## ReplicaSets
Under the covers, Deployments actually leverage a different Kubernetes object to handle Pod scaling and reboots - the **ReplicaSet**. You should never be managing ReplicaSets directly, but it's good to know they exist and understand the hierarchy of control here. Containers will be wrapped in Pods, which have their scaling and self-healing managed by ReplicaSets, which in turn are managed by Deployments.

``` mermaid
flowchart TB
    subgraph Deployment
        subgraph ReplicaSet
            Pod1[Pod]
            Pod2[Pod]
        end
    end
```

## Scaling and Self-Healing
If you deploy a pod by itself (i.e. not via a Deployment), if it dies or fails, the Pod is lost forever.
!!! info "We never "revive" Pods; the appropriate way to "revive" a failed Pod is to create a new one to replace it."
However, with the magic of Deployments, if a Pod that was created via Deployment fails, it will be replaced. Remember that Deployment controllers continuously watch for deviations from your desired state; so if you specified that your application should run 3 Pods and one of the Pods fails, the controller will recognize that actual state (2 Pods) no longer matches desired state (3 Pods), and it will kick off a series of actions to deploy another Pod.

## Rolling Updates
This same logic enables seamless, zero-downtime updates for your applications. For example, if your application is currently running with five Pods at version v1.2, and you want to update to v1.3 after some improvements or fixes, you would update your Deployment spec to reflect the new version. The Deployment controller recognizes that the actual state (v1.2) does not match the desired state (v1.3) and initiates a rolling update. This process involves gradually terminating older-version Pods and replacing them with new-version Pods to ensure no downtime.

Some things to keep in mind for this to work: your application(s) need(s) to maintain loose coupling and maintain backwards and forwards compatability (cloud native application design pattern). For upgrades or rollbacks to truly have zero-downtime, forward and backword compatibility is a must, as is having clearly defined API specs.

There are different rolling update strategies you can employ that specify how to handle rollouts/rollbacks, how many can be spun up or down at once, etc. For more in-depth information on these strategies, refer to [the official Kubernetes documentation](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#strategy).

## Rollbacks
Rollbacks work in the same manner as rolling updates from above but in reverse. Imagine you had an issue with `v1.3` and need to roll back to `v1.2`. It's as simple as updating your Deployment spec and letting the Deployment controller notice this change and begin that reconciliation process. Kubernetes let you specify how many revisions (old versions) of your Deployments should be maintained for the purposes of rollbacks. In your Deployment spec, this is defined by the `revisionHistoryLimit` block.  

You can view the update history of a Deployment by running the following command:  
``` shell
kubectl rollout history deployment/<deployment-name>
```

## Scaling
Performing manual scaling operations with Deployments is also super straightforward and can be done in a similar manner to the one above. If you decide you actually want 10 Pods instead of 5, it's as simple as updating your Deployment spec and updating the `Replicas` block to the desired amount of Pods. Once again, the Deployment controller will notice the variation in states and begin reconciliation.

## Monitoring and Debugging Deployments
Effective management of deployments includes monitoring their status and performance. You can use `kubectl` to track the progress of a deployment and check for any issues. For example, `kubectl rollout status deployment/<deployment-name>` provides real-time updates about the deployment process. Additionally, examining the logs of Pods managed by a Deployment can offer insights into runtime operations and help identify errors or misconfigurations.
