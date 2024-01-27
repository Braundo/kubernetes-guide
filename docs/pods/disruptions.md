## Types of Disruptions
- **Involuntary Disruptions**: Unavoidable cases like hardware failure, cloud provider issues, etc.
- **Voluntary Disruptions**: Actions initiated by the application owner or cluster administrator, such as draining a node for repair or upgrade.


## Mitigating Disruptions
- Request the resources your pod needs.
- Replicate your application for higher availability.
- Use anti-affinity to spread applications across racks or zones.


## Pod Disruption Budgets (PDB)
- Allows you to specify how many pods of a replicated application can be down simultaneously.
- Cluster managers should respect PDBs by calling the Eviction API.


## Pod Disruption Conditions
- A beta feature that adds a dedicated condition to indicate that the Pod is about to be deleted due to a disruption.


## Separation of Roles
- Discusses the benefits of separating the roles of Cluster Manager and Application Owner.


## Options for Cluster Administrators
- Accept downtime, failover to another cluster, or write disruption-tolerant applications and use PDBs.
