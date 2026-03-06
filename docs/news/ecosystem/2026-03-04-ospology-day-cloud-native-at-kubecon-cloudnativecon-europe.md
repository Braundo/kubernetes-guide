---
title: "OSPOlogy Day Cloud Native at KubeCon + CloudNativeCon Europe"
date: 2026-03-04
category: ecosystem
source_url: "https://www.cncf.io/blog/2026/03/04/ospology-day-cloud-native-at-kubecon-cloudnativecon-europe/"
generated: "2026-03-06T19:32:43.911301+00:00"
---

# OSPOlogy Day Cloud Native at KubeCon + CloudNativeCon Europe

**Source:** [CNCF Blog](https://www.cncf.io/blog/2026/03/04/ospology-day-cloud-native-at-kubecon-cloudnativecon-europe/)
**Published:** 2026-03-04 | **Category:** Ecosystem

## Summary

OSPOlogy Day Cloud Native is taking place at KubeCon + CloudNativeCon Europe as a dedicated event focused on peer mentoring and group discussions around cloud strategy management. The session addresses the maturation of cloud native management, particularly how platform engineering has evolved into a cross-organizational product. Topics include rising supply chain security expectations and the increasing regulatory requirements facing cloud native organizations.

## Why It Matters

Platform engineering has crossed a threshold from experimental practice to production discipline that spans organizational boundaries. When platform teams build internal developer platforms on Kubernetes, they're no longer just managing infrastructure. They're shipping products to internal customers with SLAs, security guarantees, and compliance requirements that directly impact business operations. This shift means your platform decisions now face scrutiny from security teams, legal departments, and executive leadership, not just your SRE peers.

The emphasis on supply chain security and regulation reflects real pressure points in production environments. If you're running Kubernetes at scale, you're already dealing with questions about SBOM generation for container images, policy enforcement through admission controllers, and audit trails for compliance frameworks. The regulatory landscape has materialized faster than many platform teams expected. What seemed like future concerns two years ago are now blocking deployments and requiring architectural changes to RBAC policies, secret management, and artifact verification pipelines.

Peer mentoring sessions at events like OSPOlogy Day provide tactical value beyond typical conference talks. Group discussions with operators facing similar problems yield practical approaches to platform standardization, governance models for CRD proliferation, and strategies for managing multiple clusters across regulatory boundaries. These conversations often surface solutions that never make it into official documentation but solve real operational headaches.

## What You Should Do

1. Audit your current platform engineering governance model and identify where cross-organizational dependencies exist. Map which teams consume your platform APIs and what compliance requirements they inherit from your infrastructure choices.

2. Review your supply chain security posture by checking whether you can produce SBOMs for all container images in production clusters. Run `kubectl get pods --all-namespaces -o json | jq '.items[].spec.containers[].image'` to inventory images and verify you have provenance data.

3. Document your current admission control policies and identify gaps in policy enforcement for security and compliance requirements. List all ValidatingWebhookConfigurations and MutatingWebhookConfigurations to understand what's actually being enforced.

4. Establish a channel for sharing platform engineering practices with peer organizations. Consider joining the OSPOlogy community or similar forums where you can compare approaches to common problems like multi-tenancy isolation, cost allocation, and developer experience.

## Further Reading

- [OSPOlogy Day Cloud Native announcement](https://www.cncf.io/blog/2026/03/04/ospology-day-cloud-native-at-kubecon-cloudnativecon-europe/)
- [CNCF Supply Chain Security Best Practices](https://github.com/cncf/tag-security/tree/main/supply-chain-security)
- [Kubernetes Policy Management Overview](https://kubernetes.io/docs/concepts/policy/)
- [Platform Engineering Maturity Model (CNCF)](https://tag-app-delivery.cncf.io/)

---
*Published 2026-03-06 on k8s.guide*
