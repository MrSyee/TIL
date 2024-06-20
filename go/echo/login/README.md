# login-logout with auth
- Authentication with JWT(JSON Web Token)
- Authorization

## Dependency
- [Casbin](https://casbin.org/): An authorization library that supports access control models like ACL, RBAC, ABAC
- [Redis](https://redis.io/): The open source, in-memory data store used by millions of developers as a database, cache, streaming engine, and message broker.
```
brew install redis  # for mac
```
- [argon2id](https://github.com/alexedwards/argon2id): For hashing password

## Progress
1. Login: Generate Access Token (JWT) and Refresh Token Cookie.
2.

## Run
Run API server and redis cache server
```
make run
redis-server
```

### Login
```
# login
# -c cookie.txt saves the cookie as a file
TOKEN=$(curl -X POST -c cookie.txt -d 'username=admin' -d 'password=password' localhost:8080/login | jq -r ".token")
```
