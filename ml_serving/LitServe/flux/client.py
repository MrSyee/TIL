import argparse
import os
import requests
from datetime import datetime
import time

# Update this URL to your server's URL if hosted remotely
API_URL = "http://127.0.0.1:9900/predict"

def send_request(prompt):
    os.makedirs("outputs", exist_ok=True)

    t0 = time.perf_counter()
    response = requests.post(API_URL, json={"prompt": prompt})
    t1 = time.perf_counter()
    print(f"Spend time: {t1 - t0}")
    if response.status_code == 200:
        filename = f"outputs/output-{datetime.now()}.png"

        with open(filename, "wb") as image_file:
            image_file.write(response.content)

        print(f"Image saved to {filename}")
    else:
        print(f"Error: Response with status code {response.status_code} - {response.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sends a prompt to the Flux server and receives the generated image")
    parser.add_argument("--prompt", required=True, help="Prompt to feed to the model")
    args = parser.parse_args()

    send_request(args.prompt)
