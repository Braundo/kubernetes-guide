## Feature State
- As of Kubernetes v1.28, the Mixed Version Proxy is an **alpha** feature.
- Allows an API Server to proxy resource requests to other peer API servers running different Kubernetes versions.


## Use Case
- Useful for clusters with multiple API servers running different versions, especially during long-lived rollouts to new Kubernetes releases.
- Helps in directing resource requests to the correct `kube-apiserver`, preventing unexpected 404 errors during upgrades.


## Enabling Mixed Version Proxy
- Enable the UnknownVersionInteroperabilityProxy feature gate when starting the API Server.
- Requires specific command-line arguments like `--peer-ca-file`, `--proxy-client-cert-file`, `--proxy-client-key-file`, and `--requestheader-client-ca-file`.


## Proxy Transport and Authentication
- Source `kube-apiserver` uses existing flags -proxy-client-cert-file and -proxy-client-key-file to present its identity.
- Destination `kube-apiserver` verifies the peer connection based on the -requestheader-client-ca-file argument.


## Configuration for Peer API Server Connectivity
- Use `--peer-advertise-ip` and `--peer-advertise-port` to set the network location for proxying requests.
- If unspecified, it defaults to the values from `--advertise-address` or `--bind-address`.


## Mixed Version Proxying Mechanism
- Special filter in the aggregation layer identifies API groups/versions/resources that the local server doesn't recognize.
- Attempts to proxy those requests to a peer API server capable of handling them.
- If the peer API server fails to respond, a `503 ("Service Unavailable")` error is returned.


## How it Works Under the Hood
- Uses the internal `StorageVersion` API to check which API servers can serve the requested resource.
- If no peer is known for that API group/version/resource, a `404 ("Not Found")` response is returned.
- If the selected peer fails to respond, a `503 ("Service Unavailable")` error is returned.