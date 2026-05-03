---
icon: lucide/scan-eye
title: Kubernetes Image Scanning and Signing Explained (Supply Chain Security)
description: Learn how container image scanning and signing improve Kubernetes supply chain security and reduce risk.
hide:
 - footer
---

# Image Scanning and Signing

Kubernetes inherits software risk from container images. Supply chain controls are required before deployment.

Two core controls:

- scanning: detect known vulnerabilities and policy violations
- signing: verify artifact provenance and integrity

## Scanning strategy

Use both build-time and continuous scanning.

- build-time scanning blocks obvious risky artifacts early
- continuous scanning catches newly disclosed CVEs after image publish

Common scanning tools:

- **Trivy** (Aqua Security): fast, widely adopted, scans images, filesystems, IaC, and Kubernetes manifests
- **Grype** (Anchore): focused vulnerability scanner with SBOM integration
- **Snyk**: commercial scanner with deep language-level dependency analysis

High-value outputs:

- CVE severity and fix availability
- package inventory and dependency tree
- base image drift from approved baseline

## SBOM and traceability

Generate SBOMs for every release image.

SBOMs enable fast response to new advisories because you can query where affected libraries are running without rebuilding everything first.

## Signing and verification

Sign released images and verify signatures in admission.

`cosign` with Sigstore-based keyless workflows is the modern standard -- it uses a short-lived certificate from Fulcio (tied to a workload identity like GitHub Actions OIDC) rather than a long-lived key file.

```bash
# Sign in CI (keyless - uses OIDC identity)
cosign sign ghcr.io/example/api:v1.9.0

# Verify (specify expected identity and OIDC issuer)
cosign verify \
  --certificate-identity "https://github.com/example/api/.github/workflows/release.yml@refs/heads/main" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  ghcr.io/example/api:v1.9.0
```

Always specify `--certificate-identity` and `--certificate-oidc-issuer` during verification. Without them, you only verify a signature exists -- not that it came from your expected CI workflow.

## Digest pinning

Use image digests instead of mutable tags in production manifests:

```yaml
image: ghcr.io/example/api@sha256:abc123...
```

Tags like `:v1.9.0` can be overwritten. A digest reference is immutable -- you know exactly which bits are running.

## Admission enforcement

Scanning and signing only matter if policy is enforced at deploy time.

Common admission enforcement tools:

- **Kyverno** or **OPA/Gatekeeper**: policy engines that can require image signatures and registry allowlists
- **Connaisseur**: focused admission webhook for image signature verification
- **Sigstore policy-controller**: dedicated controller for Sigstore-based image verification policies

Typical admission rules:

- only allow images from approved registries
- require valid cosign signature from trusted identity
- block images with Critical CVEs that have available fixes
- require digest-pinned image references in production namespaces

## Platform operating guidance

- use immutable image tags for release promotion
- reduce base image footprint to reduce vulnerability surface
- separate policy between production and development namespaces
- define emergency break-glass path with audit trail

## Summary

Supply chain security in Kubernetes requires scanning, SBOM generation, signing, and admission enforcement as one coherent pipeline.

## Related Security Concepts

- [Security Primer](security.md)
- [Pod Security](psa.md)
- [Audit and Logging](audit-logging.md)
