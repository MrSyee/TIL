"""
Diffusion 모델의 추론 속도를 최적화하는 방법
1. float32 -> float16으로 줄인다.
2. Scheduler를 변경하여 step 수를 줄인다.

Experiments
- Machine: Tesla P40 GPU
    - float32: 16.35
    - float16: 86.96
    - float32 + DPMSolverMultistepScheduler: 6.39
    - float16 + DPMSolverMultistepScheduler: 34.43

- Machine: Tesla T4
    - float32: 25.21
    - float16: 8.53
    - float32 + DPMSolverMultistepScheduler: 10.14
    - float16 + DPMSolverMultistepScheduler: 3.45

- Machine: Ampere A40 (torch 1.13.1)
    - float32: 36.23
    - float16: 4.86
    - float32 + DPMSolverMultistepScheduler: 2.73
    - float16 + DPMSolverMultistepScheduler: 1.50
"""

import os
import time

import torch
from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler


output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)

model_id = "runwayml/stable-diffusion-v1-5"
prompt = "portrait photo of a old warrior chief"

# Float32
pipeline = DiffusionPipeline.from_pretrained(model_id, use_safetensors=True)
pipeline = pipeline.to("cuda")

generator = torch.Generator("cuda").manual_seed(1)

start = time.time()
image = pipeline(prompt, generator=generator).images[0]
print(f"Spend time of float32: {time.time() - start}")

image.save(os.path.join(output_dir, "output1.png"))

# Float16
pipeline = DiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16, use_safetensors=True)
pipeline = pipeline.to("cuda")

generator = torch.Generator("cuda").manual_seed(1)

start = time.time()
image = pipeline(prompt, generator=generator).images[0]
print(f"Spend time of float16: {time.time() - start}")

image.save(os.path.join(output_dir, "output2.png"))


# DPMSolverMultistepScheduler
pipeline = DiffusionPipeline.from_pretrained(model_id, use_safetensors=True)
pipeline = pipeline.to("cuda")
pipeline.scheduler = DPMSolverMultistepScheduler.from_config(pipeline.scheduler.config)

generator = torch.Generator("cuda").manual_seed(1)

start = time.time()
image = pipeline(prompt, generator=generator, num_inference_steps=20).images[0]
print(f"Spend time of float32 with DPMSolverMultistepScheduler: {time.time() - start}")

image.save(os.path.join(output_dir, "output3.png"))


# float16 + DPMSolverMultistepScheduler
pipeline = DiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16, use_safetensors=True)
pipeline = pipeline.to("cuda")
pipeline.scheduler = DPMSolverMultistepScheduler.from_config(pipeline.scheduler.config)

generator = torch.Generator("cuda").manual_seed(1)

start = time.time()
image = pipeline(prompt, generator=generator, num_inference_steps=20).images[0]
print(f"Spend time of float16 with DPMSolverMultistepScheduler: {time.time() - start}")

image.save(os.path.join(output_dir, "output4.png"))