---
icon: material/database-lock
---
## Background
Alongside the ability to store and retrieve data, another key capability for applications is the ability to be configured or instantiated via environment variables or commands.  

In the traditional monolithic application days, environment variables and configurations were bundled up with the application and deployed as one large object. However, in the cloud-native application model it's important to decouple these for many reasons:  

1. **Environment Flexibility**: Decoupling allows the same application to run across different environments (development, staging, production) without code changes. Environment-specific configurations can be applied externally, improving the portability of the application.
1. **Scalability and Dynamic Management**: When configuration is externalized, it's easier to scale applications horizontally since the configuration can be managed and applied independently. This allows for dynamic reconfiguration in response to changes in load or other factors without redeploying or restarting containers.
1. **Security and Sensitive Data Handling**: Keeping sensitive configuration data, such as secrets and credentials, separate from the application codebase helps maintain security. It ensures that sensitive data is not exposed within the code and can be securely managed using secrets management tools.
1. **Continuous Deployment and Rollbacks**: Decoupling facilitates continuous deployment practices by allowing configurations to be updated independently of the application. This separation also simplifies rollback procedures in case a configuration change needs to be reverted without affecting the application version that's running.
1. **Maintainability and Clarity**: Keeping configuration separate from application code helps maintain a clean codebase and makes it clearer for developers to understand the application logic. It avoids cluttering the application with environment-specific conditionals and settings, making the code easier to maintain and evolve.  

Let's take a look at an example from point #1 there. Imagine you have an application that runs in 3 different environments: `dev`, `perf`, and `prod`. Each environment has different configurations such as credentials, network policies, security policies, etc. In the old world, if you were to package those configurations with the application, you'd end up with three separate images stored in three separate repositories. Any time a developer needs to make an update to the application, they must ensure they update it across all three repos, rebuild all three images, and redeploy all three images.

``` mermaid
flowchart LR
    subgraph app repos
        dev[(<b>dev</b><br><tt>- dev credentials<br>- dev network policy<br>- dev security policy)]
        perf[(<b>perf</b><br><tt>- perf credentials<br>- perf network policy<br>- perf security policy)]
        prod[(<b>prod</b><br><tt>- prod credentials<br>- prod network policy<br>- prod security policy)]
    end
    subgraph app images
        dev2[<b>dev image]
        perf2[<b>perf image]
        prod2[<b>prod image]
    end
    subgraph environments
        dev3[<b>dev]
        perf3[<b>perf]
        prod3[<b>prod]
    end
    dev -->|builds| dev2
    perf -->|builds| perf2
    prod -->|builds| prod2
    dev2 -->|deployed| dev3
    perf2 -->|deployed| perf3
    prod2 -->|deployed| prod3
```

A better way to handle this is by decoupling those configuration values from your application. You build and maintain a single application repository and build & run that single image in all environments. For this to be possible, your applications should be built as plain as possible with as little configuration necessary embedded. The configurations for each environment are then stored separately and applied to the various environments at runtime.  

In this manner, application code is updated in *one* repository, *one* image is used, and configurations are independently managed.

``` mermaid
flowchart LR
    subgraph app repo
        app[(<b>app source code</b>)]
    end
    subgraph app image
        app2[<b>app image]
    end
    subgraph environments
        dev[<b>dev]
        perf[<b>perf]
        prod[<b>prod]
    end
    subgraph ConfigMaps
    dev1[("dev CM")]
    perf1[("perf CM")]
    prod1[("prod CM")]
    end
    app -->|builds| app2
    app2 -->|apply config| dev1
    app2 -->|apply config| perf1
    app2 -->|apply config| prod1
    dev1 --> |deployed| dev
    perf1 --> |deployed| perf
    prod1 --> |deployed| prod
```

## ConfigMaps
Kubernetes allows this to happen through the use of a **ConfigMap (CM)**. ConfigMaps are used to store non-sensitive information and configuration data such as:  

1. Hostnames
1. Server configurations
1. Database configurations
1. Account names
1. Environment variables

!!! warning "You should not use ConfigMaps to store sensitive data such as passwords. Secrets should be used for that purpose."  

Under the covers, ConfigMaps are effectively key-value pairs. **Keys** are completely arbitrary and can be any name created from letters, numbers, underscores, dashes, and dots. **Values** can contain anything. As with many other key-value paradigms, they are separated by a colon (`key`:`value`). 

As mentioned above, a (simple) database configuration might look something like this in a ConfigMap definition:

``` yaml
hostname: mysql-dev-01
db-port: 3306
username: vinny
```

Data stored in ConfigMaps can be injected into a container in a number of ways:  

1. As environment variable(s)
1. Arguments in the container's startup command
1. As files in a volume

These methods are all transparent to the application - it has no idea the ConfigMap is even a thing, it just knows it's data is where it's supposed to be. How it got there is an irrelevant mystery.

#### Environment Variables
To inject data as environment variables, you created a ConfigMap and map its entries to environment variables inside of the Pod spec template. Once the Pod and underlying container start, the environment variables will appear as standard environment variables for the OS relevant to that container.  

