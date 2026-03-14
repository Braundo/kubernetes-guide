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

High-value outputs:

- CVE severity and fix availability
- package inventory and dependency tree
- base image drift from approved baseline

## SBOM and traceability

Generate SBOMs for every release image.

SBOMs enable fast response to new advisories because you can query where affected libraries are running without rebuilding everything first.

## Signing and verification

Sign released images and verify signatures in admission.

`cosign` with Sigstore-based workflows is a common modern approach.

```bash
cosign sign --keyless ghcr.io/example/api:v1.9.0
cosign verify --keyless ghcr.io/example/api:v1.9.0
```

## Admission enforcement

Scanning and signing only matter if policy is enforced at deploy time.

Typical admission rules:

- only allow images from approved registries
- require valid signatures from trusted identity or keys
- block images above configured CVE severity threshold

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
