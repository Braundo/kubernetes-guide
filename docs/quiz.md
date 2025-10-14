---
hide:
  - navigation
---

<?quiz?>
question: Which command lists all Pods in the current namespace?
answer-correct: <code>kubectl get pods</code> [why: This is the standard command to list all Pods in the current namespace.]
answer: <code>kubectl list pods</code> [why: There is no <code>list</code> subcommand in <code>kubectl</code>.]
answer: <code>kubectl pods</code> [why: <code>pods</code> is a resource, not a standalone command.]
answer: <code>kubectl ps</code> [why: <code>ps</code> is a Linux process listing command, not a Kubernetes command.]
content:
  The <code>kubectl get pods</code> command lists all Pods in the current namespace by default. Add <code>-A</code> to show Pods across all namespaces.
<?/quiz?>

<?quiz?>
question: Which object is responsible for ensuring the desired number of Pods are running?
answer: DaemonSet [why: Ensures one Pod per node, not a specific count.]
answer: StatefulSet [why: Manages ordered, persistent Pods but not generic counts.]
answer-correct: ReplicaSet [why: It maintains a specified number of identical Pods by creating or deleting them as needed.]
answer: Job [why: Ensures completion of tasks, not persistent Pod count.]
content:
  ReplicaSets monitor and maintain the number of replicas specified in their configuration to match the desired state.
<?/quiz?>

<?quiz?>
question: What does the <code>kubectl describe pod</code> command do?
answer-correct: Shows detailed information about a specific Pod, including events and status [why: It provides verbose details like labels, containers, IPs, and recent events.]
answer: Shows only Pod names [why: That’s what <code>kubectl get pods</code> does, not <code>describe</code>.]
answer: Deletes the Pod [why: The <code>delete</code> command is used to remove resources.]
answer: Creates a new Pod [why: <code>apply</code> or <code>create</code> are used to add resources, not <code>describe</code>.]
content:
  <code>kubectl describe</code> provides detailed resource information useful for debugging Pod failures or scheduling issues.
<?/quiz?>

<?quiz?>
question: Which controller ensures a Pod runs on every node?
answer: ReplicaSet [why: Ensures a set number of Pods exist globally, not per node.]
answer: Deployment [why: Manages ReplicaSets and rolling updates, not one-per-node Pods.]
answer-correct: DaemonSet [why: Deploys one Pod per node, commonly used for logging and monitoring agents.]
answer: StatefulSet [why: Provides stable identifiers and volumes, not per-node deployment.]
content:
  DaemonSets are ideal for node-level agents such as log shippers, metrics collectors, and network tools.
<?/quiz?>

<?quiz?>
question: What is the smallest deployable unit in Kubernetes?
answer-correct: Pod [why: A Pod is the smallest unit that can be deployed and managed in Kubernetes.]
answer: Node [why: A node runs Pods but is not deployed via Kubernetes workloads.]
answer: Container [why: Containers are part of Pods; Pods are the actual deployable units.]
answer: ReplicaSet [why: Controls Pods but isn’t itself a workload unit.]
content:
  Pods encapsulate one or more containers, storage, and networking resources as the basic execution unit.
<?/quiz?>

<?quiz?>
question: What is the default namespace in Kubernetes?
answer: kube-system [why: Reserved for system-level components.]
answer: kube-public [why: Used for cluster-wide public resources.]
answer-correct: default [why: User-created resources without a specified namespace go here by default.]
answer: kube-node-lease [why: Used for node heartbeats, not user workloads.]
content:
  The <code>default</code> namespace is where Kubernetes places user workloads when no namespace is specified.
<?/quiz?>

<?quiz?>
question: Which command shows the cluster’s API resources?
answer-correct: <code>kubectl api-resources</code> [why: Lists all resource kinds supported by the API server.]
answer: <code>kubectl get api</code> [why: There’s no such subcommand.]
answer: <code>kubectl describe api</code> [why: Doesn’t list resource types; used for describing specific resources.]
answer: <code>kubectl resources</code> [why: Not a valid command.]
content:
  <code>kubectl api-resources</code> displays all resource types and their short names, namespaces, and API groups.
