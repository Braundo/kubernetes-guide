---
icon: material/clock-outline
---

<h1>Jobs & CronJobs</h1>

Not all Kubernetes workloads run forever. Sometimes, you just need to run something once—or on a schedule. That’s where <strong>Jobs</strong> and <strong>CronJobs</strong> come in.

---

<h2>Jobs</h2>

A <strong>Job</strong> runs a Pod (or Pods) to completion. Perfect for:
- One-time tasks
- Batch processing
- Migrations or post-deployment hooks

Kubernetes guarantees the Job runs to completion—even if a Pod crashes or a node fails, a new Pod will be scheduled.

<h3>Minimal Job Example</h3>

```yaml
kind: Job
spec:
  template:
    spec:
      containers:
        - name: hello
          image: busybox
          command: ["echo", "Hello World"]
      restartPolicy: Never
```

> <strong>Tip:</strong> The <code>restartPolicy</code> for Jobs must be <code>Never</code> or <code>OnFailure</code>.

---

<h2>CronJobs</h2>

A <strong>CronJob</strong> runs Jobs on a repeating schedule, just like Linux cron.

Use CronJobs for:
- Periodic cleanup tasks
- Scheduled reports
- Time-based batch jobs

<h3>Cron Syntax Example</h3>

```yaml
kind: CronJob
spec:
  schedule: "0 * * * *"  # every hour
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: task
              image: busybox
              args: ["echo", "Hourly job"]
          restartPolicy: OnFailure
```

> CronJobs use the same `jobTemplate` spec as regular Jobs.

---

## Cron Syntax Quick Guide

| Field         | Meaning         |
|---------------|------------------|
| Minute        | 0–59             |
| Hour          | 0–23             |
| Day of Month  | 1–31             |
| Month         | 1–12             |
| Day of Week   | 0–6 (Sun=0)      |

Examples:
- `0 0 * * *` = Every day at midnight
- `*/5 * * * *` = Every 5 minutes

---

## Summary

- Use a **Job** for tasks that need to run once and finish.
- Use a **CronJob** to schedule Jobs using cron syntax.
- Both are useful for batch jobs, cleanup scripts, and other non-service workloads.