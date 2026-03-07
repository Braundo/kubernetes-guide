---
title: "Tomcat in the Crosshairs: New Research Reveals Ongoing Attacks"
date: 2025-04-02
category: security
generated: "2026-03-07T00:50:56.021888+00:00"
---

# Tomcat in the Crosshairs: New Research Reveals Ongoing Attacks

News headlines reported that it took just 30 hours for attackers to exploit a newly discovered vulnerability in Apache Tomcat servers.

## Advisory Summary

Aqua Nautilus researchers have identified an active attack campaign targeting Apache Tomcat servers. Attackers are deploying new malware to hijack resources, with exploitation occurring as quickly as 30 hours after vulnerability disclosure.

## Affected Components and Versions

Apache Tomcat servers are being actively targeted. Specific versions were not detailed in the report, but the campaign exploits newly discovered vulnerabilities in Tomcat deployments.

## Why It Matters

Tomcat is widely used as a servlet container in Kubernetes environments. The speed of exploitation (30 hours post-disclosure) leaves minimal time for patching. Compromised Tomcat servers can lead to resource hijacking, potentially impacting application availability, performance, and enabling lateral movement within clusters.

## What to Do

- Audit all Tomcat deployments in your clusters immediately
- Apply the latest Apache Tomcat security patches
- Review Tomcat server logs for suspicious activity or unauthorized access
- Implement network policies to restrict Tomcat pod communications
- Consider using runtime security monitoring to detect malware execution
- Verify that Tomcat containers run with minimal privileges and read-only root filesystems where possible

## Source Links

- [Aqua Security Blog](https://blog.aquasec.com/new-campaign-against-apache-tomcat)

## Related Pages

- Parent index: [Section index](index.md)
- Related: [IngressNightmare Advisory Briefing (CVE-2025-1097, CVE-2025-1098, CVE-2025-24514, CVE-2025-1974)](2025-03-26-cve-2025-ingressnightmare-ingress-nginx.md)
- Related: [CVE-2025-30066 Advisory Briefing (GitHub Actions Supply Chain)](2025-03-16-cve-2025-30066-github-actions.md)
- Newsletter: [This Week in Kubernetes](../../index.md#weekly-newsletter)
- Evergreen reference: [Kubernetes security primer](../../security/security.md)
