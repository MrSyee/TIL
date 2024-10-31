# Qdrant quickstart

## Prerequisites
- minikube: 1.34.0

## Run
- Run qdrant with docker
```
docker run --rm -p 6333:6333 -p 6334:6334 \
	-v $(pwd)/qdrant_storage:/qdrant/storage:z \
	qdrant/qdrant
```
    - Check http://localhost:6333/dashboard
- Create collection and add vectors
    - Collection 생성 및 더미 vector 삽입
```
python create.py
```

- Run query

```
python query.py
```
