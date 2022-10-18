PROFILE_NAME=knative

cluster:
	minikube start --driver=docker --profile=$(PROFILE_NAME) --cpus=3 --memory=6g
	kubectl get nodes

finalize:
	minikube delete --profile $(PROFILE_NAME)
