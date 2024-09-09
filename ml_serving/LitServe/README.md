# LitServe

## Run
### Quickstart
```
python quickstart.py

INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
Swagger UI is available at http://0.0.0.0:8000/docs
INFO:     Started server process [1813209]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
Setup complete for worker 0.
INFO:     127.0.0.1:19202 - "POST /predict HTTP/1.1" 200 OK
```
```
python client.py

Status: 200
Response:
 {"output":{"output":80.0}}

```


## Reference
- https://github.com/Lightning-AI/LitServe
- https://medium.com/@vigneshhp/supercharge-your-ai-deployments-by-50-faster-with-litserve-a95191e60500
- https://lightning.ai/lightning-ai/studios/deploy-a-private-api-for-stable-diffusion-2