---
icon: material/laptop
---

# Getting a Local Kubernetes Cluster

For most users, setting up a local Kubernetes cluster using Docker Desktop or KinD (Kubernetes in Docker) is the best option when learning. It's free and allows you to quickly and easily get your hands on and start playing with Kubernetes.

### Option 1: Docker Desktop

Docker Desktop is a straightforward way to get Docker, Kubernetes, and `kubectl` on your computer, along with a user-friendly interface for managing your cluster contexts.

**Steps to Set Up Docker Desktop:**

1. **Install Docker Desktop:**
   - Search for "Docker Desktop" online.
   - Download and run the installer for your operating system (Linux, Mac, or Windows).
   - Follow the installation prompts. For Windows users, install the WSL 2 subsystem when prompted.

2. **Enable Kubernetes in Docker Desktop:**
   - Click the Docker icon in your menu bar or system tray and go to Settings.
   - Select "Kubernetes" from the left navigation bar.
   - Check "Enable Kubernetes" and click "Apply & restart."
   - Wait a few minutes for Docker Desktop to pull the required images and start the cluster. The Kubernetes icon in the Docker Desktop window will turn green when the cluster is ready.

3. **Verify the Installation:**
   - Open a terminal and run the following commands to ensure Docker and kubectl are installed and working:
     ```sh
     $ docker --version
     $ kubectl version --client=true -o yaml
     ```
   - Ensure the cluster is running with:
     ```sh
     $ kubectl get nodes
     ```

### Option 2: KinD (Kubernetes in Docker)

KinD is an excellent tool for running local Kubernetes clusters using Docker containers. It’s lightweight, flexible, and ideal for development and testing. It's my tool of choice for local development/experimentation.

**Steps to Set Up KinD:**

**Install KinD:**

   - Follow the instructions on the [KinD GitHub page](https://kind.sigs.k8s.io/) to install KinD on your system.
   - For macOS users, you can simply run `brew install kind` to get up and running quickly.

**Create a KinD Cluster:**
     ```sh
     $ kind create cluster
     ```
**Verify your cluster is running:**
```sh
$ kubectl get nodes
```

## Working with kubectl
`kubectl` is the command-line tool used to interact with your Kubernetes clusters. It's essential for deploying applications, inspecting and managing cluster resources, and troubleshooting issues.

### Installation
If you've followed the steps to set up either Docker Desktop or KinD, you should already have kubectl installed. If not, you can install it separately:

Linux:

``` sh
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```
Mac:

``` sh
brew install kubectl
```

Windows:

Download the executable from the [official Kubernetes site](https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/) and add it to your system PATH.
