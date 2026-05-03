---
icon: lucide/bell-ring
title: News
description: Curated Kubernetes news covering releases, security advisories, and ecosystem developments.
hide:
 - footer
---

# News

Curated Kubernetes news: release changes, security advisories, and ecosystem developments - filtered for operator impact.

<!-- AUTO-LATEST:START -->
| Date | News | Summary |
| --- | --- | --- |
| 2026-05-02 | [Kubernetes v1.36: Staleness Mitigation and Observability for Controllers](2026-05-02-kubernetes-v1-36-staleness-mitigation-observability.md) | Kubernetes v1.36 introduces focused improvements to controller staleness mitigation and observability. |
| 2026-04-26 | [Kubernetes v1.36: ハル (Haru)](2026-04-26-kubernetes-v1-36-haru.md) | Kubernetes v1.36, themed \"ハル (Haru)\" after the Japanese word for spring, arrives with 70 enhancements spanning 18 stable graduations, 25 beta promotions, and 25 new alpha features. |
| 2026-03-29 | [Istio Ambient Multicluster, Gateway API Inference Extension, and What They Mean for AI Infrastructure](2026-03-29-istio-ambient-multicluster-gateway-api-inference-extension.md) | Three Istio announcements out of KubeCon EU 2026 landed in close succession: ambient multicluster hit beta, the Gateway API Inference Extension integration arrived, and agentgateway joined the data plane experimentally. |
| 2026-03-28 | [Kubernetes 1.35 GA: In-Place Pod Resizing Stable and Restart Semantics Formalized](2026-03-28-when-kubernetes-restarts-pod-when-it-doesn-t.md) | Kubernetes 1.35 has reached general availability with in-place pod resource resizing now stable. This release resolves a critical terminology gap that has caused operational confusion across production environments. |
| 2026-03-28 | [KubeCon Europe 2026: What Came Out of Amsterdam](2026-03-28-kubecon-europe-2026-amsterdam-recap.md) | KubeCon Europe 2026 in Amsterdam confirmed what many platform teams already suspected: AI infrastructure is not a separate problem from Kubernetes. Here is what actually mattered and what you should do with it. |
| 2026-03-18 | [CVE-2026-3864: NFS CSI Driver Path Traversal Can Delete Unintended Directories](2026-03-18-cve-2026-3864-csi-nfs-path-traversal.md) | A path traversal vulnerability in the Kubernetes CSI Driver for NFS allows privileged users to craft volume identifiers that cause the driver to delete or modify directories outside its managed path on the NFS server. |
| 2026-03-14 | [Making etcd incidents easier to debug in production Kubernetes](2026-03-14-making-etcd-incidents-easier-debug-production-kubernetes.md) | Kubernetes control plane incidents often begin with ambiguous symptoms like slow API responses, request timeouts, or complete cluster unresponsiveness. |
| 2026-03-11 | [Announcing the AI Gateway Working Group](2026-03-11-announcing-ai-gateway-working-group.md) | The Kubernetes project has formalized a new AI Gateway Working Group, signaling that the community considers AI workload networking a problem space mature enough to deserve its own coordinated standards effort. |
| 2026-03-08 | [Deep dive: Simplifying resource orchestration with Amazon EKS Capabilities](2026-03-08-deep-dive-simplifying-resource-orchestration-amazon-eks.md) | Amazon EKS Capabilities represent a meaningful shift in how AWS positions platform tooling: rather than leaving teams to self-manage Kubernetes ecosystem components, AWS now runs those components on managed… |
| 2026-03-06 | [Spotlight on SIG Architecture API Governance](2026-03-06-spotlight-sig-architecture-api-governance.md) | Kubernetes API Governance decides what enters the core API, how versions graduate, and how deprecations are enforced. This SIG Architecture spotlight is a practical planning signal for platform teams. |
| 2026-03-06 | [Ingress-NGINX Migration Risk Signals Before March 2026 Retirement](2026-03-06-ingress-nginx-migration-risk-signals.md) | Ingress-NGINX retirement in March 2026 introduces migration risk from controller-specific behavior. Teams should validate regex, rewrite, redirect, and policy assumptions before moving to Gateway API. |
| 2026-03-06 | [Cluster API v1.12: Introducing In-place Updates and Chained Upgrades](2026-03-06-cluster-api-v1-12-introducing-place-updates-chained-upgrades.md) | Cluster API v1.12.0 shipped on January 27, 2026, introducing two significant lifecycle management capabilities: in-place updates and chained upgrades. |
| 2026-02-27 | [Kubernetes Gateway API v1.5.0: TLSRoute Reaches Stable](2026-02-27-gateway-api-v1.5.0-tlsroute-stable.md) | TLSRoute graduates to the Standard channel as v1 in Gateway API v1.5.0, along with CORS filters, ListenerSet, and client certificate validation reaching GA. |
<!-- AUTO-LATEST:END -->

## Related

- [Opinion & Overview](../insights/opinion/index.md)
- [Tool Radar](../insights/tool-radar/index.md)
- [Newsletter signup](../index.md#weekly-newsletter)
