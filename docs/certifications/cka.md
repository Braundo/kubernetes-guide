---
icon: lucide/badge-info
title: Certified Kubernetes Administrator (CKA) Exam Guide
description: Deep preparation guide for the CKA exam - commands, YAML patterns, troubleshooting workflows, and exam strategies that actually help you pass.
hide:
 - footer
---

# Certified Kubernetes Administrator (CKA)

The CKA is a **two-hour, hands-on lab exam** across multiple Kubernetes clusters. You're solving real problems under time pressure - no multiple choice, no theory. This guide focuses on the things that actually matter: the commands you need muscle memory for, the YAML you should be able to produce fast, and the systematic approaches that prevent you from spinning in place during troubleshooting questions.

---

## Exam Facts

| | |
|---|---|
| Format | Browser-based terminal, multiple live clusters |
| Duration | 2 hours |
| Passing score | 66% |
| Price | $395 USD (one free retake included) |
| Open book | `kubernetes.io/docs` and `github.com/kubernetes` only |
| Questions | ~17 tasks, each worth 4–13% |

---

## First 3 Minutes: Terminal Setup

Do this before touching any question. It saves 10+ minutes across the exam.

```bash
# Autocomplete (massive time saver)
source <(kubectl completion bash)
echo "source <(kubectl completion bash)" >> ~/.bashrc

# Alias - use k everywhere
alias k=kubectl
complete -F __start_kubectl k

# Set default editor to vim if you're comfortable with it
export KUBE_EDITOR=vim
```

**Vim settings** (add to `~/.vimrc` if you use vim):
```
set expandtab
set tabstop=2
set shiftwidth=2
```

For nano users, the terminal's default is usually fine - don't waste time on this.

---

## Time Management

- Each question shows its **percentage weight** - use that to triage. A 13% question deserves 3x more time than a 4% one.
- **Skip and flag** anything taking more than 3–4 minutes. Come back after completing the easier tasks.
- Always verify your answer: `kubectl get <resource> -n <namespace>` after every task.
- The exam has **multiple cluster contexts**. **Always run the context-switch command** shown at the top of each question before starting. Forgetting this is one of the most common failure modes.

```bash
kubectl config use-context <cluster-name>
```

---

## Domain 1: Cluster Architecture, Installation & Configuration (25%)

### kubeadm - Know This Cold

**Bootstrap a cluster:**
```bash
kubeadm init --apiserver-advertise-address=<IP> --pod-network-cidr=10.244.0.0/16
```

Copy the `kubeadm join` output. Then set up kubeconfig:
```bash
mkdir -p $HOME/.kube
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
chown $(id -u):$(id -g) $HOME/.kube/config
```

**Join a worker node** (use the token from `kubeadm init` output):
```bash
kubeadm join <control-plane-ip>:6443 \
  --token <token> \
  --discovery-token-ca-cert-hash sha256:<hash>
```

If the token expired, generate a new one:
```bash
kubeadm token create --print-join-command
```

**Upgrade a cluster** (this is a multi-step process - get it right):
```bash
# On the control plane node:
apt-get update
apt-get install -y kubeadm=1.XX.X-*
kubeadm upgrade plan
kubeadm upgrade apply v1.XX.X

# Drain the node, then upgrade kubelet/kubectl:
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data
apt-get install -y kubelet=1.XX.X-* kubectl=1.XX.X-*
systemctl daemon-reload
systemctl restart kubelet
kubectl uncordon <node>

# Repeat drain/upgrade/uncordon for each worker node
```

### etcd Backup and Restore

This appears on nearly every CKA exam. Memorize the exact flags.

**Backup:**
```bash
ETCDCTL_API=3 etcdctl snapshot save /opt/etcd-backup.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key
```

**Verify backup:**
```bash
ETCDCTL_API=3 etcdctl snapshot status /opt/etcd-backup.db
```

**Restore:**
```bash
ETCDCTL_API=3 etcdctl snapshot restore /opt/etcd-backup.db \
  --data-dir=/var/lib/etcd-restored

# Update the etcd static pod manifest to point to the new data dir:
# Edit /etc/kubernetes/manifests/etcd.yaml
# Change: --data-dir=/var/lib/etcd  →  --data-dir=/var/lib/etcd-restored
# Also update the hostPath volume to match the new data-dir
```

**Common mistake:** forgetting to update `hostPath` in the etcd manifest after restore. The manifest has both a `--data-dir` flag *and* a volume mount - both need to match the new path.

### Static Pods

Static pods are managed by the kubelet directly, not the API server. Their manifests live in `/etc/kubernetes/manifests/`.

