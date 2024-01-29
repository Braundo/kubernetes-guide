## Privileged Policy
**Purpose**: For system and infrastructure-level workloads managed by privileged, trusted users.  
**Characteristics**: No restrictions, allows for known privilege escalations.


## Baseline Policy
**Purpose**: For common containerized workloads, prevents known privilege escalations.  
**Characteristics**:
- Disallows privileged access to the Windows node.
- Sharing host namespaces is not allowed.
- Privileged Pods are disallowed.
- Adding additional capabilities beyond a specified list is disallowed.
- HostPath volumes are forbidden.
- HostPorts are disallowed or restricted to a known list.
- Overrides to the default AppArmor profile are restricted.
- Setting custom SELinux user or role options is forbidden.
- The default /proc masks are required.
- Seccomp profile must not be set to Unconfined.
- Only a "safe" subset of sysctls is allowed.


## Restricted Policy
**Purpose**: For security-critical applications and lower-trust users.
**Characteristics**:
- Enforces everything from the baseline profile.
- Only permits specific volume types.
- Privilege escalation is not allowed.
- Containers must run as non-root users.
- Seccomp profile must be explicitly set to one of the allowed values.
- Containers must drop ALL capabilities except `NET_BIND_SERVICE`.
