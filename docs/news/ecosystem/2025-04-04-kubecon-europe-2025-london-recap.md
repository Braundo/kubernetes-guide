---
title: "KubeCon Europe 2025: What Actually Mattered in London"
date: 2025-04-04
category: ecosystem
description: "KubeCon Europe 2025 in London was the conference where AI workloads stopped being a future concern and started being a present-day operational problem. Here is what mattered and why."
---

# KubeCon Europe 2025: What Actually Mattered in London

About 12,000 people packed the ExCeL Arena in London for KubeCon + CloudNativeCon Europe 2025. It was also the tenth anniversary of the CNCF, which gave the event a retrospective quality that made the forward-looking announcements hit differently. Ten years ago, Kubernetes was a Google project that most companies were skeptical about. Now HSBC runs 600 million API hits a day on it. Michelin cut platform costs by 44% and reduced upgrade lead time by 85% after moving to it. Norway built its entire government developer platform on top of it.

The scale is real. But the more interesting question coming out of London is what comes next. Here is what actually mattered.

## Overview

KubeCon EU 2025 landed at a specific inflection point: the community has largely solved the "how do we run Kubernetes reliably" question for most workloads, and is now grappling with two harder ones. First, how do you run AI workloads -- specifically LLM inference -- on Kubernetes at production scale without duct-taping your load balancer config together? Second, how do you keep the project secure and governable as it matures into critical global infrastructure?

Both questions got serious treatment in London. The answers are still incomplete, but the direction is clear.

## Top Stories and Operator Takeaways

### LLM-Aware Load Balancing: The Infrastructure Problem Nobody Solved Yet

The Day 3 keynote from Clayton Coleman (Google) and Jiaxin Shan (ByteDance) was the most technically consequential of the conference. The core argument: standard load balancers are the wrong tool for LLM inference workloads, and that gap is costing production teams real money and latency.

Here is why this matters. When you send a request to a stateless API, any backend is as good as any other. Round-robin works fine. LLM inference is different. A model server handling multiple active sessions has meaningful state -- KV cache, active token generation, VRAM pressure -- that varies dramatically between backends in real time. A request routed to the wrong backend gets queued behind 50 other requests that are generating tokens, even though three other backends are nearly idle. You have wasted GPU time, worse p99 latency, and frustrated users.

The proposal from Coleman and Shan is to model two things: the cost of an incoming request (based on prompt length, expected output, criticality) and the real-time capacity of each backend (based on continuously gathered metrics). Route with that information, and you stop treating $5/hour GPU instances like they are interchangeable compute. Their prediction: 2025 is the year production LLM scaling on Kubernetes becomes a real engineering discipline rather than an improvised one.

Separately, the Gateway API Inference Extension project was introduced as a standards-track effort to bring model-aware routing into the Gateway API ecosystem. Instead of each team building their own routing logic for AI backends, the project proposes two new CRDs -- one for defining inference model backends with priority levels, one for inference pools -- that fit naturally into existing Gateway/HTTPRoute infrastructure. Platform teams who are already building Gateway API infrastructure should pay attention to this. It could mean that your existing investment in Gateway API translates cleanly to AI routing rather than requiring a separate ingress layer for AI workloads.

**The so-what:** If you are or will be running LLM workloads on Kubernetes, the load balancing story is unsolved and actively being standardized. Follow the Gateway API Inference Extension project. Do not build a custom solution yet -- the abstractions are still being defined, and you want to land on the standard ones.

### Ingress-NGINX: The Security Reckoning

The week before KubeCon EU, the Kubernetes Security Response Committee dropped CVE-2025-1974, rated CVSS 9.8. The short version: anything with access to the pod network -- including other workloads in your VPC -- could potentially take over your entire Kubernetes cluster through ingress-nginx's admission controller, with no credentials required. In many real-world deployments, the pod network is accessible from the corporate network or the full cloud VPC. This was as bad as it sounds.

The patches came out immediately (v1.12.1 and v1.11.5), but the vulnerability surfaced a deeper problem that the London conference made explicit: ingress-nginx has always been maintained by one or two people, on their own time, doing the work that critical infrastructure requires. That is not sustainable for something deployed in over 40% of Kubernetes clusters. The project announced it would enter best-effort maintenance mode through early 2026, followed by retirement.

