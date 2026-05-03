---
icon: lucide/badge-info
title: Certified Kubernetes Application Developer (CKAD) Exam Guide
description: Deep preparation guide for the CKAD exam - fast manifest generation, multi-container patterns, probes, config management, and exam strategies that actually help you pass.
hide:
 - footer
---

# Certified Kubernetes Application Developer (CKAD)

The CKAD is a **two-hour, hands-on lab exam** focused entirely on running applications in Kubernetes - not managing the cluster. You'll be creating and modifying workloads, wiring up config and secrets, writing probes, exposing services, and debugging broken apps. Speed is the biggest constraint: you need to produce correct YAML fast and know the right `kubectl` flags without looking them up.

---

## Exam Facts

| | |
|---|---|
| Format | Browser-based terminal, multiple live clusters |
| Duration | 2 hours |
| Passing score | 66% |
| Price | $395 USD (one free retake included) |
| Open book | `kubernetes.io/docs` only |
| Questions | ~15–20 tasks across multiple namespaces |

---

## First 3 Minutes: Terminal Setup

```bash
# kubectl autocomplete
source <(kubectl completion bash)
echo "source <(kubectl completion bash)" >> ~/.bashrc

# Essential alias
alias k=kubectl
complete -F __start_kubectl k

# Editor (pick one and stick with it)
export KUBE_EDITOR=vim    # or nano
```

**Vim settings** (`~/.vimrc`):
```
set expandtab
set tabstop=2
set shiftwidth=2
```

---

## The Core Skill: Generate YAML, Don't Write It

Writing manifests from scratch is slow and error-prone. Use `--dry-run=client -o yaml` to generate a scaffold, then edit.

```bash
# Pod
kubectl run mypod --image=nginx --dry-run=client -o yaml > pod.yaml

# Pod with specific port
kubectl run mypod --image=nginx --port=8080 --dry-run=client -o yaml > pod.yaml

# Pod with env var
kubectl run mypod --image=nginx --env="DB_HOST=localhost" --dry-run=client -o yaml > pod.yaml

# Pod with labels
kubectl run mypod --image=nginx --labels="app=frontend,tier=web" --dry-run=client -o yaml > pod.yaml

# Pod with command override
kubectl run mypod --image=busybox --dry-run=client -o yaml -- /bin/sh -c "sleep 3600" > pod.yaml

# Deployment
kubectl create deployment myapp --image=nginx --replicas=3 --dry-run=client -o yaml > deploy.yaml

# Job
kubectl create job myjob --image=busybox --dry-run=client -o yaml -- /bin/sh -c "echo hello" > job.yaml

# CronJob
kubectl create cronjob mycron --image=busybox --schedule="*/5 * * * *" --dry-run=client -o yaml -- date > cron.yaml

# ConfigMap
kubectl create configmap app-config \
  --from-literal=DB_HOST=localhost \
  --from-literal=DB_PORT=5432 \
  --dry-run=client -o yaml > cm.yaml

# ConfigMap from file
kubectl create configmap app-config --from-file=config.properties --dry-run=client -o yaml

# Secret
kubectl create secret generic app-secret \
  --from-literal=password=mysecret \
  --dry-run=client -o yaml > secret.yaml

# ServiceAccount
kubectl create serviceaccount my-sa --dry-run=client -o yaml

# Service
kubectl create service clusterip mysvc --tcp=80:8080 --dry-run=client -o yaml
kubectl expose deployment myapp --port=80 --target-port=8080 --dry-run=client -o yaml
```

---

## Domain 1: Application Design & Build

### Multi-Container Pod Patterns

These appear regularly. Know the YAML for each.

**Sidecar** - enhances the main container (log shipper, proxy):
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-sidecar
spec:
  volumes:
  - name: shared-logs
    emptyDir: {}
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log/nginx
  - name: log-shipper
    image: busybox
    command: ["/bin/sh", "-c", "tail -f /logs/access.log"]
    volumeMounts:
    - name: shared-logs
      mountPath: /logs