Here's how that might look when injecting some database information into a container using a ConfigMap called `myCM`:  

`myCM`:
``` yaml
## rest of file omitted for simplicity
data:
  database: mysql-01
  loc: STL
  user: vinny
```

**Pod definition**:
``` yaml
spec:
  containers:
  ...
    env:
      - name: host
      valueFrom:
        configMapKeyRef:
          name: myCM
          key: database
      - name: location
      valueFrom:
        configMapKeyRef:
          name: myCM
          key: loc
      - name: user
      valueFrom:
        configMapKeyRef:
          name: myCM
          key: user
```

With these configs, this is what the mapping from <span style="color: red;">ConfigMap</span> to <span style="color: orange;">container</span> variables would look like:  

- <span style="color: red;">database</span> :material-arrow-left-right: <span style="color: orange;">host</span>
- <span style="color: red;">loc</span> :material-arrow-left-right: <span style="color: orange;">location</span>
- <span style="color: red;">user</span> :material-arrow-left-right: <span style="color: orange;">user</span>  

If you were to login interactively to the container, you would be able to seamlessly view these environment variables:  

``` shell
$ echo $host
mysql-01

$ echo $location
STL

$ echo $user
vinny
```

#### Container Startup Commands
This method of injecting data into containers from ConfigMaps is pretty straightforward. In your Pod template YAML, you specify a startup command and insert variables defined from your ConfigMap. Below is an example of inserting the database hostname from above into a startup command for the container. Here is how the Pod YAML might look:

``` yaml
# other sections omitted for simplicity
spec:
  containers:
  - name: my-container-1
    image: busybox
    command: ["/bin/sh", "-c", "echo Database to use is $(host)"]
    env:
      - name: host
        valueFrom:
          configMapKeyRef:
            name: myCM
            key: database
```

From this Pod definition, when the container starts it will run the following shell command that we defined:

``` shell
echo Database to use is $(host)
```

In our config, we mapped `host` to the `database` key in `myCM`, which we defined as having a value of `mysql-01`. Thus, when the container runs that command, it will produce the following output:

``` shell
Database to use is mysql-01
```

#### Volumes
The most flexible way to leverage ConfigMaps is with volumes. By using them with volumes you can reference entire configuration files and make live updates to them which will be reflected in *running* containers. The entire process can be summed up in the following steps:

1. Create a ConfigMap
1. Create a ConfigMap volume in your Pod spec
1. Mount the ConfigMap volume into the container

``` mermaid
flowchart LR
    subgraph ConfigMap
        cm1[<tt>central = STL]
        cm2[<tt>west = SF]
    end

    subgraph Pod
        cmv[(ConfigMap<br>vol)]
        subgraph container
        fs["<b>/etc/regions</b><br><tt>-- central<br>-- west"]
        end
    end
ConfigMap --> cmv
cmv --> fs
```

Here's an example YAML file that would create a Pod called `configMapVol`, a volume called `volMap`, and mounts the `volMap` volume to `/etc/regions`:  

``` yaml
apiVersion: v1
kind: Pod
metadata:
  name: configMapVol
spec:
  volumes:
    - name: volMap
      configMap:
        name: my-cm
  containers:
    - name: container1
      image: busybox
      volumeMounts:
        - name: volMap
          mountPath: /etc/regions
```

If you were to deploy this Pod and exec into it, you could run an `ls` command to view the files we defined in the ConfigMap diagram above mounted at `/etc/regions`:  

``` shell
$ kubectl exec configMapVol -- ls /etc/regions
central
west
```

## Secrets
Secrets are extremely similar in shape and function to ConfigMaps in that they hold configuration data that can be injected into containers at run-time. However, Secrets differ in the fact that they base-64 encode values and are made for storing sensitive data such as tokens, certificates, and passwords.

!!! warning "These values are not encrypted by default and can easily be decoded."  

A standard flow for implementing secrets looks like this:  

``` mermaid
flowchart TD
    A[Create Secret and persist to cluster store - unencrypted] --> B[Pod is configured to use Secret]
    B --> C[Secret data is transferred - unencrypted - to the node]
    C --> D[Node kubelet starts the Pod and its containers]
    D --> E[Secret is mounted into the container's temp filesystem and decoded into plain text]
    E --> F[Application consumes Secret]
    F --> G[Secret is deleted from the node once the Pod is deleted]
```
Additionally here is an example of how a YAML file might look for creating a Secret:

``` yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
data:
  password: UGFzc3dvcmQxMjM=
  user: dmlubnk=

# rest of file omitted for simplicity
```

And here's an example of how to define a Pod and use the Secret as a volume:  

``` yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  volumes:
  - name: secret-vol
    secret: 
      secretName: my-secret
  containers:
  - name: my-container
    image: busybox
    volumeMounts:
    - name: secret-vol
      mountPath: /etc/secrets/
```

!!! info "Secrets are mounted as read-only objects in the containers to prevent accidental manipulation."