---
icon: material/circle-small
---

## TLS
- A certificate is used to guarantee trust between two parties during a transaction
- Asymmetrical encryption is where generate **private** and **public** keys
    - You keep the **private** key with you
    - The public key can, in theory, be shared out anywhere
    - Even if an attacker has the **public** key (i.e. lock), they can’t actually decrypt the data, access the server, etc. unless they have the **private** key to do so


## Certificates
- Every component in Kubernetes communicates via secure communications
- Kubernetes requires **at least one** Certificate Authority (CA) per cluster

### Creating Certificates

**For creating the certificates for the CA:**
<br>

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

**Generating client certificates (i.e. admin user here)**
<br>

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
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUNZekNDQWN5Z0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRVUZBREF1TVFzd0NRWURWUVFHRXdKVlV6RU0gCk1Bb0dBMVVFQ2hNRFNVSk5NUkV3RHdZRFZRUUxFd2hNYjJOaGJDQkRRVEFlRncwNU9URXlNakl3TlRBd01EQmEgCkZ3MHdNREV5TWpNd05EVTVOVGxhTUM0eEN6QUpCZ05WQkFZVEFsVlRNUXd3Q2dZRFZRUUtFd05KUWsweEVUQVAgCkJnTlZCQXNUQ0V4dlkyRnNJRU5CTUlHZk1BMEdDU3FHU0liM0RRRUJBUVVBQTRHTkFEQ0JpUUtCZ1FEMmJaRW8gCjd4R2FYMi8wR0hrck5GWnZseEJvdTl2MUptdC9QRGlUTVB2ZThyOUZlSkFRMFFkdkZTVC8wSlBRWUQyMHJIMGIgCmltZERMZ05kTnlubXlSb1MyUy9JSW5mcG1mNjlpeWMyRzBUUHlSdm1ISWlPWmJkQ2QrWUJIUWkxYWRrajE3TkQgCmNXajZTMTR0VnVyRlg3M3p4MHNOb01TNzlxM3R1WEtyRHN4ZXV3SURBUUFCbzRHUU1JR05NRXNHQ1ZVZER3R0cgCitFSUJEUVErRXp4SFpXNWxjbUYwWldRZ1lua2dkR2hsSUZObFkzVnlaVmRoZVNCVFpXTjFjbWwwZVNCVFpYSjIgClpYSWdabTl5SUU5VEx6TTVNQ0FvVWtGRFJpa3dEZ1lEVlIwUEFRSC9CQVFEQWdBR01BOEdBMVVkRXdFQi93UUYgCk1BTUJBZjh3SFFZRFZSME9CQllFRkozK29jUnlDVEp3MDY3ZExTd3IvbmFseDZZTU1BMEdDU3FHU0liM0RRRUIgCkJRVUFBNEdCQU1hUXp0K3phajFHVTc3eXpscjhpaU1CWGdkUXJ3c1paV0pvNWV4bkF1Y0pBRVlRWm1PZnlMaU0gCkQ2b1lxK1puZnZNMG44Ry9ZNzlxOG5od3Z1eHBZT25SU0FYRnA2eFNrcklPZVp0Sk1ZMWgwMExLcC9KWDNOZzEgCnN2WjJhZ0UxMjZKSHNRMGJoek41VEtzWWZid2ZUd2ZqZFdBR3k2VmYxbllpL3JPK3J5TU8KLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLSA=
    
...
```