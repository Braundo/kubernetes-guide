## Concepts
- **Priority Level**: This is a configuration that defines how requests that match the level are to be handled. It specifies things like the concurrency shares, the queue length, and the queuing discipline.

- **Flow Schema**: This is used to classify incoming requests. It specifies conditions like the verbs (`GET`, `POST`, etc.), the resources (`Pods`, `Services`, etc.), and the namespaces that the requests are coming from. Once a request matches a Flow Schema, it is then handled according to its associated Priority Level.


## Configuration
**FlowSchema**:  
- `spec.matches`: Defines what requests will match this schema. You can specify multiple criteria like HTTP verbs, API groups, resources, etc.
- `spec.priorityLevelConfiguration.name`: Specifies the name of the Priority Level to use for requests that match this schema.
<br/><br/>

**PriorityLevelConfiguration**:  
- `spec.type`: Can be either "Exempt" (ignores all other fields and never queues) or "Limited" (respects other fields).
- `spec.assuredConcurrencyShares`: For "Limited" type, this sets the weight of this priority level vs others.
- `spec.queues`: For "Limited" type, this sets the number of queues for this priority level.
- `spec.queueLengthLimit`: For "Limited" type, this sets the max size of each queue.
- `spec.handSize`: For "Limited" type, this sets the number of less loaded queues that a given request is randomly assigned to.



## Example Configuration

``` yaml
# PriorityLevelConfiguration: \
Catch-all priority level
apiVersion: flowcontrol.apiserver.\
k8s.io/v1beta1
kind: PriorityLevelConfiguration
metadata:
  name: catch-all
spec:
  type: Limited
  assuredConcurrencyShares: 1
  queues: 128
  queueLengthLimit: 100
  handSize: 6

---
# FlowSchema: Catch-all flow schema
apiVersion: flowcontrol.apiserver \
.k8s.io/v1beta1
kind: FlowSchema
metadata:
  name: catch-all
spec:
  priorityLevelConfiguration:
    name: catch-all
  matchingPrecedence: 1000  # a fairly \
  low precedence
  rules:
    - subjects:
        - kind: Group
          name: system:masters
      rule:
        verbs:
          - '*'
        apiGroups:
          - '*'
        resources:
          - '*'
```


## Best Practices
- **Be Cautious**: Misconfiguration can lead to degraded API server performance. Therefore, it's crucial to test configurations under simulated conditions to understand their impact.

- **Monitoring**: Keep an eye on the API server's performance metrics to ensure that the Priority and Fairness configurations are having the desired effect.