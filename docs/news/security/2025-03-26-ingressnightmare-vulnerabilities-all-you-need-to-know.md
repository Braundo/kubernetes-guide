---
title: "IngressNightmare Vulnerabilities: All You Need to Know"
date: 2025-03-26
category: security
source_url: "https://blog.aquasec.com/ingress-nginx-vulnerabilities-what-you-need-to-know"
generated: "2026-03-06T19:45:05.330610+00:00"
---

# IngressNightmare Vulnerabilities: All You Need to Know

**Source:** [Aqua Security Blog](https://blog.aquasec.com/ingress-nginx-vulnerabilities-what-you-need-to-know)
**Published:** 2025-03-26 | **Category:** Security

## Summary

On March 24, 2025, four critical vulnerabilities (CVE-2025-1097, CVE-2025-1098, CVE-2025-24514, and CVE-2025-1974) were disclosed in the ingress-nginx Controller for Kubernetes, collectively named IngressNightmare. These flaws allow attackers to gain unauthorized access to all secrets stored across all namespaces in a Kubernetes cluster, potentially leading to complete cluster takeover.

## Why It Matters

The ingress-nginx controller runs with elevated privileges by design, and these vulnerabilities turn that architectural requirement into a critical attack vector. If you run ingress-nginx in production, assume that an attacker who can exploit these CVEs has access to every secret in your cluster: service account tokens, database credentials, API keys, TLS certificates. This is not a namespace isolation bypass, it is complete secret exfiltration capability across the entire cluster.

The blast radius extends beyond immediate credential theft. With access to service account tokens from privileged namespaces, an attacker can escalate to node access, manipulate workloads, or pivot to the control plane depending on your RBAC configuration. If you store sensitive secrets in etcd without encryption at rest, or if your secrets include credentials for external systems, the compromise extends beyond Kubernetes itself.

This disclosure reinforces a hard lesson about ingress controllers: they sit at the trust boundary between external traffic and your cluster, and they require broad permissions to function. The combination makes them high-value targets. If you have been considering the Gateway API migration or evaluating alternative ingress implementations, IngressNightmare provides operational justification for that architectural review.

## What You Should Do

1. Check your ingress-nginx version immediately: run `kubectl get deployment -n ingress-nginx ingress-nginx-controller -o jsonpath='{.spec.template.spec.containers[0].image}'` and compare against the patched versions listed in the advisory.

2. Review your audit logs for suspicious activity: search for unexpected secret access patterns, particularly cross-namespace secret reads from the ingress-nginx service account in the past 30 days.

3. Rotate all secrets in your cluster after patching, prioritizing service account tokens, database credentials, and any secrets that grant access to external systems or production infrastructure.

4. Verify that your ingress-nginx RBAC permissions follow least privilege: check if the controller has broader permissions than required, and confirm that encryption at rest is enabled for etcd if not already configured.

5. Test the patched version in a non-production environment before rolling it to production, as ingress controller updates can affect traffic routing and require careful validation of existing Ingress resources.

## Further Reading

- [IngressNightmare Vulnerabilities: All You Need to Know](https://blog.aquasec.com/ingress-nginx-vulnerabilities-what-you-need-to-know) (source article)
- [ingress-nginx GitHub Security Advisories](https://github.com/kubernetes/ingress-nginx/security/advisories)
- [Kubernetes Secrets Documentation](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Gateway API Documentation](https://gateway-api.sigs.k8s.io/)

---
*Published 2026-03-06 on k8s.guide*
