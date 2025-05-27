---
icon: material/file-document-outline
---

In Kubernetes, **audit logging** and centralized **log collection** are critical components of a secure and observable platform. Audit logs help detect policy violations or suspicious behavior, while application and cluster logs help with troubleshooting, monitoring, and forensics.

---

<h2>Audit Logs in Kubernetes</h2>

Kubernetes audit logs record the <strong>who, what, when, and where</strong> of every request made to the Kubernetes API server. These logs are essential for security analysis, compliance, and intrusion detection.
<br>
Audit logging must be configured explicitly and is typically enabled on the control plane node(s).

### Key Fields in Audit Events

Each audit log entry includes:

- `user.username`: Who initiated the request
- `verb`: What operation was attempted (e.g. `create`, `get`, `patch`)
- `objectRef`: Which resource was affected
- `responseStatus`: Whether it succeeded or failed
- `stage`: The phase of request processing (e.g. `RequestReceived`, `ResponseComplete`)

### Example JSON Entry (Simplified)

```json
{
  "kind": "Event",
  "apiVersion": "audit.k8s.io/v1",
  "user": {
    "username": "admin"
  },
  "verb": "create",
  "objectRef": {
    "resource": "pods",
    "namespace": "default",
    "name": "nginx"
  },
  "responseStatus": {
    "code": 201
  },
  "stage": "ResponseComplete"
}
```

---

## Enabling Audit Logging

Audit logging is configured via the `--audit-policy-file` and `--audit-log-path` flags on the API server.

### Example startup flags:

```bash
--audit-policy-file=/etc/kubernetes/audit-policy.yaml
--audit-log-path=/var/log/kubernetes/audit.log
```

You also define a **policy file** to control which events get logged:

---

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
  - level: Metadata
    verbs: ["create", "delete"]
    resources:
      - group: ""
        resources: ["pods"]
```

---

## Centralized Logging Stack

To collect and analyze logs from applications, control plane components, and nodes, you’ll typically deploy a **logging stack**.

### Common Choices:

| Tool            | Purpose                                      |
|------------------|----------------------------------------------|
| Fluent Bit       | Lightweight log forwarder (agent)           |
| Fluentd          | Full-featured log collector/transformer     |
| Loki             | Scalable log store optimized for Kubernetes |
| Elasticsearch    | Popular full-text search engine             |
| Kibana / Grafana | Visualization dashboards                    |

These tools collect logs from container stdout/stderr or files (e.g., `/var/log/containers/`) and ship them to a centralized location.

---

## Recommended Architecture

A typical Kubernetes logging pipeline:

```
Pods/Containers
     ↓
Fluent Bit / Fluentd (DaemonSet)
     ↓
Loki / Elasticsearch / Custom Sink
     ↓
Grafana / Kibana / Alerting Tools
```

This allows:

- Full-text search over logs
- Filtering by label, container, namespace, or timestamp
- Long-term storage for audit/compliance
- Alerts on suspicious activity

---

## Best Practices

- Rotate and retain audit logs securely (e.g., via logrotate or cloud log sinks)
- Don’t log full request/response bodies unless necessary
- Separate audit logs from normal logs in storage and access control
- Use RBAC to restrict access to sensitive audit and control plane logs
- Encrypt logs in transit and at rest if stored outside the cluster

---

## Summary

Audit logging and centralized logging are essential for both **security** and **observability** in Kubernetes. Audit logs capture cluster-level events for compliance and threat detection, while the logging stack enables real-time visibility and operational insights. Both should be included in any production-grade Kubernetes deployment.