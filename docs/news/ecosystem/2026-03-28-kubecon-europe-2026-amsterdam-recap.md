---
title: "KubeCon Europe 2026: What Came Out of Amsterdam"
date: 2026-03-28
category: ecosystem
description: "KubeCon Europe 2026 in Amsterdam confirmed what many platform teams already suspected: AI infrastructure is not a separate problem from Kubernetes. Here is what actually mattered and what you should do with it."
---

# KubeCon Europe 2026: What Came Out of Amsterdam

Amsterdam was not subtle about it. Every major announcement at KubeCon + CloudNativeCon Europe 2026 touched AI in some way, and not in the "we bolted a ChatGPT wrapper onto our dashboard" sense. Kyverno graduated. Dapr Agents shipped v1.0. Istio added ambient multicluster and Gateway API Inference Extension in beta. CNCF dropped survey data showing 66% of organizations are running generative AI workloads on Kubernetes right now. And yet only 7% of those same organizations hit daily deployments for AI workloads.

That number deserves a moment. Two thirds of orgs are running AI on Kubernetes, but almost none of them are operating it with the same discipline they apply to their regular workloads. That is the gap the community spent four days in Amsterdam trying to figure out how to close.

## Overview

The conference ran March 23-26 at the RAI Amsterdam Convention Centre, which made it the first KubeCon EU held in the Netherlands. Timing was notable: it landed immediately after Ingress-NGINX officially hit end-of-life. So in the hallways you had two very different conversations happening in parallel - people trying to figure out their Gateway API migration, and people trying to figure out how to run LLMs without their infrastructure falling apart. Sometimes the same person was having both conversations.

CNCF and SlashData put out fresh numbers at the event. The global cloud native developer population is now at 19.9 million, up from 15.6 million just six months ago. That is 28% growth in half a year, which is the kind of number that sounds made-up until you look at how fast AI tooling has pulled data scientists and ML engineers into Kubernetes workflows. Platform engineering specifically has become the default: 88% of backend developers now work within some form of infrastructure standardization, up from 80% six months prior. The percentage working with no formalized DevOps or platform practices at all dropped to 12%. A year ago that felt like an aspirational goal for the industry. Now it is just where things are.

## Top Stories and Operator Takeaways

### Kyverno Graduates, and the Org List Makes the Case

On March 24, CNCF announced Kyverno's graduation. The project started as a Kubernetes-native admission controller in 2020 and has since grown into something considerably broader - a policy engine that runs as a controller, CLI, container image, or SDK, and plugs into Argo CD, Flux, and Backstage. Bloomberg, Coinbase, Deutsche Telekom, LinkedIn, Spotify, Vodafone, and Wayfair are all publicly running it in production.

The Rego question is going to come up if you are an OPA shop. It is a fair one. Kyverno uses a YAML-based policy syntax that Kubernetes teams tend to find more approachable, especially for operators who are comfortable with manifests but less so with a purpose-built query language. Whether that tradeoff is right for your environment depends on your team. But the graduation tells you that the community has fully committed to this as the primary answer for Kubernetes-native policy, and the list of adopters at production scale suggests the pattern is working.

**The so-what:** No policy engine means no guardrails on what gets admitted to your clusters. If that is your situation, fix it. Kyverno is the safe bet right now. If you are on OPA/Rego and happy there, this graduation does not require you to change anything - but it is worth doing an honest assessment of whether your current setup is actually being maintained and extended by your team, or just running.

### Dapr Agents v1.0: Someone Finally Solved the Infrastructure Part

Most AI agent frameworks are focused on the reasoning layer. Tools for chaining prompts, managing context windows, routing between models. That is important, but it leaves teams on their own for everything underneath - retries when the model times out, persisting state across restarts, figuring out how to give your agent a verifiable identity when it talks to other services. Those problems are not glamorous, but they will bite you in production.

Dapr Agents v1.0 is specifically the infrastructure layer. Durable workflows that survive restarts. Automatic failure recovery. State persistence across 30+ database backends. SPIFFE-based identity so your agents have real cryptographic identity when communicating with other services. Multi-agent coordination. Built-in observability. The SPIFFE piece in particular is not something teams think about until an agent with access to sensitive systems is running without any verifiable identity, and then they really think about it.

