## Motivation
- You can set different **RuntimeClasses** for different Pods to balance performance and security.
- For example, you might use a runtime that employs hardware virtualization for Pods requiring high levels of information security.


## Setup
1. **Configure the CRI implementation on nodes**: This is runtime-dependent and involves setting up configurations that have a corresponding handler name.
2. **Create RuntimeClass resources**: Each configuration set up in step 1 should have an associated handler name. For each handler, create a corresponding RuntimeClass object.


## Usage
- You can specify a `runtimeClassName` in the Pod spec to use a particular **RuntimeClass**.
- If the specified **RuntimeClass** doesn't exist or the CRI can't run the corresponding handler, the Pod will enter a Failed state.


## Scheduling
- You can set constraints to ensure that Pods running with this RuntimeClass are scheduled to nodes that support it.
- This is done through the scheduling field for a RuntimeClass.