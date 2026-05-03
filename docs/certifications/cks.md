---
icon: lucide/badge-info
title: Certified Kubernetes Security Specialist (CKS) Exam Guide
description: Deep preparation guide for the CKS exam - Falco rules, audit policies, encryption config, Pod Security, securityContext, RBAC, NetworkPolicy, and exam strategies that actually help you pass.
hide:
 - footer
---

# Certified Kubernetes Security Specialist (CKS)

The CKS is the hardest Kubernetes certification. It's hands-on, time-pressured, and tests **applied security knowledge** across a live cluster - not familiarity with concepts. You need an active CKA before you can sit it, and you'll need that cluster administration depth to solve the problems.

The exam tests your ability to *harden what's already there*, *detect what's happening*, and *limit blast radius when things go wrong*. The questions aren't "configure a cluster from scratch" - they're "fix this insecure thing" or "write this policy to enforce this constraint."

---

## Exam Facts

| | |
|---|---|
| Format | Browser-based terminal, live cluster |
| Duration | 2 hours |
| Passing score | 67% |
| Prerequisite | Active CKA certification |
| Open book | `kubernetes.io`, `falco.org/docs`, `github.com/falcosecurity` |

---

## First 3 Minutes: Terminal Setup

```bash
source <(kubectl completion bash)
alias k=kubectl
complete -F __start_kubectl k
export KUBE_EDITOR=vim
```

The CKS includes more tool-specific work than CKA/CKAD - `falco`, `trivy`, `kubesec`, `apparmor_parser`. Know the basic syntax of each before the exam.

---

## Domain 1: Cluster Setup (10%)

### Secure API Server Flags

The API server is configured via its static pod manifest: `/etc/kubernetes/manifests/kube-apiserver.yaml`

**Commonly tested flags:**

```yaml
# Disable anonymous authentication
- --anonymous-auth=false

# Enable only needed admission plugins
- --enable-admission-plugins=NodeRestriction,PodSecurity

# Disable insecure port (should already be 0 in modern k8s)
- --insecure-port=0

# Audit logging
- --audit-log-path=/var/log/kubernetes/audit.log
- --audit-policy-file=/etc/kubernetes/audit-policy.yaml
- --audit-log-maxage=30
- --audit-log-maxbackup=10
- --audit-log-maxsize=100

# Encryption at rest
- --encryption-provider-config=/etc/kubernetes/encryption-config.yaml
```

After editing the static pod manifest, kubelet restarts the API server automatically. Wait for it:
```bash
watch kubectl get pods -n kube-system
# or
crictl ps | grep apiserver
```

### Audit Policies

Audit policies control what gets logged. They match events by stage and level.

**Stages:** `RequestReceived`, `ResponseStarted`, `ResponseComplete`, `Panic`

**Levels:**
- `None` - don't log
- `Metadata` - log request metadata (who, what resource, when) but not body
- `Request` - log metadata + request body
- `RequestResponse` - log metadata + request body + response body

```yaml
# /etc/kubernetes/audit-policy.yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
# Don't log reads of configmaps and secrets (noisy)
- level: None
  resources:
  - group: ""
    resources: ["configmaps", "secrets"]
  verbs: ["get", "list", "watch"]

# Log all changes to pods at RequestResponse level
- level: RequestResponse
  resources:
  - group: ""
    resources: ["pods"]
  verbs: ["create", "update", "patch", "delete"]

# Log all actions in sensitive namespaces at Request level
- level: Request
  namespaces: ["kube-system", "kube-public"]

# Default: log metadata for everything else
- level: Metadata
```

**Key pattern:** rules are evaluated top-to-bottom; first match wins. Put specific rules before the catch-all.

### Secrets Encryption at Rest

Without this, secrets are stored as base64 (not encrypted) in etcd. The exam often asks you to enable or verify encryption.

```yaml
# /etc/kubernetes/encryption-config.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources:
  - secrets
  providers:
  - aescbc:
      keys:
      - name: key1
        secret: <base64-encoded-32-byte-key>
  - identity: {}    # fallback for existing unencrypted secrets
```

Generate a key:
```bash
head -c 32 /dev/urandom | base64
```

After adding the flag to the API server, **existing secrets are not automatically re-encrypted**. You must force a rewrite:
```bash
kubectl get secrets --all-namespaces -o json | kubectl replace -f -
```

Verify encryption worked (look for `k8s:enc:aescbc` prefix in etcd data):
```bash
ETCDCTL_API=3 etcdctl get /registry/secrets/default/my-secret \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key | hexdump -C | head
```

---

## Domain 2: System Hardening (15%)

### Pod Security Standards and Admission

Pod Security Admission (PSA) replaced PodSecurityPolicy. It enforces security standards at the namespace level via labels.

