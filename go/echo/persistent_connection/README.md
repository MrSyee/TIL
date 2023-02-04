# Golang echo: Communication between services using Persistent connection

## Introduction
- Request from main service to microservices.
- Use persistent connection.

## Run
Run service Echo server.
```bash
# service: 8080
go run main.go

   ____    __
  / __/___/ /  ___
 / _// __/ _ \/ _ \
/___/\__/_//_/\___/ v4.9.0
High performance, minimalist Go web framework
https://echo.labstack.com
____________________________________O/_______
                                    O\
⇨ http server started on [::]:8080
```
Run microservice Echo server.
```bash
# microservice: 8081, request 8080
go run main.go

   ____    __
  / __/___/ /  ___
 / _// __/ _ \/ _ \
/___/\__/_//_/\___/ v4.10.0
High performance, minimalist Go web framework
https://echo.labstack.com
____________________________________O/_______
                                    O\
⇨ http server started on [::]:8081
```
Run client
```bash
# client: Request 8081
go run main.go
```
```bash
go run main.go -n 6
Hello, World!  +  0
Hello, World!  +  1
Hello, World!  +  2
Hello, World!  +  3
Hello, World!  +  4
Hello, World!  +  5
```
You can check using wireshark that connection is created only once. And connection is closed after 10 seconds.
![image](https://user-images.githubusercontent.com/17582508/216748429-ad3c953a-5f93-476a-b28c-bff0fc5bd8b9.png)
