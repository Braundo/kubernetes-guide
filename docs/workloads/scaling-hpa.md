---
icon: lucide/maximize-2
---

# Scaling & HPA

One of the primary reasons companies choose Kubernetes is its ability to handle variable traffic. When your app gets featured on the front page of a major site, you need more power *now*. When everyone goes to sleep at 3 AM, you want to stop paying for idle servers.

Kubernetes handles this through **scaling**. While you can manually scale things up and down, the real magic lies in automation.

-----

## The Manual Way (Imperative Scaling)

The easiest way to scale a Deployment or StatefulSet is to just tell Kubernetes to change the replica count.

```bash
kubectl scale deployment my-web-app --replicas=10
```

Within seconds, the Deployment controller sees that you want 10 Pods but only have 2 running, and it immediately rushes to create 8 more.

This is great for testing or known events, but it requires a human to wake up at 3 AM when the servers get overloaded. We want robots to do that for us.

-----

## Introducing the HPA (Horizontal Pod Autoscaler)

The **HorizontalPodAutoscaler (HPA)** is a robot designed for one job: to watch a metric (like CPU usage) and automatically adjust the number of replicas in your Deployment up or down based on rules you define.

### The Thermostat Analogy

Think of the HPA like the thermostat in your house.

1.  **You set a target temperature:** "I want this room to stay at 72°F."
2.  **The thermostat watches the thermometer:** It constantly checks current conditions.
3.  **It takes action:**
      * If it's 65°F (too cold/low load), it turns on the furnace (scales up).
      * If it's 78°F (too hot/high load), it turns on the AC (scales down).

In Kubernetes, the HPA works the same way:

1.  **You set a target:** "I want the average CPU usage across all my Pods to be 50%."
2.  **The HPA watches the metrics server:** It asks, "What is the current average CPU usage?"
3.  **It takes action:**
      * If the average is 80% (too hot), it calculates how many *more* replicas are needed to bring the average back down to 50%, and scales up.
      * If the average is 20% (too cold), it calculates how many Pods it can remove while still staying near 50%, and scales down.

### A Simple HPA Example

To use the HPA, your Pods **must** have resource requests defined. The HPA makes its scaling decisions based on the percentage of the *requested* amount being used.

Here is a simple HPA resource. It tells Kubernetes to manage the `my-web-app` deployment, keeping its CPU usage around 50%, with a minimum of 2 Pods and a maximum of 10.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-web-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
```

Once applied, you can watch it work:

```bash
kubectl get hpa
```

You'll see output showing the current state vs. the target state:

```
NAME          REFERENCE               TARGETS   MINPODS   MAXPODS   REPLICAS
web-app-hpa   Deployment/my-web-app   32%/50%   2         10        3
```

In this case, current usage is 32%, which is below the 50% target, so the HPA will not scale up. If traffic spiked and usage went to 80%, the HPA would increase the replica count.

-----

## The Metrics Server Requirement

Just like a thermostat needs a thermometer, the HPA needs metrics data.

The HPA controller doesn't magically know how much CPU your Pods are using. It relies on a separate cluster add-on called the **Metrics Server**. The Metrics Server collects resource usage data from every node and exposes it via the Kubernetes API.

  * If you run `kubectl top pods` and get an error, your Metrics Server is probably not installed or is broken.
  * If the Metrics Server isn't working, the HPA cannot work.

Most managed Kubernetes services (like EKS, AKS, GKE) come with the Metrics Server pre-installed. If you are building your own cluster with `kubeadm`, you will need to install it yourself.

-----

## Going Deeper: Other Types of Scaling

While the HPA is the most common form of scaling, it's important to know about the others to see the bigger picture.

### Vertical Pod Autoscaler (VPA)

While HPA scales *horizontally* (adding **more** machines), the VPA scales *vertically* (making existing machines **bigger**).

If your Pod is constantly crashing due to OutOfMemory (OOM) errors, the VPA can notice this and automatically restart the Pod with higher memory limits.

!!! warning
    VPA and HPA usually shouldn't be used on the same metric (e.g., CPU) at the same time. They will fight each other. The HPA will try to add pods to lower CPU usage, while the VPA tries to remove pods to increase CPU utilization.

### Cluster Autoscaler (CA)

HPA and VPA only deal with Pods. But what happens when your HPA requests 100 new Pods, and your physical nodes run out of space to host them? Your Pods will get stuck in a `Pending` state.

The **Cluster Autoscaler** watches for pending Pods that cannot be scheduled due to a lack of resources. When it sees this, it talks to your cloud provider API (AWS, Google, Azure) and provisions a brand new virtual machine (Node) to add to your cluster. Conversely, if a node is underutilized for a long time, the CA can move Pods off it and delete the node to save money.

-----

## Summary

  * **Manual Scaling** is easy but doesn't react to changing traffic.
  * The **HPA (HorizontalPodAutoscaler)** automates scaling replicas up and down based on metrics like CPU or memory.
  * Think of the HPA like a **thermostat**, trying to keep your environment at a target utilization level.
  * The HPA requires the **Metrics Server** to be running in your cluster to function.
  * For a fully elastic cluster, you combine the **HPA** (to scale Pods) with the **Cluster Autoscaler** (to scale the underlying Nodes).

!!! tip
    Scaling is not instant. It takes time for Metrics Server to gather data, time for the HPA to calculate the change, and time for the new application Pod to start up and pass its readiness probes. Don't set your target too high (e.g., 95%), or your app might crash from overload before the new Pods are ready to help. A target of 50-70% is a common starting point.