```

**Init Container** - runs to completion before main containers start:
```yaml
spec:
  initContainers:
  - name: init-db
    image: busybox
    command: ['sh', '-c', 'until nslookup mydb; do echo waiting; sleep 2; done']
  containers:
  - name: app
    image: myapp:1.0
```

Use init containers for: waiting for a dependency, seeding a volume, running migrations.

**Ephemeral container** (debug a running pod):
```bash
kubectl debug -it <pod> --image=busybox --target=<container>
```

### Jobs and CronJobs

```yaml
# Job - runs once
apiVersion: batch/v1
kind: Job
metadata:
  name: pi
spec:
  completions: 3       # run this many times total
  parallelism: 2       # run this many in parallel
  backoffLimit: 4      # retry up to 4 times before marking failed
  template:
    spec:
      restartPolicy: Never   # Never or OnFailure - not Always
      containers:
      - name: pi
        image: perl
        command: ["perl", "-Mbignum=bpi", "-wle", "print bpi(2000)"]
```

```yaml
# CronJob
apiVersion: batch/v1
kind: CronJob
metadata:
  name: cleanup
spec:
  schedule: "0 2 * * *"   # 2am daily
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: cleanup
            image: busybox
            command: ["/bin/sh", "-c", "echo cleanup done"]
```

Cron schedule cheat sheet:
```
* * * * *
│ │ │ │ └── day of week (0-7, 0 and 7 = Sunday)
│ │ │ └──── month (1-12)
│ │ └────── day of month (1-31)
│ └──────── hour (0-23)
└────────── minute (0-59)
```

---

## Domain 2: Application Configuration

### ConfigMaps - Four Ways to Use Them

**1. Environment variable (single key):**
```yaml
env:
- name: DB_HOST
  valueFrom:
    configMapKeyRef:
      name: app-config
      key: DB_HOST
```

**2. All keys as env vars:**
```yaml
envFrom:
- configMapRef:
    name: app-config
```

**3. Mounted as a file:**
```yaml
volumes:
- name: config-vol
  configMap:
    name: app-config
containers:
- volumeMounts:
  - name: config-vol
    mountPath: /etc/config
    # each key becomes a file: /etc/config/DB_HOST, etc.
```

**4. Mounted as a specific file:**
```yaml
volumes:
- name: config-vol
  configMap:
    name: app-config
    items:
    - key: config.properties
      path: app.properties   # mounted as /etc/config/app.properties
```

### Secrets - Same Patterns, Different Object

```yaml
# Single key env var
env:
- name: PASSWORD
  valueFrom:
    secretKeyRef:
      name: app-secret
      key: password

# All keys as env vars
envFrom:
- secretRef:
    name: app-secret

# Volume mount (files)
volumes:
- name: secret-vol
  secret:
    secretName: app-secret
```

**Gotcha:** secret values in YAML must be base64 encoded. `kubectl create secret` handles this automatically. If you're writing the YAML by hand:
```bash
echo -n "mypassword" | base64   # outputs: bXlwYXNzd29yZA==
```

### Resource Requests and Limits

```yaml
containers:
- name: app
  image: nginx
  resources:
    requests:
      memory: "64Mi"
      cpu: "250m"     # 250 millicores = 0.25 CPU
    limits:
      memory: "128Mi"
      cpu: "500m"
```

- **Requests**: what the scheduler uses to find a node; guaranteed to the container
- **Limits**: hard ceiling; CPU is throttled at limit, memory causes OOM kill
- `100m` = 0.1 CPU, `1000m` = 1 CPU, `1` = 1 CPU

### SecurityContext

```yaml
# Pod-level (applies to all containers)
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000

# Container-level (overrides pod-level)
  containers:
  - name: app
    securityContext:
      runAsNonRoot: true
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
        add: ["NET_BIND_SERVICE"]
```

### ServiceAccounts

```yaml
# Create a ServiceAccount
kubectl create serviceaccount my-sa -n default

# Bind a Role to it
kubectl create rolebinding my-sa-binding \
  --role=pod-reader \
  --serviceaccount=default:my-sa

