---
title: "KubeCon Europe 2026: What Came Out of Amsterdam"
date: 2026-03-28
category: ecosystem
description: "KubeCon Europe 2026 in Amsterdam confirmed what many platform teams already suspected: AI infrastructure is not a separate problem from Kubernetes. Here is what actually mattered and what you should do with it."
---

# KubeCon Europe 2026: What Came Out of Amsterdam

There is a joke that every KubeCon has a theme and the theme is always AI now. Amsterdam did not do much to disprove it. But this year the AI angle felt different - less aspirational, more operational. Teams are not showing up to KubeCon to learn whether they should run AI workloads on Kubernetes. They are showing up because they already do, and something is always on fire.

A stat that kept circulating: 66% of organizations are now running generative AI on Kubernetes, but only 7% hit daily deployments for those workloads. Put another way, most teams have figured out how to get a model running, but almost nobody has figured out how to operate it with the same rigor they apply to everything else. That is the actual problem the community spent four days trying to work on.

## Overview

KubeCon EU 2026 ran March 23-26 at the RAI Amsterdam Convention Centre. It landed right at the Ingress-NGINX end-of-life milestone, which gave the hallway conversations a particular flavor - half the networking chatter was people comparing notes on Gateway API migrations, and the other half was debugging inference workload behavior. Often the same person.

The community size numbers keep growing. Fresh survey data from CNCF and SlashData puts the global cloud native developer population at roughly 20 million, up nearly 30% in just six months. The growth is partly genuine expansion into new domains like AI engineering and industrial IoT, and partly a reflection of how internal developer platforms are absorbing developers who never thought of themselves as infrastructure people. Either way, 88% of backend developers now operate within some kind of standardized infrastructure environment - a figure that would have been optimistic as a five-year goal just a few years back.

## Top Stories and Operator Takeaways

### Kyverno Graduated, and the Adopter List Is the Argument

CNCF projects graduating is fairly routine at this point, but Kyverno's graduation landed differently because of who is running it. Bloomberg, Coinbase, Deutsche Telekom, LinkedIn, Vodafone, Wayfair - the organizations that publicly acknowledge using it are exactly the kinds of environments where bad policy tooling causes real damage. These are not orgs that try things for fun.

What Kyverno has become is worth understanding. It started as a way to write admission policies in YAML instead of Rego, which made it more approachable for teams that live in Kubernetes manifests all day. Over time it grew into something that operates across the full stack - as a controller, a CLI tool, a container, or an SDK - and now integrates directly with GitOps tooling like Argo CD and Flux. Graduation is the community's way of saying this is no longer an experiment.

The OPA comparison will come up. Rego is expressive and powerful and also genuinely difficult to maintain for teams that do not write it regularly. Kyverno does not require it. Whether that tradeoff is worth making depends on your team. What the graduation tells you is that the Kyverno path is stable and trusted at scale, so the decision is a real one now rather than a "maybe later."

**The so-what:** If you are not enforcing admission policies today, this graduation should be the thing that makes you actually do something about it. If you are on OPA and it is working, no action required - but ask yourself honestly whether your Rego policies are being actively extended or whether they are running and nobody really touches them anymore.

### Dapr Agents Shipped v1.0, and the Infrastructure Part Is the Point

Most agent frameworks give you the logic layer and leave the rest as an exercise for the reader. You get prompt chaining, context management, maybe some tooling for routing between models. What you do not get is a story for when the model times out halfway through a job, or when your agent needs to talk to another service and you want that communication to carry a verifiable identity, or when state needs to survive a pod restart.

Dapr Agents v1.0 is specifically targeting that gap. The runtime handles durable execution with retries, state that persists across failures into whichever database you are already using, and workload identity via SPIFFE so agents have real cryptographic credentials when they call other services. Multi-agent coordination is in there too. The observability hooks are native rather than bolted on.

