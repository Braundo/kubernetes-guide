---
hide:
  - navigation
---

<?quiz?>
question: Which command lists all Pods in the current namespace?
answer-correct: <code>kubectl get pods</code>
answer: <code>kubectl list pods</code>
answer: <code>kubectl pods</code>
answer: <code>kubectl ps</code>
content:
<?/quiz?>

<?quiz?>
question: What is the smallest deployable unit in Kubernetes?
answer-correct: Pod
answer: Container
answer: Deployment
answer: Job
content:
<?/quiz?>

<?quiz?>
question: Which file format is most commonly used for Kubernetes manifests?
answer-correct: YAML
answer: JSON
answer: INI
answer: TOML
content:
<?/quiz?>

<?quiz?>
question: Which object manages stateless replicas and rolling updates?
answer-correct: Deployment
answer: StatefulSet
answer: DaemonSet
answer: Service
content:
<?/quiz?>

<?quiz?>
question: Which component runs on every node and manages containers?
answer-correct: kubelet
answer: kube-proxy
answer: scheduler
answer: etcd
content:
<?/quiz?>

<?quiz?>
question: What is etcd’s primary role in Kubernetes?
answer-correct: Store cluster state and configuration
answer: Balance network traffic
answer: Run Pods on nodes
answer: Provide container runtime
content:
<?/quiz?>

<?quiz?>
question: Which object exposes a set of Pods as a stable network endpoint?
answer-correct: Service
answer: Ingress
answer: EndpointSlice
answer: NetworkPolicy
content:
<?/quiz?>

<?quiz?>
question: The default Service type is…
answer-correct: ClusterIP
answer: NodePort
answer: LoadBalancer
answer: ExternalName
content:
<?/quiz?>

<?quiz?>
question: Which command shows detailed info about a specific Pod?
answer-correct: <code>kubectl describe pod <name></code>
answer: <code>kubectl info pod <name></code>
answer: <code>kubectl details pod <name></code>
answer: <code>kubectl show pod <name></code>
content:
<?/quiz?>

<?quiz?>
question: What does a ConfigMap store?
answer-correct: Non-sensitive configuration data
answer: TLS private keys
answer: Container images
answer: Node credentials
content:
<?/quiz?>

<?quiz?>
question: Which object should store passwords or API keys?
answer-correct: Secret
answer: ConfigMap
answer: ServiceAccount
answer: Role
content:
<?/quiz?>

<?quiz?>
question: A DaemonSet ensures that a Pod…
answer-correct: Runs on every (or selected) node
answer: Has persistent storage
answer: Scales with CPU usage
answer: Can receive external traffic
content:
<?/quiz?>

<?quiz?>
question: A StatefulSet primarily provides…
answer-correct: Stable network IDs and ordered, persistent Pods
answer: Automatic image updates
answer: Node-level logging
answer: In-cluster DNS records
content:
<?/quiz?>

<?quiz?>
question: Which command applies a manifest file?
answer-correct: <code>kubectl apply -f file.yaml</code>
answer: <code>kubectl use file.yaml</code>
answer: <code>kubectl run file.yaml</code>
answer: <code>kubectl start -f file.yaml</code>
content:
<?/quiz?>

<?quiz?>
question: NodePort Services…
answer-correct: Expose the Service on the same port across all nodes
answer: Expose only within the cluster
answer: Require an Ingress controller
answer: Always allocate port 443
content:
<?/quiz?>

<?quiz?>
question: Which controller ensures a specified number of identical Pods are running?
answer-correct: ReplicaSet
answer: Job
answer: CronJob
answer: EndpointSlice
content:
<?/quiz?>

<?quiz?>
question: Which object provides HTTP routing and TLS termination at L7?
answer-correct: Ingress (with controller)
answer: Service ClusterIP
answer: Endpoint
answer: NodePort only
content:
<?/quiz?>

<?quiz?>
question: What does <code>kubectl logs</code> show?
answer-correct: Container logs from a Pod
answer: Node kernel logs
answer: API server audit logs
answer: etcd change log
content:
<?/quiz?>

