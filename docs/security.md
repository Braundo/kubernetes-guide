---
icon: material/shield-lock-outline
---

<h1>Security Primer</h1>

Kubernetes security is like building a fortress with many walls—each layer protects your cluster, workloads, data, and users. Understanding how these layers work together is the key to a secure environment.

---

<h2>The 4Cs of Kubernetes Security</h2>

Kubernetes security is built on the <strong>4Cs</strong> model:

1. <strong>Cloud / Infrastructure</strong>
2. <strong>Cluster</strong>
3. <strong>Container</strong>
4. <strong>Code</strong>

> <strong>Analogy:</strong> Think of the 4Cs as security gates: each one must be strong to keep your cluster safe.

Each layer is an opportunity for both defense and attack. True security means securing <strong>every</strong> level.

---

<h2>Common Threat Vectors</h2>

| Surface Area        | Risk Example                                 |
|---------------------|-----------------------------------------------|
| Misconfigured RBAC  | Users can access or delete sensitive resources|
| Insecure Pods       | Privileged containers, exposed hostPath       |
| Unsafe Images       | Vulnerable base images or untrusted sources   |
| Over-permissive Network | No NetworkPolicy = open lateral movement |
| Secrets in plain text | Poorly handled sensitive data               |

> <strong>Tip:</strong> Most real-world incidents result from misconfigurations, not zero-day exploits.

---

<h2>Key Kubernetes Security Concepts</h2>

Quick overview of what matters most:

<h3>🔐 Authentication & Authorization</h3>
- <strong>Authentication</strong>: Who are you?
- <strong>Authorization (RBAC)</strong>: What are you allowed to do?
- <strong>Admission Controllers</strong>: Should this action be allowed or changed?

These protect access to the Kubernetes API and workloads.

---

<h3>🧱 Pod Security</h3>
- Prevent privilege escalation
- Block host access
- Apply security contexts
- Enforce using <strong>Pod Security Admission (PSA)</strong>

---

<h3>🕵️‍♂️ Audit Logs</h3>
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

<br>
Security isn't a checkbox — it's a process. Let’s dig into each piece.
<br>