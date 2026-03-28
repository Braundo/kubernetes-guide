---
title: "Kubernetes Gateway API v1.5.0: TLSRoute Reaches Stable"
date: 2026-02-27
category: releases
description: "TLSRoute graduates to the Standard channel as v1 in Gateway API v1.5.0, along with CORS filters, ListenerSet, and client certificate validation reaching GA."
---

# Kubernetes Gateway API v1.5.0: TLSRoute Reaches Stable

*Released February 27, 2026*

The Kubernetes Gateway API project shipped version 1.5.0, and while the release packed several notable promotions, one stands out for platform teams managing production traffic: **TLSRoute has graduated to the Standard channel as `v1`**, marking its official promotion to stable and generally available.

---

## Release Summary

Gateway API v1.5.0 is a stability-focused release. The headline change is TLSRoute graduating to `v1` in the Standard channel — moving from an alpha API with breakage caveats to a stable, production-safe primitive. Several other features also reach GA in this release, including HTTPRoute CORS filters, ListenerSet, and Gateway client certificate validation.

---

## Key Changes

v1.5.0 promotes multiple features to Standard:

- **TLSRoute `v1`:** graduates from `v1alpha2` in the Experimental channel to `v1` in the Standard channel. The `v1alpha2` version stays available through v1.5.x but will be removed in v1.6.
- **HTTPRoute CORS filter:** native cross-origin request handling without custom middleware, now stable.
- **Gateway Client Certificate validation:** mutual TLS policy at the Gateway level reaches GA.
- **ListenerSet:** a composability primitive for multi-team Gateway sharing, now in Standard.
- **Certificate selection for Gateway TLS origination:** finer-grained control over which cert is used when a Gateway initiates TLS upstream.
- **ReferenceGrant moves to `v1`:** cements the cross-namespace trust model that underpins Gateway API's security story.

---

## Breaking Changes and Deprecations

- **TLSRoute `v1alpha2` deprecated:** still available in Experimental through v1.5.x, removed in v1.6. Teams referencing `v1alpha2` should migrate before upgrading to v1.6.
- **New `ValidatingAdmissionPolicy`** (`safe-upgrades.gateway.networking.k8s.io`) blocks installing Experimental CRDs after Standard CRDs are present, and prevents downgrading below v1.5.0. This policy can be intentionally removed if a specific workflow requires it.
- **TLSRoute CEL validation requires Kubernetes 1.31+.** Clusters on older versions will need to upgrade before the full validation story applies.

---

## Why It Matters for Operators

For organizations operating at scale, API stability is a prerequisite for adoption. The `v1alpha2` label carried an implicit warning: *this could change under you*. That friction was real. Many organizations were hesitant to build automation, GitOps pipelines, or compliance tooling on top of an alpha API.

`v1` removes that hesitation. Concretely, platform teams can now:

- **Standardize TLSRoute in infrastructure-as-code** without worrying about breaking changes forcing rewrites.
- **Build internal platform tooling** on a stable API surface with confidence in long-term support.
- **Meet compliance and audit requirements** more easily — stable APIs are far easier to document, govern, and sign off on.
- **Adopt TLSRoute across multi-cluster environments** without treating it as experimental infrastructure.

Gateway API's conformance testing model means implementations (Envoy Gateway, Cilium, Istio, and others) must validate against the stable spec, giving teams more confidence that behavior is consistent and portable across ingress controllers.

---

## Upgrade Actions

1. **Migrate TLSRoute resources from `v1alpha2` to `v1`** before upgrading to v1.6, which removes the alpha version.
2. **Verify your cluster runs Kubernetes 1.31+** to benefit from TLSRoute's CEL validation.
3. **Review the new `ValidatingAdmissionPolicy`** (`safe-upgrades.gateway.networking.k8s.io`) — if your CRD management workflow conflicts with it, remove it intentionally rather than working around it.
4. **Update conformance tests** if you maintain a Gateway API implementation — required sections changed with the new stable promotions.

---

## Source Links

- [Gateway API v1.5.0 Release Notes](https://github.com/kubernetes-sigs/gateway-api/releases/tag/v1.5.0)
- [GEP-2643: TLSRoute v1](https://gateway-api.sigs.k8s.io/geps/gep-2643/)
- [GEP-1713: ListenerSet](https://gateway-api.sigs.k8s.io/geps/gep-1713/)
- [GEP-1767: HTTPRoute CORS Filter](https://gateway-api.sigs.k8s.io/geps/gep-1767/)
- [Gateway API Conformance Documentation](https://gateway-api.sigs.k8s.io/concepts/conformance/)

## Related Pages

- Parent index: [Release news](index.md)
- Related: [Gateway API](../../networking/gateway-api.md)
- Related: [Ingress](../../networking/ingress.md)
- Related: [Services and Networking](../../networking/services-networking.md)
- Related: [Security news](../security/index.md)
- Newsletter: [This Week in Kubernetes](../../index.md#weekly-newsletter)