This was not a surprise to anyone following the project closely. What KubeCon EU confirmed is that the direction is Gateway API, and the migration path is real. Multiple conformant implementations now exist -- Envoy Gateway, Cilium, Istio, kgateway -- and the tooling is maturing. The Ingress2Gateway migration assistant continues to improve.

**The so-what:** If you are still running ingress-nginx, you have a prioritization decision to make. The CVE should have already moved this up your backlog. Retirement means no security patches after March 2026. Start scoping your Gateway API migration now. The ecosystem has matured enough that this is engineering work, not research.

### In-Place Pod Resize: Boring in the Best Way

Kubernetes v1.33 released shortly after KubeCon EU with in-place pod resize graduating to Beta and enabled by default. This feature has been in alpha since v1.27, and the promotion to Beta is the signal that it is ready for production evaluation.

The basic premise: you should be able to change CPU and memory requests on a running pod without killing and recreating it. For stateless workloads, this is a nice-to-have. For stateful workloads -- databases, caches, ML model servers with loaded weights -- forced restarts to change resource limits are genuinely painful. Teams have been working around this limitation with overprovisioning and manual intervention for years.

The Beta implementation has nuances. CPU adjustments do not increment restart counters and do not change pod UID or IP. Memory resizing depends on the configured resize policy: with the RestartContainer policy, memory changes restart the container (incrementing restart count) while preserving pod identity. Operators need to understand which mode their workloads are in before looking at restart count metrics, or they will misread their signals.

**The so-what:** Start testing in-place resize on non-critical stateful workloads. Review your resource adjustment workflows -- any runbook that says "update resource limits, delete the pod" should be revisited. Audit your restart-count alerting logic, since resize-triggered restarts look identical to crash restarts in current tooling.

### Apple, HSBC, and Michelin: What Production at Scale Actually Looks Like

The Day 2 end-user panel was worth paying attention to for calibration purposes. These are not organizations experimenting with cloud native. They are running it as core infrastructure.

HSBC is handling 600 million API hits per day across 7,000+ services in production, running in roughly a dozen large clusters. Their insight on upgrades: they run clusters in blue/green pairs and rehydrate from etcd backups before cutting traffic over. That is a legitimate operational strategy for minimizing upgrade risk at their scale, and it is the kind of thing that does not show up in documentation.

Apple's Katie Gamanji presented on Private Cloud Compute, which is how Apple scales AI capabilities while maintaining end-to-end encryption. They use Swift open source libraries and gRPC as core components. Kubernetes is underneath it all. The fact that Apple is comfortable enough with the ecosystem to present on their architecture publicly is its own kind of signal about where cloud native sits in the industry.

Michelin's story was the most concrete: switching from a vendor-managed platform to self-managed Kubernetes cut platform costs by 44% and reduced upgrade lead time from weeks to near-real-time. The driver was not ideology -- it was misalignment with their previous vendor's roadmap combined with a desire to attract engineers who wanted to work with modern tooling.

**The so-what:** If you are in an organization still building the business case for platform investment, these numbers are useful ammunition. Michelin's cost reduction came from regaining control of the platform lifecycle. HSBC's blue/green cluster strategy is worth studying if you are operating at multi-cluster scale and still doing in-place upgrades.

### Observability Is Not a Three-Tab Problem Anymore

Kasper Borg Nissen from Dash0 made an argument in his keynote that resonated throughout the conference: the problem is not that teams lack logs, metrics, or traces. The problem is that they treat them as separate entities and rely on humans to correlate signals across browser tabs. That is inefficient and error-prone.

Christine Yen from Honeycomb made a related point about LLMs specifically. AI systems are hard to test, hard to mock, and hard to debug with traditional observability approaches because they are inherently non-deterministic. The answer is bundling observability with eval systems -- capturing good and bad outcomes as they happen so the system can evolve. This is not a new skillset, she argued. Platform engineers already understand instrumentation and feedback loops. They need to apply those skills to AI pipelines.

The eBay presentation was the most grounded: 4,600 microservices, 15 petabytes of logs per day, and a team that started using LLMs not to replace their observability stack but to summarize and explain critical paths during incidents. They found specific flows where automation added real value and leaned into those. The lesson: start with the specific problem, not the general category.

