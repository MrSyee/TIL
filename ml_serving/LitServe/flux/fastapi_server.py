from fastapi import FastAPI, Response
from diffusers import FluxPipeline
from io import BytesIO
import torch
import time
import uvicorn
from pydantic import BaseModel



class PredictRequest(BaseModel):
    prompt: str


device = "cuda"

base_model = 'black-forest-labs/FLUX.1-dev'
pipe = FluxPipeline.from_pretrained(base_model, torch_dtype=torch.bfloat16).to(device)

app = FastAPI()

@app.post("/predict")
async def predict(requests: PredictRequest):
    try:
        start = time.time()
        image = pipe(
            requests.prompt,
            width=1024,
            height=1024,
            num_inference_steps=20,
            generator=torch.Generator().manual_seed(int(time.time())),
            guidance_scale=3.5,
        ).images[0]
        print(f"Spend time: {time.time() - start}")

        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return Response(content=buffered.getvalue(), headers={"Content-Type": "image/png"})

    except Exception as err:
        print(err)
        raise err


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9900)