## Running an example Job
- Use `kubectl create -f ` to create a Job from a YAML file.
- `kubectl get jobs` to list all Jobs and their statuses.


## Writing a Job spec
- `metadata.name` to specify the Job name.
- `spec.template.spec.containers[].image` to specify the container image.
- `spec.template.spec.restartPolicy` must be either `Never` or `OnFailure`.


## Job Labels
- Labels are key-value pairs attached to Jobs.
- Useful for organizing and querying Jobs.


## Pod Template
- Nested inside the Job spec under spec.template.
- Specifies the Pod's containers, volumes, and other configurations.


## Pod selector
- Automatically generated based on Job's `metadata.labels`.
- Do not set `.spec.selector` field manually unless you know what you're doing.


## Parallel execution for Jobs
- `spec.parallelism`: Number of Pods running simultaneously.
- `spec.completions`: Number of Pods that must complete successfully for the Job to be marked as complete.


## Completion mode
- Indexed Jobs: Each Pod gets a unique index between 0 and spec.completions-1.
NonIndexed: No unique identifiers for Pods.


## Handling Pod and container failures
- `spec.backoffLimit`: Number of allowed failures before Job is marked as failed.
- `spec.activeDeadlineSeconds`: Time in seconds that a Job is allowed to run.


## Pod backoff failure policy
- Exponential backoff for restarting failed Pods.
Controlled by spec.backoffLimit and spec.activeDeadlineSeconds.


## Backoff limit per index
- In Indexed Jobs, each index has its own backoff limit and retry mechanism.


## Pod failure policy
- No explicit failure policy, but can be managed using `spec.backoffLimit` and `spec.activeDeadlineSeconds`.


## Job termination and cleanup
- Deleting a Job will also delete all its Pods.
- Use `kubectl delete job --selector=` to delete multiple Jobs.


## Clean up finished jobs automatically
- `.spec.ttlSecondsAfterFinished`: Time-to-live in seconds after Job completion, after which the Job and its Pods are deleted.


## TTL mechanism for finished Jobs
- TTL controller in Kubernetes takes care of this.
- Only works if the feature gate `TTLAfterFinished` is enabled.


## Job patterns
- **One-off Jobs**: Run once and terminate.
- **CronJobs**: Scheduled Jobs, defined using cron syntax.


## TTL-After-Finished Controller
- Provides a TTL (time to live) mechanism to limit the lifetime of Job objects that have finished execution.


## Cleanup for Finished Jobs
- Supported only for Jobs.
- You can specify `.spec.ttlSecondsAfterFinished` field to clean up finished Jobs automatically.
- The timer starts once the Job status changes to Complete or Failed.
- After TTL expires, the Job becomes eligible for cascading removal, including its dependent objects.
- Kubernetes honors object lifecycle guarantees, such as waiting for finalizers.


## Setting TTL
- You can set the TTL seconds at any time.
- Can be specified in the Job manifest.
- Can be manually set for existing, already finished Jobs.
- Can use a mutating admission webhook to set this field dynamically at Job creation time or after the Job has finished.
- You can write your own controller to manage the cleanup TTL for Jobs based on selectors.


## Caveats
- **Updating TTL for Finished Jobs**: You can modify the TTL period even after the job is created or has finished. However, retention is not guaranteed if you extend the TTL after it has already expired.
- **Time Skew**: The feature is sensitive to time skew in your cluster, which may cause the control plane to clean up Job objects at the wrong time.


## Cronjobs
- CronJobs are used for performing regular scheduled actions like backups, report generation, etc.


## Schedule Syntax
- Uses Cron syntax for scheduling.
- Extended "Vixie cron" step values are supported.
- Macros like `@monthly`, `@weekly`, etc., can also be used.


## Job Template
- Defines a template for the Jobs that the CronJob creates.
- Same schema as a Job but nested and without `apiVersion` or `kind`.


## Deadline for Delayed Job Start
- Optional `.spec.startingDeadlineSeconds` field.
- Defines a deadline for starting the Job if it misses its scheduled time.


## Concurrency Policy
- Optional `.spec.concurrencyPolicy` field.
- Options: `Allow` (default), `Forbid`, `Replace`.


## Schedule Suspension
- Optional `.spec.suspend` field to suspend execution of Jobs.


## Jobs History Limits
- `.spec.successfulJobsHistoryLimit` and `.spec.failedJobsHistoryLimit` fields are optional.


## Time Zones
- Time zones can be specified using `.spec.timeZone`.


## Job Creation
- A CronJob creates a Job object approximately once per execution time of its schedule.