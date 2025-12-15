---
icon: material/puzzle
---


Kubernetes is great at managing *stateless* things. If a web server dies, Kubernetes replaces it. Easy.

But what about complex, *stateful* applications like a Database?

  * You can't just kill a database pod randomly; you might corrupt data.
  * You can't just scale up a database by adding replicas; you need to configure leader election and data replication.
  * You need to take backups before upgrades.

Standard Kubernetes (Deployments/StatefulSets) doesn't know how to do any of that specific logic.

**Operators** solve this. An Operator is essentially a **Robot Sysadmin** packaged as software. It runs inside your cluster and knows exactly how to manage a specific application (like Postgres, Kafka, or Prometheus) day-to-day.

-----

## 1\. Custom Resource Definitions (CRDs)

Before we can have a robot, we need a language to talk to it.

Kubernetes comes with standard resources: `Pod`, `Service`, `Deployment`.
But what if you want to create a `PostgresCluster` or a `KafkaTopic`?

**CRDs (Custom Resource Definitions)** allow you to extend the Kubernetes API. They let you invent your own YAML objects.

### The CRD (The "Noun")

The CRD is just the *definition* of the new object. It tells Kubernetes: *"Hey, `Prometheus` is now a valid word in this cluster, and it looks like this schema."*

Once a CRD is installed, you can apply YAMLs like this:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: my-monitoring
spec:
  version: v2.26.0
  replicas: 2
  retention: 30d
```

Without the CRD, Kubernetes would reject this file saying `error: unknown resource type "Prometheus"`.

-----

## 2\. The Operator (The "Verb")

A CRD is just a piece of paper. If you create a `Prometheus` object, nothing happens... unless there is a Controller watching it.

**The Operator** is a Pod running custom code (usually written in Go).

1.  It **watches** for changes to its specific Custom Resources (e.g., someone created a `Prometheus` object).
2.  It **reads** the spec (e.g., "User wants 2 replicas and 30d retention").
3.  It **translates** that into standard Kubernetes objects (creating StatefulSets, ConfigMaps, Services, and PersistentVolumes).
4.  It **maintains** the state. If a backup fails, the Operator tries again.

-----

## The Operator Pattern

The "Operator Pattern" combines these two things:

1.  **CRDs:** To define the Desired State.
2.  **Custom Controller:** To implement the logic to reach that state.

### Example: The Prometheus Operator

Instead of manually managing thousands of lines of config files for Prometheus, you simply install the **Prometheus Operator**.

1.  **You:** `kubectl apply -f my-monitor.yaml` (asking for a monitoring stack).
2.  **Operator:** Sees the file.
3.  **Operator:** Automatically generates the complex `StatefulSet` configurations, creates the `Service`, mounts the correct `Secrets`, and reloads the configuration if it changes.

-----

## Operator Capability Levels

Not all Operators are created equal. The **Operator Capability Model** defines how smart the robot is.

| Level | Name | Description |
| :--- | :--- | :--- |
| **I** | **Basic Install** | Can deploy the app and minimal config. |
| **II** | **Seamless Upgrades** | Can handle version upgrades (e.g., v1.0 -\> v1.1) automatically. |
| **III** | **Full Lifecycle** | Can manage storage, backups, and failure recovery. |
| **IV** | **Deep Insights** | Provides metrics, alerts, and log processing. |
| **V** | **Auto Pilot** | Automatically scales, tunes performance, and heals without humans. |

*Aim for Level III+ operators for critical databases.*

-----

## How to Find & Install Operators

You don't usually write Operators; you buy or download them.

**OperatorHub.io** is the public registry for Kubernetes Operators.
It includes verified operators for:

  * Databases (Postgres, MongoDB, Redis)
  * Messaging (Kafka, RabbitMQ)
  * Monitoring (Prometheus, Grafana)

### Installation Methods

1.  **Plain YAML / Helm:** Many operators can be installed just by `kubectl apply` or `helm install`.
2.  **OLM (Operator Lifecycle Manager):** A system that runs on your cluster to manage the installation and *automatic upgrades* of Operators (similar to "Windows Update" for K8s apps).

-----

## Developing Your Own (Briefly)

If you are a software vendor, you might need to build an operator for your product. You typically use:

  * **Operator SDK:** A toolkit to bootstrap the code.
  * **Kubebuilder:** A framework for building Kubernetes APIs in Go.

<!-- end list -->

```bash
# Concept: Scaffolding a new Operator
operator-sdk init --domain=my-company.com
operator-sdk create api --group database --version v1 --kind PostgreSQL
```

This generates the boilerplate Go code so you can focus on the business logic: *"When user creates X, do Y."*

-----

## Summary

  * **CRDs** let you extend the Kubernetes API with your own custom objects.
  * **Operators** are the software brains that manage those custom objects.
  * Operators replace human operational knowledge (backups, scaling, upgrades) with code.
  * Use **OperatorHub.io** to find ready-to-use operators for popular software.

!!! tip "Pro Tip"
    Be careful with "Level 1" operators. If an operator only helps you install the app but doesn't help you back it up or upgrade it, you might be better off just using a Helm Chart. The real value of an Operator is "Day 2" management.