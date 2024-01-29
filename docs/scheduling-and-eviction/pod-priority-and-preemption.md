## How to Use Priority and Preemption
- Add one or more `PriorityClasses`.
- Create Pods with `priorityClassName` set to one of the added `PriorityClasses`.



## PriorityClass
- Defines a mapping from a priority class name to the integer value of the priority.
- Optional fields: `globalDefault` and `description`.



## Non-preempting PriorityClass
**Pods with preemptionPolicy**: Never cannot preempt other pods but may still be preempted by higher-priority pods.



## Pod Priority
After you have one or more PriorityClasses, you can create Pods that specify one of those PriorityClass names in their specifications.



## Effect of Pod Priority on Scheduling Order
The scheduler orders pending Pods by their priority.



## Preemption
If no Node is found that satisfies all the specified requirements of the Pod, preemption logic is triggered.



## Limitations of Preemption
- Graceful termination of preemption victims.
- `PodDisruptionBudget` is supported, but not guaranteed.
- Inter-Pod affinity on lower-priority Pods.
- Cross node preemption is not supported.