At the conference, ZEISS Vision Care presented a real production use case: Dapr Agents extracting optical parameters from highly variable, unstructured documents. Exactly the kind of workload where the logic layer is complex but the infrastructure requirements are just as demanding - you cannot lose state mid-document, and failures need to be retried reliably.

The reason this matters beyond the feature list is that Dapr Agents runs on the Dapr runtime, which already has significant production history. You are not adopting an experimental project.

**The so-what:** If you are running AI agents in production and your current reliability story involves custom retry logic and hoping your state backend does not restart, look at Dapr Agents seriously. The SPIFFE integration alone is worth the evaluation if your agents touch anything sensitive.

### Istio Had a Lot Going On

Three things came out of Istio at the conference, and they are each worth tracking separately rather than lumping them together.

Ambient multicluster hit beta. This has been the missing piece in the ambient mode story. Moving traffic management to node-level proxies instead of sidecars works well in single clusters, but the original implementation did not extend cleanly to multi-cluster topologies. Beta means there is enough production testing behind it to try carefully. For teams running across regions or multiple clouds, this is meaningful - the same simplified mesh model that ambient mode brought to single clusters can now span cluster boundaries.

Gateway API Inference Extension reached beta inside Istio. The extension routes traffic to LLM inference backends in a model-aware way, accounting for things like KV cache state, backend load, and request priority. Standard load balancers treat all HTTP requests as equivalent. This does not, which matters a lot when you have GPU-backed model servers and sending a request to an overloaded backend costs you real money and real latency. Having Istio back this with a standards-track implementation is the signal that this is the path forward, not some proprietary routing hack.

Experimental support for agentgateway also landed as part of the Istio data plane. Originally created by Solo.io, now a Linux Foundation project. It handles the kind of dynamic, long-lived traffic patterns that AI agent workflows produce, which are meaningfully different from typical request-response traffic.

**The so-what:** If you run Istio, the ambient multicluster beta is your next thing to evaluate. If you run AI inference behind any mesh or gateway, track the Inference Extension beta - it is becoming the standard. If you are still evaluating service meshes, ambient mode's multicluster story is now legitimately competitive with alternatives that required separate tooling to solve this.

### The AI Conformance Program Has Real Requirements Now

The Kubernetes AI Conformance Program launched in November 2025 with 18 certified platforms. By KubeCon EU it had grown to 31, adding OVHcloud, SpectroCloud, JD Cloud, and China Unicom Cloud. More importantly, the program now has formal technical requirements tied to Kubernetes v1.35, called Kubernetes AI Requirements or KARs.

KAR-10 covers high-performance pod-to-pod communication. KAR-11 is advanced inference ingress. KAR-41 is disaggregated inference support. Two specific v1.35 features are now mandatory for certification: stable in-place pod resizing (so inference models can adjust resources without a container restart) and workload-aware scheduling (to avoid deadlocks during distributed training). The program is also extending to agentic workloads.

This is useful as a vendor evaluation tool. Certified platforms have made specific commitments about the underlying Kubernetes primitives your AI workloads depend on. An uncertified platform may work fine, but you will be finding out the hard way whether it handles disaggregated inference or training deadlock avoidance correctly.

**The so-what:** Use the KARs as a checklist regardless of whether your platform is certified. KAR-11 and KAR-41 in particular are worth validating against your current setup if you are running inference at any scale.

### SNCF Won the Top End User Award With a Genuinely Interesting Architecture

France's national railway company took home the Top End User Award for 2026. SNCF migrated 70% of 2,000 applications to the cloud and standardized on Kubernetes as a consistent abstraction layer across 200+ AWS and Azure clusters. For workloads with genuine data sovereignty or regulatory requirements, they built a private cloud on OpenStack that matches public cloud capabilities and runs the same Kubernetes control plane.

The thing that makes this worth studying is not the scale - plenty of organizations run hundreds of clusters. It is that they used Kubernetes as a genuine abstraction rather than a thin wrapper. The same deployment patterns, same tooling, same observability work whether the compute is AWS, Azure, or OpenStack. The platform team manages the heterogeneity, and application teams mostly do not see it.

That sounds nice in theory. It requires discipline to actually pull off. Every shortcut - a platform-specific feature used directly here, a different GitOps pipeline there - chips away at the abstraction and eventually makes the differences visible to the people it was supposed to shield.