<?/quiz?>

<?quiz?>
question: Which object provides stable network identity for a set of Pods?
answer: Deployment [why: Ensures rollout of Pods, not networking identity.]
answer-correct: Service [why: Provides a consistent virtual IP and DNS name for Pods.]
answer: ReplicaSet [why: Manages Pod replicas but doesn’t handle networking.]
answer: Ingress [why: Handles external HTTP/S access, not internal service discovery.]
content:
  Services provide stable internal networking and load balancing for Pods, even when Pods are replaced.
<?/quiz?>

<?quiz?>
question: Which Kubernetes resource is used to store confidential data?
answer-correct: Secret [why: Stores sensitive data like tokens or passwords, encoded and mounted securely.]
answer: ConfigMap [why: Stores non-sensitive configuration data.]
answer: PersistentVolume [why: Provides storage, not configuration or secrets.]
answer: Role [why: Used for RBAC permissions, not data storage.]
content:
  Secrets keep sensitive information separate from code, and can be injected into Pods via environment variables or volumes.
<?/quiz?>

<?quiz?>
question: Which file defines how a Kubernetes object should be created?
answer-correct: Manifest file [why: A YAML or JSON file describing object metadata, spec, and desired state.]
answer: kubeconfig [why: Configures client connection, not objects.]
answer: Dockerfile [why: Builds container images, not Kubernetes resources.]
answer: ServiceAccount [why: Controls access, not object definition.]
content:
  Kubernetes manifests define resources declaratively so they can be version-controlled and applied with <code>kubectl apply</code>.
<?/quiz?>

<?quiz?>
question: What is the purpose of <code>kubectl apply</code>?
answer: Deletes a resource [why: <code>delete</code> removes resources, not <code>apply</code>.]
answer-correct: Creates or updates resources declaratively from manifests [why: It compares desired vs actual state and reconciles them.]
answer: Lists resources [why: <code>get</code> lists, <code>apply</code> manages configuration.]
answer: Runs a Pod interactively [why: <code>run</code> is used to launch a Pod directly.]
content:
  <code>kubectl apply</code> declaratively manages configuration, enabling continuous reconciliation of resource definitions.
<?/quiz?>

<?quiz?>
question: What is the default network model in Kubernetes?
answer-correct: Flat, routable Pod network [why: All Pods can communicate directly without NAT by default.]
answer: NAT-based network [why: Kubernetes avoids NAT between Pods for simplicity.]
answer: Segmented per-node network [why: Not the default; overlays or policies can add segmentation.]
answer: External-only network [why: Pods need internal networking to function.]
content:
  Kubernetes networking assumes every Pod can reach every other Pod directly using its IP.
<?/quiz?>

<?quiz?>
question: Which command displays cluster node information?
answer: <code>kubectl get pods</code> [why: Lists Pods, not nodes.]
answer-correct: <code>kubectl get nodes</code> [why: Shows node names, status, roles, and versions.]
answer: <code>kubectl describe cluster</code> [why: Not a valid command.]
answer: <code>kubectl show nodes</code> [why: No <code>show</code> command in <code>kubectl</code>.]
content:
  <code>kubectl get nodes</code> lists the nodes registered in your cluster along with their status and roles.
<?/quiz?>

<?quiz?>
question: Which controller ensures completed Pods don’t restart?
answer: Deployment [why: Used for long-running workloads.]
answer: ReplicaSet [why: Ensures Pod count, not job completion.]
answer-correct: Job [why: Runs Pods to completion and doesn’t restart successful ones.]
answer: StatefulSet [why: Manages ordered Pods with persistent identity.]
content:
  Jobs are ideal for one-time tasks like batch processing or migrations.
<?/quiz?>

