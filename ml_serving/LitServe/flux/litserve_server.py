from io import BytesIO
from fastapi import Response
import torch
import time
import litserve as ls
from optimum.quanto import freeze, qfloat8, quantize
from diffusers import FlowMatchEulerDiscreteScheduler, AutoencoderKL
from diffusers.models.transformers.transformer_flux import FluxTransformer2DModel
from diffusers.pipelines.flux.pipeline_flux import FluxPipeline
from transformers import CLIPTextModel, CLIPTokenizer,T5EncoderModel, T5TokenizerFast


class FluxLitAPI(ls.LitAPI):
    def setup(self, device):
        print("device", device)

        # # Load the model
        # scheduler = FlowMatchEulerDiscreteScheduler.from_pretrained("black-forest-labs/FLUX.1-dev", subfolder="scheduler", revision="refs/pr/1")
        # text_encoder = CLIPTextModel.from_pretrained("openai/clip-vit-large-patch14", torch_dtype=torch.bfloat16).to(device)
        # tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14", torch_dtype=torch.bfloat16)
        # text_encoder_2 = T5EncoderModel.from_pretrained("black-forest-labs/FLUX.1-dev", subfolder="text_encoder_2", torch_dtype=torch.bfloat16, revision="refs/pr/1").to(device)
        # tokenizer_2 = T5TokenizerFast.from_pretrained("black-forest-labs/FLUX.1-dev", subfolder="tokenizer_2", torch_dtype=torch.bfloat16, revision="refs/pr/1")
        # vae = AutoencoderKL.from_pretrained("black-forest-labs/FLUX.1-dev", subfolder="vae", torch_dtype=torch.bfloat16, revision="refs/pr/1").to(device)
        # transformer = FluxTransformer2DModel.from_pretrained("black-forest-labs/FLUX.1-dev", subfolder="transformer", torch_dtype=torch.bfloat16, revision="refs/pr/1").to(device)

        # quantize to 8-bit to fit on an L4
        # quantize(transformer, weights=qfloat8)
        # freeze(transformer)
        # quantize(text_encoder_2, weights=qfloat8)
        # freeze(text_encoder_2)

        self.pipe = FluxPipeline.from_pretrained("black-forest-labs/FLUX.1-dev", torch_dtype=torch.bfloat16).to(device)
        # self.pipe.text_encoder_2 = text_encoder_2
        # self.pipe.transformer = transformer
        # self.pipe.enable_model_cpu_offload()

        print(self.pipe.device)
        print("Complete setup!")


    def decode_request(self, request):
        # Extract prompt from request
        prompt = request["prompt"]
        return prompt

    def predict(self, prompt):
        print("Start predict!")
        start = time.time()
        # Generate image from prompt
        image = self.pipe(
            prompt=prompt,
            width=1024,
            height=1024,
            num_inference_steps=20,
            generator=torch.Generator().manual_seed(int(time.time())),
            guidance_scale=3.5,
        ).images[0]
        print(f"Spend time: {time.time() - start}")
        print("End predict!")

        return image

    def encode_response(self, image):
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return Response(content=buffered.getvalue(), headers={"Content-Type": "image/png"})

# Starting the server
if __name__ == "__main__":
    api = FluxLitAPI()
    server = ls.LitServer(api, timeout=False, accelerator="gpu", devices=1)
    server.run(port=9900, num_api_servers=2)
