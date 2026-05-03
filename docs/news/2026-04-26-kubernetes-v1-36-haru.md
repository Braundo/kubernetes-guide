---
title: "Kubernetes v1.36: ハル (Haru)"
date: 2026-04-26
category: releases
description: "Kubernetes v1.36, themed \"ハル (Haru)\" after the Japanese word for spring, arrives with 70 enhancements spanning 18 stable graduations, 25 beta promotions, and 25 new alpha features."
generated: "2026-04-26T18:19:38.255129-05:00"
---

# Kubernetes v1.36: ハル (Haru)

Kubernetes v1.36, themed "ハル (Haru)" after the Japanese word for spring, arrives with 70 enhancements spanning 18 stable graduations, 25 beta promotions, and 25 new alpha features.

## Release Summary

Released April 22, 2026, this version continues the project's predictable cadence while introducing changes that will affect cluster operations, particularly around API stability and feature maturity. The release includes both deprecations and removals that require operator attention before upgrading production environments. The release team has signaled that platform teams should review compatibility impacts carefully, as several features moving to stable status will alter default behaviors. With 70 total enhancements across the stability spectrum, v1.36 represents one of the more substantive releases in recent memory.

## Key Changes

The v1.36 release brings 18 features to stable status, meaning they are enabled by default and their APIs are guaranteed backward compatibility for multiple future releases. This graduation tier represents the largest category of production-ready enhancements in this cycle. Platform operators gain access to battle-tested functionality that has survived both beta testing periods and real-world validation.

Twenty-five features have entered beta, which in Kubernetes terms means they are enabled by default but still subject to potential changes before stabilization. Beta features carry feature gate controls, allowing operators to disable them if issues emerge. The substantial beta cohort suggests the project is maturing a broad set of capabilities simultaneously, from storage and networking primitives to scheduling and autoscaling improvements.

The 25 alpha features represent experimental work requiring explicit feature gate activation. These additions target forward-looking use cases and will need multiple release cycles before production readiness. Alpha features can change significantly or be removed entirely, making them unsuitable for critical workloads but valuable for testing emerging patterns.

This distribution of 18-25-25 across stability tiers indicates an active development pipeline with roughly equal investment in stabilizing existing work, advancing mid-stage features, and exploring new territory. The balance suggests healthy project maturity without stagnation.

## Breaking Changes and Deprecations

The release notes explicitly state that deprecations and removals are present in v1.36, though the summary excerpt does not enumerate specific items. Operators must conduct a thorough pre-upgrade audit using this checklist:

First, review all feature gates currently enabled in your cluster configuration. Cross-reference each against the v1.36 release notes to identify any that have been removed or changed. Feature gates for graduated stable features are typically removed, which can break clusters that explicitly disable them.

Second, audit all API resources in use across namespaces. Run `kubectl api-resources` against a test cluster running v1.36 and compare the output to your current version. Look for missing API versions, particularly any beta APIs that may have been removed after their deprecation window expired. Check for any custom resources or operators that depend on deprecated APIs.

Third, examine container runtime configurations and CSI drivers. Kubernetes regularly deprecates older interfaces as replacements mature. Verify that all storage classes, volume plugins, and runtime socket paths remain supported.

Fourth, scan admission webhooks and API aggregation layers for compatibility. Changes to API machinery can affect webhook configurations and extension API servers. Test all custom admission controllers against v1.36 API semantics in a non-production environment.

Fifth, validate monitoring and observability pipelines. Metric names, labels, and endpoints occasionally change during major refactors. Confirm that Prometheus scrapers, log collectors, and tracing systems can parse v1.36 component outputs.

Finally, review all automation that parses kubectl output or interacts with the API programmatically. Output format changes, even minor ones, can break CI/CD pipelines and infrastructure-as-code tooling.

## Why It Matters for Operators

The volume of stable graduations signals reduced churn in core functionality. Features reaching stable status receive API compatibility guarantees, reducing the maintenance burden of tracking beta changes across upgrade cycles. Operators can build automation and runbooks around stable APIs with confidence they will remain functional.

The 25 beta features entering default-enabled status will affect cluster behavior immediately upon upgrade. Unlike alpha features that require opt-in, beta features activate automatically unless explicitly disabled. This means upgrade testing must validate not just existing workload compatibility, but also the operational impact of newly enabled behaviors. Resource consumption patterns, scheduling decisions, and network policies may shift due to beta feature activation.

The substantial alpha feature set demonstrates continued innovation but also presents a testing burden. Operators interested in influencing feature direction should evaluate alpha capabilities in non-production clusters and provide feedback to SIG maintainers. Early testing helps surface edge cases before features reach wider deployment.

## Upgrade Actions

Before upgrading any production cluster, establish a v1.36 test environment that mirrors your production topology. Deploy representative workloads and run them through normal operational cycles for at least 72 hours. Monitor for unexpected behavior, performance regressions, or compatibility issues.

Review the complete v1.36 release notes and changelog, paying particular attention to the deprecations and removals section. Create a spreadsheet tracking each deprecated item against your current cluster inventory. Assign remediation owners for any conflicts discovered.

Update all operators, controllers, and custom resource definitions to versions certified for Kubernetes v1.36. Check vendor compatibility matrices before proceeding. Test updated components in your staging environment before production rollout.

Verify backup and disaster recovery procedures work correctly with v1.36. Take full cluster backups before upgrading and validate restoration processes in isolated test clusters.

Execute upgrades during maintenance windows with rollback plans prepared. Upgrade control plane nodes first, validate API server functionality, then proceed with worker node pools using a phased rollout strategy. Monitor cluster health metrics continuously during the upgrade process.

## Source Links

- [Kubernetes Blog](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/)

## Related Pages

- Parent index: [News](index.md)
- Related: [Kubernetes 1.35 GA: In-Place Pod Resizing Stable and Restart Semantics Formalized](2026-03-28-when-kubernetes-restarts-pod-when-it-doesn-t.md)
- Related: [Cluster API v1.12: Introducing In-place Updates and Chained Upgrades](2026-03-06-cluster-api-v1-12-introducing-place-updates-chained-upgrades.md)
- Newsletter: [This Week in Kubernetes](../index.md#weekly-newsletter)
- Evergreen reference: [Maintenance and upgrades](../operations/maintenance.md)
