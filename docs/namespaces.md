---
icon: material/select
---

# Kubernetes Namespaces

Namespaces provide a way to divide cluster resources between multiple users. They are intended for use in environments with many users spread across multiple teams, or projects.

## Understanding Namespaces

<h3>Purpose of Namespaces</h3>

Namespaces allow you to create multiple virtual clusters within the same physical cluster. They help in organizing and managing resources efficiently.

<h3>Common Use Cases</h3>

- **Environment Separation:** Separate development, testing, and production environments.
- **Resource Quotas:** Apply resource limits to different teams or projects.
- **Access Control:** Implement fine-grained access control using Role-Based Access Control (RBAC).

## Managing Namespaces

<h3>Creating a Namespace</h3>

```sh
kubectl create namespace dev
```

<h3>Viewing Namespaces</h3>

```sh
kubectl get namespaces
```

<h3>Deleting a Namespace</h3>

```sh
kubectl delete namespace dev
```

<h3>Advanced Namespace Management</h3>

Namespaces can be used to implement advanced management strategies:

- **Network Policies:** Control traffic flow between namespaces to enhance security.
- **Custom Resource Definitions (CRDs):** Use CRDs to extend namespace capabilities with custom resources.
- **Monitoring and Logging:** Implement monitoring solutions to track resource usage and access patterns across namespaces.

<h3>Example: Network Policies for Namespaces</h3>

Network policies can be applied to namespaces to control traffic flow. Here's an example:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-namespace
  namespace: dev
spec:
  podSelector:
    matchLabels: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: frontend
```

This policy allows traffic from Pods in the `frontend` namespace to Pods in the `dev` namespace.

## Best Practices

- **Consistent Naming:** Use a consistent naming convention for namespaces.
- **Limit Resource Usage:** Apply resource quotas and limits to manage resource consumption.
- **Regular Audits:** Conduct regular audits to ensure compliance with policies.