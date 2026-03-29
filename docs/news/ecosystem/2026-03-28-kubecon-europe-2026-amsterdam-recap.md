---
title: "KubeCon Europe 2026: What Came Out of Amsterdam"
date: 2026-03-28
category: ecosystem
description: "KubeCon Europe 2026 in Amsterdam confirmed what many platform teams already suspected: AI infrastructure is not a separate problem from Kubernetes. Here is what actually mattered and what you should do with it."
---

# KubeCon Europe 2026: What Came Out of Amsterdam

KubeCon + CloudNativeCon Europe 2026 wrapped up in Amsterdam last week, and the through-line was impossible to miss. Every major announcement touched AI in some way -- not speculatively, but in concrete, operational terms. Kyverno graduated. Dapr Agents shipped v1.0. Istio added ambient multicluster and Gateway API Inference Extension in beta. CNCF published data showing 66% of organizations are now running generative AI workloads on Kubernetes. And yet only 7% of those organizations achieve daily deployments for AI workloads.

That gap between "we run AI on Kubernetes" and "we operate AI on Kubernetes the way we operate everything else" is where the community is focused right now. Amsterdam made that gap visible and showed the early work being done to close it.

## Overview

The conference was held March 23-26 at the RAI Amsterdam Convention Centre. It came immediately after Ingress-NGINX's end-of-life milestone in March 2026, so a lot of the networking conversation centered on what comes next for teams still mid-migration. Simultaneously, the AI infrastructure story matured enough that you could no longer attend a single keynote without hearing about inference workloads, model weight distribution, or agent orchestration.

The CNCF and SlashData released updated numbers at the event: the global cloud native developer population has reached 19.9 million, up from 15.6 million just six months ago. That is a 28% jump in half a year, and it reflects how cloud native practices are spreading beyond traditional backend platform teams into AI engineering, gaming, and industrial IoT. Platform engineering specifically is reshaping how developers interact with infrastructure -- 88% of backend developers now work within some form of infrastructure standardization, up from 80% six months prior.

## Top Stories and Operator Takeaways

### Kyverno Graduates: Policy-as-Code Is Now a Baseline Expectation

CNCF announced Kyverno's graduation on March 24, and the list of organizations publicly depending on it tells you everything about where the ecosystem is. Bloomberg, Coinbase, Deutsche Telekom, LinkedIn, Spotify, Vodafone, and Wayfair all use Kyverno to enforce governance across their Kubernetes environments.

What makes this graduation significant is what Kyverno has become since its early days as an admission controller. It now operates as a broader policy engine across the cloud native stack -- running as an admission controller, CLI, container image, or SDK -- and integrates tightly with Argo CD, Flux, and Backstage for policy-driven GitOps workflows. The graduation represents the community formally recognizing that declarative, Kubernetes-native policy enforcement has crossed from nice-to-have to foundational infrastructure.

**The so-what:** If you are not running a policy engine in your Kubernetes environments today, you are behind the field. Kyverno's graduation is the signal that this category of tooling is stable and trusted at scale. For teams already running OPA or other policy tooling, the graduation is worth revisiting from a "what would we do today" perspective, particularly if your current setup relies heavily on Rego.

### Dapr Agents v1.0: Production AI Agents Without Rolling Your Own Guardrails

Dapr Agents v1.0 shipped at KubeCon EU 2026 as a production-stable framework for running AI agents on Kubernetes. The core pitch is straightforward: most agent frameworks focus on the reasoning and logic layer, leaving teams to figure out failure recovery, state persistence, and secure communication themselves. Dapr Agents provides those missing infrastructure pieces baked in.

The v1.0 feature set includes durable, long-running agent workflows with automatic retries and recovery, persistent state backed by more than 30 database integrations, SPIFFE-based secure identity and communication, multi-agent coordination, and built-in observability. A session at the conference featured ZEISS Vision Care, which is using Dapr Agents to extract optical parameters from highly variable, unstructured documents -- a production AI workload where failure recovery and state management are non-negotiable.

What matters here is not the feature list. It is that Dapr Agents is built on the same Dapr runtime that already runs in production across thousands of organizations. Teams adopting Dapr Agents are not betting on a greenfield project -- they are extending infrastructure that already has production credibility.

**The so-what:** If your organization is deploying AI agents into production and you are currently duct-taping together retries, state management, and secure communication yourself, Dapr Agents v1.0 is worth a serious evaluation. The SPIFFE integration in particular is meaningful: agents that handle sensitive data need verifiable identity, and getting that right from scratch is genuinely hard.

### Istio Goes All-In on AI Traffic

Istio announced a wave of updates at the conference that collectively represent the most significant evolution of the project since ambient mode launched. Three things stand out.

