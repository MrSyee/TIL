.PHONY: build
build:
	go build main.go

run:
	$(MAKE) build
	./main

# For developers
setup-dev:
	sh setup-dev.sh

.PHONY: format
format:
	golines -m 100 -t 4 -w *.go
	swag fmt