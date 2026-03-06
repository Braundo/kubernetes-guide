---
title: "Kubernetes v1.34: Use An Init Container To Define App Environment Variables"
date: 2025-09-10
category: releases
source_url: "https://kubernetes.io/blog/2025/09/10/kubernetes-v1-34-env-files/"
generated: "2026-03-06T19:32:28.446744+00:00"
---

# Kubernetes v1.34: Use An Init Container To Define App Environment Variables

**Source:** [Kubernetes Blog](https://kubernetes.io/blog/2025/09/10/kubernetes-v1-34-env-files/)
**Published:** 2025-09-10 | **Category:** Releases

## Summary

Kubernetes v1.34 introduces an alpha feature gate called `EnvFiles` that allows containers to load environment variables directly from files stored in Pod volumes, specifically emptyDir volumes. This approach bypasses the traditional ConfigMap and Secret API calls, enabling init containers to write environment variable files that application containers can consume without mounting the files into the container filesystem. The feature requires cluster-wide enablement of the EnvFiles feature gate.

## Why It Matters

This feature addresses a specific operational pain point: the tight coupling between workload lifecycle and configuration management. Today's ConfigMap and Secret pattern requires separate API resources, RBAC policies, and careful orchestration to ensure configurations update before or alongside Pod restarts. For teams running vendor containers that demand runtime-generated credentials (license tokens, session keys, short-lived certificates), the current options are awkward. You either bake secrets into image layers, use external secret operators with their own failure modes, or mount volumes that expose sensitive files to container processes.

The init container pattern here is elegant for ephemeral configuration. An init container can call an external API, generate a time-bound token, write it to an emptyDir volume as an env file, and exit. The main container picks up those variables without the kubelet ever creating a ConfigMap object or requiring etcd writes. This reduces API server load and removes a whole class of RBAC complexity around who can read which Secrets in which namespaces.

The operational tradeoff is clear: this only works for data that can be generated at Pod start time and doesn't need to change during the container's lifetime. You lose the hot-reload capability that some controllers provide when ConfigMaps change. For license keys and bootstrap tokens, that's acceptable. For feature flags or database connection strings that need runtime updates, stick with ConfigMaps and tools like Reloader.

## What You Should Do

1. Check your Kubernetes version with `kubectl version --short` and confirm you're running v1.34 or later before testing this feature.

2. Enable the feature gate on your control plane and all kubelets by adding `--feature-gates=EnvFiles=true` to kubelet arguments, then restart the kubelet service on each node.

3. Create a test Pod with an init container that writes environment variables to `/env/.env` in an emptyDir volume, then configure your main container to reference that file using the new `envFrom.file` field pointing to the volume path.

4. Verify the feature works by exec-ing into the running container with `kubectl exec -it <pod-name> -- printenv` and confirming variables from the file appear without the file being visible in the container filesystem.

5. Document that this feature is alpha and unsuitable for production workloads until it reaches beta in a future release, likely v1.36 or later.

## Further Reading

- [Kubernetes v1.34 announcement: Use An Init Container To Define App Environment Variables](https://kubernetes.io/blog/2025/09/10/kubernetes-v1-34-env-files/)
- [Kubernetes feature gates documentation](https://kubernetes.io/docs/reference/command-line-tools-reference/feature-gates/)
- [Init Containers documentation](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/)

---
*Published 2026-03-06 on k8s.guide*