**Three profiles:**
- `privileged` - no restrictions
- `baseline` - prevents obvious escalation
- `restricted` - follows all current best practices

**Three modes:**
- `enforce` - violating pods are rejected
- `audit` - violations logged but allowed
- `warn` - user gets a warning but pod is allowed

```bash
# Label a namespace to enforce restricted policy
kubectl label namespace my-ns \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/enforce-version=latest

# Audit baseline, warn on restricted (common exam pattern)
kubectl label namespace my-ns \
  pod-security.kubernetes.io/audit=baseline \
  pod-security.kubernetes.io/warn=restricted
```

**What "restricted" requires in the pod spec:**
```yaml
spec:
  securityContext:
    runAsNonRoot: true
    seccompProfile:
      type: RuntimeDefault
  containers:
  - securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop: ["ALL"]
```

### securityContext - Know Every Field

```yaml
# Pod-level context
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000            # files created in volumes owned by this group
    runAsNonRoot: true       # reject if UID=0
    sysctls:
    - name: net.core.somaxconn
      value: "1024"

# Container-level context (overrides pod-level)
  containers:
  - name: app
    securityContext:
      allowPrivilegeEscalation: false   # can't gain more privs than parent
      readOnlyRootFilesystem: true       # immutable container FS
      privileged: false
      runAsNonRoot: true
      capabilities:
        drop: ["ALL"]
        add: ["NET_BIND_SERVICE"]        # only add what's needed
      seccompProfile:
        type: RuntimeDefault             # or Localhost with a custom profile
```

**`readOnlyRootFilesystem: true`** is a high-signal security control. If the app needs to write, use `emptyDir` volumes for `/tmp` and other write paths:
```yaml
volumeMounts:
- name: tmp
  mountPath: /tmp
volumes:
- name: tmp
  emptyDir: {}
```

### AppArmor

AppArmor profiles restrict what a container process can do at the kernel level.

```yaml
# Apply AppArmor profile to a container
spec:
  securityContext:
    appArmorProfile:
      type: Localhost
      localhostProfile: my-profile   # must be loaded on each node
```

```bash
# Check if a profile is loaded on a node
cat /sys/kernel/security/apparmor/profiles | grep my-profile

# Load a profile
apparmor_parser -q /etc/apparmor.d/my-profile

# Check what profile a container is using
kubectl get pod <name> -o yaml | grep apparmor
```

### Seccomp

Seccomp filters syscalls available to a container.

```yaml
securityContext:
  seccompProfile:
    type: RuntimeDefault        # use container runtime's default profile
    # or:
    type: Localhost
    localhostProfile: profiles/my-profile.json   # relative to /var/lib/kubelet/seccomp/
```

---

## Domain 3: Minimize Microservice Vulnerabilities (20%)

### Image Scanning with Trivy

```bash
# Scan an image
trivy image nginx:latest

# Scan for HIGH and CRITICAL only
trivy image --severity HIGH,CRITICAL nginx:latest

# Scan without pulling (if already available)
trivy image --skip-update nginx:latest

# Scan a running pod's image
kubectl get pod <name> -o jsonpath='{.spec.containers[*].image}'
trivy image <image>

# Output as JSON (useful for piping)
trivy image -f json -o results.json nginx:latest
```

**What to do with results:**
- Identify the CVE IDs and affected packages
- The exam might ask you to find the fixed version or identify which packages are vulnerable
- May ask you to change an image to a more secure alternative (e.g., `nginx:alpine`)

### Open Policy Agent / Gatekeeper

OPA/Gatekeeper enforces custom policy via `ConstraintTemplate` and `Constraint` objects.

```bash
# Check if Gatekeeper is installed
kubectl get pods -n gatekeeper-system

# List constraint templates
kubectl get constrainttemplates

# List constraints
kubectl get constraints
```

Gatekeeper uses Rego policies. The exam may ask you to create a simple `Constraint` from an existing `ConstraintTemplate`:

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: require-team-label
spec:
  match:
    kinds:
    - apiGroups: [""]
      kinds: ["Namespace"]
  parameters:
    labels: ["team"]
```

### Admission Controllers

```bash
# Check which admission controllers are enabled
cat /etc/kubernetes/manifests/kube-apiserver.yaml | grep admission

# Common security-relevant admission controllers:
# - NodeRestriction: limits what kubelet can modify
# - PodSecurity: enforces Pod Security Standards
# - AlwaysPullImages: forces image pull on every pod start (prevents cached image abuse)
```

---

## Domain 4: Supply Chain Security (20%)

### ImagePolicyWebhook

An admission controller that calls an external webhook to approve/deny images.

```yaml
# /etc/kubernetes/admission-config.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: AdmissionConfiguration
plugins:
- name: ImagePolicyWebhook
  configuration:
    imagePolicy:
      kubeConfigFile: /etc/kubernetes/webhook-kubeconfig.yaml
      allowTTL: 50
      denyTTL: 50
      retryBackoff: 500
      defaultAllow: false   # deny if webhook is unavailable