```bash
# View control plane static pod manifests
ls /etc/kubernetes/manifests/
# kube-apiserver.yaml  kube-controller-manager.yaml  kube-scheduler.yaml  etcd.yaml

# Modify a static pod: edit the file directly
vi /etc/kubernetes/manifests/kube-apiserver.yaml
# kubelet will detect the change and restart the pod automatically

# Create a static pod on a worker node:
# 1. Find the staticPodPath in the kubelet config
cat /var/lib/kubelet/config.yaml | grep staticPodPath
# 2. Drop your manifest in that path
```

### Certificate Management

```bash
# Check certificate expiry
kubeadm certs check-expiration

# Renew all certificates
kubeadm certs renew all

# Renew a specific cert
kubeadm certs renew apiserver
```

---

## Domain 2: Workloads & Scheduling (15%)

### Generate YAML Fast - Don't Write From Scratch

```bash
# Pod
kubectl run nginx --image=nginx --dry-run=client -o yaml > pod.yaml

# Deployment
kubectl create deployment myapp --image=nginx --replicas=3 --dry-run=client -o yaml > deploy.yaml

# Job
kubectl create job myjob --image=busybox --dry-run=client -o yaml -- /bin/sh -c "echo hello" > job.yaml

# CronJob
kubectl create cronjob mycron --image=busybox --schedule="*/5 * * * *" --dry-run=client -o yaml -- /bin/sh -c "date" > cron.yaml

# Service
kubectl create service clusterip mysvc --tcp=80:8080 --dry-run=client -o yaml > svc.yaml

# ConfigMap
kubectl create configmap myconfig --from-literal=key1=val1 --dry-run=client -o yaml

# Secret
kubectl create secret generic mysecret --from-literal=password=abc123 --dry-run=client -o yaml
```

### Scheduling Controls

**NodeSelector** - simple label match:
```yaml
spec:
  nodeSelector:
    disktype: ssd
```

**Node Affinity** - more expressive:
```yaml
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: disktype
            operator: In
            values:
            - ssd
```

**Taints and Tolerations:**
```bash
# Add a taint to a node
kubectl taint nodes node1 app=blue:NoSchedule

# Remove a taint
kubectl taint nodes node1 app=blue:NoSchedule-
```

```yaml
# Toleration in a pod spec
spec:
  tolerations:
  - key: "app"
    operator: "Equal"
    value: "blue"
    effect: "NoSchedule"
```

**Manual scheduling** (bypass the scheduler):
```yaml
spec:
  nodeName: node01   # skip scheduler entirely
```

**Priority Classes:**
```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority
value: 1000000
globalDefault: false
---
spec:
  priorityClassName: high-priority
```

### Rollouts

```bash
# Rollout status
kubectl rollout status deployment/myapp

# History
kubectl rollout history deployment/myapp

# Rollback
kubectl rollout undo deployment/myapp

# Rollback to specific revision
kubectl rollout undo deployment/myapp --to-revision=2

# Pause/resume (useful for canary)
kubectl rollout pause deployment/myapp
kubectl rollout resume deployment/myapp
```

---

## Domain 3: Services & Networking (20%)

### Service Types

```bash
# Expose a deployment
kubectl expose deployment myapp --port=80 --target-port=8080 --type=ClusterIP

# NodePort (exam often asks you to set a specific nodePort)
kubectl expose deployment myapp --port=80 --type=NodePort --dry-run=client -o yaml > svc.yaml
# Then edit svc.yaml to add: nodePort: 30080 under ports
```

### DNS - What You Must Know

Every service gets a DNS name: `<service>.<namespace>.svc.cluster.local`

```bash
# Test DNS from inside the cluster
kubectl run tmp --image=busybox --rm -it --restart=Never -- nslookup kubernetes
kubectl run tmp --image=busybox --rm -it --restart=Never -- nslookup my-svc.my-namespace.svc.cluster.local
```

**CoreDNS troubleshooting:**
```bash
# Check CoreDNS pods
kubectl get pods -n kube-system -l k8s-app=kube-dns

# Check CoreDNS config
kubectl describe configmap coredns -n kube-system

# DNS resolution fails? Check that pods can reach the DNS service IP
kubectl get svc -n kube-system kube-dns
```

### NetworkPolicy

NetworkPolicy is **additive** - if no policy selects a pod, all traffic is allowed. Once any policy selects a pod, only traffic explicitly allowed passes.

**Deny all ingress:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: default
spec:
  podSelector: {}
  policyTypes:
  - Ingress
```

**Allow ingress from specific namespace/pod:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-frontend
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: frontend-ns
      podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
```

**Gotcha:** when `namespaceSelector` and `podSelector` are in the same `-from` list item, they're ANDed. When they're in separate list items, they're ORed. This is a frequent exam trick.