First, ambient multicluster reached beta. Ambient mode eliminates the sidecar container per-pod overhead by moving traffic management to node-level proxies, and extending that to multicluster topologies has been the remaining rough edge. Beta status here means the feature has enough operational testing behind it to deploy carefully in production. For organizations running applications across multiple regions or cloud providers, this is the path to simplified cross-cluster service mesh without the per-pod overhead.

Second, Gateway API Inference Extension integration reached beta in Istio. This is the standardized approach for routing traffic to LLM inference backends in a model-aware way -- accounting for things like KV cache state, backend load, and request priority rather than treating all inference requests as equivalent HTTP traffic. With Istio backing this, teams that are already running Istio as their service mesh have a clear, standards-backed path to inference-aware routing without introducing another ingress layer.

Third, experimental support for agentgateway landed as part of the Istio data plane. Originally created by Solo.io and now a Linux Foundation project, agentgateway is designed for dynamic, AI-driven traffic patterns where connections are often long-lived and traffic shapes differ significantly from typical request-response services.

**The so-what:** If you are running Istio today, the ambient multicluster beta is your next upgrade checkpoint. If you are running AI inference workloads behind any kind of mesh or gateway, the Inference Extension beta in Istio gives you a vendor-neutral, community-backed approach to inference routing. Track it. If you are evaluating service meshes, ambient mode's multicluster story now competes seriously with approaches that required separate tooling to handle cross-cluster traffic.

### The Kubernetes AI Conformance Program Got Serious

CNCF announced that the Kubernetes AI Conformance Program has nearly doubled to 31 certified platforms since launching in November 2025, adding OVHcloud, SpectroCloud, JD Cloud, and China Unicom Cloud. More importantly, the program's v1.35 requirements were codified as formal Kubernetes AI Requirements (KARs) with specific technical benchmarks.

The new KARs include requirements for high-performance pod-to-pod communication (KAR-10), advanced inference ingress (KAR-11), and disaggregated inference support (KAR-41). Two v1.35 Kubernetes features are now explicitly required for AI platform certification: stable in-place pod resizing (so inference models can adjust resources without restarting) and workload-aware scheduling (to avoid resource deadlocks during distributed training). The program is also expanding certification to cover agentic workloads, using the same sandboxing model Kubernetes applies to containers.

**The so-what:** The AI Conformance Program is a purchasing signal as much as a technical one. If you are evaluating Kubernetes distributions for AI workloads, certified platforms give you a baseline guarantee around the primitives that actually matter -- resource flexibility, inference ingress, and scheduling behavior. If you are running AI workloads on an uncertified platform, the KARs are worth reviewing as a self-assessment checklist regardless.

### SNCF Wins Top End User Award Running 200+ Clusters Across Two Clouds

France's national railway company, SNCF, won the Top End User Award for 2026. Their case is interesting because it sits at the intersection of cloud migration and data sovereignty, two concerns that do not always resolve cleanly.

SNCF migrated 70% of 2,000 applications to the cloud and standardized on Kubernetes as a unified abstraction across 200+ AWS and Azure clusters. For workloads that require on-premise control -- regulatory requirements, data sovereignty, operational continuity -- they built a private cloud using OpenStack, providing public cloud parity and full automation without handing control to a hyperscaler.

The architecture pattern is worth noting. Kubernetes as a consistent control plane across public and private environments reduces operational complexity significantly. The same tooling, the same deployment patterns, and the same observability pipelines work regardless of whether the underlying compute is AWS, Azure, or bare metal OpenStack. SNCF's platform team manages that heterogeneity through abstraction rather than specialization.

**The so-what:** For organizations in regulated industries or with genuine data sovereignty requirements, SNCF's approach is a reference architecture worth studying. The key insight is that Kubernetes-as-abstraction-layer works across environments, but only if you invest in making that abstraction real -- consistent control planes, consistent GitOps pipelines, consistent observability. Shortcuts in any of those layers make the heterogeneity visible to application teams again.

### Model Weights Are Infrastructure, and Nobody Is Treating Them That Way

A recurring theme across multiple sessions was the gap between how organizations manage application containers and how they manage AI model weights. Containers get OCI registries, version tags, security scanning, signed provenance, and Kubernetes-native pulling. Model weights, which can range from tens of gigabytes to multiple terabytes, get ad hoc download scripts, shared S3 buckets, and manual copy operations.

The community is converging on treating model artifacts as first-class OCI artifacts, packaging them in the same container registries used for application images. This enables the full ecosystem of container tooling to apply to model delivery: security scanning, cryptographic provenance, GitOps-driven deployment, and Kubernetes-native pulling. The approach is still early, but the pattern is clear.

The numbers make the urgency obvious. A quantized LLaMA-3 70B model weighs approximately 140 GB. Frontier multimodal models can exceed 1 TB. Distributing these to GPU inference nodes across regions through shell scripts and shared filesystems is not a scaling strategy. It is a liability.

