#!/bin/sh

# go
go get github.com/labstack/echo/v4  # for the echo server
# go get github.com/go-playground/validator/v10  # validator
go get github.com/labstack/echo/v4/middleware  # for middlewares (logger)
go get github.com/swaggo/echo-swagger  # swagger ui
go get github.com/swaggo/swag/cmd/swag@v1.8.7  # swagger cli
go get golang.org/x/tools/cmd/goimports@v0.3.0  # format
go get github.com/segmentio/golines@v0.11.0  # format
go get github.com/golangci/golangci-lint/cmd/golangci-lint@v1.50.1  # lint
