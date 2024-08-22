import asyncio
import json
import time

import requests
import websockets

# 서버 URL 설정
server_url = "http://localhost:18500"
download_endpoint = f"{server_url}/download/"
progress_endpoint = f"{server_url}/progress/"
ws_endpoint = f"ws://localhost:18500/ws/"


async def download_file(url: str, save_path: str):
    # 다운로드 요청 보내기
    print(type(url), type(save_path))
    response = requests.post(
        download_endpoint, params={"url": url, "save_path": save_path}
    )

    if response.status_code != 200:
        print(
            f"[Error] Wrong response:\n"
            + f"\tStatus code: {response.status_code}\n"
            + f"\tResponse: {response.json()}"
        )
        return None

    # 작업 ID 받기
    task_id = response.json().get("task_id")
    print(f"Download started with task ID: {task_id}")

    # WebSocket을 통해 진행 상황 모니터링
    async with websockets.connect(f"{ws_endpoint}{task_id}") as websocket:
        while True:
            progress_message = await websocket.recv()
            print(progress_message)  # 다운로드 진행 상황 출력

            if "Download completed" in progress_message:
                break

    print("Download process completed.")


# 비동기 루프 실행
if __name__ == "__main__":
    url_to_download = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth"  # 다운로드할 파일의 URL
    save_file_path = "output/output.pth"  # 저장할 파일의 경로

    loop = asyncio.get_event_loop()
    loop.run_until_complete(download_file(url_to_download, save_file_path))