A concrete case from the conference: ZEISS Vision Care is using it to pull structured optical parameters out of highly variable paper documents. That use case is not a demo - it is a production pipeline where losing state mid-document is a real business problem, not an inconvenience. The kind of thing that exposes exactly what breaks when you build your own retry and state layer from scratch.

The reason the v1.0 label matters here is that Dapr Agents runs on the Dapr runtime, which already has years of production history behind it. You are not adopting an experimental side project.

**The so-what:** If agents are in your roadmap and your current reliability plan is "we will figure it out," Dapr Agents is worth a proper evaluation before you build something custom. The SPIFFE integration is especially worth looking at if any of your agents touch systems with real access controls.

### Istio Made Three Moves Worth Watching

Ambient multicluster hit beta. This is the piece of the ambient mode story that has been missing. The idea behind ambient mode - moving traffic management off individual pod sidecars and onto shared node-level proxies - works well within a single cluster. Extending it across clusters has been the hard part. Beta means there is real operational mileage behind it now. For teams running across clouds or regions and dreading the per-pod overhead of traditional sidecar meshes, this is worth evaluating.

The Gateway API Inference Extension integration also landed in beta inside Istio. The extension routes inference traffic based on what is actually happening at the backend - which servers have available GPU memory, how loaded the KV cache is, whether the request is interactive or a batch job that can wait. Standard load balancers cannot see any of that. They round-robin blind. This one matters if you are spending real money on GPU time and losing it to bad routing decisions.

Third, experimental support landed for agentgateway as part of the Istio data plane. It is a Linux Foundation project now, originally out of Solo.io, built to handle the traffic patterns that AI agent workflows produce. Those patterns are long-lived and irregular in ways that typical HTTP request-response routing does not handle well.

**The so-what:** Ambient multicluster in beta is the signal to start testing if you have been waiting for multi-cluster ambient support before migrating. Inference Extension beta is worth tracking if you have inference workloads behind any gateway - it is becoming the standard routing approach. Agentgateway is experimental and early, but keep an eye on it.

### The AI Conformance Program Now Has Teeth

When the Kubernetes AI Conformance Program launched last November with 18 certified platforms, it was mostly a signal. By Amsterdam it had grown to 31 platforms and published formal technical requirements - Kubernetes AI Requirements, or KARs - tied to actual v1.35 capabilities.

The requirements that matter for most teams: KAR-10 is about pod-to-pod networking performance at the speeds inference workloads need. KAR-11 covers the inference ingress layer. KAR-41 addresses disaggregated inference, which is relevant when you are splitting prefill and decode across different hardware. Stable in-place pod resizing is now a mandatory capability for certification - because inference servers that need more memory should be able to get it without a full container restart. Workload-aware scheduling is also required to prevent the kind of distributed training deadlock that wastes entire job runs.

Agentic workload certification is coming next.

**The so-what:** The KAR list is a useful self-assessment even if your platform is not certified. Run through KAR-11 and KAR-41 against your current setup and see what you find. For vendor evaluations, the certification program gives you a structured way to ask pointed questions rather than trusting marketing claims.

### SNCF Won the Top End User Award for Doing the Boring Part Well

France's national railway operator, SNCF, took home the 2026 Top End User Award. The case is not flashy - no novel architecture patterns, no bleeding-edge tooling. What they did was migrate 70% of 2,000 applications to the cloud across 200+ clusters on AWS and Azure, while simultaneously running a private OpenStack cloud for workloads that cannot leave French data centers, and using Kubernetes as the consistent control plane across all of it.

That last part is harder than it sounds. Maintaining a consistent operational model across public cloud and private infrastructure means resisting the temptation to use platform-specific features that break the abstraction. Different GitOps pipelines for different environments, different observability setups, different deployment patterns - each exception is small until you have fifty of them and your platform team is supporting three different operating models instead of one.

SNCF did not take those shortcuts, which is why their platform team can manage 200+ clusters without a proportionally large headcount.

**The so-what:** If your organization has genuine sovereignty requirements and is trying to avoid running two completely separate operational models, the SNCF architecture is the reference worth studying. The underlying principle - Kubernetes as real abstraction, not a thin veneer over different systems - applies regardless of your specific cloud setup.

