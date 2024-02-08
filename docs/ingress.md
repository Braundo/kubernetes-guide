---
icon: material/shuffle-variant
---

## Overview
**Ingress** aims to bridge the gap that exists with NodePort and LoadBalancer Services. NodePorts are great, but must use a high port number and require you to know the FQDN or IP address of your nodes. LoadBalancer Services don't require this, but they are limited to one internal Service per load-balancer. So, if you have 50 applications you need exposed to the interent, you'd need 50 of your cloud provider's load-balancers instantiated - which would probably be cost prohibitive in most cases.  

Ingresses come into play here by allowing multiple Services to be "fronted" by a single cloud load-balancer. To accomplish this, Ingress will use a single LoadBalancer Service and use host-based or path-based routing to send traffic to the appropriate underlying Service.  

``` mermaid
flowchart LR
    CLD[cloud] --> LBS
    LBS[<b>LoadBalancer<br>Service] --> ing1[<b>Ingress controller</b><br><br><i>- routing rules<br>- reading host &<br>path names]
    ing1 --> SVC1[<tt>svc a]
    ing1 --> SVC2[<tt>svc b]
    ing1 --> SVC3[<tt>svc c]
```

## Routing Examples

#### Host-based Routing
``` mermaid
flowchart LR
    CLD[client] --> |ham.foo.bar| LBS
    CLD[client] --> |eggs.foo.bar| LBS
    LBS[<b>LoadBalancer<br>Service] --> ing1[<b>Ingress controller]
    ing1 --> |ham.foo.bar|SVC1[<b>ham-svc]
    ing1 --> |eggs.foo.bar|SVC2[<b>eggs-svc]
```
<br/><br/><br/>
#### Path-based Routing
``` mermaid
flowchart LR
    CLD[client] --> |foo.bar/ham| LBS
    CLD[client] --> |foo.bar/eggs| LBS
    LBS[<b>LoadBalancer<br>Service] --> ing1[<b>Ingress controller]
    ing1 --> |foo.bar/ham|SVC1[<b>ham-svc]
    ing1 --> |foo.bar/eggs|SVC2[<b>eggs-svc]
```

## More Information
For a deeper dive into Ingress, refer to [the official Kubernetes documentation](https://kubernetes.io/docs/concepts/services-networking/ingress/).