---
icon: material/clipboard-check-multiple-outline
---

A comprehensive command reference for everyday Kubernetes use — cleaner, deeper, and more practical than the standard cheat sheets.

---

## 🔧 Context & Configuration

| Command | Description |
|--------|-------------|
| `kubectl config get-contexts` | List all contexts |
| `kubectl config use-context <context>` | Switch to a different context |
| `kubectl config current-context` | Show the active context |
| `kubectl config view --minify` | View config of current context |
| `kubectl config set-context` | Create or modify a context |
| `kubectl config set-cluster` | Set a cluster config |
| `kubectl config set-credentials` | Configure user credentials |
| `kubectl config unset users.<user>` | Remove a user from config |

---

## 📦 Pods

| Command | Description |
|--------|-------------|
| `kubectl get pods` | List all pods in current namespace |
| `kubectl get pods -A` | List pods across all namespaces |
| `kubectl get pod <name> -o wide` | Show pod details including IP and node |
| `kubectl describe pod <name>` | Detailed pod information |
| `kubectl logs <pod>` | Logs from main container |
| `kubectl logs <pod> -c <container>` | Logs from a specific container |
| `kubectl exec -it <pod> -- /bin/sh` | Open shell session in pod |
| `kubectl delete pod <pod>` | Delete a pod (useful for restart) |

---

## 🚀 Deployments

| Command | Description |
|--------|-------------|
| `kubectl get deploy` | List deployments |
| `kubectl describe deploy <name>` | View deployment details |
| `kubectl scale deploy <name> --replicas=3` | Scale deployment |
| `kubectl rollout status deploy <name>` | Track rollout progress |
| `kubectl rollout history deploy <name>` | Show rollout history |
| `kubectl rollout undo deploy <name>` | Roll back to previous revision |
| `kubectl edit deploy <name>` | Edit deployment in-place |
| `kubectl delete deploy <name>` | Delete a deployment |

---

## 📋 Services

| Command | Description |
|--------|-------------|
| `kubectl get svc` | List services |
| `kubectl describe svc <name>` | Detailed service info |
| `kubectl expose pod nginx --port=80 --type=ClusterIP` | Expose pod as service |
| `kubectl port-forward svc/<svc> 8080:80` | Forward local port to service |
| `kubectl get endpoints` | Show service endpoints |

---

## 🌐 Ingress

| Command | Description |
|--------|-------------|
| `kubectl get ingress` | List ingress resources |
| `kubectl describe ingress <name>` | Details of an ingress resource |

---

## 📦 ConfigMaps & Secrets

| Command | Description |
|--------|-------------|
| `kubectl get configmap` | List ConfigMaps |
| `kubectl create configmap <name> --from-literal=key=value` | Create from literal |
| `kubectl create configmap <name> --from-file=file.txt` | Create from file |
| `kubectl get secret` | List Secrets |
| `kubectl create secret generic <name> --from-literal=password=secret` | Create basic secret |
| `kubectl get secret <name> -o yaml` | View base64-encoded secret |
| `kubectl get secret <name> -o jsonpath="{.data.key}" \| base64 -d` | Decode a secret |

---

## 🔐 RBAC & ServiceAccounts

| Command | Description |
|--------|-------------|
| `kubectl create sa <name>` | Create a ServiceAccount |
| `kubectl get sa` | List ServiceAccounts |
| `kubectl get clusterrolebinding -A` | List all ClusterRoleBindings |
| `kubectl describe clusterrolebinding <name>` | Show details of binding |
| `kubectl auth can-i get pods --as=system:serviceaccount:ns:sa` | Check access for a ServiceAccount |

---

## 📂 Namespaces

| Command | Description |
|--------|-------------|
| `kubectl get ns` | List namespaces |
| `kubectl create ns <name>` | Create a namespace |
| `kubectl delete ns <name>` | Delete a namespace |
| `kubectl config set-context --current --namespace=<ns>` | Set default namespace for current context |

---

## 🛠 Jobs & CronJobs

| Command | Description |
|--------|-------------|
| `kubectl create job hello --image=busybox -- echo Hello` | Run one-time job |
| `kubectl get jobs` | List jobs |
| `kubectl delete job <name>` | Delete a job |
| `kubectl create cronjob hello --image=busybox --schedule="*/5 * * * *" -- echo Hi` | Schedule recurring job |
| `kubectl get cronjob` | List CronJobs |

---

## 📦 Storage (PVs & PVCs)

| Command | Description |
|--------|-------------|
| `kubectl get pv` | List PersistentVolumes |
| `kubectl get pvc` | List PersistentVolumeClaims |
| `kubectl describe pvc <name>` | PVC details |
| `kubectl delete pvc <name>` | Delete a PVC |

---

## 🔍 Debugging & Troubleshooting

| Command | Description |
|--------|-------------|
| `kubectl get events --sort-by=.metadata.creationTimestamp` | Show recent events |
| `kubectl logs <pod> --previous` | Logs from a crashed pod |
| `kubectl exec -it <pod> -- /bin/sh` | Open shell in pod |
| `kubectl debug -it <pod> --image=busybox --target=<container>` | Ephemeral debug container |
| `kubectl top pod` | Show pod CPU/memory usage |
| `kubectl get pods -o wide` | Show node assignments and IPs |

---

## 📤 YAML & Apply

| Command | Description |
|--------|-------------|
| `kubectl apply -f <file>.yaml` | Apply a YAML manifest |
| `kubectl delete -f <file>.yaml` | Delete resource defined in YAML |
| `kubectl apply -f <file>.yaml --dry-run=client -o yaml` | Preview resource definition |
| `kubectl explain <resource>` | Show schema for a resource |

---

## 📊 Output Formatting

| Command | Description |
|--------|-------------|
| `-o wide` | Show more details (e.g. IPs, nodes) |
| `-o yaml` | Output full YAML |
| `-o jsonpath="{.items[*].metadata.name}"` | Query JSON paths |
| `--field-selector status.phase=Running` | Filter by field |
| `-l app=nginx` | Filter by label |
| `--sort-by=.metadata.name` | Sort output |

---

## 🔁 Port Forwarding & Proxies

| Command | Description |
|--------|-------------|
| `kubectl port-forward pod/<pod> 8080:80` | Port forward to pod |
| `kubectl port-forward svc/<svc> 9090:80` | Port forward to service |
| `kubectl proxy` | Run API proxy at localhost:8001 |

---

## 🧼 Cleanup & Deletion

| Command | Description |
|--------|-------------|
| `kubectl delete all --all` | Delete all resources in namespace |
| `kubectl delete pod,svc -l app=nginx` | Delete resources by label |
| `kubectl delete pvc --all` | Remove all PVCs |

---

## 🧪 Common Shortcuts

| Task | Command |
|------|---------|
| Restart a pod | `kubectl delete pod <pod>` (Deployment auto-recreates) |
| Watch pod status | `watch kubectl get pods` |
| Quick deploy NGINX | `kubectl create deploy nginx --image=nginx` |
| Expose NGINX | `kubectl expose deploy nginx --port=80 --type=LoadBalancer` |

---
