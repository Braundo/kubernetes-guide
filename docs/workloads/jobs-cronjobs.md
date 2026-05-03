---
icon: lucide/timer
title: Kubernetes Jobs and CronJobs Explained (Batch and Scheduled Workloads)
description: Learn how Kubernetes Jobs and CronJobs work, how retries and scheduling behave, and common batch-processing patterns.
hide:
 - footer
---

# Jobs and CronJobs

Deployments are for long-running services. Jobs and CronJobs are for work that should complete.

## Job fundamentals

A Job runs pods until completion criteria are met.

```mermaid
flowchart LR
    CJ[CronJob] -->|creates on schedule| J[Job]
    J -->|creates| P1[Pod attempt 1]
    P1 -->|failure| P2[Pod attempt 2]
    P2 -->|success| Done([Job complete])
```

Key settings:

- `completions`: total successful runs required
- `parallelism`: how many pods run at once
- `backoffLimit`: retry attempts before failure
- `activeDeadlineSeconds`: overall execution timeout
- `ttlSecondsAfterFinished`: cleanup for completed jobs

For parallel work where each pod handles a distinct work item, use `completionMode: Indexed`. Kubernetes assigns each pod a unique index (via the `JOB_COMPLETION_INDEX` environment variable) so workers can partition their input.

```yaml
spec:
  completions: 10
  parallelism: 3
  completionMode: Indexed
```

## Job example

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: nightly-reindex
spec:
  backoffLimit: 3
  ttlSecondsAfterFinished: 3600
  template:
    spec:
      restartPolicy: OnFailure
      containers:
        - name: worker
          image: ghcr.io/example/reindexer:v1.4.2
          args: ["--tenant", "all"]
```

`restartPolicy` for Job pods must be `OnFailure` or `Never`.

## CronJob fundamentals

A CronJob creates Jobs on a schedule.

Critical settings:

- `schedule`: cron expression in controller time zone
- `concurrencyPolicy`: `Allow`, `Forbid`, or `Replace`
- `startingDeadlineSeconds`: late-start tolerance
- `successfulJobsHistoryLimit` and `failedJobsHistoryLimit`

## CronJob example

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-backup
spec:
  schedule: "0 2 * * *"
  concurrencyPolicy: Forbid
  startingDeadlineSeconds: 1800
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 2
  jobTemplate:
    spec:
      backoffLimit: 2
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: backup
              image: ghcr.io/example/backup:v3.1.0
              args: ["/bin/sh", "-c", "backup.sh"]
```

## Reliability practices

- Make jobs idempotent so retries do not corrupt state
- Use locking when parallel workers touch shared systems
- Set resource requests and limits to avoid noisy-neighbor effects
- Alert on missed schedules and repeated failures

## Useful commands

```bash
kubectl get jobs
kubectl get cronjobs
kubectl describe cronjob nightly-backup
kubectl create job --from=cronjob/nightly-backup manual-backup-test
```

## Common mistakes

- letting CronJobs overlap when tasks are not concurrency-safe
- no TTL cleanup, leaving thousands of completed objects
- assuming a successful Job means downstream side effects succeeded

## Summary

Jobs and CronJobs are the Kubernetes primitives for batch execution and scheduling. With idempotent task design and strict concurrency controls, they are reliable for production automation.

## Related Concepts

- [Pods and Deployments](pods-deployments.md) for long-running services
- [Resource Limits and Requests](../configuration/limits-requests.md)
- [Troubleshooting](../operations/troubleshooting.md)