<?quiz?>
question: The Kubernetes scheduler is responsible for…
answer-correct: Placing Pods on suitable nodes
answer: Creating ReplicaSets
answer: Upgrading the control plane
answer: Persisting cluster state
content:
<?/quiz?>

<?quiz?>
question: RoleBinding grants permissions…
answer-correct: To a subject within a specific namespace
answer: Cluster-wide to all users
answer: Only to nodes
answer: Only to ServiceAccounts in kube-system
content:
<?/quiz?>

<?quiz?>
question: ClusterRole vs. Role difference?
answer-correct: ClusterRole can apply cluster-wide; Role is namespace-scoped
answer: ClusterRole is for nodes only
answer: Role is immutable
answer: ClusterRole can only read resources
content:
<?/quiz?>

<?quiz?>
question: Taints on a node…
answer-correct: Repel Pods unless they tolerate the taint
answer: Force Pods to co-locate
answer: Expose node ports externally
answer: Remove labels from nodes
content:
<?/quiz?>

<?quiz?>
question: What’s the counterpart allowing Pods onto tainted nodes?
answer-correct: Tolerations
answer: Affinity
answer: Selectors
answer: Annotations
content:
<?/quiz?>

<?quiz?>
question: Node selectors on a Pod…
answer-correct: Constrain scheduling to nodes with matching labels
answer: Configure network ACLs
answer: Set resource limits
answer: Select Services by label
content:
<?/quiz?>

<?quiz?>
question: Pod anti-affinity does what?
answer-correct: Encourages Pods to avoid co-locating on the same node
answer: Forces Pods to run on the same node
answer: Blocks scheduling entirely
answer: Auto-scales Pods
content:
<?/quiz?>

<?quiz?>
question: Which probe determines if traffic should be sent to a container?
answer-correct: readinessProbe
answer: livenessProbe
answer: startupProbe
answer: healthProbe
content:
<?/quiz?>

<?quiz?>
question: Liveness vs Readiness - pick the best statement.
answer-correct: Liveness checks if the process is alive; Readiness gates traffic
answer: Both gate traffic only
answer: Readiness restarts the container
answer: Liveness exposes a Service
content:
<?/quiz?>

<?quiz?>
question: What is a Job used for?
answer-correct: Run Pods to completion (once or a set number)
answer: Maintain a fixed number of replicas
answer: Expose workloads externally
answer: Persist cluster config
content:
<?/quiz?>

<?quiz?>
question: CronJob adds which capability?
answer-correct: Time-based scheduling for Jobs
answer: Horizontal scaling
answer: Pod priority
answer: Blue/green deployment
content:
<?/quiz?>

<?quiz?>
question: What is a LimitRange?
answer-correct: Policy to set default/maximum resource requests & limits per object
answer: Node CPU hard cap
answer: Storage quota per namespace
answer: A Pod anti-affinity rule
content:
<?/quiz?>

<?quiz?>
question: ResourceQuota does what?
answer-correct: Caps aggregate resource consumption per namespace
answer: Enforces Pod security policies
answer: Manages node pool size
answer: Schedules critical Pods first
content:
<?/quiz?>

<?quiz?>
question: NetworkPolicy objects can restrict…
answer-correct: Ingress and egress traffic to/from Pods
answer: Service creation
answer: Node taints
answer: etcd access control lists
content:
<?/quiz?>

<?quiz?>
question: The kube-proxy component primarily…
answer-correct: Implements Service virtual IPs and simple load-balancing
answer: Schedules Pods
answer: Stores API objects
answer: Mounts volumes
content:
<?/quiz?>

<?quiz?>
question: A CustomResourceDefinition (CRD) allows you to…
answer-correct: Extend the Kubernetes API with new resource types
answer: Replace the API server
answer: Modify kubelet flags on nodes
answer: Create new namespaces automatically
content:
<?/quiz?>

<?quiz?>
question: An Admission Controller can…
answer-correct: Intercept/validate/mutate API requests before persistence
answer: Assign Pod IPs
answer: Balance traffic across Services
answer: Manage node OS upgrades
content:
<?/quiz?>

