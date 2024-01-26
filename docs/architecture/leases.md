## Leases in Distributed Systems
- Leases provide a mechanism to lock shared resources and coordinate activities.
- In Kubernetes, represented by Lease objects in the `coordination.k8s.io` API Group.


## Node Heartbeats
- The Lease API is used to communicate kubelet node heartbeats to the Kubernetes API server.
- Each Node has a corresponding Lease object in the `kube-node-lease` namespace.
- The `spec.renewTime` field is updated with each heartbeat, and the control plane uses this timestamp to determine Node availability.


## Leader Election
- Leases ensure only one instance of a component runs at a given time.
- Used by control plane components like `kube-controller-manager` and `kube-scheduler` in HA configurations.


## API Server Identity
- Starting in Kubernetes v1.26, each `kube-apiserver` uses the Lease API to publish its identity.
- Enables future capabilities that may require coordination between each `kube-apiserver`.


## Workloads
- Custom workloads can define their own use of Leases for leader election or coordination.
- Good practice to name the Lease in a way that is linked to the component or product.


## Garbage Collection
- Expired leases from `kube-apiservers` that no longer exist are garbage-collected by new `kube-apiservers` after 1 hour.


## Feature Gate
- API server identity leases can be disabled by disabling the `APIServerIdentity` feature gate.