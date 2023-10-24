"""
Reference:
    - https://colab.research.google.com/github/huggingface/notebooks/blob/main/diffusers/diffusers_intro.ipynb
"""
import os

import torch
from diffusers import (
    UNet2DModel,
    DDPMScheduler,
    DDIMScheduler,
)
import PIL.Image
import numpy as np
import tqdm

torch.manual_seed(0)
output_dirs = "outputs"
os.makedirs(output_dirs, exist_ok=True)


def display_sample(sample, i, save_name):
    """Save image."""
    image_processed = sample.cpu().permute(0, 2, 3, 1)
    image_processed = (image_processed + 1.0) * 127.5
    image_processed = image_processed.numpy().astype(np.uint8)

    image_pil = PIL.Image.fromarray(image_processed[0])
    print(f"Image at step {i}")
    image_pil.save(os.path.join(output_dirs, save_name))


# Model
repo_id = "google/ddpm-church-256"
model = UNet2DModel.from_pretrained(repo_id)
print(model.config)

# Noise input
noisy_sample = torch.randn(
    1, model.config.in_channels, model.config.sample_size, model.config.sample_size
)
print(noisy_sample.shape)
display_sample(noisy_sample, 0, "noisy_sample.jpg")

# Inference
with torch.no_grad():
    noisy_residual = model(sample=noisy_sample, timestep=2).sample
print(noisy_residual.shape)
display_sample(noisy_residual, 0, "noisy_residual.jpg")


# Scheduler
"""
Scheduler important config
- `num_train_timesteps` defines the length of the denoising process, e.g. how many timesteps are need to process random gaussian noise to a data sample.
- `beta_schedule` define the type of noise schedule that shall be used for inference and training
- `beta_start` and `beta_end` define the smallest noise value and highest noise value of the schedule.
"""
scheduler = DDPMScheduler.from_config(repo_id)
print(scheduler.config)


less_noisy_sample = scheduler.step(
    model_output=noisy_residual, timestep=2, sample=noisy_sample
).prev_sample
print(less_noisy_sample.shape)

# Removing noise
model.to("cuda")
sample = noisy_sample.to("cuda")


for i, t in enumerate(tqdm.tqdm(scheduler.timesteps)):
    # 1. predict noise residual
    with torch.no_grad():
        residual = model(sample, t).sample

    # 2. compute less noisy image and set x_t -> x_t-1
    sample = scheduler.step(residual, t, sample).prev_sample

    # 3. optionally look at image
    if (i + 1) % 50 == 0:
        display_sample(sample, i + 1, f"{i:04}_output.jpg")


# DDIM Scheduler: Faster than DDPM
scheduler = DDIMScheduler.from_config(repo_id)
scheduler.set_timesteps(num_inference_steps=50)

sample = noisy_sample.to("cuda")
for i, t in enumerate(tqdm.tqdm(scheduler.timesteps)):
  # 1. predict noise residual
  with torch.no_grad():
      residual = model(sample, t).sample

  # 2. compute previous image and set x_t -> x_t-1
  sample = scheduler.step(residual, t, sample).prev_sample

  # 3. optionally look at image
  if (i + 1) % 10 == 0:
      display_sample(sample, i + 1, f"{i:04}_DDIM_output.jpg")
