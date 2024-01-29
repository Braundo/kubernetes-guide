## Kubeconfig Files
Kubeconfig files are used to store information about clusters, users, namespaces, and authentication mechanisms. The `kubectl` command-line tool relies on these files to interact with the cluster. By default, `kubectl` looks for a file named `config` in the `$HOME/.kube` directory. You can specify other kubeconfig files by setting the `KUBECONFIG` environment variable or using the `--kubeconfig` flag.


## Supporting Multiple Clusters, Users, and Authentication Mechanisms
If you have multiple clusters and various authentication methods, kubeconfig files help you manage them. For instance:  
- A running kubelet might use certificates for authentication.
- A user might use tokens.
- Administrators might provide sets of certificates to individual users.



## Context
In a kubeconfig file, a context is used to group access parameters under a name. Each context has three parameters: cluster, namespace, and user. The `kubectl` tool uses parameters from the current context by default. You can switch contexts using the `kubectl config use-context` command.


## The KUBECONFIG Environment Variable
This variable holds a list of kubeconfig files. On Linux and Mac, the list is colon-delimited, while on Windows, it's semicolon-delimited. If the variable doesn't exist, the default kubeconfig file `$HOME/.kube/config` is used. If it does exist, `kubectl` merges the files listed in the variable.


## Merging Kubeconfig Files
`kubectl` follows specific rules when merging kubeconfig files:  
- If the `-kubeconfig` flag is set, only that file is used.
- If the `KUBECONFIG` variable is set, the files listed are merged.
- The first file to set a value wins, and conflicting entries are ignored.



## File References
Paths in a kubeconfig file are relative to the location of the kubeconfig file itself. On the command line, they are relative to the current working directory.


## Proxy Configuration
You can configure `kubectl` to use a proxy for each cluster by setting `proxy-url` in the kubeconfig file.
