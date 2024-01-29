## What are Service Accounts?
A service account is a non-human account in Kubernetes that provides a distinct identity within a cluster. These accounts are useful for various purposes, such as authenticating to the API server or implementing identity-based security policies. Service accounts have specific properties:  
- **Namespaced**: Bound to a Kubernetes namespace.
- **Lightweight**: Defined in the Kubernetes API.
- **Portable**: Can be easily included in configuration bundles for containerized workloads.


## Default Service Accounts
When you create a cluster, Kubernetes automatically creates a default ServiceAccount for every namespace. These default accounts have limited permissions, primarily for API discovery. If you delete the default ServiceAccount, the control plane replaces it.

## Use Cases
Service accounts can be used in scenarios like:  
- Pods needing to communicate with the Kubernetes API server.
- Pods requiring an identity for an external service.
- External services needing to communicate with the Kubernetes API server.
- Third-party security software relying on ServiceAccount identities.


## How to Use Service Accounts
- **Create a ServiceAccount**: Use `kubectl` or a manifest to define the object.
- **Grant Permissions**: Use mechanisms like RBAC to grant the necessary permissions.
- **Assign to Pods**: During Pod creation, assign the ServiceAccount.



## Granting Permissions
You can use Kubernetes RBAC to grant minimal permissions to each service account, adhering to the principle of least privilege.


## Cross-Namespace Access
RBAC can also be used to allow service accounts in one namespace to perform actions in another namespace.


## Assigning a ServiceAccount to a Pod
To assign a ServiceAccount to a Pod, set the `spec.serviceAccountName` field in the Pod specification. Kubernetes will automatically provide the credentials for that ServiceAccount to the Pod.


## Authenticating Service Account Credentials
ServiceAccounts use signed JSON Web Tokens (JWTs) to authenticate. The API server validates these tokens based on various parameters like signature, expiry, and audience.


## Authenticating in Your Own Code
If you have services that need to validate Kubernetes service account credentials, you can use methods like the TokenReview API or OIDC discovery.


## Alternatives
- Issue your own tokens and use Webhook Token Authentication for validation.
- Use service meshes like Istio for providing certificates to Pods.