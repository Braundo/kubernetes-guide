---
title: "Kubernetes v1.34: Service Account Token Integration for Image Pulls Graduates to Beta"
date: 2025-09-03
category: releases
source_url: "https://kubernetes.io/blog/2025/09/03/kubernetes-v1-34-sa-tokens-image-pulls-beta/"
generated: "2026-03-06T19:21:08.668702+00:00"
---

# Kubernetes v1.34: Service Account Token Integration for Image Pulls Graduates to Beta

**Source:** [Kubernetes Blog](https://kubernetes.io/blog/2025/09/03/kubernetes-v1-34-sa-tokens-image-pulls-beta/)
**Published:** 2025-09-03 | **Category:** Releases

## Summary

Kubernetes v1.34 promotes Service Account Token Integration for Kubelet Credential Providers from alpha to beta, enabling workload-specific service account tokens to authenticate image pulls instead of long-lived image pull secrets. This feature graduated after its alpha debut in v1.33 and represents a significant step toward eliminating static credentials from cluster image pulls. The beta release introduces breaking changes from alpha, including a mandatory `cacheType` field in credential provider configurations.

## Why It Matters

Image pull secrets have been a persistent operational liability in Kubernetes clusters. These long-lived credentials sit in namespaces, often with broad registry access, creating both security exposure and operational overhead. Platform teams rotate these secrets manually, manage distribution across namespaces, and accept the risk that compromise of a single secret can expose private container images across multiple registries. This feature shifts authentication to ephemeral, scoped tokens tied to pod service accounts—the same pattern that eliminated long-lived tokens for in-cluster API access years ago.

The graduation to beta signals production readiness with the usual stability guarantees: the API won't change without deprecation warnings, and the feature will be enabled by default in most distributions. However, the breaking change around `cacheType` means teams who tested this in alpha on v1.33 must update their credential provider configurations before upgrading to v1.34. This isn't a passive upgrade—any cluster using alpha credential providers with service account tokens will break without config changes.

For platform teams building least-privilege container delivery pipelines, this closes a critical gap. External credential providers can now exchange short-lived service account tokens for registry credentials dynamically, making image pull authentication consistent with pod identity. This integrates cleanly with workload identity patterns already established through OIDC federation and projected service account tokens.

## What You Should Do

1. Check if your cluster uses Kubelet credential providers by searching for `CredentialProviderConfig` files referenced in kubelet configuration: `kubectl get nodes -o jsonpath='{.items[*].status.nodeInfo.kubeletVersion}'` to confirm version, then inspect kubelet flags on nodes for `--image-credential-provider-config` and `--image-credential-provider-bin-dir`.

2. If running v1.33 with alpha service account token integration enabled, audit your credential provider configurations before upgrading to v1.34 and add the required `cacheType` field to prevent kubelet failures during image pulls.

3. Evaluate whether your current image pull secret distribution mechanism could be replaced by this feature—if you're syncing secrets across namespaces or using tools like external-secrets operator solely for registry credentials, this pattern offers a more secure alternative.

4. Test the beta feature in a non-production cluster by configuring a credential provider that requests service account tokens, then deploy workloads and verify image pulls succeed with `kubectl describe pod <name>` checking for ImagePullBackOff errors.

5. Review your registry provider's support for exchanging service account tokens—AWS ECR, Google Artifact Registry, and Azure Container Registry have existing credential provider implementations that may already support or plan to support this integration.

## Further Reading

- [Kubernetes v1.34 Service Account Token Integration announcement](https://kubernetes.io/blog/2025/09/03/kubernetes-v1-34-sa-tokens-image-pulls-beta/)
- [Kubelet Credential Provider documentation](https://kubernetes.io/docs/tasks/administer-cluster/kubelet-credential-provider/)
- [KEP-2133: Kubelet Credential Providers](https://github.com/kubernetes/enhancements/tree/master/keps/sig-node/2133-kubelet-credential-providers)

---
*Published 2026-03-06 on k8s.guide*
