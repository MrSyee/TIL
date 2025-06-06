# Quickstart Milvus

## Docker compose로 Milvus 설치
### Start Milvus
- etcd port 겹치는 문제로 2379 -> 2380 으로 수정

```bash
# 이미 설치되어 있음.
wget https://github.com/milvus-io/milvus/releases/download/v2.5.12/milvus-standalone-docker-compose.yml -O docker-compose.yml

# Start Milvus
sudo docker compose up -d

```

```bash
...

[+] Running 4/4
 ✔ Network milvus               Created                                                              0.1s
 ✔ Container milvus-etcd        Started                                                              0.5s
 ✔ Container milvus-minio       Started                                                              0.5s
 ✔ Container milvus-standalone  Started                                                              0.9s

```

### Stop and delete Milvus
```bash
# Stop milvus
docker compose down

# Delete service data
rm -rf volumes

```

## Quickstart Milvus
### Install Milvus
```bash
pip install -U pymilvus
```

### Set up and Test Vector DB
```bash
uv run quickstart.py
```
