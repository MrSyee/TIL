.PHONY: build
build:
	go build main.go

run:
	$(MAKE) build
	./main

format:
	golines -m 100 -t 4 -w ./*.go

lint:
	golangci-lint run