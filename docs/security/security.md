---
icon: lucide/shield-ellipsis
---

# Security Primer

Security in Kubernetes is not a single feature you turn on. It is a **process**.

Because Kubernetes abstracts so much (networks, storage, compute), it also abstracts the attack surface. A hacker doesn't need physical access to your server if they can trick your API server into launching a privileged pod that mounts the host's filesystem.

To secure a cluster, we use a "Defense in Depth" strategy known as the **4Cs of Cloud Native Security**.

-----

## 1\. The 4Cs Model

Think of security like an onion. If an attacker peels back one layer, they shouldn't immediately reach the core.

| Layer | Responsibility | Key Defenses |
| :--- | :--- | :--- |
| **Cloud** | The Datacenter / Hardware | Firewall rules, IAM User access, Encrypted Disks. |
| **Cluster** | The Control Plane | **RBAC**, API Audit Logging, Etcd Encryption. |
| **Container** | The Image & Runtime | **Image Scanning**, Signing, limiting root users. |
| **Code** | Your Application | Static Analysis, Dependency Checks, HTTPS. |

!!! tip "The Weakest Link Rule"
    You can have the best Firewall (Cloud) and the strictest RBAC (Cluster), but if your developer hardcodes an AWS Secret Key into their Python script (Code), you are hacked.

-----

## 2\. The Attack Chain (How Hackers Break In)

Understanding *how* you get hacked helps you understand *why* we need these controls.

1.  **The Exploit:** An attacker finds a vulnerability in your web app (e.g., Log4j).
2.  **The Foothold:** They get a shell inside your Container.
3.  **The Escalation:** They notice the container is running as `root` and has a ServiceAccount mounted.
4.  **The Lateral Move:** They use the ServiceAccount to talk to the Kubernetes API and list all Secrets in the cluster.
5.  **The Goal:** They find a database password in a Secret and steal your data.

**Your Goal:** Break this chain at every single step.

-----

## 3\. The Defense Toolkit

Here is how they fit together.

### 1. Cluster Access (The Front Door)

  * **Authentication:** Who are you? (OIDC, Certificates).
  * **Authorization (RBAC):** What can you do? (Roles, Bindings).

### 2. Workload Hardening (The Cells)

  * **Pod Security Admission (PSA):** Prevent "super-user" containers. Disallow privileged mode and host mounts.
  * **Security Context:** Force containers to run as non-root users.

### 3. Network Segmentation (The Walls)

  * **Network Policies:** By default, every Pod can talk to every other Pod. Use Policies to block traffic between "Frontend" and "Database" unless explicitly allowed.

### 4. Supply Chain (The Ingredients)

  * **Image Scanning:** Check your Docker images for known CVEs before they ever reach the cluster.
  * **Signing:** Ensure only *your* trusted images are allowed to run.

-----

## 4\. Shift Left: DevSecOps

In the old days, security was a "gate" at the end. In Kubernetes, security must be defined in the YAML.

  * **Linting:** Use tools like `kube-linter` or `checkov` to scan your YAML files for mistakes (like `privileged: true`) *before* you commit them to Git.
  * **Admission Controllers:** Use tools like **OPA Gatekeeper** or **Kyverno** to reject insecure YAMLs at the API level.

-----

## Summary

  * **Security is layered.** Don't rely on just one tool.
  * **Misconfiguration is the \#1 threat.** Most breaches happen because someone left a door open (permissive RBAC, no NetworkPolicy), not because of a sophisticated zero-day.
  * **Least Privilege:** Give every user, pod, and service account the *minimum* permission they need to work. Nothing more.