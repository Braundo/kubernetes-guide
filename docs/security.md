---
icon: material/shield-lock-outline
---

# Security Primer

Kubernetes security isn't just one feature — it's a collection of layered controls designed to protect **clusters**, **workloads**, **data**, and **users**. Understanding how these layers work together is critical to hardening your environment.

---

## The 4Cs of Kubernetes Security

Kubernetes security builds on the **4Cs** model:

1. **Cloud / Infrastructure**
2. **Cluster**
3. **Container**
4. **Code**

Each layer provides opportunities for both defense and attack. Strong security means securing **each level**, not just one.

---

## Common Threat Vectors

| Surface Area        | Risk Example                                 |
|---------------------|-----------------------------------------------|
| Misconfigured RBAC  | Users can access or delete sensitive resources|
| Insecure Pods       | Privileged containers, exposed hostPath       |
| Unsafe Images       | Vulnerable base images or untrusted sources   |
| Over-permissive Network | No NetworkPolicy = open lateral movement |
| Secrets in plain text | Poorly handled sensitive data               |

---

## Key Kubernetes Security Concepts

Here’s a quick overview of what you’ll encounter in the upcoming sections:

### 🔐 Authentication & Authorization

- **Authentication** – Who are you?
- **Authorization (RBAC)** – What can you do?
- **Admission Controllers** – Should this action be allowed or mutated?

These mechanisms protect access to the Kubernetes API and workloads.

---

### 🧱 Pod Security

- Prevent privilege escalation
- Block host access
- Apply security contexts
- Enforce using **Pod Security Admission (PSA)**

---

### 🕵️‍♂️ Audit Logs

- Record every API request
- Help detect suspicious or unauthorized behavior
- Required for compliance in regulated environments

---

### 🔍 Image Scanning

- Analyze container images for known vulnerabilities
- Prevent deployment of unsafe workloads
- Tools: Trivy, Grype, Cosign, Clair

---

### 🔐 Secrets Management

- Use `Secret` objects (with encryption at rest)
- Avoid embedding secrets in images or environment variables
- Consider sealed secrets or external tools like Vault

---

### 🔒 Network Security

- Use **NetworkPolicies** to restrict Pod-to-Pod traffic
- Combine with Ingress controllers and TLS
- Isolate workloads by namespace or label

---

## Shift Left: DevSecOps in Kubernetes

Modern Kubernetes security integrates with CI/CD pipelines:

- Scan containers during build
- Validate policies (e.g., with OPA/Gatekeeper)
- Reject non-compliant resources before deployment

---

## Summary

Kubernetes security is broad and layered. The upcoming sections break it down into actionable areas like:

- Pod-level hardening (PSA)
- Audit and observability
- Image security and scanning
- Runtime policies and network controls

Security isn't a checkbox — it's a process. Let’s dig into each piece.