## Configuration Example
Here's an example configuration for collecting spans and logging them to standard output:

``` yaml
receivers:
  otlp:
    protocols:
      grpc:
exporters:
  logging:
    logLevel: debug
service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [logging]
```



## Component Traces
- **kube-apiserver traces**: The kube-apiserver generates spans for incoming HTTP requests and for outgoing requests to webhooks, etcd, and re-entrant requests. It propagates the W3C Trace Context with outgoing requests but does not make use of the trace context attached to incoming requests.
- **kubelet traces**: The kubelet's CRI interface and authenticated HTTP servers are instrumented to generate trace spans. The endpoint and sampling rate are configurable. Trace context propagation is also configured.



## Enabling Tracing in kube-apiserver
To enable tracing in the kube-apiserver, you can provide a tracing configuration file using the `--tracing-config-file=` flag.


## Enabling Tracing in the kubelet
To enable tracing in the kubelet, you can apply the tracing configuration. Here's an example snippet:

``` yaml
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
featureGates:
  KubeletTracing: true
tracing:
  samplingRatePerMillion: 100
```



## Stability and Performance Overhead
Tracing instrumentation is still under active development and may change in various ways. Also, exporting spans comes with a small performance overhead on the networking and CPU side.