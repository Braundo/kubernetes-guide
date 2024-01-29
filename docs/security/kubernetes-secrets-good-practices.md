## Principles and Practices
In Kubernetes, a Secret is an object that stores sensitive information like passwords, OAuth tokens, and SSH keys. Secrets offer better control over sensitive information and reduce the risk of accidental exposure. By default, Secret values are base64 encoded and stored unencrypted, but you can configure them to be encrypted at rest. Pods can reference Secrets in various ways, such as in a volume mount or as an environment variable.


## Configure Encryption at Rest
Secrets are stored unencrypted in etcd by default. It's recommended to configure encryption for Secret data in etcd.


## Configure Least-Privilege Access to Secrets
When planning your access control mechanism, like Kubernetes Role-based Access Control (RBAC), restrict access to Secret objects. Limit watch or list access to only the most privileged, system-level components. Only grant 'get' access if the component's behavior requires it.


## Additional Recommendations
- Use short-lived Secrets.
- Implement audit rules that alert on specific events, like concurrent reading of multiple Secrets by a single user.
- Improve etcd management policies, such as wiping or shredding the durable storage used by etcd once it's no longer in use.
- If there are multiple etcd instances, configure encrypted SSL/TLS communication between them.



## Configure Access to External Secrets
You can use third-party Secrets store providers to keep your confidential data outside your cluster. The Kubernetes Secrets Store CSI Driver is a DaemonSet that allows the kubelet to retrieve Secrets from external stores and mount them into specific Pods. ## For Developers


## Restrict Secret Access to Specific Containers
If a Pod has multiple containers and only one needs access to a Secret, configure the volume mount or environment variable so that the other containers don't have access.


## Protect Secret Data After Reading
After reading the Secret from an environment variable or volume, your application should still protect the value. For example, avoid logging the Secret or transmitting it to an untrusted party.


## Avoid Sharing Secret Manifests
If you configure a Secret through a manifest with the Secret data encoded as base64, avoid sharing this file or checking it into a source repository.