<?quiz?>
question: What is the difference between a ReplicaSet and a Deployment?
answer: They’re identical [why: A Deployment manages ReplicaSets but adds rollout control.]
answer-correct: Deployment manages ReplicaSets and handles rolling updates [why: Deployments add versioning, rollback, and declarative updates.]
answer: ReplicaSet handles rollbacks [why: It doesn’t; Deployments do.]
answer: ReplicaSet manages multiple Deployments [why: Reverse relationship; Deployments manage ReplicaSets.]
content:
  Deployments provide a higher-level abstraction for updates and rollbacks on top of ReplicaSets.
<?/quiz?>

<?quiz?>
question: Which Kubernetes component schedules Pods to nodes?
answer: kubelet [why: Runs Pods on nodes but doesn’t schedule them.]
answer-correct: kube-scheduler [why: Assigns Pods to nodes based on constraints and resources.]
answer: kube-controller-manager [why: Handles replication and other controllers, not scheduling.]
answer: etcd [why: Key-value store for cluster state, not scheduling.]
content:
  The kube-scheduler evaluates resource availability and assigns Pods to suitable nodes.
<?/quiz?>

<?quiz?>
question: Which API resource provides cluster configuration for users?
answer: ConfigMap [why: Stores configuration for applications, not cluster access.]
answer: Secret [why: Stores sensitive data, not kubeconfig information.]
answer-correct: kubeconfig [why: Defines cluster connection details, authentication, and context for users.]
answer: ServiceAccount [why: Grants in-cluster access for Pods, not external users.]
content:
  <code>kubeconfig</code> files store credentials, cluster API URLs, and contexts for user access.
<?/quiz?>

<?quiz?>
question: What is a ServiceAccount used for?
answer: Assigning RBAC roles to users [why: RBAC Roles are bound to Subjects; ServiceAccounts are for Pods.]
answer-correct: Providing Pods with in-cluster identity [why: Enables Pods to authenticate with the API server.]
answer: Managing network policies [why: NetworkPolicies define traffic rules, not access credentials.]
answer: Storing environment variables [why: That’s done via ConfigMaps or Secrets.]
content:
  ServiceAccounts are automatically mounted into Pods to provide secure in-cluster authentication tokens.
<?/quiz?>

<?quiz?>
question: What does <code>kubectl logs</code> show?
answer-correct: Output from a container running in a Pod [why: Displays standard output and error logs for debugging.]
answer: Event history for a Pod [why: <code>kubectl describe pod</code> shows events.]
answer: Node system logs [why: Node logs are external to <code>kubectl logs</code>.]
answer: Resource usage metrics [why: Use <code>kubectl top</code> for metrics.]
content:
  <code>kubectl logs</code> retrieves container logs directly from the Kubernetes API.
<?/quiz?>

<?quiz?>
question: Which command runs a temporary Pod for debugging?
answer: <code>kubectl logs</code> [why: Shows logs but doesn’t create Pods.]
answer-correct: <code>kubectl run -it --rm</code> [why: Creates an interactive Pod that deletes itself afterward.]
answer: <code>kubectl debug node</code> [why: Used to debug node issues, not ephemeral Pods.]
answer: <code>kubectl exec -it</code> [why: Executes into existing Pods, doesn’t create new ones.]
content:
  <code>kubectl run -it --rm</code> launches a throwaway interactive container useful for quick debugging.
<?/quiz?>

<?quiz?>
question: Which command allows you to execute a command inside a running Pod?
answer-correct: <code>kubectl exec -it pod-name -- command</code> [why: Executes an interactive shell or command inside an existing container.]
answer: <code>kubectl run</code> [why: Creates a new Pod; does not exec into an existing one.]
answer: <code>kubectl attach</code> [why: Attaches to output of the main process; doesn’t start a new command.]
answer: <code>kubectl connect</code> [why: Not a valid kubectl subcommand.]
content:
  <code>kubectl exec</code> is used to run commands inside containers for debugging or manual inspection.
<?/quiz?>

<?quiz?>
question: What is the role of the kubelet?
answer-correct: Ensures containers described in PodSpecs are running [why: It monitors Pods on its node and reports status to the API server.]
answer: Assigns Pods to nodes [why: That’s the scheduler’s job.]
answer: Stores cluster state [why: etcd stores state, not the kubelet.]
answer: Controls networking between nodes [why: Managed by CNI plugins, not kubelet.]
content:
  The kubelet is the node agent that makes sure containers are healthy and running as expected.
