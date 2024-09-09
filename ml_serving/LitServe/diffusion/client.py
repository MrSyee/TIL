# Copyright The Lightning AI team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import argparse
import requests
import os
import base64
import io

from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "url",
        type=str,
        default="http://10.130.198.23:18900",
        help="http://backend-ip:port",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    output_path = "outputs"
    os.makedirs(output_path, exist_ok=True)

    input_json = {
        "prompt": "1girl, girl has a book"
    }
    response = requests.post(f"{args.url}/predict", json=input_json)
    print(f"Status: {response.status_code}")

    if response.status_code != 200:
        raise Exception("Request Fail.")

    encoded_image = response.json().get("image")
    image_byte = io.BytesIO(base64.b64decode(encoded_image))
    image = Image.open(image_byte)

    image.save(f"{output_path}/result.png")



if __name__ == "__main__":
    main()