**The so-what:** If your current observability setup requires three tabs and manual correlation, that is a platform debt item. The ecosystem is moving toward unified observability platforms. Evaluate whether your current tooling can grow in that direction or whether you are building on a foundation that requires a harder migration later.

### Sovereign Cloud and the European Regulatory Picture

Two European-specific threads ran through the conference. The first was NeoNephos, a sovereign cloud-edge continuum announced by SAP and Vasu Chandrasekhara. Europe's interest in digital sovereignty -- owning the infrastructure stack, not just licensing it from US hyperscalers -- is translating into concrete technical projects. NeoNephos is early, but it represents where European public sector and regulated industries are heading.

The second was the Cyber Resilience Act. The CRA is EU legislation that will require software products with digital elements to meet cybersecurity standards before being sold in Europe. For open source, the implications are complex -- the CNCF and its projects are actively working through what compliance means for community-developed software. Eddie Knight and Michael Lieberman gave a full session on cutting through the regulatory ambiguity. If you are building commercial products on CNCF projects and selling into Europe, this is now a legal requirement you need to understand, not a background concern.

**The so-what:** European platform teams, especially in regulated industries, should start tracking CRA compliance requirements now. For everyone: sovereign cloud is a real procurement driver in Europe, and if you sell into that market, understanding what "cloud native sovereignty" means for your buyers is becoming necessary context.

### What the CNCF TOC Said About Gaps

The TOC keynote identified gaps the community considers important enough to prioritize for the next decade. Three stood out: multicluster management, cost management and sustainability, and tooling around infrastructure provisioning and secret management.

Multicluster management remains genuinely unsolved. There is no single standard for how clusters discover each other, share policies, or route traffic between workloads. Teams are building this themselves on top of various tools. The community acknowledges this is a gap, which is more progress than pretending the problem does not exist.

Cost management is the other one worth noting. Kubernetes makes it easy to provision resources and genuinely difficult to understand what you are spending. Most platform teams are running on intuition and monthly cloud bills rather than per-workload cost visibility. The ecosystem has tools -- OpenCost, Kubecost -- but the TOC identifying this as a gap suggests the community wants better first-party solutions.

**The so-what:** If your organization does not have a multicluster strategy, you are not alone. But you should have a position on whether you are going to try to solve it yourself or wait for the ecosystem to mature. On cost: if you cannot answer "what does each team's Kubernetes usage cost per month" today, that is worth fixing.

## Source Links

- [KubeCon EU 2025 Day One Keynote Recap](https://www.cncf.io/blog/2025/04/02/kubecon-cloudnativecon-europe-2025-day-one-keynote-recap/)
- [KubeCon EU 2025 Day Two Keynote Recap](https://www.cncf.io/blog/2025/04/03/kubecon-cloudnativecon-europe-2025-day-two-keynote-recap/)
- [KubeCon EU 2025 Day Three Keynote Recap](https://www.cncf.io/blog/2025/04/07/kubecon-cloudnativecon-europe-2025-day-three-keynote-recap/)
- [Ingress-NGINX CVE-2025-1974: What You Need to Know](https://kubernetes.io/blog/2025/03/24/ingress-nginx-CVE-2025-1974/)
- [Ingress NGINX Retirement: What You Need to Know](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/)
- [Kubernetes v1.33: In-Place Pod Resize Graduated to Beta](https://kubernetes.io/blog/2025/05/16/kubernetes-v1-33-in-place-pod-resize-beta/)
- [Introducing Gateway API Inference Extension](https://kubernetes.io/blog/2025/06/05/introducing-gateway-api-inference-extension/)
- [CNCF Golden Kubestronaut Program Launch](https://www.cncf.io/announcements/2025/04/01/cncf-launches-golden-kubestronaut-program-and-expands-cloud-native-education-initiatives/)

## Related Pages

- Parent index: [Ecosystem news](index.md)
- Related: [Announcing the AI Gateway Working Group](2026-03-11-announcing-ai-gateway-working-group.md)
- Related: [Ingress-NGINX Migration Risk Signals Before March 2026 Retirement](2026-03-06-ingress-nginx-migration-risk-signals.md)
- Related: [Gateway API v1.5.0: TLSRoute Reaches Stable](../releases/2026-02-27-gateway-api-v1.5.0-tlsroute-stable.md)
- Newsletter: [This Week in Kubernetes](../../index.md#weekly-newsletter)
