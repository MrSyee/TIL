
import asyncio
import aiohttp
import os
import uuid

from fastapi import FastAPI, BackgroundTasks, WebSocket
from typing import Dict

app = FastAPI()

# 작업 진행 상황을 저장하는 메모리 (Redis로 대체 가능)
progress_dict: Dict[str, int] = {}

async def download_file(task_id: str, url: str, save_path: str):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            with open(save_path, 'wb') as f:
                async for chunk in response.content.iter_chunked(1024):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        progress = (downloaded_size / total_size) * 100
                        progress_dict[task_id] = progress
            progress_dict[task_id] = 100  # 다운로드 완료 시 100%로 설정

@app.post("/download/")
async def initiate_download(url: str, save_path: str, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())  # 고유한 작업 ID 생성
    progress_dict[task_id] = 0
    background_tasks.add_task(download_file, task_id, url, save_path)
    return {"task_id": task_id}

@app.get("/progress/{task_id}")
async def get_progress(task_id: str):
    progress = progress_dict.get(task_id, 0)
    return {"task_id": task_id, "progress": progress}

@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()
    while True:
        progress = progress_dict.get(task_id, 0)
        await websocket.send_text(f"Download progress: {progress}%")
        if progress >= 100:
            await websocket.send_text("Download completed")
            break
        await asyncio.sleep(1)  # 1초마다 진행률 확인
    await websocket.close()