# uv monorepo
uv의 workspace 기능으로 monorepo 구성 테스트

## uv-monorepo 설정
### root
```bash
# root(uv-monorep) 위치에서
uv init
uv venv
uv sync
```

### api
```bash
# root/api/vision 위치에서
uv init
```
이때 `root`의 `pyproject.toml`을 확인해보면 workspace로 연결됨

```
# pyproject.toml

...
[tool.uv.workspace]
members = ["api/vision"]
...

```
