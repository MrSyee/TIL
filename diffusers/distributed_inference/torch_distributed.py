import os

import torch
import torch.distributed as dist
import torch.multiprocessing as mp
from diffusers import DiffusionPipeline

output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)

pipe = DiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16)

def run_inference(rank, world_size):
    dist.init_process_group("nccl", rank=rank, world_size=world_size)
    pipe.to(rank)

    if torch.distributed.get_rank() == 3:
        prompt = "a dog"
    elif torch.distributed.get_rank() == 4:
        prompt = "a cat"

    result = pipe(prompt).images[0]
    result.save(f"{output_dir}/result_{rank}.png")

def main():
    world_size = 2
    mp.spawn(run_inference, args=(world_size,), nprocs=world_size, join=True)


if __name__ == "__main__":
    main()
