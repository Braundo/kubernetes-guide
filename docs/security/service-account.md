---
icon: material/circle-small
---

## Understanding ServiceAccounts in Kubernetes

Kubernetes distinguishes between two primary types of accounts used for interacting with the cluster:

1. **User Accounts**: These are meant for humans or administrators of the cluster, managing authentication and authorization from an operational perspective.
2. **ServiceAccounts**: Intended for processes running in Pods that need to interact with the Kubernetes API. Unlike user accounts, ServiceAccounts are managed entirely by Kubernetes and are designed to provide an identity for processes to carry out automated actions within the cluster.

<br><br>

## Creating and Managing ServiceAccounts

To create a ServiceAccount in your current Namespace, use the following `kubectl` command:
```bash
kubectl create serviceaccount <name>
```

You must separately created a token (`kubectl create token <name>`), which the ServiceAccount can use as an authentication bearer token when interacting with the Kubernetes API
<br><br>

## Automatic Association with Pods

In Kubernetes, every Namespace comes with a default ServiceAccount. Whenever a Pod is created without specifying a ServiceAccount, it is automatically associated with the 'default' ServiceAccount of its Namespace. The credentials of this ServiceAccount, specifically its token, are automatically mounted into the Pod at `/var/run/secrets/kubernetes.io/serviceaccount` to facilitate secure API calls from within the Pod.

**Specifying a ServiceAccount for Pods:**

While the default ServiceAccount is automatically assigned, you can specify a different ServiceAccount in your Pod definition to grant it specific permissions:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mypod
spec:
  containers:
  - name: mycontainer
    image: myimage
  serviceAccountName: my-service-account
```

## Permissions and Role-Based Access Control (RBAC)

By default, ServiceAccounts have limited permissions, which restrict their operations within the cluster to basic activities. This default behavior ensures that Pods cannot perform actions that affect the entire cluster, thereby enhancing the security. However, you can grant more extensive permissions to a ServiceAccount by associating it with specific roles or cluster roles through RoleBindings or ClusterRoleBindings. This mechanism allows you to finely control what each ServiceAccount can and cannot do within your cluster. 