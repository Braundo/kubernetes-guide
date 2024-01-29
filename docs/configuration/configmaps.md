## What is a ConfigMap?
A ConfigMap is an API object in Kubernetes used to store non-confidential data in key-value pairs. It allows you to decouple environment-specific configuration from your container images, making your applications easily portable.


## Motivation
The primary use case for ConfigMaps is to separate configuration data from application code. For example, you might have an environment variable named `DATABASE_HOST` that varies between your local development environment and the cloud. By using a ConfigMap, you can manage these settings independently of the container images and the application code.


## ConfigMap Object
A ConfigMap object has `data` and `binaryData` fields, which accept key-value pairs. The `data` field is designed for UTF-8 strings, while `binaryData` is for base64-encoded strings. Starting from Kubernetes v1.19, you can make a ConfigMap immutable by adding an `immutable` field to its definition.


## ConfigMaps and Pods
You can refer to a ConfigMap in a Pod spec to configure the container(s) based on the data in the ConfigMap. There are four ways to use a ConfigMap in a Pod:  
1. Inside a container command and args
2. As environment variables for a container
3. As a read-only volume for the application to read
4. By writing code that uses the Kubernetes API to read the ConfigMap



## Using ConfigMaps
ConfigMaps can be mounted as data volumes or used by other parts of the system for configuration. You can specify which keys to include and the paths where they should be mounted when defining a Pod that uses a ConfigMap.


## Immutable ConfigMaps
From Kubernetes v1.21, you can set ConfigMaps as immutable, which prevents accidental or unwanted updates and reduces the load on the `kube-apiserver`.
