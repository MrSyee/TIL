"""
Diffusion 모델 사용시 메모리 최적화 방법
초당 생성되는 이미지 수를 최대화하는 경우가 많기 때문에 간접적으로 속도도 향상됨.
1. OOM이 발생할때까지 다양한 배치 사이즈를 시도함.
2. 대부분의 메모리는 cross attention layer가 차지하므로, 이 과정을 순차적으로 진행하면 메모리 절약 가능
"""
import os
import time

import torch
from diffusers import DiffusionPipeline
from diffusers.utils import make_image_grid 


output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)

model_id = "runwayml/stable-diffusion-v1-5"
prompt = "portrait photo of a old warrior chief"


def get_inputs(batch_size=1):
    generator = [torch.Generator("cuda").manual_seed(i) for i in range(batch_size)]
    prompts = batch_size * [prompt]
    num_inference_steps = 20

    return {"prompt": prompts, "generator": generator, "num_inference_steps": num_inference_steps}


pipeline = DiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16, use_safetensors=True)
pipeline = pipeline.to("cuda")
pipeline.enable_attention_slicing()

generator = torch.Generator("cuda").manual_seed(1)

start = time.time()
images = pipeline(**get_inputs(batch_size=8)).images
print(f"Spend time of float16: {time.time() - start}")

grid = make_image_grid(images, 2, 4)
print(type(grid))

grid.save(os.path.join(output_dir, "output5.png"))