<?/quiz?>

<?quiz?>
question: Which component stores the cluster’s configuration and state?
answer: kube-scheduler [why: Handles scheduling, not persistent storage.]
answer-correct: etcd [why: Serves as the distributed key-value store backing all cluster data.]
answer: kubelet [why: Manages Pods on nodes, not cluster state.]
answer: API server [why: Fronts the control plane but persists state in etcd.]
content:
  etcd stores all configuration and state data that define the cluster’s desired and current state.
<?/quiz?>

<?quiz?>
question: Which command lists available contexts in your kubeconfig?
answer: <code>kubectl get contexts</code> [why: Not a valid subcommand; use config view or get-contexts.]
answer-correct: <code>kubectl config get-contexts</code> [why: Lists contexts with cluster, user, and namespace info.]
answer: <code>kubectl show-contexts</code> [why: Doesn’t exist.]
answer: <code>kubectl config list</code> [why: Not a valid config verb.]
content:
  <code>kubectl config get-contexts</code> shows all contexts defined in your kubeconfig file.
<?/quiz?>

<?quiz?>
question: Which type of Service exposes an application on a static IP outside the cluster?
answer: ClusterIP [why: Exposes only internally within the cluster.]
answer: NodePort [why: Exposes on each node’s port, not a stable external IP.]
answer-correct: LoadBalancer [why: Provisions an external IP via the cloud provider for external access.]
answer: ExternalName [why: Maps a DNS name to an external service, not a load balancer IP.]
content:
  LoadBalancer Services integrate with cloud provider APIs to expose apps externally with stable IPs.
<?/quiz?>

<?quiz?>
question: Which Kubernetes object defines access rules within a namespace?
answer-correct: Role [why: Grants permissions to resources within a single namespace.]
answer: ClusterRole [why: Applies cluster-wide, not limited to a namespace.]
answer: ServiceAccount [why: Represents an identity, not permissions.]
answer: ConfigMap [why: Stores configuration data, not permissions.]
content:
  Roles specify allowed actions on resources within a namespace, paired with RoleBindings.
<?/quiz?>

<?quiz?>
question: What is the difference between a Role and a ClusterRole?
answer: Role is cluster-wide [why: False; Role is namespace-scoped.]
answer: ClusterRole is namespace-scoped [why: Incorrect; it’s cluster-scoped.]
answer-correct: Role applies to one namespace, ClusterRole applies cluster-wide [why: That’s the correct scope distinction.]
answer: They are identical [why: They differ in their scope and where they’re bound.]
content:
  ClusterRoles grant permissions across all namespaces; Roles are confined to a single namespace.
<?/quiz?>

<?quiz?>
question: What does a ConfigMap store?
answer-correct: Non-sensitive key-value configuration data [why: Used for environment variables, config files, and command arguments.]
answer: Secrets [why: Secrets store sensitive data separately.]
answer: Pod logs [why: Logs are transient output, not configuration.]
answer: Node metrics [why: Metrics are runtime data, not configuration.]
content:
  ConfigMaps separate configuration from container images to improve portability.
<?/quiz?>

<?quiz?>
question: Which command deletes a resource?
answer: <code>kubectl stop</code> [why: Deprecated command; replaced by <code>delete</code>.]
answer-correct: <code>kubectl delete</code> [why: Removes resources specified by name, file, or label selector.]
answer: <code>kubectl remove</code> [why: Not a valid kubectl subcommand.]
answer: <code>kubectl clear</code> [why: Doesn’t exist; deletion handled by <code>delete</code>.]
content:
  <code>kubectl delete</code> cleanly removes resources, triggering appropriate cleanup controllers.
<?/quiz?>