```

Add to kube-apiserver:
```yaml
- --enable-admission-plugins=...,ImagePolicyWebhook
- --admission-control-config-file=/etc/kubernetes/admission-config.yaml
```

### Image Signing with Cosign

```bash
# Generate a key pair
cosign generate-key-pair

# Sign an image
cosign sign --key cosign.key myregistry.io/myapp:1.0

# Verify signature
cosign verify --key cosign.pub myregistry.io/myapp:1.0
```

### SBOM and kubesec

```bash
# Static analysis of a Kubernetes manifest
kubesec scan pod.yaml

# Output as JSON
kubesec scan pod.yaml -o json

# kubesec gives a score and specific recommendations
# Score < 0: critical issues, likely to fail if submitted in exam context
```

---

## Domain 5: Monitoring, Logging & Runtime Security (25%)

This is the largest domain. Falco is the centerpiece.

### Falco - Core Concepts

Falco monitors system calls in real time and fires alerts when they match rules. For the CKS:
- Know how to **modify an existing rule** to change its behavior
- Know how to **write a simple rule**
- Know where the default rules file is and how to reload Falco

**Falco file locations:**
```bash
/etc/falco/falco.yaml           # main config
/etc/falco/falco_rules.yaml     # default rules (do not edit directly)
/etc/falco/falco_rules.local.yaml  # your custom rules/overrides (edit this)
```

**Falco rule structure:**
```yaml
- rule: Detect Shell in Container
  desc: Alert when a shell is spawned in a container
  condition: >
    spawned_process and
    container and
    (proc.name = bash or proc.name = sh or proc.name = zsh)
  output: >
    Shell spawned in container
    (user=%user.name container=%container.name image=%container.image.repository
    command=%proc.cmdline)
  priority: WARNING
  tags: [shell, container]
```

**Key Falco fields to know:**
```
proc.name         - process name
proc.cmdline      - full command line
user.name         - user running the process
container.name    - container name
container.image.repository - image name
fd.name           - file descriptor / filename
evt.type          - syscall type (e.g., open, execve, connect)
k8s.pod.name      - Kubernetes pod name
k8s.ns.name       - Kubernetes namespace
```

**Common exam patterns:**

Override a rule to change its output or priority:
```yaml
# In /etc/falco/falco_rules.local.yaml
- rule: Terminal shell in container
  desc: Override - add namespace to output
  condition: >
    spawned_process and container and
    (proc.name = bash or proc.name = sh)
  output: >
    Shell in container (user=%user.name pod=%k8s.pod.name ns=%k8s.ns.name)
  priority: CRITICAL
  overwrite: true
```

Disable a rule:
```yaml
- rule: Contact K8S API Server From Container
  enabled: false
```

**Reload Falco after changes:**
```bash
systemctl restart falco
# or if running in a pod:
kubectl delete pod -n falco -l app=falco
```

**View Falco alerts:**
```bash
# If running as a service
journalctl -u falco -f

# If running in a pod
kubectl logs -n falco <falco-pod> -f

# Falco writes to syslog by default; also configurable to file
tail -f /var/log/falco.log
```

### Audit Logging - What to Check

When an exam question says "review audit logs":
```bash
# Audit logs location (set by --audit-log-path)
cat /var/log/kubernetes/audit.log | python3 -m json.tool | less

# Find all kubectl exec events
grep '"verb":"create"' /var/log/kubernetes/audit.log | grep '"subresource":"exec"'

# Find events by user
grep '"username":"attacker"' /var/log/kubernetes/audit.log

# Find secret access
grep '"resource":"secrets"' /var/log/kubernetes/audit.log
```

---

## Domain 6: RBAC and Least Privilege

### Principle of Least Privilege - The Exam Pattern

The exam won't give you overly complex RBAC questions, but it will ask you to:
1. Find an overly permissive role and restrict it
2. Create a minimal role for a specific task
3. Verify permissions work correctly

```bash
# Check what a service account can do
kubectl auth can-i --list --as=system:serviceaccount:default:my-sa

# Check a specific permission
kubectl auth can-i delete pods --as=system:serviceaccount:default:my-sa -n default

# Check from outside the cluster (as a user)
kubectl auth can-i get secrets --as=jane -n production
```

**Minimal role - read pods only:**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: default
spec:
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
```

**What NOT to grant:**
```yaml
# Never this in a real cluster - and CKS will ask you to fix this
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
```