**The so-what:** If your organization has data sovereignty requirements and is trying to figure out how to not maintain two completely separate operational models for cloud and on-prem, SNCF's architecture is the reference you want. The keynote from the conference is worth watching if you are making that decision.

### Model Weights Are Infrastructure, So Why Are We Still Using Shell Scripts

Something that came up repeatedly across different sessions was the mismatch between how organizations handle application containers and how they handle AI model weights. Containers go into OCI registries with version tags, security scanning, signed provenance, and proper pull mechanisms. Model weights - objects that can run from tens of gigabytes to over a terabyte - go into a shared S3 bucket and get downloaded via a script that someone wrote six months ago and nobody has touched since.

The numbers make this uncomfortable to ignore. A quantized LLaMA-3 70B is roughly 140 GB. Frontier multimodal models push past 1 TB. Shipping those via ad hoc scripts to GPU nodes across multiple regions is not a distribution strategy. It is an accident waiting to happen when someone overwrites the wrong file, or a security audit that will go badly when nobody can answer "which model version is running in production right now and can you prove it."

The community is converging on treating model artifacts as first-class OCI artifacts - same registries, same scanning tooling, same provenance mechanisms, same Kubernetes-native pull patterns. It is early, but it is clearly the direction.

**The so-what:** Ask your team how you would roll back to the previous version of a model if you needed to do it in the next 30 minutes. If the answer is complicated, you have a problem worth fixing. Start by putting version tags on your models and treating them like build artifacts. Getting them into an OCI registry is the next step.

### Platform Engineering Is Just Engineering Now

The SlashData numbers CNCF released were striking in how unremarkable they made platform engineering sound. 88% of backend developers working within standardized infrastructure. Only 12% working without any formalized DevOps or platform practices. Two years ago you could still have a legitimate debate about whether platform engineering investment was worth it. That debate is over.

CNCF also released a Backstage documentary at the conference, tracing how a Spotify-internal tool became a CNCF project and then effectively the global standard for internal developer portals in about five years. 41% of organizations are now running multi-team collaboration models for platform capabilities. The more interesting number is that 35% are using hybrid platforms that fold AI workloads into their existing developer platforms rather than building separate AI infrastructure stacks.

Separate AI infrastructure stacks have a way of becoming the platform team's problem anyway - they just become the problem later, after they have accumulated custom tooling and inconsistent operational practices that nobody owns.

**The so-what:** If you are in the 12% without platform infrastructure, you are competing for engineers with organizations that have automated away the friction you are asking people to deal with manually. If you have platform infrastructure, make AI workloads first-class citizens in it now rather than letting them grow sideways.

### Ingress-NGINX Is Done. Move On.

March 2026 was end-of-life for Ingress-NGINX, and by KubeCon EU the community had fully shifted into post-mortem mode. The Kubernetes Steering Committee and Security Response Committee issued a statement. Ingress2Gateway 1.0 shipped the week before the conference with support for 30+ Ingress-NGINX annotations and real behavioral equivalence tests - not just YAML translation, but actual verification that the Gateway API output routes traffic identically.

If you have not started migrating, you are now running unsupported software with no security patch path. That is a risk posture you need to be actively choosing, not one you drifted into.

**The so-what:** `ingress2gateway print --providers=ingress-nginx --all-namespaces`. Run it against your clusters. The warnings it emits about untranslatable configuration are your actual migration scope. Automate the rest.

## Source Links

- [Kyverno Graduation Announcement](https://www.cncf.io/announcements/2026/03/24/cloud-native-computing-foundation-announces-kyvernos-graduation/)
- [Dapr Agents v1.0 GA](https://www.cncf.io/announcements/2026/03/23/general-availability-of-dapr-agents-delivers-production-reliability-for-enterprise-ai/)
- [Istio AI Era Announcements](https://www.cncf.io/announcements/2026/03/25/istio-brings-future-ready-service-mesh-to-the-ai-era-with-new-ambient-multicluster-gateway-api-inference-extension-and-more/)
- [Kubernetes AI Conformance Program Update](https://www.cncf.io/announcements/2026/03/24/cncf-nearly-doubles-certified-kubernetes-ai-platforms/)
- [CNCF Community Award Winners including SNCF Top End User](https://www.cncf.io/announcements/2026/03/25/cncf-celebrates-innovators-advancing-cloud-native-at-kubecon-cloudnativecon-europe/)
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
