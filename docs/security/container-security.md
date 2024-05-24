---
icon: material/circle-small
---

## Image Security in Kubernetes

**Trusted Repositories:**

It is a security best practice to use container images only from trusted repositories. These can include internal repositories managed within your organization, your private repositories, or reputable public repositories with verified content such as Docker Hub’s certified repositories.
<br><br>

**Default Registry:**

When specifying an image in Kubernetes without a registry, the default is Docker Hub (`docker.io`). For example, specifying `image: nginx` in your Pod definition translates to `image: docker.io/library/nginx`. It's crucial to be aware of this default behavior to avoid unintentional deployments from unverified sources.
<br><br>

**Alternative Registries:**

Another trusted source is Google Container Registry (`gcr.io`), which hosts many of the core images used by Kubernetes itself. Utilizing such reputable sources can reduce the risk of incorporating vulnerabilities from less secure registries.


## Minimizing Privileges
Running containers as the root user can pose significant security risks, particularly if the container environment is breached. It is possible, and recommended, to run containers as a non-root user to mitigate potential damage. This is achieved by specifying a non-root user in the container’s security context:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-pod
spec:
  securityContext:
    runAsUser: 1000 # non-root user
    readOnlyRootFilesystem: true
  containers:
  - name: web-container
    image: nginx
    securityContext:
      capabilities:
        add: ["NET_BIND_SERVICE"]
```
In the snippet above, we configure security context for a Pod, including:

- what user to run as
- what Linux capabilities to give the Pod
<br><br>

You can specify the `runAsUser` at the container *or* Pod level - but `capabilities` is **not** supported at the Pod level.
<br><br>
You can find out the user that is used to execute in a container by running:
    ```bash
    kubectl exec <pod-name> -- whoami
    ```