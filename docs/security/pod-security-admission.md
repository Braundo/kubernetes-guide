## Pod Security Levels
The Pod Security Admission Controller places requirements on a Pod's Security Context and other related fields according to three levels defined by the Pod Security Standards:  
- Privileged
- Baseline
- Restricted


## Labels for Namespaces
Once the feature is enabled or the webhook is installed, you can configure namespaces with labels to define the admission control mode for pod security. The modes are:  
- **Enforce**: Policy violations will cause the pod to be rejected.
- **Audit**: Policy violations will trigger an audit annotation but are otherwise allowed.
- **Warn**: Policy violations will trigger a user-facing warning but are otherwise allowed.


## Workload Resources and Pod Templates
Pods are often created indirectly via workload objects like Deployments or Jobs. Both the audit and warning modes are applied to these workload resources, but the enforce mode is only applied to the resulting pod objects.

## Exemptions
You can define exemptions to bypass pod security enforcement. These exemptions can be based on:  
- Usernames
- RuntimeClassNames
- Namespaces 
- Certain pod field updates are also exempt from policy checks.
