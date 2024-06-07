---
icon: material/lock-outline
---

# Managing Configuration and Secrets in Kubernetes

Modern applications require dynamic configuration management and secure handling of sensitive data. Kubernetes offers ConfigMaps and Secrets to handle these requirements efficiently, allowing you to decouple configuration from application code and manage sensitive information securely.

## Introduction

In the traditional monolithic application days, environment variables and configurations were bundled up with the application and deployed as one large object. However, in the cloud-native application model it's important to decouple these for many reasons:  

1. **Environment Flexibility**: Decoupling allows the same application to run across different environments (development, staging, production) without code changes. Environment-specific configurations can be applied externally, improving the portability of the application.
2. **Scalability and Dynamic Management**: When configuration is externalized, it's easier to scale applications horizontally since the configuration can be managed and applied independently. This allows for dynamic reconfiguration in response to changes in load or other factors without redeploying or restarting containers.
3. **Security and Sensitive Data Handling**: Keeping sensitive configuration data, such as secrets and credentials, separate from the application codebase helps maintain security. It ensures that sensitive data is not exposed within the code and can be securely managed using secrets management tools.
4. **Continuous Deployment and Rollbacks**: Decoupling facilitates continuous deployment practices by allowing configurations to be updated independently of the application. This separation also simplifies rollback procedures in case a configuration change needs to be reverted without affecting the application version that's running.
5. **Maintainability and Clarity**: Keeping configuration separate from application code helps maintain a clean codebase and makes it clearer for developers to understand the application logic. It avoids cluttering the application with environment-specific conditionals and settings, making the code easier to maintain and evolve.  

## Understanding ConfigMaps

<h3>What are ConfigMaps?</h3>

ConfigMaps store non-sensitive configuration data as key-value pairs. They are first-class objects in the Kubernetes API, making them stable and widely supported.

<h3>Use Cases for ConfigMaps</h3>

ConfigMaps are used to store:

- Environment variables
- Configuration files (e.g., web server configs)
- Hostnames
- Service ports
- Account names

Avoid storing sensitive data in ConfigMaps; use Secrets for that purpose.

<h3>Creating ConfigMaps</h3>

ConfigMaps can be created imperatively or declaratively.

<h4>Imperative Creation</h4>

Create a ConfigMap with literal values:
```sh
$ kubectl create configmap app-config --from-literal=env=prod --from-literal=debug=false
```

Create a ConfigMap from a file:
```sh
$ kubectl create configmap app-config --from-file=config.properties
```

<h4>Declarative Creation</h4>

Define a ConfigMap in a YAML file (`configmap.yaml`):
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  env: prod
  debug: "false"
```

Apply the YAML file:
```sh
$ kubectl apply -f configmap.yaml
```

<h3>Using ConfigMaps</h3>

Inject ConfigMap data into Pods using environment variables, command arguments, or volumes.

![](../images/cm-mapping-flow.svg)

<h4>As Environment Variables</h4>

Define environment variables in the Pod specification:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
    - name: app-container
      image: myapp:latest
      env:
        - name: ENV
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: env
        - name: DEBUG
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: debug
```

<h4>As Volumes</h4>

Mount the ConfigMap as a volume:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  volumes:
    - name: config-volume
      configMap:
        name: app-config
  containers:
    - name: app-container
      image: myapp:latest
      volumeMounts:
        - name: config-volume
          mountPath: /etc/config
```

<h3>Kubernetes-Native Applications</h3>

Kubernetes-native applications can access ConfigMap data directly via the API server, simplifying configuration management and reducing dependencies on environment variables or volumes.

## Understanding Secrets

<h3>What are Secrets?</h3>

Secrets store sensitive data such as passwords, tokens, and certificates. They are similar to ConfigMaps but are designed to handle sensitive information securely.

<h3>Are Kubernetes Secrets Secure?</h3>

By default, Kubernetes Secrets are not encrypted in the cluster store or in transit. They are base64-encoded, which is not secure. To enhance security, use additional tools like HashiCorp Vault for better encryption.

<h3>Creating Secrets</h3>

Secrets can also be created imperatively or declaratively.

<h4>Imperative Creation</h4>

Create a Secret with literal values:
```sh
$ kubectl create secret generic db-credentials --from-literal=username=dbuser --from-literal=password=securepass
```

<h4>Declarative Creation</h4>

Define a Secret in a YAML file (`secret.yaml`):
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
data:
  username: ZGJ1c2Vy
  password: c2VjdXJlcGFzcw==
```

Apply the YAML file:
```sh
$ kubectl apply -f secret.yaml
```

<h3>Using Secrets</h3>

Inject Secret data into Pods using environment variables, command arguments, or volumes.

<h4>As Volumes</h4>

Mount the Secret as a volume:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  volumes:
    - name: secret-volume
      secret:
        secretName: db-credentials
  containers:
    - name: app-container
      image: myapp:latest
      volumeMounts:
        - name: secret-volume
          mountPath: /etc/secret
```

## Hands-On Examples

<h3>Example ConfigMap</h3>

Create a ConfigMap with configuration data:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: example-config
data:
  APP_ENV: "production"
  APP_DEBUG: "false"
```

Deploy and inspect the ConfigMap:
```sh
$ kubectl apply -f example-config.yaml
$ kubectl describe configmap example-config
```

<h3>Example Secret</h3>

Create a Secret with sensitive data:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: ZGJ1c2Vy
  password: c2VjdXJlcGFzcw==
```

Deploy and inspect the Secret:
```sh
$ kubectl apply -f db-secret.yaml
$ kubectl describe secret db-secret
```

## Summary

ConfigMaps and Secrets are essential tools in Kubernetes for managing application configuration and sensitive data. By decoupling configuration from application code and handling sensitive information securely, you can create more flexible, maintainable, and secure applications.