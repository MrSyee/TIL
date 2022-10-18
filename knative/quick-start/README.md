# Knative Quickstart

## Objective


## Working Environment
* HW: M1 Mac
* OS: macOS Monterey 12.6

## Prerequisite
This tutorial is written with:
- [Minikube](https://minikube.sigs.k8s.io/docs/start/) v1.26.1
- [Kubernetes CLI](https://kubernetes.io/docs/tasks/tools/) v1.25.0
- [Knative CLI](https://knative.dev/docs/getting-started/quickstart-install/#before-you-begin) v1.7.0


## Setup
### Install Knative CLI
```bash
brew install knative/client/kn
kn version
```
Output:
```
Version:      v20220823-local-6d86bf75
Build Date:   2022-08-23 20:27:36
Git Revision: 6d86bf75
Supported APIs:
* Serving
  - serving.knative.dev/v1 (knative-serving v0.34.0)
* Eventing
  - sources.knative.dev/v1 (knative-eventing v0.34.1)
  - eventing.knative.dev/v1 (knative-eventing v0.34.1)
```

### Install the Knative quickstart plugin
```bash
brew install knative-sandbox/kn-plugins/quickstart
```

## Run the Knative quickstart plugin
The quickstart plugin completes the following functions:

1. Checks if you have the selected Kubernetes instance installed
2. Creates a cluster called `knative`
3. Installs `Knative Serving` with Kourier as the default networking layer, and sslip.io as the DNS
4. Installs `Knative Eventing` and creates an in-memory Broker and Channel implementation

### Install Knative and create minikube cluster
You need to have a minimum of 3 CPUs and 3 GB of RAM available for the cluster to be created. The minikube cluster will be created with 6 GB of RAM.
```bash
kn quickstart minikube
minikube profile list
```
Run the following command to start the process in a secondary terminal window, then return to the primary window and press enter to continue:
```
minikube tunnel --profile knative
```

### Deploying a knative service
```
kn service create hello
--image gcr.io/knative-samples/helloworld-go \
--port 8080 \
--env TARGET=World
```
Check.
```
http://hello.default.127.0.0.1.sslip.io/
```
Result:
![image](https://user-images.githubusercontent.com/17582508/196247041-2ed4c448-72de-4881-b104-f9cb27bb8827.png)
