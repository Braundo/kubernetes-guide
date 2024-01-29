## Introduction
- Services expose applications running on a set of Pods.
- Services can have a cluster-scoped virtual IP address (ClusterIP).
- Clients connect using the virtual IP, and Kubernetes load-balances the traffic.


## How ClusterIPs are Allocated
- **Dynamically**: The control plane picks a free IP address from the configured IP range.
- **Statically**: You can specify an IP address within the configured IP range.


## Uniqueness of ClusterIP
- Every Service ClusterIP must be unique across the cluster.
- Creating a Service with an already allocated ClusterIP will result in an error.


## Why Reserve ClusterIPs
- For well-known IP addresses that other components and users in the cluster can use.
- Example: DNS Service in the cluster may use a well-known IP.


## Avoiding ClusterIP Conflicts
- Kubernetes has an allocation strategy to reduce the risk of collision.
- The ClusterIP range is divided based on a formula.
- Dynamic IP assignment uses the upper band by default.  


For the KCAD exam, understanding how ClusterIPs are allocated, both dynamically and statically, is crucial. Also, knowing how to avoid conflicts and the uniqueness constraint can be vital.


# Service Internal Traffic Policy


## Key Points:
- **Feature State**: Available in Kubernetes v1.26 as stable.
- **Purpose**: Allows internal traffic restrictions to only route internal traffic to endpoints within the originating node. This is useful for reducing costs and improving performance.
- **Configuration**: You can enable this feature by setting .spec.internalTrafficPolicy to Local in the Service specification.
- This instructs kube-proxy to only use node-local endpoints for cluster-internal traffic.

``` yaml
    apiVersion: v1
    kind: Service
    metadata:
      name: my-service
    spec:
      selector:
        app.kubernetes.io/name: MyApp
      ports:
        protocol: TCP
          port: 80
          targetPort: 9376
      internalTrafficPolicy: Local
```


## How it Works
- The kube-proxy filters the endpoints based on the `.spec.internalTrafficPolicy` setting. When set to `Local`, only node-local endpoints - are considered. When set to `Cluster` (the default), or not set, all endpoints are considered.