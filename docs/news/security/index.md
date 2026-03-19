---
icon: lucide/shield-alert
title: Security News
description: Recent Kubernetes security advisories with affected scope, operational risk, and remediation guidance.
hide:
 - footer
---

# Security News

Security news summarizes Kubernetes-relevant advisories and vulnerabilities with direct remediation guidance.
Only recent publications are listed here to avoid stale security noise.

<!-- AUTO-LATEST:START -->
| Date | News | Summary |
| --- | --- | --- |
| 2026-03-18 | [CVE-2026-3864: NFS CSI Driver Path Traversal Can Delete Unintended Directories](2026-03-18-cve-2026-3864-csi-nfs-path-traversal.md) | A path traversal vulnerability in the Kubernetes CSI Driver for NFS allows privileged users to craft volume identifiers that cause the driver to delete or modify directories outside its managed path on the NFS server. |
<!-- AUTO-LATEST:END -->

## Related

- [Release news](../releases/index.md)
- [Kubernetes security primer](../../security/security.md)
- [Newsletter signup](../../index.md#weekly-newsletter)