# Use it in a pod
spec:
  serviceAccountName: my-sa
  automountServiceAccountToken: false
```

---

## Domain 3: Application Deployment

### Deployment Strategies

**RollingUpdate** (default):
```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1          # max pods over desired count during update
      maxUnavailable: 0    # max pods that can be unavailable
```

**Recreate** (takes downtime, useful for incompatible migrations):
```yaml
spec:
  strategy:
    type: Recreate
```

**Rollout commands:**
```bash
kubectl rollout status deployment/myapp
kubectl rollout history deployment/myapp
kubectl rollout undo deployment/myapp
kubectl rollout undo deployment/myapp --to-revision=2
kubectl set image deployment/myapp nginx=nginx:1.25
```

**Canary deployment** (manual approach - two deployments, adjust replicas):
```bash
# stable: 9 replicas with label version=stable
# canary: 1 replica with label version=canary
# Both have label app=myapp so same Service selects them
# Traffic split ≈ 90/10 by replica ratio
```

### Horizontal Pod Autoscaler

```bash
kubectl autoscale deployment myapp --cpu-percent=50 --min=2 --max=10
```

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
```

**Note:** HPA requires metrics-server to be running in the cluster.

---

## Domain 4: Application Observability and Maintenance

### Probes - Get These Right

Probes are a major exam topic. There are three types, and you need to know when to use each.

**Liveness probe** - restarts the container if it fails:
```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 15   # wait before first check
  periodSeconds: 10          # check every 10s
  failureThreshold: 3        # restart after 3 consecutive failures
```

