---
title: "Supply Chain Security Risk: GitHub Action tj-actions/changed-files Compromised"
date: 2025-03-16
category: security
source_url: "https://blog.aquasec.com/supply-chain-security-threat-github-action-tj-actions-compromised"
generated: "2026-03-06T19:44:25.974392+00:00"
---

# Supply Chain Security Risk: GitHub Action tj-actions/changed-files Compromised

**Source:** [Aqua Security Blog](https://blog.aquasec.com/supply-chain-security-threat-github-action-tj-actions-compromised)
**Published:** 2025-03-16 | **Category:** Security

## Summary

On March 14th, 2025, security researchers discovered CVE-2025-30066, a critical supply chain vulnerability in the GitHub Action tj-actions/changed-files. The compromised action exposes CI/CD secrets in GitHub Actions build logs when tracking changed files in pull requests. While no evidence suggests the secrets were transmitted externally, they appear in clear text in build logs, creating a critical exposure risk for public repositories.

## Why It Matters

This incident highlights a fundamental risk in modern CI/CD pipelines: third-party GitHub Actions operate with the same privilege context as your workflows, including access to secrets. Many teams treat GitHub Actions from popular repositories as trusted dependencies without applying the same security rigor they would to container images or Helm charts. The tj-actions/changed-files action is widely deployed across infrastructure-as-code repositories that manage Kubernetes manifests, Terraform configs, and GitOps workflows. These repositories commonly contain secrets for cluster access, cloud provider credentials, and container registry authentication.

The exposure mechanism is particularly dangerous for organizations running public repositories or using GitHub's default visibility settings for Actions logs. Once secrets appear in logs, they persist in GitHub's audit trail and may be cached or indexed by automated scanners. For platform teams, this means any workflow using this action could have leaked credentials with permissions to modify cluster resources, access etcd, or manipulate RBAC policies. The window between secret exposure and rotation determines actual impact.

This compromise underscores the need for defense-in-depth in CI/CD security. Relying solely on GitHub's secrets mechanism without additional controls like short-lived credentials, OIDC federation, or secret scanning creates single points of failure. Platform teams should evaluate whether their CI/CD pipeline could survive a similar compromise in other widely-used actions.

## What You Should Do

1. Audit all repositories using tj-actions/changed-files by searching GitHub with `org:YOUR_ORG tj-actions/changed-files path:.github/workflows` and identify affected workflows, prioritizing public repositories first.

2. Review workflow run logs from the past 30 days for any repository using this action. Check for exposed secrets by examining the step output where tj-actions/changed-files executed. Treat any exposed credentials as compromised.

3. Rotate all secrets accessible to workflows that used the compromised action, including cloud provider credentials, container registry tokens, Kubernetes service account tokens, and API keys. Use `kubectl delete secret` and recreate secrets in affected namespaces.

4. Pin GitHub Actions to specific commit SHAs rather than tags in your workflow files: change `uses: tj-actions/changed-files@v1` to `uses: tj-actions/changed-files@abc123def456` to prevent automatic adoption of compromised versions.

5. Implement secrets scanning on your repositories using tools like GitHub's secret scanning or gitleaks, and configure GitHub Actions to use OIDC-based authentication for cloud providers instead of long-lived credentials where possible.

## Further Reading

- [Aqua Security: Supply Chain Security Threat - GitHub Action tj-actions Compromised](https://blog.aquasec.com/supply-chain-security-threat-github-action-tj-actions-compromised)
- [GitHub: Security hardening for GitHub Actions](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [CNCF: Software Supply Chain Best Practices](https://github.com/cncf/tag-security/tree/main/supply-chain-security)

---
*Published 2026-03-06 on k8s.guide*