**Bind to a ServiceAccount:**
```bash
kubectl create rolebinding pod-reader-binding \
  --role=pod-reader \
  --serviceaccount=default:my-sa \
  -n default
```

### NetworkPolicy - CKS-Level Patterns

The CKS goes deeper on NetworkPolicy than the CKA. Know deny-all plus specific allow patterns.

**Full isolation - deny everything:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

**Allow egress to DNS only (required with deny-all egress):**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
```

**Allow backend to receive traffic only from frontend:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-allow-frontend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - port: 8080
```

**Common mistake:** forgetting that deny-all egress blocks DNS. Apps will fail to resolve service names. Always add the DNS allow policy alongside a deny-all egress policy.

---

## High-Value Exam Patterns

These come up frequently in CKS scenarios:

### Immutable Containers

```yaml
containers:
- name: app
  securityContext:
    readOnlyRootFilesystem: true
  volumeMounts:
  - name: tmp
    mountPath: /tmp
volumes:
- name: tmp
  emptyDir: {}
```

### Disable Service Account Token Automount

```yaml
# Namespace-wide via ServiceAccount
apiVersion: v1
kind: ServiceAccount
metadata:
  name: default
  namespace: my-ns
automountServiceAccountToken: false

# Per-pod override
spec:
  automountServiceAccountToken: false
```

### Privilege Escalation Prevention

```yaml
containers:
- securityContext:
    allowPrivilegeEscalation: false
    capabilities:
      drop: ["ALL"]
    runAsNonRoot: true
    readOnlyRootFilesystem: true
```

### Verify a Pod Isn't Running as Root

```bash
kubectl exec -it <pod> -- id
# Should show uid=1000 (not 0)

kubectl exec -it <pod> -- whoami
# Should not return "root"
```

---

## Runtime Class

RuntimeClass selects a container runtime for a pod. Used to run sensitive workloads in a stronger sandbox (e.g., gVisor, Kata Containers).

```yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor
handler: runsc

---
# Use in a pod
spec:
  runtimeClassName: gvisor
```

---

## CKS Common Mistakes

1. **Breaking the API server** - editing `/etc/kubernetes/manifests/kube-apiserver.yaml` with a syntax error. Always `cp kube-apiserver.yaml kube-apiserver.yaml.bak` before editing. Check the API server came back up after every edit: `crictl ps | grep apiserver`.

2. **Encryption doesn't apply to existing secrets** - after enabling `EncryptionConfiguration`, run the replacement command to re-encrypt existing secrets.

3. **Audit policy first-match-wins** - if your specific rule comes after the catch-all, it never fires. Always order from most-specific to least-specific.

4. **Falco rule not taking effect** - Falco must be restarted after editing rules. `systemctl restart falco` or delete the pod.

5. **NetworkPolicy with deny-all egress breaks DNS** - always add a port 53 egress allow alongside your deny-all.

6. **Forgetting Pod Security namespace labels** - `kubectl label namespace` syntax is easy to mistype. Verify with `kubectl get namespace <name> -o yaml`.

7. **Wrong API group in RBAC** - core resources (pods, secrets, services) use `apiGroups: [""]`. Apps resources (deployments) use `apiGroups: ["apps"]`. Extensions use `apiGroups: ["extensions"]`.

---

## Practice Approach

1. **Killer.sh** - mandatory. The CKS simulator is brutal and harder than the real exam. Do it twice and review every missed question.
2. **Practice breaking and fixing**: enable encryption at rest, audit policy with a specific rule, write a Falco rule that fires, apply PSA labels and see what pods get rejected.
3. **Build fluency with `kubectl auth can-i --list`** - you'll use it to verify every RBAC change you make.
4. **Time yourself** - the CKS has fewer questions than CKA/CKAD but they're harder. You have less margin to get stuck.
5. **Know where to find things** - Falco docs, PSA docs, seccomp/AppArmor examples in the official k8s docs. Navigate fast.

---

## Recommended Resources

- [Killer.sh CKS Simulator](https://killer.sh) - mandatory; included with exam purchase
- [KodeKloud CKS Course](https://kodekloud.com/courses/certified-kubernetes-security-specialist-cks/) - comprehensive hands-on labs
- [Kubernetes Security Docs](https://kubernetes.io/docs/concepts/security/) - the source of truth for PSA, seccompProfile, securityContext
- [Falco Documentation](https://falco.org/docs/) - open book during the exam; bookmark the rules reference
- [Official CKS Curriculum](https://github.com/cncf/curriculum) - authoritative topic list
- [Aqua Security blog - CKS tips](https://www.aquasec.com/cloud-native-academy/kubernetes-101/cks-exam/) - practical walkthroughs of the hardest topics
