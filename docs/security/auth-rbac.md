---
icon: material/circle-small
---

## Overview
In Kubernetes, everything from creating new resources to updating or deleting them involves making requests to the API server. This is true for everyone and everything in the Kubernetes ecosystem: from developers using `kubectl`, to the Pods running in your cluster, to the kubelets on each Node, and the control plane services that oversee cluster operations.  

Let's take an example: imagine a user named "vinny" wants to deploy a new application using a Deployment named "treats" in the "petropolis" Namespace. vinny runs a `kubectl apply` command, which sends a request to the API server. This request is securely sent over TLS, carrying vinny's credentials. The API server first authenticates vinny, making sure they are who they claim to be. Next, it checks if vinny has the permissions (via RBAC) to create Deployments in the petropolis Namespace. If vinny passes these checks, the request goes through admission control for any additional policy checks before being executed on the cluster.

## Authentication (AuthN)
Authentication is all about proving who you are. It's often referred to as "authN." At its core are credentials—every request to the API server must include them. The authentication layer checks these credentials; if they don’t match, you get a "**401 Unauthorized**" response. If they check out, you move on to authorization.  

Kubernetes doesn’t keep its own user database; instead, it connects to external systems like Active Directory or cloud IAM services for identity management. This setup prevents the creation of redundant identity systems. While Kubernetes supports client certificates out of the box, for practical use, you'll likely integrate it with your existing identity management system. Hosted Kubernetes services usually offer easy integration with their native IAM solutions.  

#### Checking Your Authentication Setup
Your connection details to Kubernetes are stored in a `kubeconfig` file. This file tells tools like `kubectl` which cluster to talk to and which credentials to use. It includes sections for defining clusters, users, contexts (which pair a user with a cluster), and the current context (the default cluster-user pair for commands).  

The `clusters` section outlines details like the cluster's API server endpoint and its CA's public key. The `users` section lists user names and their tokens, which are often X.509 certificates signed by a trusted CA. The `contexts` section pairs users with clusters, and the `current-context` sets the default for commands.  

Given a specific `kubeconfig`, `kubectl` commands are directed to the specified cluster and authenticated as the defined user. If your cluster uses an external IAM, it handles the authentication. Once authenticated, the request can proceed to authorization, where Kubernetes decides if you have the necessary permissions to carry out your request.  

## Authorization
After you've proven your identity to Kubernetes (that's authentication), you're faced with authorization, often abbreviated as authZ. This is where Kubernetes decides if you're allowed to do what you're asking to do, like creating or deleting resources.

Kubernetes uses a modular system for authorization, meaning you can have different methods in play. But once any method says "yes" to a request, it's off to the next step: admission control. The most common method for making these decisions is Role-Based Access Control (RBAC).

#### Key Concepts in RBAC
RBAC boils down to three main ideas:

- **Users**: Who is making the request?
- **Actions**: What are they trying to do?
- **Resources**: What are they trying to do it to?

Essentially, RBAC controls which users can perform which actions on which resources.

#### RBAC in Action
In RBAC, you'll deal with Roles and RoleBindings:

- **Roles** specify permissions (what actions can be performed on what resources).
- **RoleBindings** link those permissions to users.

For example, you might have a Role that allows reading Deployments in a specific Namespace and a RoleBinding that grants a user those read permissions.

```yaml
kind: Role
metadata:
  namespace: petropolis
  name: read-deployments
rules:
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "watch", "list"]
```

This Role, by itself, doesn't do much. It needs to be connected to a user through a RoleBinding:

```yaml
kind: RoleBinding
metadata:
  name: read-deployments
  namespace: petropolis
subjects:
- kind: User
  name: vinny
roleRef:
  kind: Role
  name: read-deployments
```

With this setup, a user named "vinny" can list, watch, and get deployments in the "petropolis" Namespace.

#### The Bigger Picture
Kubernetes doesn't just have Roles and RoleBindings; there are also ClusterRoles and ClusterRoleBindings for cluster-wide permissions. This system allows you to define permissions once at the cluster level and then apply them to specific Namespaces as needed.

Most Kubernetes setups come with a set of pre-created roles to get you started, including powerful roles like `cluster-admin` that should be used cautiously.

#### Authorization Takeaways
Authorization in Kubernetes, especially through RBAC, is about specifying what authenticated users are allowed to do within the cluster. It's a system built on allowing certain actions while denying everything else by default, making it crucial to carefully manage permissions to maintain security and functionality in your cluster.

Once a request clears the authentication and authorization stages, it's evaluated by admission control to apply any further policies before being executed on the cluster.

## Understanding Admission Control in Kubernetes
After a request passes through authentication and authorization, it encounters the final gatekeeper before being executed: admission control. This stage is where Kubernetes applies various policies to ensure the request aligns with cluster rules and standards.

### Types of Admission Controllers
Kubernetes employs two main types of admission controllers:

- **Mutating Admission Controllers**: These can alter requests to ensure they comply with policies. For example, they might add a missing label to an object to meet a labeling policy.
- **Validating Admission Controllers**: These verify requests against policies but don't modify the requests. If a request violates a policy, it's rejected.

Mutating controllers operate before validating ones, ensuring that any modifications are in place before final checks are made. Only requests that would change the cluster's state are subject to admission control; read-only requests bypass this process.

### Example in Action
Imagine you have a policy requiring all objects to include an `app=shop` label. A mutating controller could automatically add this label if it's missing from a request, whereas a validating controller would reject any request lacking the label.

### Admission Control on a Cluster
On Docker Desktop, for instance, the `NodeRestriction` admission controller is enabled by default, limiting what nodes can modify within their scope. Real-world clusters typically enable a broader set of controllers for comprehensive policy enforcement.

A notable example is the `AlwaysPullImages` controller, a mutating type that ensures Pods always pull their container images from a registry, preventing the use of potentially unsafe local images and ensuring only nodes with proper registry credentials can pull and run containers.

### Admission Control's Role
If any admission controller rejects a request, it stops there—no further processing occurs. But if a request gets the green light from all controllers, it's saved to the cluster store and deployed.

Admission controllers are increasingly crucial for maintaining the security and integrity of production clusters, given their power to enforce policies directly on incoming requests.

## Recap of AuthN, AuthZ, and RBAC
- **Authentication (AuthN)** validates who you are, using credentials included in every API server request. While Kubernetes doesn't manage user identities internally, it integrates with external systems for robust identity checks.
  
- **Authorization (AuthZ)**, particularly through RBAC, dictates what authenticated users can do. It's a system of allowing specific actions via Roles and RoleBindings, ensuring users have only the permissions they need.

- **Admission Control** is the last hurdle, enforcing policies on requests post-authorization. It plays a key role in keeping the cluster secure by either modifying requests to align with policies (mutating) or rejecting those that don't comply (validating).

Throughout these stages, TLS secures communication, ensuring that sensitive information remains protected as it travels to the Kubernetes API server.