<?quiz?>
question: Which controller manages the rollout and rollback of application versions?
answer-correct: Deployment [why: Automates rolling updates and version rollbacks using ReplicaSets.]
answer: ReplicaSet [why: Manages Pods but not version history.]
answer: StatefulSet [why: Focuses on ordered deployment with persistence.]
answer: DaemonSet [why: Ensures one Pod per node, not version control.]
content:
  Deployments abstract ReplicaSets to enable declarative versioned updates to applications.
<?/quiz?>

<?quiz?>
question: Which Kubernetes resource defines how Pods communicate externally via HTTP/HTTPS?
answer: Service [why: Provides stable internal networking but doesn’t manage HTTP routing.]
answer-correct: Ingress [why: Manages HTTP routing, SSL termination, and host/path-based rules.]
answer: ConfigMap [why: Used for configuration, not networking routes.]
answer: Role [why: Manages permissions, not traffic.]
content:
  Ingress controllers handle inbound HTTP/S traffic routing to Services inside the cluster.
<?/quiz?>

<?quiz?>
question: What does the <code>kubectl top</code> command display?
answer-correct: CPU and memory usage for Pods or nodes [why: Uses Metrics Server to show resource utilization.]
answer: Disk usage [why: Kubernetes doesn’t report disk stats with <code>top</code>.]
answer: Events [why: Use <code>kubectl get events</code> for that.]
answer: Logs [why: Use <code>kubectl logs</code> instead.]
content:
  <code>kubectl top</code> helps monitor resource consumption for capacity planning and performance debugging.
<?/quiz?>

<?quiz?>
question: Which resource defines persistent storage in Kubernetes?
answer-correct: PersistentVolume [why: Abstracts storage backend and provides lifecycle-managed storage resources.]
answer: ConfigMap [why: Stores configuration, not storage.]
answer: Pod [why: Consumes storage, doesn’t define it.]
answer: Service [why: Provides networking, not storage.]
content:
  PersistentVolumes decouple storage provisioning from Pods, allowing reuse across workloads.
<?/quiz?>

<?quiz?>
question: Which resource requests specific storage for a Pod?
answer: PersistentVolume [why: Defines storage supply, not demand.]
answer-correct: PersistentVolumeClaim [why: Represents a request for storage by a Pod.]
answer: StorageClass [why: Defines dynamic provisioning behavior, not the claim itself.]
answer: Secret [why: Stores credentials, not storage requests.]
content:
  PersistentVolumeClaims abstract how Pods request storage independently from the underlying infrastructure.
<?/quiz?>

<?quiz?>
question: What is a StatefulSet primarily used for?
answer-correct: Managing stateful applications needing stable identity [why: Provides predictable names and persistent volumes per Pod.]
answer: Stateless workloads [why: Use Deployments for that.]
answer: Batch jobs [why: Use Jobs or CronJobs for that purpose.]
answer: Node agents [why: DaemonSets run node-level agents.]
content:
  StatefulSets guarantee stable Pod names and persistent storage for databases and stateful workloads.
<?/quiz?>

<?quiz?>
question: What does a Kubernetes Taint do?
answer-correct: Prevents Pods from being scheduled unless tolerated [why: It marks nodes to repel certain Pods unless a matching Toleration exists.]
answer: Forces Pods onto a node [why: That’s an Affinity rule, not a Taint.]
answer: Deletes unresponsive nodes [why: Node controller handles that, not Taints.]
answer: Changes Pod priority [why: PriorityClasses handle scheduling priority.]
content:
  Taints and Tolerations work together to control which Pods can be scheduled on specific nodes.
<?/quiz?>

<?quiz?>
question: Which concept defines Pod scheduling preference rather than enforcement?
answer: Taint [why: Prevents scheduling unless tolerated.]
answer-correct: Node Affinity (preferredDuringSchedulingIgnoredDuringExecution) [why: Expresses soft scheduling preferences that the scheduler tries to honor.]
answer: Toleration [why: Allows Pods onto tainted nodes but doesn’t express preference.]
answer: Selector [why: Filters resources, doesn’t define preference strength.]
content:
  Preferred affinities allow gentle steering of Pods toward specific nodes without hard enforcement.
<?/quiz?>

