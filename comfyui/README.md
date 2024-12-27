# ComfyUI

## How to setup
1. Clone [ComfyUI](https://github.com/comfyanonymous/ComfyUI?tab=readme-ov-file).
```
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
```

2. Install dependancy. (Create a virtual environment such as pyenv if necessary.)
```
pip install -r requirements.txt
```

3. (Optional) Download some basic and useful custom nodes.
- [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager)

You can download using ComfyUI Manager.
- [ComfyUI Inspire Pack](https://github.com/ltdrdata/ComfyUI-Inspire-Pack)
- [ComfyUI Impact Pack](https://github.com/ltdrdata/ComfyUI-Impact-Pack)
- [ComfyUI Easy use](https://github.com/yolain/ComfyUI-Easy-Use)
- [ComfyUI Essentials](https://github.com/cubiq/ComfyUI_essentials)


```
cd custom_nodes
git clone <custom-node>
```

4. Run comfyui.
```
python main.py

# if you want to select specific gpu
CUDA_VISIBLE_DEVICES=0 python main.py
```

## Reference
- [ComfyUI example](https://comfyanonymous.github.io/ComfyUI_examples/)
