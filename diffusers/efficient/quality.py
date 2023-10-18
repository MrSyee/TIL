"""
Diffusion 모델이 생성하는 이미지의 품질을 올리기

1. Better checkpoints
2. Better pipeline components
3. Better prompt engineering
"""

import os
import time

import torch
from diffusers import AutoencoderKL, DiffusionPipeline, DPMSolverMultistepScheduler
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
pipeline.scheduler = DPMSolverMultistepScheduler.from_config(pipeline.scheduler.config)


# better pipeline
vae = AutoencoderKL.from_pretrained("stabilityai/sd-vae-ft-mse", torch_dtype=torch.float16).to("cuda")
pipeline.vae = vae
images = pipeline(**get_inputs(batch_size=8)).images
start = time.time()
grid = make_image_grid(images, rows=2, cols=4)
print(f"Spend time of AutoencoderKL: {time.time() - start}")

grid.save(os.path.join(output_dir, "output5.png"))