## Node to Control Plane
- Follows a "hub-and-spoke" API pattern.
- All API usage from nodes or their pods terminates at the API server.
- API server listens on a secure HTTPS port, typically 443.
- Nodes should have the public root certificate and valid client credentials for secure connection.


## API Server to Kubelet
- Used for fetching logs, attaching to running pods, and port-forwarding.
- Connections terminate at the kubelet's HTTPS endpoint.
- To secure the connection, use the `--kubelet-certificate-authority` flag for the API server.
- Kubelet authentication and/or authorization should be enabled.


## API Server to Nodes, Pods, and Services
- Connections default to plain HTTP and are neither authenticated nor encrypted.
- Can be run over HTTPS but will not validate the certificate or provide client credentials.
- Not safe to run over untrusted or public networks.


## SSH Tunnels
- Supports SSH tunnels to protect control plane to nodes communication.
- API server initiates an SSH tunnel to each node and passes all traffic through the tunnel.
- Ensures traffic is not exposed outside the nodes' network.


## Konnectivity Service
- Provides TCP level proxy for control plane to cluster communication.
- Consists of the Konnectivity server in the control plane network and agents in the nodes network.
- After enabling, all control plane to nodes traffic goes through these connections.