### Everyone Is Still Copying Model Weights Around With Shell Scripts

Across multiple sessions in Amsterdam, the same uncomfortable truth kept surfacing: organizations that have completely mature container delivery pipelines, with signing, scanning, and provenance, are managing their AI model weights via whatever script someone wrote six months ago. Nobody knows exactly which version of a model is in production. Nobody has a rollback plan that takes less than an afternoon. Nobody is scanning model artifacts for tampering.

This is not entirely irrational - the tooling for treating models as proper versioned artifacts has been immature. But it is catching up. The ecosystem is coalescing around shipping model weights as OCI artifacts through the same container registries that already handle application images. Same signing mechanisms, same scanning pipelines, same Kubernetes pull patterns. The practical advantage is that if your security and deployment tooling already knows how to handle OCI images, it can handle models the same way without building a parallel system.

The scale problem is real though. These are not small files. A 70-billion-parameter quantized model is roughly 140 gigabytes. Some frontier models are over a terabyte. Getting those reliably to GPU nodes across regions through a shell script and a shared filesystem is asking for an incident.

**The so-what:** Figure out your rollback story for models before you need it. "We re-download from the source" is not a production answer when the model is 500 GB and you have an incident at 2 AM. Start by versioning your models properly and treating them as immutable artifacts. Moving them into an OCI registry is the logical next step.

### Platform Engineering Won. It Is Just Called Engineering Now.

The survey numbers released at the event made platform engineering sound less like a trend and more like a settled question. Only 12% of backend developers are working without any formalized platform or DevOps practices. 88% are within some standardized infrastructure environment. The organizations that argued against platform investment a few years ago are either now building platforms or losing people to organizations that did.

CNCF released a Backstage documentary at the conference that traces how that project went from a Spotify-internal tool to a global standard for developer portals in five years. The documentary is interesting partly as a history and partly as an illustration of how open source adoption actually works in practice - it almost did not happen, and the things that made it take off were not the obvious ones.

The number from the survey that operators should pay attention to: 35% of organizations are integrating AI workloads into their existing developer platforms rather than building separate AI infrastructure. The other 65% are, intentionally or not, building something their platform teams will eventually inherit.

**The so-what:** AI workloads that live outside your existing platform golden paths are future toil. Build the integration now. Backstage's plugin model makes it achievable without a ground-up rebuild. If you have neither an IDP nor a plan, the 12% figure is where you stand in the industry.

### Ingress-NGINX Is Over. Act Like It.

March 2026 was the end of the line for Ingress-NGINX. No more patches, no more releases, no security fixes for whatever comes next. The Kubernetes Steering Committee and Security Response Committee put out a formal statement acknowledging the end of the project. Ingress2Gateway 1.0 shipped right before the conference with meaningful migration tooling - support for 30+ Ingress-NGINX annotations, and actual behavioral equivalence tests that compare how the translated Gateway API routes traffic against the original configuration.

If your cluster is still running Ingress-NGINX and you have not started a migration, you are now running unsupported software with no security patch path. That is a choice, not a situation. Make sure you are making it consciously.

**The so-what:** `ingress2gateway print --providers=ingress-nginx --all-namespaces` against your clusters. Read the warnings carefully - they are telling you what cannot be translated automatically and will need real engineering work. Everything the tool can handle without warnings is largely automated. Start with the warnings.

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

- Parent index: [News](index.md)
- Related: [Announcing the AI Gateway Working Group](2026-03-11-announcing-ai-gateway-working-group.md)
- Related: [Ingress-NGINX Migration Risk Signals Before March 2026 Retirement](2026-03-06-ingress-nginx-migration-risk-signals.md)
- Related: [Gateway API v1.5.0: TLSRoute Reaches Stable](2026-02-27-gateway-api-v1.5.0-tlsroute-stable.md)
- Newsletter: [This Week in Kubernetes](../index.md#weekly-newsletter)
