## General Good Practice
Least Privilege: Assign minimal RBAC rights to users and service accounts. Use RoleBindings instead of ClusterRoleBindings, avoid wildcard permissions, and don't use cluster-admin accounts for daily tasks.


## Minimize Distribution of Privileged Tokens
Limit the number of nodes running powerful pods and avoid running them alongside untrusted or publicly-exposed ones. Use Taints, NodeAffinity, or PodAntiAffinity to ensure separation.


## Hardening
Review default RBAC rights and make changes to harden security. For instance, review bindings for the `system:unauthenticated` group and set `automountServiceAccountToken: false` to avoid auto-mounting of service account tokens.


## Periodic Review
Regularly review RBAC settings to remove redundant entries and check for privilege escalations.


## Privilege Escalation Risks
Be cautious with privileges like listing secrets, workload creation, and persistent volume creation as they can lead to privilege escalation.


## Denial of Service Risks
Users with object creation rights can potentially create a denial-of-service condition. Resource quotas can be used to mitigate this issue.