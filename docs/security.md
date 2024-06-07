---
icon: material/security
---

# Securing Kubernetes: Authentication, Authorization, and Admission Control

Kubernetes security is a critical aspect of managing clusters, ensuring that only authorized users and processes can access and modify resources. This section covers API security, Role-Based Access Control (RBAC), and admission control.

## Overview of Kubernetes Security

<h3>The Big Picture</h3>

Kubernetes is API-centric, with the API server as its core component. Every interaction with the cluster, whether from users, Pods, or internal services, goes through the API server. This makes securing the API server paramount.

<h3>Typical API Request Flow</h3>

A typical API request, such as creating a Deployment, follows these steps:

1. **Authentication:** Verifies the identity of the requester.
2. **Authorization:** Checks if the authenticated user has permission to perform the action.
3. **Admission Control:** Ensures the request complies with policies.

![](../images/auth-flow.svg)

## Authentication (AuthN)

<h3>Understanding Authentication</h3>

Authentication (authN) is about proving your identity. Kubernetes does not have a built-in identity database; instead, it integrates with external identity management systems. Common methods include:

- **Client Certificates:** Signed by the cluster's Certificate Authority (CA).
- **Webhook Token Authentication:** Integrates with external systems.
- **Service Accounts:** For intra-cluster communication.

<h3>Checking Your Authentication Setup</h3>

Your cluster's details and user credentials are stored in a `kubeconfig` file, typically located at: `/home/<user>/.kube/config`

**Example `kubeconfig` File:**
```yaml
apiVersion: v1
kind: Config
clusters:
- cluster:
    name: prod-eggs
    server: https://<api-server-url>:443
    certificate-authority-data: LS0mRS1F...LS0tRj==
users:
- name: vinny
  user:
    token: FfqwFGF1gASDF4...SZY3uUQ
contexts:
- context:
    name: eggs-admin
    cluster: prod-eggs
    user: vinny
current-context: eggs-admin
```

<h3>Integrating with External IAM Systems</h3>

Most production clusters integrate with enterprise-grade Identity and Access Management (IAM) systems such as Active Directory or cloud-based IAM solutions, providing robust authentication mechanisms.

## Authorization (AuthZ)

<h3>Understanding Authorization</h3>

Authorization (authZ) determines what actions authenticated users can perform. Kubernetes uses a least-privilege model with deny-by-default, meaning you must explicitly grant permissions.

<h3>Role-Based Access Control (RBAC)</h3>

RBAC is the most common authorization module, using Roles and RoleBindings to define and assign permissions.

**Key Components:**

- **Roles:** Define a set of permissions.
- **RoleBindings:** Assign roles to users or groups.

**Example Role:**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: eggs
  name: read-deployments
rules:
- verbs: ["get", "watch", "list"]
  apiGroups: ["apps"]
  resources: ["deployments"]
```

<br>

**Example RoleBinding:**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-deployments
  namespace: eggs
subjects:
- kind: User
  name: jambo
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: read-deployments
  apiGroup: rbac.authorization.k8s.io
```

<h3>ClusterRoles and ClusterRoleBindings</h3>

ClusterRoles apply to all Namespaces, allowing for broader permissions management.

**Example ClusterRole:**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: read-deployments
rules:
- verbs: ["get", "watch", "list"]
  apiGroups: ["apps"]
  resources: ["deployments"]
```

<br>

**Example ClusterRoleBinding:**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: read-deployments
subjects:
- kind: User
  name: jambo
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: read-deployments
  apiGroup: rbac.authorization.k8s.io
```

## Admission Control

<h3>Overview of Admission Controllers</h3>

Admission controllers enforce policies on requests after authentication and authorization but before they are persisted. They come in two types:

- **Mutating Controllers:** Modify requests to ensure compliance.
- **Validating Controllers:** Reject non-compliant requests.

<h3>Common Admission Controllers</h3>

- **NodeRestriction:** Limits nodes to modifying their own objects.
- **AlwaysPullImages:** Ensures images are always pulled from the registry, preventing the use of cached images.

<h3>Example: NodeRestriction</h3>

To check admission controllers in your cluster:
```sh
$ kubectl describe pod kube-apiserver-docker-desktop -n kube-system | grep admission
--enable-admission-plugins=NodeRestriction
```

## Certificates and Service Accounts

<h3>Using Client Certificates</h3>

Client certificates authenticate users and services within the cluster. They are stored in the kubeconfig file and verified by the API server.

**Example of creating a client certificate:**
```sh
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr -subj "/CN=my-user"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 365
```

<h3>Service Accounts</h3>

Service Accounts provide identities for Pods and controllers, enabling secure intra-cluster communication. Unlike user accounts, which are meant for human users, service accounts are intended for processes that run in Pods.

**Example ServiceAccount:**
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-service-account
  namespace: default
```

<h3>Using a ServiceAccount in a Pod</h3>
To use a service account in a pod, specify the `serviceAccountName` field in the pod's spec. This binds the pod to the specified service account, allowing the pod to use the account's credentials to authenticate to the API server and other services.

**Example of a Pod using a ServiceAccount:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  serviceAccountName: my-service-account
  containers:
  - name: my-container
    image: myimage
```

## Practical Example

<h3>Deploying a "Secure" Application</h3>

**1. Create a Namespace:**
   ```sh
   $ kubectl create namespace secure-app
   ```

**2. Create a ServiceAccount:**

   ```yaml
   # serviceaccount.yaml
   apiVersion: v1
   kind: ServiceAccount
   metadata:
     name: secure-app-sa
     namespace: secure-app
   ```

   ```sh
   $ kubectl apply -f serviceaccount.yaml
   ```

**3. Deploy a Pod using the ServiceAccount:**

   ```yaml
   # pod.yaml
   apiVersion: v1
   kind: Pod
   metadata:
     name: secure-pod
     namespace: secure-app
   spec:
     serviceAccountName: secure-app-sa
     containers:
     - name: secure-container
       image: nginx
   ```
   ```sh
   $ kubectl apply -f pod.yaml
   ```

**4. Create a Role and RoleBinding:**

   ```yaml
   # role.yaml
   apiVersion: rbac.authorization.k8s.io/v1
   kind: Role
   metadata:
     namespace: secure-app
     name: pod-reader
   rules:
   - apiGroups: [""]
     resources: ["pods"]
     verbs: ["get", "watch", "list"]
   ```

   ```yaml
   # rolebinding.yaml
   apiVersion: rbac.authorization.k8s.io/v1
   kind: RoleBinding
   metadata:
     name: read-pods
     namespace: secure-app
   subjects:
   - kind: ServiceAccount
     name: secure-app-sa
     namespace: secure-app
   roleRef:
     kind: Role
     name: pod-reader
     apiGroup: rbac.authorization.k8s.io
   ```

   ```sh
   $ kubectl apply -f role.yaml
   $ kubectl apply -f rolebinding.yaml
   ```

## Summary

Securing a Kubernetes cluster involves multiple layers of authentication, authorization, and admission control. By understanding and implementing these mechanisms, you can ensure that your cluster is protected from unauthorized access and that all actions comply with defined policies.