<?quiz?>
question: Which command upgrades a running Deployment to a new image?
answer-correct: <code>kubectl set image deployment/myapp mycontainer=newimage:tag</code> [why: Updates the container image field in the Deployment.]
answer: <code>kubectl rollout undo</code> [why: Rolls back to a previous version, not upgrade.]
answer: <code>kubectl apply -f pod.yaml</code> [why: Creates or updates individual Pods; not used for Deployment rolling updates.]
answer: <code>kubectl edit node</code> [why: Modifies node config, not workloads.]
content:
  Use <code>kubectl set image</code> to trigger a rolling update for Deployments.
<?/quiz?>

<?quiz?>
question: Which object ensures recurring job execution on a schedule?
answer: Job [why: Runs once to completion, not scheduled.]
answer-correct: CronJob [why: Wraps Jobs and schedules them using cron syntax.]
answer: Deployment [why: Maintains long-running Pods, not scheduled Jobs.]
answer: DaemonSet [why: Runs Pods per node, not per time schedule.]
content:
  CronJobs are ideal for periodic tasks like backups, cleanup, or reports.
<?/quiz?>

<?quiz?>
question: Which resource defines policies controlling network traffic between Pods?
answer: Role [why: Manages RBAC, not networking.]
answer-correct: NetworkPolicy [why: Specifies allowed ingress and egress traffic between Pods.]
answer: ConfigMap [why: Holds configuration, not firewall rules.]
answer: Ingress [why: Handles external traffic, not Pod-to-Pod security.]
content:
  NetworkPolicies enable fine-grained network segmentation and zero-trust design inside clusters.
<?/quiz?>

<?quiz?>
question: What is the function of an Admission Controller?
answer-correct: Intercepts API requests to enforce policies or mutate objects [why: Validates and modifies requests before persistence in etcd.]
answer: Schedules Pods [why: Scheduler handles placement, not admission.]
answer: Controls node networking [why: Not its function; CNI handles that.]
answer: Manages user authentication [why: Handled earlier by API server authentication chain.]
content:
  Admission Controllers enforce governance, security, and compliance at resource creation time.
<?/quiz?>

<?quiz?>
question: What does <code>kubectl rollout undo</code> do?
answer-correct: Reverts a Deployment to its previous revision [why: It rolls back to the last successful ReplicaSet version.]
answer: Deletes the Deployment [why: That’s <code>kubectl delete</code>.]
answer: Pauses a rollout [why: <code>kubectl rollout pause</code> handles that.]
answer: Shows rollout status [why: <code>kubectl rollout status</code> reports progress.]
content:
  Rollback restores a Deployment’s prior configuration, useful after a bad release.
<?/quiz?>

<?quiz?>
question: Which field in a Pod manifest specifies resource limits?
answer-correct: <code>resources.limits</code> [why: Defines maximum CPU/memory usage per container.]
answer: <code>spec.replicas</code> [why: Used in Deployments, not Pods.]
answer: <code>spec.containers.env</code> [why: Defines environment variables, not resources.]
answer: <code>spec.volumes</code> [why: Defines volumes, not resource constraints.]
content:
  Resource limits prevent any single container from consuming excessive CPU or memory.
<?/quiz?>

<?quiz?>
question: Which command shows all API versions supported by the cluster?
answer-correct: <code>kubectl api-versions</code> [why: Lists API groups and versions exposed by the API server.]
answer: <code>kubectl get versions</code> [why: Not a valid subcommand.]
answer: <code>kubectl version</code> [why: Shows client/server version info, not API groups.]
answer: <code>kubectl get api</code> [why: Invalid subcommand.]
content:
  <code>kubectl api-versions</code> lists available API groups to verify supported resource versions.
<?/quiz?>

<?quiz?>
question: Which resource defines storage provisioning templates?
answer-correct: StorageClass [why: Describes how volumes are dynamically provisioned and reclaimed.]
answer: PersistentVolumeClaim [why: Requests storage, doesn’t define how to create it.]
answer: Secret [why: Stores sensitive data, not storage settings.]
answer: Pod [why: Consumes storage but doesn’t define storage classes.]
content:
  StorageClasses enable dynamic storage provisioning and abstract backend details like disk type or performance.
