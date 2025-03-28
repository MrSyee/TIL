import os

import cv2
import numpy as np
from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/healthcheck")
async def healthcheck():
    return {"status": True}


@app.post("/image")
async def create_noise_image(size: int):
    if size <= 0:
        raise HTTPException(status_code=400, detail="Size must be positive")

    # 노이즈 이미지 생성
    noise = np.random.randint(0, 255, (size, size), dtype=np.uint8)

    # output 디렉토리 생성
    os.makedirs("output", exist_ok=True)

    # 이미지 저장
    output_path = "output/image.png"
    cv2.imwrite(output_path, noise)

    return {"message": f"Image saved to {output_path}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
