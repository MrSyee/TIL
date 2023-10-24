import os

from diffusers import DDPMPipeline
import cv2

output_dirs = "outputs"
os.makedirs(output_dirs, exist_ok=True)

# Pipeline
image_pipe = DDPMPipeline.from_pretrained("google/ddpm-celebahq-256")
image_pipe.to("cuda")

print(image_pipe)

images = image_pipe(num_inference_steps=10).images
print(type(images[0]))
images[0].save(os.path.join(output_dirs, "pipe_outputs.jpg"))
