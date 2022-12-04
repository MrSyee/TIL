# Golang echo: API gateway pattern
[API Gateway pattern](https://microservices.io/patterns/apigateway.html)

![image](https://user-images.githubusercontent.com/17582508/205474383-b7aea97f-013e-404b-8a64-0aa29465c3b7.png)

```mermaid
flowchart LR
    User <--> Service
    Service <--> Microservice
```

## Run
```bash
# microservice
cd microservice
make docs
make run

# service
cd service
make docs
make run
```

You can use Swagger to test.
- http://localhost:10000/docs/index.html
## Result
- Sum
<img width="1274" alt="image" src="https://user-images.githubusercontent.com/17582508/205488298-2ef02e84-bbf3-4ff0-8610-166b8864aea9.png">
