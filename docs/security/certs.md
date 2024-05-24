---
icon: material/circle-small
---


## TLS (Transport Layer Security)
TLS is essential for securing data in transit. It provides encryption, integrity, and authentication to ensure that communications between Kubernetes components (like Nodes, Pods, and the API server) remain confidential and secure from tampering.

**Role of Asymmetric Encryption:**

Asymmetric encryption, a fundamental component of TLS, involves a pair of keys:

- **Private Key**: Kept secret and used to decrypt data and sign digital signatures.
- **Public Key**: Distributed openly and used to encrypt data and verify signatures.

When a Kubernetes component, such as a user or another cluster component, needs to establish a trusted connection, it presents a certificate containing its public key. This certificate acts as a "digital passport" to prove its identity to another party in the transaction. The trust is established through a Certificate Authority (CA) that signs these certificates. Even if a malicious actor intercepts the public key, they cannot decrypt the communications or impersonate the certificate holder without the corresponding private key.
<br><br>

**Certificate Usage in Kubernetes:**

In Kubernetes, TLS certificates are used to secure the connections between:
- Nodes and the API server
- Users and the API server
- Inter-pod communications when configured

This security mechanism ensures that sensitive data such as API tokens, application data, and administrative commands are transmitted securely over the network, preventing unauthorized access and ensuring data integrity.
<br><br>

**Practical Implications:**

By utilizing TLS, Kubernetes enhances the overall security posture of your cluster, safeguarding your infrastructure against interception and ensuring that only authorized users and services can communicate with sensitive components. Proper management of these certificates—including regular updates and revocations as necessary—is critical to maintaining the security integrity of the entire system.



## Certificates
Every component in Kubernetes communicates via secure communications. 

Kubernetes requires at least one Certificate Authority (CA) to anchor the trust in the cluster. This CA is responsible for issuing certificates for all of the Kubernetes components and can also sign the certificates for the users. Having a dedicated CA within the cluster allows for a managed and secure mechanism to handle encryption and authentication across all communications within the cluster.


### Creating CA certs:

Generate keys:
    
```bash
openssl genrsa -out ca.key 2048
```
    
<br>

Create certificate signing request:
```bash
openssl req -new -key ca.key -subj "/CN=KUBERNETES=CA" -out ca.csr
```
<br>

Sign the certificate. Note this will be *self-signed* using it’s own private key we generated in step 1 above, as we are just now initially creating the CA. Subsequent tickets will all be signed by this CA:    
```bash
openssl x509 -req -in ca.csr -signkey ca.key -out ca.crt
```
<br>

### Creating client certs:

Generate keys:    
```bash
openssl genrsa -out admin.key 2048
```

<br>

Certificate signing request. Note you must add group details (`O=system:masters`) when creating user certs:   
```bash
openssl req -new -key admin.key -sub "/CN=kube-admin/O=system:masters" -out admin.csr
```
<br>

Sign certificates by specifying CA cert (`-CA ca.crt`) and key (`-CAkey ca.key`):    
```bash
openssl x509 -req -in admin.csr -CA ca.crt -CAkey ca.key -out admin.crt
```
    
<br>
### What to do with certs?

One simple way to use them (i.e. admin user cert here) is to include them in REST calls to the API server. You must include the client key (`admin.key`), the client cert (`admin.crt`) and the CA cert (`ca.crt`) in your call:

```bash
curl https://kube-apiserver:6443/api/v1/pods --key admin.key --cert admin.crt --cacert ca.crt
```
<br>
Another easy thing to do is to include them in a **kubeconfig** file:

```yaml
apiVersion: v1
clusters:
- cluster:
    certificate-authority: ca.crt
    server: https://kube-apiserver:6443
  name: kubernetes-cluster-1
kind: Config
users:
- name: kubernetes-admin
  user:
    client-certificate: admin.crt
    client-key: admin.key
```

!!! info "All certificate operations are carried out by the **ControllerManager** on the control plane"
<br>
# KubeConfig

A **kubeconfig** file lets you specify certificate information without having to type it in every time you run a `kubectl` command
> By default, `kubectl` will look for a **kubeconfig** file at `$HOME/.kube/config`

<br>

A **kubeconfig** file consists of three specific parts:
1. **clusters**: specification of the cluster you want to connect to (i.e. dev, production, etc.)
2. **users**: the user account you will use to run commands(i.e. admin, dev, etc.)
3. **contexts** the "marrying" of a cluster and a user (i.e. dev user on production cluster)
> Under each **cluster** and **user** specs, you can list out the necessary certificates required for access

<br>
```yaml
apiVersion: v1
kind: Config

clusters:
- name: my-kube-playground
  cluster:
    certificate-authority: ca.crt
    server: https://my-kube-playground:6443
    
contexts:
- name: my-kube-admin@my-kube-playground
  context:
    cluster: my-kube-playground
    user: my-kube-admin
    namespace: finance # this field is optional
users:
- name: my-kube-admin
  user:
    client-certificate: admin.crt
    client-key: admin.key
```

To change contexts, run:
    
```bash
kubectl config use-context <context-name>
```
<br>
    

You can also specify the certificate info via **base64** as well:
``` yaml
apiVersion: v1
kind: Config

clusters:
- name: my-kube-playground
  cluster:
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0....
    
...
```