## API-Initiated Evictions vs Regular Deletion
- **Regular Deletion**: When you delete a pod using `kubectl delete pod `, the pod is terminated immediately without any checks for ongoing processes or disruption budgets.
- **API-Initiated Evictions**: When you use the Eviction API, Kubernetes respects the `PodDisruptionBudget` and `terminationGracePeriodSeconds` settings, ensuring that the pod is terminated in a way that minimizes disruption to your application.



## Creating an Eviction Object
- To initiate an eviction, you create an Eviction object. This is similar to sending a `DELETE` request to the API server but with more control.
- The Eviction object specifies the pod to be evicted and can also include additional parameters like `deleteOptions`.



## Admission Checks
- When you request an eviction, the API server performs several checks to ensure that the eviction can proceed safely.
- **PodDisruptionBudget**: Checks if the eviction would violate any configured `PodDisruptionBudgets`.
- **Node Conditions**: Checks if the node on which the pod is running is in a condition to handle the eviction.
<br/>
Based on these checks, the API server may respond with:  
- `200 OK`: Eviction can proceed.
- `429 Too Many Requests`: Eviction cannot proceed due to `PodDisruptionBudget` violation.
- `500 Internal Server Error`: Eviction cannot proceed due to an internal error.



## Troubleshooting
- **Stuck Evictions**: Sometimes, you may find that evictions are not proceeding and are stuck returning 429 or 500 responses.
- **Abort or Pause**: You may need to abort or pause any automated operations that are causing the API server to be overwhelmed.
- **Direct Deletion**: As a last resort, you can directly delete the pod, but this is not recommended as it bypasses all safety checks.