**Readiness probe** - removes pod from service endpoints if it fails (doesn't restart):
```yaml
readinessProbe:
  tcpSocket:
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

**Startup probe** - for slow-starting apps; disables liveness/readiness until it passes:
```yaml
startupProbe:
  exec:
    command: ["/bin/sh", "-c", "cat /tmp/healthy"]
  failureThreshold: 30   # 30 * 10s = 5 minutes to start
  periodSeconds: 10
```

**Probe types:**
- `httpGet` - HTTP GET, success if 200–399
- `tcpSocket` - TCP connection succeeds
- `exec` - command exits with 0

**Common mistake:** setting `initialDelaySeconds` too low for a slow app. The liveness probe fires before the app is up, triggers a restart, and you get a CrashLoopBackOff even though the app itself is fine.

### Debugging

```bash
# Pod not starting
kubectl describe pod <name>   # look at Events section
kubectl logs <name>
kubectl logs <name> --previous   # logs from crashed container

# Running pod - inspect without exec
kubectl describe pod <name>
kubectl top pod <name>   # resource usage (needs metrics-server)

# Get a shell
kubectl exec -it <pod> -- /bin/sh
kubectl exec -it <pod> -c <container> -- /bin/sh   # specific container

# Debug without exec available
kubectl debug -it <pod> --image=busybox --target=<container>

# Copy logs out
kubectl cp <pod>:/var/log/app.log ./app.log
```

---

## Domain 5: Services and Networking

### Service Types

```yaml
# ClusterIP (default) - internal only
apiVersion: v1
kind: Service
metadata:
  name: my-svc
spec:
  selector:
    app: myapp
  ports:
  - port: 80           # port the service listens on
    targetPort: 8080   # port on the pod
  type: ClusterIP

# NodePort - exposed on every node
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 8080
    nodePort: 30080    # optional; 30000-32767 if not set
```

**Headless Service** - no cluster IP; returns pod IPs directly via DNS:
```yaml
spec:
  clusterIP: None
  selector:
    app: myapp
```

DNS format for headless pods: `<pod-name>.<service>.<namespace>.svc.cluster.local`

### Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-svc
            port:
              number: 8080
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-svc
            port:
              number: 80
```

### NetworkPolicy

```yaml
# Deny all ingress to a set of pods
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress

# Allow only from specific pod
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - port: 8080
```

---

## Domain 6: Environment, Configuration and Security (Exam Remix)

This catches exam-takers who know the concepts but fumble the syntax. Quick reference:

**Projected volume** - merge multiple sources into one volume:
```yaml
volumes:
- name: projected
  projected:
    sources:
    - configMap:
        name: app-config
    - secret:
        secretName: app-secret
```

**Downward API** - expose pod metadata to the container:
```yaml
env:
- name: POD_NAME
  valueFrom:
    fieldRef:
      fieldPath: metadata.name
- name: POD_IP
  valueFrom:
    fieldRef:
      fieldPath: status.podIP
- name: CPU_LIMIT
  valueFrom:
    resourceFieldRef:
      containerName: app
      resource: limits.cpu
```

---

## Speed Techniques That Matter

**Edit live resources:**
```bash
kubectl edit deployment myapp   # opens in $KUBE_EDITOR
```

**Patch a single field without opening an editor:**
```bash
kubectl patch deployment myapp -p '{"spec":{"replicas":5}}'
kubectl set image deployment/myapp nginx=nginx:1.25
kubectl set resources deployment myapp -c=nginx --limits=cpu=200m,memory=512Mi
```

**Check all resources in a namespace quickly:**
```bash
kubectl get all -n <namespace>
```

**Get YAML of existing resource (to understand what's there):**
```bash
kubectl get pod <name> -o yaml
kubectl get deployment <name> -o yaml
```

**`kubectl explain` - use instead of searching docs for field names:**
```bash
kubectl explain pod.spec.containers.livenessProbe
kubectl explain deployment.spec.strategy
kubectl explain cronjob.spec.jobTemplate.spec
```

---

## What CKAD Exam Questions Actually Look Like

Understanding the format helps you read questions efficiently:

- *"Create a Pod named `web` in namespace `app` using image `nginx:1.25` that uses ConfigMap `web-config` to set env var `APP_MODE` from key `mode`."*
- *"A deployment `frontend` is failing. Find and fix the issue."* (Usually: wrong image, bad probe, wrong resource limits)
- *"Update the deployment `api` to use a rolling update strategy with `maxSurge=2` and `maxUnavailable=1`."*
- *"Create a Job `data-export` that runs 5 completions with max 2 parallel."*
- *"The pod `app` should not be able to use more than 200m CPU. Set appropriate limits."*

**Pattern for every question:** read carefully, identify what resource/namespace, generate or edit YAML, apply, verify.

---

## Common CKAD Mistakes

1. **Wrong namespace** - most questions specify one. Always use `-n <ns>` or `--namespace`.
2. **`restartPolicy: Always` on a Job** - Jobs need `Never` or `OnFailure`. This is the most common Job mistake.
3. **Forgetting `selector` in a Service** - the selector must match the pod labels.
4. **Missing `containerPort`** - doesn't break functionality (it's informational only) but some exam graders check for it.
5. **ConfigMap/Secret key case mismatch** - `DB_HOST` vs `db_host` - exact match required.
6. **Liveness probe too aggressive** - `failureThreshold: 1` with `initialDelaySeconds: 0` will restart a healthy pod before it finishes starting.
7. **Not verifying** - spend 15 seconds confirming the resource exists and has the right spec.

---

## Practice Approach

1. **Use Killer.sh** - the free simulator included with your exam purchase. It's harder than the real exam and gives you a realistic time constraint.
2. **Practice generating YAMLs from scratch without the docs** - the exam has the docs available, but looking things up takes time. Know the core manifest patterns cold.
3. **Time constraint drills** - give yourself 2 minutes per task. If you can't do it in 2 minutes, practice that scenario until you can.
4. **Deliberately practice the annoying parts**: multi-container pods, projection volumes, complex probe configurations, CronJob schedules.

---

## Recommended Resources

- [Killer.sh CKAD Simulator](https://killer.sh) - the best prep tool, included with exam purchase
- [KodeKloud CKAD Course](https://kodekloud.com/courses/certified-kubernetes-application-developer-ckad/) - good hands-on labs
- [Kubernetes Official Docs](https://kubernetes.io/docs/) - your only reference during the exam
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/) - bookmark this
- [Official CKAD Curriculum](https://github.com/cncf/curriculum) - the authoritative topic list
