---
icon: material/shield-check
---

Container images are one of the most common vectors for introducing vulnerabilities into Kubernetes clusters. Malicious, outdated, or misconfigured images can lead to privilege escalation, supply chain attacks, or data breaches. To address this, Kubernetes platforms and DevSecOps workflows rely on **image scanning** and **image signing**.

---

## Image Scanning

**Image scanning** analyzes container images for known vulnerabilities in operating system packages, libraries, and application dependencies.

### When to Scan:
- During CI/CD before pushing to a registry
- On a schedule, as CVEs are constantly updated
- Before deployment into production clusters

### Common Tools:

| Tool     | Type              | Key Features                                            |
|----------|-------------------|---------------------------------------------------------|
| **Trivy**    | CLI / CI / Kubernetes | Lightweight, fast scanner with SBOM support             |
| **Grype**    | CLI / CI            | Deep image scanning, good SBOM integration             |
| **Clair**    | API / Registry       | Integrates with container registries like Harbor       |
| **Anchore**  | CI/CD platform       | Policy-based scanning and reporting                    |
| **Aqua / Prisma / Snyk** | Enterprise | Advanced scanning, RBAC integration, UI dashboards    |

### Example: Scanning with Trivy

```bash
trivy image nginx:1.21
```

This command checks for CVEs in the `nginx:1.21` image and provides severity breakdowns and remediation guidance.

---

## Image Signing

Image signing ensures the **authenticity and integrity** of container images. Signed images can be verified before they are pulled or deployed to ensure they haven’t been tampered with.

Signing involves:
1. Creating a cryptographic signature for an image
2. Attaching it to the image metadata or registry
3. Verifying the signature during admission or runtime

### Tools:

| Tool     | Purpose                          | Notes                                         |
|----------|----------------------------------|-----------------------------------------------|
| **cosign** | Signing and verifying OCI images | Lightweight and integrates with Sigstore      |
| **Notary v2** | Signing framework (Docker 2.0) | Upcoming standard for OCI image signing       |
| **Sigstore** | Ecosystem for supply chain trust | Powers cosign, keyless signing, policy        |

### Example: Signing and Verifying with cosign

```bash
# Sign the image
cosign sign ghcr.io/example/image:tag

# Verify the image signature
cosign verify ghcr.io/example/image:tag
```

Cosign supports **keyless signing** using identity providers like GitHub Actions or OIDC credentials.

---

## Enforcing Signed Images

Signed images can be enforced at admission time using:

- **Kyverno**: Policy engine that can block unsigned or unverified images
- **OPA Gatekeeper**: Rego-based policies for image trust
- **Sigstore Policy Controller**: Native support for verifying signatures on admission

### Example: Kyverno Policy Snippet

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signatures
spec:
  validationFailureAction: enforce
  rules:
  - name: require-signed-images
    match:
      resources:
        kinds:
        - Pod
    validate:
      message: "Image must be signed with cosign."
      pattern:
        spec:
          containers:
          - image: "*"
            imagePullPolicy: "Always"
```

---

## Best Practices

- Integrate scanning into CI/CD pipelines to catch issues early
- Continuously monitor for newly discovered CVEs
- Use image signing to enforce trusted provenance
- Regularly rotate signing keys and scan SBOMs (Software Bill of Materials)
- Avoid `:latest` tags — use immutable, versioned image references

---

## Summary

Scanning and signing container images are critical steps in securing your Kubernetes supply chain. Scanning prevents vulnerable software from being deployed, while signing ensures you're running trusted, unmodified images. Together, they help protect your workloads from tampering and known exploits, forming the foundation of modern Kubernetes security.