```yaml
# AND (pod must be in that namespace AND have that label)
ingress:
- from:
  - namespaceSelector:
      matchLabels:
        ns: prod
    podSelector:
      matchLabels:
        app: frontend

# OR (pod is in that namespace OR has that label)
ingress:
- from:
  - namespaceSelector:
      matchLabels:
        ns: prod
  - podSelector:
      matchLabels:
        app: frontend
```

### Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: myapp-svc
            port:
              number: 80
```

---

## Domain 4: Storage (10%)

### PersistentVolume + PersistentVolumeClaim

The key thing to know: a PVC binds to a PV when the access modes and storage class match. The PV must have **at least** the requested capacity.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-data
spec:
  capacity:
    storage: 1Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  hostPath:
    path: /data/pv
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-data
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 500Mi
```

Mount the PVC in a pod:
```yaml
spec:
  volumes:
  - name: data-vol
    persistentVolumeClaim:
      claimName: pvc-data
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - mountPath: /data
      name: data-vol
```

**Access modes to know:**
- `ReadWriteOnce` (RWO) - one node, read/write
- `ReadOnlyMany` (ROX) - many nodes, read only
- `ReadWriteMany` (RWX) - many nodes, read/write

### StorageClass

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
```

To use a storage class in a PVC, add `storageClassName: fast` to the PVC spec.

---

## Domain 5: Troubleshooting (30%)

This is the biggest domain. Develop a systematic approach and never skip steps.

### Pod Troubleshooting Workflow

```bash
# Step 1: What's the state?
kubectl get pod <name> -n <ns>

# Step 2: Why is it in that state?
kubectl describe pod <name> -n <ns>
# Look at: Events, Conditions, Container statuses, exit codes

# Step 3: What's the application saying?
kubectl logs <name> -n <ns>
kubectl logs <name> -n <ns> --previous   # logs from crashed container

# Step 4: Get inside if it's running
kubectl exec -it <name> -n <ns> -- /bin/sh
```

**Exit codes that matter:**
- `0` - success
- `1` - application error
- `137` - OOM killed (137 = 128 + 9/SIGKILL)
- `139` - segfault
- `OOMKilled` in reason - hit memory limit, increase `resources.limits.memory`

### Common Pod Failure States

| Status | Likely cause |
|--------|-------------|
| `Pending` | No node can schedule it - check taints, resource requests, nodeSelector |
| `ImagePullBackOff` | Image name/tag wrong, registry auth missing, network issue |
| `CrashLoopBackOff` | App keeps crashing - check logs, check command/args |
| `OOMKilled` | Memory limit too low - check `kubectl describe` for reason |
| `ContainerCreating` | Volume mount issue, init container running, CNI problem |
| `Terminating` (stuck) | `kubectl delete pod <name> --grace-period=0 --force` |

### Control Plane Troubleshooting

If the API server is down, `kubectl` won't work. Use `crictl` or `docker` directly.

```bash
# Check static pod containers (control plane)
crictl ps -a

# Check kubelet (the thing that runs static pods)
systemctl status kubelet
journalctl -u kubelet -n 50 --no-pager

# Common kubelet issues:
# - config file path wrong
# - node not joining because of token expiry
# - swap enabled (kubelet refuses to start with swap on)
```

**Control plane component logs (if running as static pods):**
```bash
# API server logs
kubectl logs -n kube-system kube-apiserver-<node>

# Scheduler logs
kubectl logs -n kube-system kube-scheduler-<node>

# Controller manager logs
kubectl logs -n kube-system kube-controller-manager-<node>

# If API server is down, use crictl:
crictl logs <container-id>
```

### Node Troubleshooting

```bash
# Node status
kubectl get nodes
kubectl describe node <name>    # look at Conditions and Events

# SSH to the node, then:
systemctl status kubelet
journalctl -u kubelet -f

# Check if kubelet config is valid
cat /var/lib/kubelet/config.yaml

# Node NotReady often means:
# - kubelet is stopped: systemctl start kubelet
# - CNI is broken: check /etc/cni/net.d/
# - disk pressure: df -h
# - memory pressure: free -m
```

### Network Troubleshooting

```bash
# Can pod reach service?
kubectl exec -it <pod> -- curl http://<service>:<port>

# Can pod reach another pod?
kubectl exec -it <pod> -- ping <pod-ip>

# DNS resolution
kubectl exec -it <pod> -- nslookup <service>
kubectl exec -it <pod> -- cat /etc/resolv.conf

# Check kube-proxy
kubectl get pods -n kube-system -l k8s-app=kube-proxy
kubectl logs -n kube-system <kube-proxy-pod>

# Check iptables rules (on a node)
iptables -t nat -L | grep <service-name>
```

### Node Drain and Maintenance

```bash
# Cordon (stop new pods, keep existing)
kubectl cordon node01

# Drain (evict all pods)
kubectl drain node01 --ignore-daemonsets --delete-emptydir-data

