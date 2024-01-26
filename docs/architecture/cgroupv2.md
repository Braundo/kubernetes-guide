On Linux, control groups constrain resources that are allocated to processes. The kubelet and the underlying container runtime need to interface with cgroups to enforce resource management for pods and containers which includes cpu/memory requests and limits for containerized workloads. There are two versions of cgroups in Linux: `cgroup v1` and `cgroup v2`. `cgroup v2` is the new generation of the cgroup API.


## What is `cgroup v2`?
- `cgroup v2` is the next version of the Linux cgroup API.
- Provides a unified control system with enhanced resource management capabilities.
- Offers improvements like a single unified hierarchy design in API, safer sub-tree delegation to containers, and enhanced resource allocation management.


## Using `cgroup v2`
- Recommended to use a Linux distribution that enables and uses `cgroup v2` by default.


## Requirements
- OS distribution should enable `cgroup v2`.
- Linux Kernel version should be 5.8 or later.
- Container runtime should support `cgroup v2`, e.g., `containerd v1.4` and later, `cri-o v1.20` and later.


## Linux Distribution `cgroup v2` support
- Linux distributions that support `cgroup v2`, such as Container Optimized OS, Ubuntu, Debian GNU/Linux, Fedora, Arch Linux, and RHEL.


## Migrating to `cgroup v2`
- Ensure you meet the requirements and then upgrade to a kernel version that enables `cgroup v2` by default.
- The kubelet automatically detects `cgroup v2` and performs accordingly.


## Identify the cgroup version on Linux Nodes
- To check which cgroup version your distribution uses, you can run specific commands like:
``` bash
stat -fc %T /sys/fs/cgroup/.
```