<?quiz?>
question: Which command shows current resource usage (metrics) for Pods?
answer-correct: <code>kubectl top pods</code>
answer: <code>kubectl htop</code>
answer: <code>kubectl metrics pods</code>
answer: <code>kubectl get metrics</code>
content:
<?/quiz?>

<?quiz?>
question: PersistentVolumeClaim (PVC) represents…
answer-correct: A user’s request for storage resources
answer: A node’s local disk
answer: A storage class driver
answer: A snapshot policy
content:
<?/quiz?>

<?quiz?>
question: A StorageClass is used to…
answer-correct: Dynamically provision volumes with parameters and reclaim policies
answer: Label nodes for storage
answer: Encrypt Secrets
answer: Expose storage via NodePort
content:
<?/quiz?>

<?quiz?>
question: What does imagePullPolicy: IfNotPresent do?
answer-correct: Pulls the image only if it’s not cached on the node
answer: Always pulls the image
answer: Never pulls the image
answer: Pulls once per namespace
content:
<?/quiz?>

<?quiz?>
question: PodDisruptionBudget (PDB) helps…
answer-correct: Limit voluntary disruptions to maintain minimum available Pods
answer: Limit CPU throttling
answer: Configure NetworkPolicy defaults
answer: Force node cordon during updates
content:
<?/quiz?>

<?quiz?>
question: What is kubeadm primarily used for?
answer-correct: Bootstrap/upgrade a secure Kubernetes cluster
answer: Package charts
answer: Provide CNI plugins
answer: Collect node logs
content:
<?/quiz?>

<?quiz?>
question: Which field ensures Pods start in a defined order in StatefulSets?
answer-correct: <code>podManagementPolicy</code> (OrderedReady)
answer: <code>runPolicy: Sequential</code>
answer: <code>startupProbe: serial</code>
answer: <code>initOrder: ascending</code>
content:
<?/quiz?>

<?quiz?>
question: Pod priority and preemption allow…
answer-correct: Higher-priority Pods to evict lower-priority ones during pressure
answer: Nodes to share CPU
answer: Services to gain public IPs automatically
answer: CRDs to load earlier
content:
<?/quiz?>

<?quiz?>
question: An Init Container runs…
answer-correct: Before app containers start, to perform setup tasks
answer: After all containers exit
answer: Only on the first node
answer: Concurrently with all containers
content:
<?/quiz?>

<?quiz?>
question: What does a Sidecar container commonly provide?
answer-correct: Auxiliary features like logging, proxying, or config reloading
answer: Storage provisioning
answer: Node health checks
answer: etcd clustering
content:
<?/quiz?>

<?quiz?>
question: EndpointSlice improves over Endpoints by…
answer-correct: Scaling better for large numbers of endpoints
answer: Encrypting all pod-to-pod traffic
answer: Replacing Services entirely
answer: Forcing sticky sessions
content:
<?/quiz?>

<?quiz?>
question: Which object defines fine-grained pod-to-pod DNS records?
answer-correct: Headless Service
answer: NodePort Service
answer: Ingress
answer: NetworkPolicy
content:
<?/quiz?>

<?quiz?>
question: Which <code>kubectl command lets you run a command inside a running container?
answer-correct: <code>kubectl exec -it <pod> -- <cmd></code>
answer: <code>kubectl run -it <pod> <cmd></code>
answer: <code>kubectl attach <cmd></code>
answer: <code>kubectl shell <pod></code>
content:
<?/quiz?>

<?quiz?>
question: What label key is commonly used by Services to select Pods?
answer-correct: <code>app or app.kubernetes.io/name</code>
answer: <code>podIP</code>
answer: <code>controller-revision-hash</code>
answer: <code>node-role.kubernetes.io/control-plane</code>
content:
<?/quiz?>

<?quiz?>
question: An IngressClass resource…
answer-correct: Selects which controller should implement a given Ingress
answer: Assigns public IPs to Services
answer: Creates TLS certificates
answer: Configures kube-proxy modes
content:
<?/quiz?>
