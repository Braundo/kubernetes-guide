---
icon: material/clock-outline
---

# Jobs & CronJobs

Not all workloads in Kubernetes are long-running services. Sometimes, you just need to run something once — or on a schedule. That’s where **Jobs** and **CronJobs** come in.

---

## Jobs

A **Job** runs a Pod (or set of Pods) to completion. It's ideal for:

- One-time tasks
- Batch processing
- Migrations or post-deployment hooks

Kubernetes ensures the Job runs successfully to completion — even if a Pod crashes or a node fails, a new Pod will be scheduled.

### Minimal Job Example

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

> ⓘ The `restartPolicy` for Jobs must be `Never` or `OnFailure`.

---

## CronJobs

A **CronJob** runs Jobs on a repeating schedule, similar to Linux cron syntax.

Use CronJobs for:

- Periodic cleanup tasks
- Scheduled report generation
- Time-based batch jobs

### Cron Syntax Example

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