# Return to service
kubectl uncordon node01
```

**`--ignore-daemonsets`** is almost always required - without it, drain fails if DaemonSet pods are present.

---

## RBAC - Know the Four Objects

```bash
# Create a Role (namespace-scoped)
kubectl create role pod-reader \
  --verb=get,list,watch \
  --resource=pods \
  -n default

# Create a ClusterRole (cluster-scoped)
kubectl create clusterrole secret-reader \
  --verb=get,list \
  --resource=secrets

# Bind a Role to a user/serviceaccount
kubectl create rolebinding read-pods \
  --role=pod-reader \
  --user=jane \
  -n default

# Bind a ClusterRole to a serviceaccount
kubectl create clusterrolebinding read-secrets-global \
  --clusterrole=secret-reader \
  --serviceaccount=default:my-sa

# Check what a user can do
kubectl auth can-i list pods --as=jane -n default
kubectl auth can-i "*" "*"  # check if you're admin
```

**ServiceAccount in a Pod:**
```yaml
spec:
  serviceAccountName: my-sa
  automountServiceAccountToken: false   # disable if not needed
```

---

## Useful One-Liners for the Exam

```bash
# Get all pods with their node assignments
kubectl get pods -o wide

# Get all pods across all namespaces
kubectl get pods -A

# Get events sorted by time (crucial for troubleshooting)
kubectl get events -n <ns> --sort-by=.lastTimestamp

# Force delete a stuck pod
kubectl delete pod <name> --grace-period=0 --force

# Watch pod status live
kubectl get pods -w

# Copy files to/from a pod
kubectl cp <pod>:/path/to/file ./local-file
kubectl cp ./local-file <pod>:/path/to/file

# Quick resource usage
kubectl top nodes
kubectl top pods -A

# Find which node a pod is on
kubectl get pod <name> -o jsonpath='{.spec.nodeName}'

# Get all containers in a pod
kubectl get pod <name> -o jsonpath='{.spec.containers[*].name}'

# Get a specific field from all pods
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.podIP}{"\n"}{end}'

# Explain a resource spec
kubectl explain pod.spec.containers.resources
```

---

## What to Memorize vs. Look Up

**Memorize** (no time to search):
- Terminal setup commands (aliases, completion)
- `kubectl run/create/expose` flags
- etcd backup command with all flags
- Node drain flags
- `kubeadm token create --print-join-command`
- kubelet restart: `systemctl daemon-reload && systemctl restart kubelet`
- `kubectl auth can-i`

**Look up** (docs are fast if bookmarked):
- Full `kubeadm upgrade` steps
- PV/PVC YAML structure
- NetworkPolicy spec structure
- Ingress YAML
- affinity/anti-affinity syntax

**Bookmark in advance** (know where to find quickly):
- `kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/`
- `kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/`
- `kubernetes.io/docs/concepts/services-networking/network-policies/`
- `kubernetes.io/docs/reference/generated/kubectl/kubectl-commands`

---

## Common Exam Mistakes

1. **Forgetting to switch context** before starting a question - always run the `kubectl config use-context` line given in the question.
2. **Wrong namespace** - many tasks specify a namespace. Always use `-n <namespace>` explicitly.
3. **Not verifying your work** - take 20 seconds after each task to confirm the resource exists and looks right.
4. **Spending too long on one task** - if you're stuck after 5 minutes on a low-weight task, flag it and move on.
5. **etcd restore: forgetting to update hostPath** in the etcd static pod manifest.
6. **Drain failing** - add `--ignore-daemonsets --delete-emptydir-data` to handle almost all drain failures.
7. **Editing a running deployment and forgetting to save** - use `:wq` in vim; confirm with `kubectl get`.

---

## Practice Approach

1. **Use Killer.sh** - it comes free with your exam registration and is harder than the real exam. Do it twice.
2. **Build clusters with kubeadm** in VMs or cloud instances - not just managed services. You need to know the plumbing.
3. **Time yourself** - practice 17 tasks in 2 hours. Build speed with `kubectl` before sitting the exam.
4. **Break things on purpose** - misconfigure etcd, stop kubelet, corrupt a static pod manifest, then fix it. Troubleshooting fluency comes from breaking things, not reading about them.

---

## Recommended Resources

- [Killer.sh CKA Simulator](https://killer.sh) - comes with exam purchase; the single best prep tool
- [KodeKloud CKA Course](https://kodekloud.com/courses/certified-kubernetes-administrator-cka/) - solid hands-on labs
- [Kubernetes Official Docs](https://kubernetes.io/docs/) - your only reference during the exam; know how to navigate it fast
- [Official CKA Curriculum](https://github.com/cncf/curriculum) - the authoritative list of exam topics
