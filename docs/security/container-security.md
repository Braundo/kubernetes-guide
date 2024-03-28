---
icon: material/circle-small
---

## Image Security
- Generally, it's best-practice to only use container images from repositories that you trust - either one's internal to your company, your own private repo, or Docker's verified registry (although you should still be careful with these).
<br><br>

- If you don’t specify a registry in the `image` name in your manifest, it’s assumed to be Docker’s default registry - `docker.io`
    - i.e. putting `image: nginx` will assume it’s *actually* `image: docker.io/library/nginx`
<br><br>

- Another popular container repo is `gcr.io` - Google’s container repository where a lot of Kubernetes core images reside

## Security in Docker

- By default, Docker runs processes in containers as `root`
    - You can change this though
<br><br>

- Processes running in a container are also visible as running processes on the host itself
<br><br>

- The `root` user in the container is not the same as the `root` user on the host
    - It’s limited in it’s ability to impact the host or other processes on the host

## Security Contexts

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-pod
spec:
  containers:
  - name: ubuntu
    image: ubuntu
	  securityContext:
	    runAsUser: 1000
	    capabilities:
	      add: ["MAC_ADMIN"]
```
In the snippet above, we configure security context for a Pod, including:

- what user to run as
- and Linux capabilities to give the Pod
<br><br>

- You can specify the `runAsUser` at the container *or* Pod level - but `capabilities` is **not** supported at the Pod level
<br><br>
- You can find out the user that is used to execute in a container by running:
    ```bash
    kubectl exec <pod-name> -- whoami
    ```