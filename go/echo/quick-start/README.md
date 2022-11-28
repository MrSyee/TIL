# Golang echo: Communication between services

## Introduction
- Request from main service to microservices.
- Service outputs results combined response of microservices.

## Installation
```bash
go mod init quick-start  # for project initialization
go get github.com/labstack/echo/v4  # for the server
go get github.com/labstack/echo/v4/middleware  # for middlewares (logger)
go get github.com/swaggo/echo-swagger  # swagger ui
go install github.com/swaggo/swag/cmd/swag@latest # swagger cli
```

## Run
```bash
swag init
go run main.go
```
```bash

   ____    __
  / __/___/ /  ___
 / _// __/ _ \/ _ \
/___/\__/_//_/\___/ v4.9.0
High performance, minimalist Go web framework
https://echo.labstack.com
____________________________________O/_______
                                    O\
⇨ http server started on [::]:1323
```

### Get
```bash
curl http://localhost:1323/users/Joe
```
```bash
Joe%
```

### Post
```bash
curl -d "name=Joe Smith" -d "email=joe@labstack.com" http://localhost:1323/users
```
```bash
name:Joe Smith, email:joe@labstack.com%
```

### Swagger
Connect `http://localhost:1323/docs/` in your browser.
<img width="1453" alt="image" src="https://user-images.githubusercontent.com/17582508/204183330-e1e283bc-a4d3-4772-9eb2-49df7b7b89f4.png">

## Reference
- [Guide](https://echo.labstack.com/guide/)
- [Echo-Swagger](https://github.com/swaggo/echo-swagger)
- [Swagger declarative comments format](https://github.com/swaggo/swag#declarative-comments-format)
