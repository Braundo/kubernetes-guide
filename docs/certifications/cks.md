---
icon: lucide/badge-info
title: Certified Kubernetes Security Specialist (CKS) Exam Guide
description: Learn what to expect on the CKS exam and how to prepare for Kubernetes security concepts and hands-on tasks.
hide:
  - footer
---

# Certified Kubernetes Security Specialist (CKS)

The **CKS** certification tests your ability to secure Kubernetes clusters and workloads. It’s hands-on, intense, and assumes you already understand Kubernetes deeply (CKA is a prerequisite).

---

## Exam Overview

- **Format**: Hands-on lab with scenarios
- **Duration**: 2 hours
- **Passing score**: 67%
- **Prerequisite**: Active CKA certification
- **Open book**: Access to [kubernetes.io](https://kubernetes.io) + [GitHub repos](https://github.com/kubernetes)

---

## Domains & Weights

| Domain                      | Weight |
|-----------------------------|--------|
| Cluster Setup               | 10%   |
| System Hardening            | 15%   |
| Minimize Microservice Vulnerabilities | 20% |
| Supply Chain Security       | 20%   |
| Monitoring, Logging & Runtime Security | 25% |
| RBAC & Network Policies     | 10%   |

---

## What You Should Master

### 1. Cluster Setup (10%)

- TLS certificates & CA bundles
- Encrypt secrets at rest (KMS + `EncryptionConfiguration`)
- Audit policy config and log location
- API server flags: `--audit-log-path`, `--enable-admission-plugins`

---

### 2. System Hardening (15%)

- Restrict host access: block `hostPath`, `hostNetwork`, `privileged`
- Use `securityContext`:

    - `runAsNonRoot`, `readOnlyRootFilesystem`, `allowPrivilegeEscalation: false`
    
- Restrict capabilities (`capabilities.drop: ["ALL"]`)
- Pod Security Admission (PSA) with restricted profile
- Runtime namespace protections (AppArmor / seccomp)

---

### 3. Minimize Microservice Vulnerabilities (20%)

- Scan images with **Trivy**, **Grype**, or **Dockle**
- Sign images with **cosign** and verify before deployment
- Use scratch/minimal base images
- Avoid running as root in Dockerfiles
- Validate liveness/readiness probe security

---

### 4. Supply Chain Security (20%)

- Use trusted registries and signed images
- Scan YAML manifests for insecure configurations (e.g., `kubesec`, `kube-score`)
- Admission control:

    - Validating/mutating webhooks
    - Gatekeeper/OPA policies

- ImagePullPolicy: `Always`

---

### 5. Monitoring, Logging & Runtime Security (25%)

- Audit policy and log filtering
- Tools:

    - **Falco** (real-time threat detection)
    - **Sysdig**, **AuditD**, or `ausearch`

- Monitor execs, privilege escalation, network anomalies
- Understand and tune Falco rules

---

### 6. RBAC & Network Policies (10%)

- Create `Role`, `ClusterRole`, `RoleBinding`, `ClusterRoleBinding`
- Apply `NetworkPolicy` to restrict Pod traffic (ingress/egress)
- Avoid `*` verbs and `*` resources in RBAC
- Restrict access by namespace and API group

---

## Practice Tips

- Practice scanning + signing images:
  - `trivy image nginx:latest`
  - `cosign sign --key cosign.key myrepo/app:1.0`
- Create test policies for:

    - PSA
    - RBAC + `kubectl auth can-i`
    - NetworkPolicy deny-by-default rules

- Trigger and detect audit events
- Write Falco rules for suspicious behaviors

---

## Test Environment Tips

- Use bookmarks:

    - [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
    - [Audit Logging](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/)
    - [Sysdig Falco](https://falco.org/docs/)

- Open multiple terminals: cluster work, docs lookup, test scripts
- Save frequently used YAML snippets

---

## Recommended Resources

- [Kubernetes Official Docs](https://kubernetes.io/docs/)
- [Killer.sh Simulator (CKS)](https://killer.sh/cks/)
- [KodeKloud CKS Course](https://kodekloud.com/p/certified-kubernetes-security-specialist/)
- [Linux Foundation CKS Training](https://training.linuxfoundation.org/certification/certified-kubernetes-security-specialist-cks/)
- [Sysdig Falco + GitHub rules](https://github.com/falcosecurity/falco)

---

## Summary

CKS is all about **applying security best practices under pressure**. You’ll configure audit logs, write PodSecurity controls, patch RBAC, restrict networks, and scan or sign container images - all in live clusters.

Hands-on practice is key. Read YAML fast. Think like an attacker.
