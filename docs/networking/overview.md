---
icon: material/circle-small
---

## Pod Networking

- Kubernetes does not come with a built-in solution for Pod networking, but it does have clear expectations:
    - Every Pod should have it’s own unique IP address
    - Every Pod should be able to communicate with every other Pod on the same Node
    - Every Pod should be able to communicate with every other Pod on other nodes *without* NAT
<br><br>

- There are any networking solutions that solve this for you:
    - weave, calico, flannel, etc.

## CNI in Kubernetes

- The plugin is configured in the `kubelet.service`
    - So all of the networking magic can happen when the Kubelet is creating the containers
<br><br>

- You can view this by running `px -aux | grep kubelet`
<br><br>

- The `/opt/cni/bin` directory contains all of the CNI plugins as executables
<br><br>
- The CNI config directory has a set of configuration files and the Kubelet looks here to find out what plugin to use: `/etc/cni/net.d`
    - If there are multiple listed, it will chose the first one in alphabetical order

## Network Policy

- By default, all Pods and Services can talk to all other Pods and Services within a Kubernetes cluster regardless of which Node(s) they are on - `Allow All` by default
<br><br>

- To disable communication between certain Pods or Services, you would implement a **NetworkPolicy**
    - You link a NetworkPolicy to one or more Pods
<br><br>

- To link a NetworkPolicy to a Pod, you leverage **labels** and **selectors**
<br><br>

This policy can be configured as part of a NetworkPolicy definition:
    
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
    name: db-policy
spec:
    podSelector:
    matchLabels:
        role: db
    policyTypes:
    - Ingress
    ingress:
    - from:
    - podSelector:
        matchLabels:
            name: api-pod
    - namespaceSelector:
        matchLabels:
            name: prod # must have this label on the Namespace for it to work
    ports:
    - protocol: TCP
        port: 3306
```
<br><br>

- Kubernetes networking solutions that support NetworkPolicies:
    - Kube-router
    - Calico
    - Romana
    - Weave-net
<br><br>


You do **not** need to allow egress for a response to ingress. For example, imagine an API pod hitting a DB pod. The DB can **allow** **ingress** from the API server and not have to specify to **allow egress** for the API server to get results - the response is allowed back by default

- i.e. when you’re determining rules, you only need to be concerned with *where the traffic originates*, not responses
<br><br>

- You can omit the `podSelector` and just use `namespaceSelector` to allow all traffic within the Namespace to connect
<br><br>

You can specify resources *outside* of the Kubernetes by IP addresses as well with the `ipBlock.cidr` section:
    
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
    name: db-policy
spec:
    podSelector:
    matchLabels:
        role: db
    policyTypes:
    - Ingress
    ingress:
    - from:
    **- ipBlock:
        cidr: 192.168.5.10/32**
    ports:
    - protocol: TCP
        port: 3306
```
<br><br>

You specify the AND/OR criteria of the selectors by dashes. For example, this rule will allow traffic from Pods that match the given label **AND** match the given Namespace:    
```yaml
...
ingress:
- from:
    **-** podSelector:
        matchLabels:
        name: api-pod
    namespaceSelector:
        matchLabels:
        name: Prod
...
```
<br><br>

This will allow traffic from Pods that match either **OR** criteria:
    
```yaml
...
ingress:
- from:
    **-** podSelector:
        matchLabels:
        name: api-pod
    **-** namespaceSelector:
        matchLabels:
        name: Prod
...
```
<br><br>

For egress, we need an egress rule:
``` yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-policy
spec:
  podSelector:
    matchLabels:
      role: db
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - ipBlock:
        cidr: 192.168.5.10/32
    ports:
    - protocol: TCP
      port: 3306
  egress:
  - to: 
    - ipBlock:
        cidr: 192.168.5.10/32
    ports:
	   - protocol: TCP
	     port: 80
```