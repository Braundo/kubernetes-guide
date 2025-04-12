---
icon: material/timer-sand
---


In Kubernetes, **Jobs** and **CronJobs** are workload resources designed to run tasks that are either one-off (batch jobs) or recurring (scheduled tasks). Unlike Deployments or StatefulSets, Jobs are not intended for long-running applications, but rather for tasks that need to complete successfully once or on a schedule.

---

## What is a Job?

A **Job** is a controller that creates one or more Pods and ensures that a specified number of them successfully terminate. Jobs are useful for batch processing, migrations, cleanup tasks, or data processing pipelines.

### Example Use Cases:
- Database schema migrations
- Data processing (e.g., ETL tasks)
- One-time background tasks

### Example YAML:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: data-processing-job
spec:
  template:
    spec:
      containers:
      - name: processor
        image: my-data-processor:latest
        args: ["--run-once"]
      restartPolicy: OnFailure
```

---

## What is a CronJob?

A **CronJob** creates Jobs on a scheduled basis, similar to a Unix cron. It’s perfect for recurring tasks such as cleanup scripts, report generation, or periodic data syncs.

### Schedule Format:
The `schedule` field uses standard cron notation:

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday)
│ │ │ │ │
│ │ │ │ │
│ │ │ │ │
* * * * *
```

### Example YAML:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: log-cleanup
spec:
  schedule: "0 3 * * *"  # Every day at 3:00 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: cleaner
            image: my-cleaner:latest
            args: ["--clean", "/var/log"]
          restartPolicy: OnFailure
```

---

## Key Fields and Options

| Field                     | Description                                                                 |
|---------------------------|-----------------------------------------------------------------------------|
| `schedule`                | Cron format string that defines the execution interval                     |
| `concurrencyPolicy`       | Controls whether jobs can run concurrently (`Allow`, `Forbid`, `Replace`) |
| `startingDeadlineSeconds` | How long to wait before marking a missed job as failed                    |
| `successfulJobsHistoryLimit` | How many successful job runs to keep in history                         |
| `failedJobsHistoryLimit`     | How many failed job runs to keep in history                             |
| `ttlSecondsAfterFinished`    | Automatically clean up old jobs after this many seconds                 |

---

## Best Practices

- **Use `restartPolicy: OnFailure`** for Job Pods so they retry if the container fails.
- **Set `ttlSecondsAfterFinished`** to avoid clutter from completed Jobs.
- **Use `concurrencyPolicy: Forbid`** in CronJobs if jobs must not overlap.
- **Set resource limits** to prevent runaway tasks from consuming too much cluster capacity.

---

## Summary

| Feature     | Job                                | CronJob                              |
|-------------|-------------------------------------|---------------------------------------|
| One-off     | ✅                                  | ❌                                     |
| Scheduled   | ❌                                  | ✅                                     |
| Retryable   | ✅ (via `restartPolicy`)            | ✅ (inherits Job behavior)            |
| Cleanup     | Optional with `ttlSecondsAfterFinished` | Optional with `ttlSecondsAfterFinished` |
| Use Case    | Data migration, ETL, cleanup        | Backups, scheduled reports, cleanup   |

Use **Jobs** when you need a task to run once until successful. Use **CronJobs** when you need tasks to run on a repeating schedule with optional history and overlap control.