<?/quiz?>

<?quiz?>
question: What is the function of kube-proxy?
answer-correct: Manages virtual networking and Service IP routing on nodes [why: Maintains iptables/ipvs rules for Services.]
answer: Schedules Pods [why: The scheduler does that.]
answer: Stores cluster config [why: etcd holds cluster state.]
answer: Controls container runtime [why: kubelet interfaces with the runtime, not kube-proxy.]
content:
  kube-proxy maintains network rules so Services and Pods can communicate reliably.
<?/quiz?>

<?quiz?>
question: What is a Pod Security Policy (PSP)?
answer-correct: A deprecated policy for defining allowed security contexts [why: PSP restricted Pod privilege levels and was replaced by Pod Security Standards.]
answer: A NetworkPolicy type [why: NetworkPolicy controls traffic, not security contexts.]
answer: A RoleBinding [why: RBAC manages permissions, not security posture.]
answer: An Admission Controller plugin [why: PSPs were enforced via admission, but not identical.]
content:
  PSPs controlled Pod-level security but are deprecated in favor of PodSecurity admission controls.
<?/quiz?>

<?quiz?>
question: Which Kubernetes feature limits resource consumption per namespace?
answer-correct: ResourceQuota [why: Defines maximum CPU, memory, and object counts per namespace.]
answer: LimitRange [why: Sets per-Pod or per-container min/max, not namespace-wide totals.]
answer: NetworkPolicy [why: Controls traffic, not resources.]
answer: Role [why: Manages permissions, not resource usage.]
content:
  ResourceQuotas ensure fair resource distribution and prevent namespace overconsumption.
<?/quiz?>

<?quiz?>
question: Which command displays running controllers and their versions?
answer-correct: <code>kubectl get deployment -n kube-system</code> [why: Shows controllers running as Deployments in the system namespace.]
answer: <code>kubectl controllers</code> [why: Invalid subcommand.]
answer: <code>kubectl describe nodes</code> [why: Describes nodes, not controllers.]
answer: <code>kubectl get pods</code> [why: Shows Pods but not specifically controllers.]
content:
  System controllers often run as Deployments inside the <code>kube-system</code> namespace.
<?/quiz?>

<?quiz?>
question: Which scheduling concept prevents Pods with specific labels from sharing the same node?
answer-correct: Pod Anti-Affinity [why: Ensures Pods with matching labels avoid co-location on a single node.]
answer: Taint [why: Repels Pods globally, not label-based co-location.]
answer: NodeSelector [why: Forces placement on matching nodes but doesn’t separate Pods.]
answer: Toleration [why: Lets Pods tolerate taints; doesn’t enforce anti-placement.]
content:
  Pod Anti-Affinity helps distribute workloads for redundancy and high availability.
<?/quiz?>

<?quiz?>
question: Which Kubernetes command displays current cluster context?
answer-correct: <code>kubectl config current-context</code> [why: Prints the active context name from kubeconfig.]
answer: <code>kubectl show context</code> [why: Not a valid subcommand.]
answer: <code>kubectl get-context</code> [why: Missing the correct prefix (<code>config</code>).]
answer: <code>kubectl use-context</code> [why: Switches context; doesn’t display it.]
content:
  Contexts represent combinations of cluster, user, and namespace in the kubeconfig file.
<?/quiz?>

<?quiz?>
question: Which field defines the restart behavior for failed containers?
answer-correct: <code>restartPolicy</code> [why: Controls whether a container restarts on failure; valid values: Always, OnFailure, Never.]
answer: <code>livenessProbe</code> [why: Detects failure but doesn’t control restart policy directly.]
answer: <code>readinessProbe</code> [why: Determines traffic eligibility, not restarts.]
answer: <code>backoffLimit</code> [why: Used by Jobs, not general Pods.]
content:
  <code>restartPolicy</code> dictates how Kubernetes handles container restarts within a Pod.
<?/quiz?>
