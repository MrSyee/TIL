"""
1. Sliced VAE
- 한 번에 한 장의 이미지 latent의 배치를 디코딩 하도록 한다.
- 제한된 VRAM 메모리로 32 이상의 많은 Batch 처리가 가능하게 한다.

```
pipe.enable_vae_slicing()
```

2. Tiled VAE
- 이미지를 겹치는 타일로 분할하고, 타일마다 디코딩하여 추후 출력에서 혼합하여 하나의 이미지를 만든다.
- 제한된 VRAM 메모리로 고화질의 이미지(e.g. 4K)를 만들수 있도록 한다.

```
pipe.enable_vae_tiling()
pipe.enable_xformers_memory_efficient_attention()
```

3. CPU offloading
- CPU에 가중치는 offload해두었다가 Forward 연산시에만 GPU에 가중치를 load 하면 메모리를 3GB 미만으로 줄일 수 있다.
- 메모리가 절약되지만 성능은 낮아진다. (속도? 퀄리티?) -> 아마 속도

```
pipe.enable_sequential_cpu_offload()
```

4. Model offloading
- CPU offloading은 메모리를 줄여주지만, 속도가 느려진다.
- 추론시 서브모듈이 GPU로 이동하고, 새 모듈이 실행되면 즉시 CPU로 반환되기 때문이다.
- 각 모델을 구성하는 서브모듈을 다루는 대신에, 전체 모델을 GPU로 옮기는 방법.
- 모델 오프로딩 중에는 파이프라인의 주요 구성 요소 중 하나(일반적으로 텍스트 인코더, UNet 및 VAE)만 GPU에 배치되고 다른 구성 요소는 CPU에서 대기한다.
- 여러 반복을 위해 실행되는 UNet과 같은 컴포넌트는 더 이상 필요하지 않을 때까지 GPU에 남아 있는다.
- CPU offloading의 보완책

```
pipe.enable_model_cpu_offload()

# Model offloading can also be combined with attention slicing for additional memory savings.
pipe.enable_attention_slicing()
```

5. Channels-last memory format
- 채널-라스트 메모리 형식은 차원 순서를 유지하기 위해 메모리에서 NCHW 텐서를 정렬하는 대체 방식입니다.
- 채널 마지막 텐서는 채널이 가장 밀도가 높은 차원이 되는 방식으로 정렬됩니다(이미지를 픽셀 단위로 저장).
- 현재 모든 연산자가 채널 마지막 형식을 지원하는 것은 아니므로 최악의 성능을 초래할 수 있지만 모델에 적합한지 확인해야 합니다.
- 잘 이해가 가진 않음.

6. Tracing

7. Memory-efficient attention
- 메모리 효율적인 어텐션을 사용. 최근 모델은 Flash Attention.

"""

