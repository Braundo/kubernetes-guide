## Terminology
- **DNS**: Domain Name System
- **FQDN**: Fully Qualified Domain Name
- **SRV Records**: Service records in DNS


## What is DNS for Services and Pods?
- Kubernetes creates DNS records for Services and Pods.
- Allows for name-based service discovery within the cluster.


## DNS Records
- Services and Pods get DNS records.
- "Normal" Services get A/AAAA records.
- Headless Services also get A/AAAA records but resolve to the set of IPs of all Pods selected by the Service.
- SRV Records are created for named ports.


## Pods
- Pods have A/AAAA records.
- The DNS resolution is `pod-ip-address.my-namespace.pod.cluster-domain.example`.
- Pods exposed by a Service have additional DNS resolution.


## Pod's hostname and subdomain fields
- The hostname is by default the Pod's `metadata.name`.
- The hostname can be overridden by `spec.hostname`.
- The fully qualified domain name (FQDN) can be set using `spec.subdomain`.


## Pod's DNS Policy
- DNS policies can be set per-Pod.
- Options include `Default`, `ClusterFirst`, `ClusterFirstWithHostNet`, and `None`.


## Pod's DNS Config
- Allows more control over DNS settings for a Pod.
- Can specify nameservers, searches, and options.


## DNS search domain list limits
- Kubernetes does not limit the DNS Config until the length of the search domain list exceeds 32 or the total length of all search domains exceeds 2048.


## DNS resolution on Windows nodes
- `ClusterFirstWithHostNet` is not supported on Windows nodes.
- Windows treats all names with a `.` as a FQDN and skips FQDN resolution.