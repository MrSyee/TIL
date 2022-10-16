"""
Reference:
    - https://github.com/NVIDIA/DALI/blob/main/docs/examples/getting_started.ipynb
"""
from timeit import default_timer as timer

from nvidia.dali.pipeline import Pipeline
from nvidia.dali import pipeline_def
import nvidia.dali.fn as fn
import nvidia.dali.types as types
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

image_dir = "data/images"
max_batch_size = 8
test_batch_size = 64

def speedtest(pipeline, batch, n_threads):
    pipe = pipeline(batch_size=batch, num_threads=n_threads, device_id=0)
    pipe.build()
    # warmup
    for i in range(5):
        pipe.run()
    # test
    n_test = 20
    t_start = timer()
    for i in range(n_test):
        pipe.run()
    t = timer() - t_start
    print("Speed: {} imgs/s".format((n_test * batch)/t))

########################################
# 1. Simple pipeline: Read images and labels
########################################
@pipeline_def(batch_size=max_batch_size, num_threads=1)
def simple_pipeline():
    jpegs, labels = fn.readers.file(file_root=image_dir)
    images = fn.decoders.image(jpegs, device='cpu')

    return images, labels


def show_images(image_batch, save_name):
    columns = 4
    rows = (max_batch_size + 1) // (columns)
    fig = plt.figure(figsize = (24,(24 // columns) * rows))
    gs = gridspec.GridSpec(rows, columns)
    for j in range(rows*columns):
        plt.subplot(gs[j])
        plt.axis("off")
        plt.imshow(image_batch.at(j))
        plt.savefig(save_name)


pipe = simple_pipeline(device_id=0)
pipe.build()

images, labels = pipe.run()
# TensorListCPU
print("Type of images: ", type(images), "\tShape of 1st: ", images[0].shape())
print("Type of labels: ", type(labels), "\tShape of 1st: ", labels[0].shape())

show_images(images, "output1.png")


########################################
# 2. Random Rotate pipeline
########################################
@pipeline_def
def random_rotated_pipeline():
    jpegs, labels = fn.readers.file(file_root=image_dir, random_shuffle=True, initial_fill=21)
    images = fn.decoders.image(jpegs, device='cpu')
    angle = fn.random.uniform(range=(-10.0, 10.0))
    rotated_images = fn.rotate(images, angle=angle, fill_value=0)

    return rotated_images, labels


pipe = random_rotated_pipeline(batch_size=max_batch_size, num_threads=1, device_id=0, seed=1234)
pipe.build()

pipe_out = pipe.run()
images, labels = pipe_out
show_images(images, "output2.png")


########################################
# 3. Random Rotate pipeline with GPU
########################################
@pipeline_def
def random_rotated_gpu_pipeline():
    jpegs, labels = fn.readers.file(file_root=image_dir, random_shuffle=True, initial_fill=21)
    images = fn.decoders.image(jpegs, device='cpu')
    angle = fn.random.uniform(range=(-10.0, 10.0))
    rotated_images = fn.rotate(images.gpu(), angle=angle, fill_value=0)

    return rotated_images, labels

pipe = random_rotated_gpu_pipeline(batch_size=max_batch_size, num_threads=1, device_id=0, seed=1234)
pipe.build()

# Image: TensorListGPU, Label: TensorListCPU
images, labels = pipe.run()
print("Type of images: ", type(images), "\tShape of 1st: ", images[0].shape())
print("Type of labels: ", type(labels), "\tShape of 1st: ", labels[0].shape())

show_images(images.as_cpu(), "output3.png")


#################################################
# 4. Random Rotate pipeline with hybrid decoding
#################################################
@pipeline_def
def random_rotated_hybrid_pipeline():
    jpegs, labels = fn.readers.file(file_root=image_dir, random_shuffle=True, initial_fill=21)
    images = fn.decoders.image(jpegs, device='mixed')
    angle = fn.random.uniform(range=(-10.0, 10.0))
    rotated_images = fn.rotate(images, angle=angle, fill_value=0)

    return images, labels


pipe = random_rotated_hybrid_pipeline(batch_size=max_batch_size, num_threads=1, device_id=0, seed=1234)
pipe.build()

images, labels = pipe.run()
print("Type of images: ", type(images), "\tShape of 1st: ", images[0].shape())
print("Type of labels: ", type(labels), "\tShape of 1st: ", labels[0].shape())

show_images(images.as_cpu(), "output4.png")

########################################
# 5. Speedtest between CPU and GPU
########################################
speedtest(random_rotated_pipeline, test_batch_size, 4)
# Speed: 159.85212002201334 imgs/s
speedtest(random_rotated_gpu_pipeline, test_batch_size, 4)
# Speed: 2894.0575884953496 imgs/s
speedtest(random_rotated_hybrid_pipeline, test_batch_size, 4)
# Speed: 5631.80402588913 imgs/s
