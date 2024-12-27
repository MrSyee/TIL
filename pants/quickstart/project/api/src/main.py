import requests
import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def healthcheck(url: str):
    """Healthcheck.

    - Hi
    - Hello
    """
    return requests.get(url).json()


@app.get("/call-bob")
async def call_bob():
    return "ok"


@app.get("/be-called")
async def be_called():
    return "ok"


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")
