Container lifecycle hooks allow containers to be aware of events in their management lifecycle and run specific code when these events occur.

## Container Hooks
- **PostStart**: This hook is executed immediately after a container is created. However, there's no guarantee that it will execute before the container's `ENTRYPOINT`. No parameters are passed to the handler.
- **PreStop**: This hook is called right before a container is terminated due to various reasons like API request, liveness/startup probe failure, etc. The hook must complete before the `TERM` signal to stop the container is sent.


## Hook Handler Implementations
- Containers can implement two types of hook handlers:
    - `Exec`: Executes a specific command inside the container's cgroups and namespaces.
    - `HTTP`: Executes an HTTP request against a specific endpoint on the container.


## Hook Handler Execution
- Hook calls are synchronous within the context of the Pod containing the container.
- For `PostStart` hooks, the Container `ENTRYPOINT` and hook fire asynchronously.
- `PreStop` hooks must complete before the `TERM` signal can be sent.


## Hook Delivery Guarantees
- Generally, hook delivery is intended to be at least once, meaning a hook may be called multiple times for any given event.


## Debugging Hook Handlers
- Logs for hook handlers are not exposed in Pod events. If a handler fails, it broadcasts an event like `FailedPostStartHook` or `FailedPreStopHook`.

