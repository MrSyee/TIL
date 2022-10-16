# Dali

NVIDIA Data Loading Library (DALI) is a collection of highly optimized building blocks and an execution engine that accelerates the data pipeline for computer vision and audio deep learning applications.


## Prerequisites
Install [Anaconda](https://www.anaconda.com/products/distribution) and execute followings:

```bash
make env
conda activate dali
make setup
```

## How to run
```
python getting_start.py
```

The output is output1 ~ output4.png.
1. Simple pipeline: Read images and labels (output1.png)
2. Random Rotate pipeline (output2.png)
3. Random Rotate pipeline with GPU (output3.png)
4. Random Rotate pipeline with hybrid decoding (output4.png)
5. Speedtest between CPU and GPU

## Reference
- https://github.com/NVIDIA/DALI/blob/main/docs/examples/getting_started.ipynb
- https://docs.nvidia.com/deeplearning/dali/main-user-guide/docs/supported_ops.html