**The so-what:** If your organization is running AI inference at any meaningful scale, take stock of how you are managing model artifacts. If the answer involves shell scripts, shared storage mounts, or manual S3 operations, that is technical debt with operational risk attached. The OCI artifact model is not perfect yet, but it is the direction the ecosystem is heading. Implementing version tagging and registry-based distribution for your models now reduces risk and aligns you with the tooling that will mature around this pattern.

### Platform Engineering Is the Default Now

The SlashData report released at the conference showed 88% of backend developers working within some form of infrastructure standardization. The proportion of developers working without formalized DevOps or platform practices dropped from 20% to 12% in six months. Platform engineering has crossed from trend to expectation.

The Backstage documentary released at the conference captures how this happened. Backstage went from a Spotify internal tool to a CNCF project to a global standard for internal developer portals in about five years. The number is remarkable: 41% of organizations are now using multi-team collaboration models to manage platform capabilities, and 35% are using hybrid platforms that integrate AI workloads into existing developer platforms rather than building separate AI infrastructure stacks.

That last data point is the operationally significant one. Organizations that are integrating AI into existing platform infrastructure -- the same IDPs, the same golden paths, the same deployment pipelines -- are positioned better than those building parallel AI stacks that their platform teams have to maintain separately.

**The so-what:** If your organization does not have an internal developer platform story, you are increasingly the exception, not the rule. For organizations that do have platform infrastructure, the 35% integration number is the signal: AI workloads should flow through your existing platform golden paths, not around them. Backstage's plugin model makes this achievable without rewriting your IDP from scratch.

### Ingress-NGINX Is Done: The Ecosystem Moved On

Ingress-NGINX hit end-of-life in March 2026, and by KubeCon EU, the conversation had shifted entirely to migration. The Kubernetes Steering Committee and Security Response Committee issued a formal statement. Ingress2Gateway 1.0 shipped the week before the conference with support for 30+ common Ingress-NGINX annotations and behavioral equivalence tests that verify the Gateway API translation actually works.

If your migration is not started, it is late. If it is in progress, the tooling exists to finish it. The Kubernetes project is done maintaining the old path.

**The so-what:** Run `ingress2gateway print --providers=ingress-nginx --all-namespaces` against your clusters and review the output. Pay attention to the warnings about untranslatable configuration. Those warnings are your actual migration scope. Everything else can be automated.

## Source Links

- [Kyverno Graduation Announcement](https://www.cncf.io/announcements/2026/03/24/cloud-native-computing-foundation-announces-kyvernos-graduation/)
- [Dapr Agents v1.0 GA](https://www.cncf.io/announcements/2026/03/23/general-availability-of-dapr-agents-delivers-production-reliability-for-enterprise-ai/)
- [Istio AI Era Announcements](https://www.cncf.io/announcements/2026/03/25/istio-brings-future-ready-service-mesh-to-the-ai-era-with-new-ambient-multicluster-gateway-api-inference-extension-and-more/)
- [Kubernetes AI Conformance Program Update](https://www.cncf.io/announcements/2026/03/24/cncf-nearly-doubles-certified-kubernetes-ai-platforms/)
- [CNCF Community Award Winners (SNCF Top End User)](https://www.cncf.io/announcements/2026/03/25/cncf-celebrates-innovators-advancing-cloud-native-at-kubecon-cloudnativecon-europe/)
- [State of Cloud Native Development Q1 2026](https://www.cncf.io/announcements/2026/03/24/cncf-and-slashdata-report-finds-cloud-native-community-reaches-nearly-20-million-developers/)
- [Platform Engineering Tools Maturing Report](https://www.cncf.io/announcements/2026/03/24/cncf-and-slashdata-report-finds-platform-engineering-tools-maturing-as-organizations-prepare-for-ai-driven-infrastructure/)
- [Backstage Documentary Release](https://www.cncf.io/announcements/2026/03/25/cncf-backstage-documentary-highlights-project-evolution-from-development-to-global-open-source-standard-for-platform-engineering/)
- [The Weight of AI Models: Why Infrastructure Always Arrives Slowly](https://www.cncf.io/blog/2026/03/27/the-weight-of-ai-models-why-infrastructure-always-arrives-slowly/)

## Related Pages

- Parent index: [Ecosystem news](index.md)
- Related: [Announcing the AI Gateway Working Group](2026-03-11-announcing-ai-gateway-working-group.md)
- Related: [Ingress-NGINX Migration Risk Signals Before March 2026 Retirement](2026-03-06-ingress-nginx-migration-risk-signals.md)
- Related: [Gateway API v1.5.0: TLSRoute Reaches Stable](../releases/2026-02-27-gateway-api-v1.5.0-tlsroute-stable.md)
- Newsletter: [This Week in Kubernetes](../../index.md#weekly-newsletter)
