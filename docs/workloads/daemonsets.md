## What is a DaemonSet?
- A **DaemonSet** ensures that all (or some) nodes in a Kubernetes cluster run a copy of a specific Pod.
- Typical uses include running a cluster storage daemon, logs collection daemon, or node monitoring daemon on every node.


## Writing a DaemonSet Spec
- You can describe a DaemonSet in a YAML file.
- Required fields include `apiVersion`, `kind`, and `metadata`.


# Pod Template
- The `.spec.template` is a Pod template with the same schema as a Pod.
- It must have a `RestartPolicy` equal to `Always`.


## Pod Selector
- The `.spec.selector` field is a pod selector that must match the labels of the `.spec.template`.


## Running Pods on Select Nodes
- You can specify node selectors or affinities to control on which nodes the Pods will run.


## How Daemon Pods are Scheduled
- The DaemonSet controller adds spec.affinity.nodeAffinity to match the target host.
- Different schedulers can be specified for the Pods.


## Taints and Tolerations
- DaemonSet controller automatically adds a set of tolerations to DaemonSet Pods to ensure they can be scheduled even under various node conditions.


## Communicating with Daemon Pods
- Various patterns like `Push`, `NodeIP` and `Known Port`, `DNS`, and `Service` can be used for communication.


## Updating a DaemonSet
- Node labels can be changed, and the DaemonSet will update accordingly.
- Rolling updates and rollbacks can be performed.


## Alternatives to DaemonSet
- Daemon processes can also be run directly on nodes using init scripts, but DaemonSets offer several advantages like monitoring, logging, and resource isolation.


## Deployments vs DaemonSets
- Use Deployments for stateless services and DaemonSets for node-level functionalities.
