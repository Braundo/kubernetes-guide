---
icon: material/circle-small
---

There are two types of accounts in Kubernetes

1. **Service** - bots
2. **User** - humans
<br><br>

To create a service account, run `kubectl create serviceaccount <name>`

- You must separately created a token (`kubectl create token <name>`), which the ServiceAccount can use as an authentication bearer token when interacting with the Kubernetes API
<br><br>

For every Namespace in Kubernetes, there is a **default** ServiceAccount

- Whenever a Pod is created, the default ServiceAccount and it’s token are automatically mounted to that Pod as a volume


!!! warning "The default ServiceAccount only has basic permissions to run Kubernetes operations"


- You can modify your Pod definition to leverage a different ServiceAccount, if desired under `spec.serviceAccountName`

    - You **cannot** edit the existing ServiceAccount of a Pod (immutable), but you **can** for Deployments