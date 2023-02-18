# Triton quick-start

## Prerequisites
- Install [Docker](https://docs.docker.com/engine/install/)
- pytorch
```bash
pip install torch
```
- triton docker image
```bash
docker pull nvcr.io/nvidia/tritonserver:22.09-py3
```

## Create a model repository
### Create a model
```bash
python identity.py
```

### Set model in a model repository
```
tree model_repository

model_repository
├── identity
│   ├── 1
│   │   └── dummy
│   └── config.pbtxt
└── identity_core
    ├── 1
    │   └── model.pt
    └── config.pbtxt

4 directories, 4 files
```

## Run triton
```bash
$ docker run --rm -p 9000:8000 -p 9001:8001 -p 9002:8002 -v $(pwd)/model_repository:/models nvcr.io/nvidia/tritonserver:22.09-py3 tritonserver --model-repository=/models

=============================
== Triton Inference Server ==
=============================

NVIDIA Release 22.09 (build 44909144)
Triton Server Version 2.26.0

Copyright (c) 2018-2022, NVIDIA CORPORATION & AFFILIATES.  All rights reserved.

Various files include modifications (c) NVIDIA CORPORATION & AFFILIATES.  All rights reserved.

This container image and its contents are governed by the NVIDIA Deep Learning Container License.
By pulling and using the container, you accept the terms and conditions of this license:
https://developer.nvidia.com/ngc/nvidia-deep-learning-container-license

WARNING: The NVIDIA Driver was not detected.  GPU functionality will not be available.
   Use the NVIDIA Container Toolkit to start this container with GPU support; see
   https://docs.nvidia.com/datacenter/cloud-native/ .

W0218 07:19:12.870731 1 pinned_memory_manager.cc:236] Unable to allocate pinned system memory, pinned memory pool will not be available: no CUDA-capable device is detected
I0218 07:19:12.873854 1 cuda_memory_manager.cc:115] CUDA memory pool disabled
I0218 07:19:13.144376 1 model_lifecycle.cc:459] loading: identity_core:1
WARNING: [Torch-TensorRT] - Unable to read CUDA capable devices. Return status: 100
I0218 07:19:15.371282 1 libtorch.cc:1985] TRITONBACKEND_Initialize: pytorch
I0218 07:19:15.371327 1 libtorch.cc:1995] Triton TRITONBACKEND API version: 1.10
I0218 07:19:15.371334 1 libtorch.cc:2001] 'pytorch' TRITONBACKEND API version: 1.10
I0218 07:19:15.371369 1 libtorch.cc:2034] TRITONBACKEND_ModelInitialize: identity_core (version 1)
W0218 07:19:15.374567 1 libtorch.cc:284] skipping model configuration auto-complete for 'identity_core': not supported for pytorch backend
I0218 07:19:15.375629 1 libtorch.cc:313] Optimized execution is enabled for model instance 'identity_core'
I0218 07:19:15.378796 1 libtorch.cc:332] Cache Cleaning is disabled for model instance 'identity_core'
I0218 07:19:15.378840 1 libtorch.cc:349] Inference Mode is disabled for model instance 'identity_core'
I0218 07:19:15.378852 1 libtorch.cc:444] NvFuser is not specified for model instance 'identity_core'
I0218 07:19:15.379002 1 libtorch.cc:2078] TRITONBACKEND_ModelInstanceInitialize: identity_core (CPU device 0)
I0218 07:19:15.498386 1 model_lifecycle.cc:693] successfully loaded 'identity_core' version 1
I0218 07:19:15.502594 1 model_lifecycle.cc:459] loading: identity:1
E0218 07:19:15.502974 1 ensemble_scheduler.cc:1311] unable to create stream for identity: no CUDA-capable device is detected
I0218 07:19:15.506800 1 model_lifecycle.cc:693] successfully loaded 'identity' version 1
I0218 07:19:15.506899 1 server.cc:563]
+------------------+------+
| Repository Agent | Path |
+------------------+------+
+------------------+------+

I0218 07:19:15.506937 1 server.cc:590]
+---------+---------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Backend | Path                                                    | Config                                                                                                                                                        |
+---------+---------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
| pytorch | /opt/tritonserver/backends/pytorch/libtriton_pytorch.so | {"cmdline":{"auto-complete-config":"true","min-compute-capability":"6.000000","backend-directory":"/opt/tritonserver/backends","default-max-batch-size":"4"}} |
+---------+---------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------+

I0218 07:19:15.511363 1 server.cc:633]
+---------------+---------+--------+
| Model         | Version | Status |
+---------------+---------+--------+
| identity      | 1       | READY  |
| identity_core | 1       | READY  |
+---------------+---------+--------+

I0218 07:19:15.511615 1 metrics.cc:757] Collecting CPU metrics
I0218 07:19:15.511824 1 tritonserver.cc:2264]
+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Option                           | Value                                                                                                                                                                                                |
+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| server_id                        | triton                                                                                                                                                                                               |
| server_version                   | 2.26.0                                                                                                                                                                                               |
| server_extensions                | classification sequence model_repository model_repository(unload_dependents) schedule_policy model_configuration system_shared_memory cuda_shared_memory binary_tensor_data statistics trace logging |
| model_repository_path[0]         | /models                                                                                                                                                                                              |
| model_control_mode               | MODE_NONE                                                                                                                                                                                            |
| strict_model_config              | 0                                                                                                                                                                                                    |
| rate_limit                       | OFF                                                                                                                                                                                                  |
| pinned_memory_pool_byte_size     | 268435456                                                                                                                                                                                            |
| response_cache_byte_size         | 0                                                                                                                                                                                                    |
| min_supported_compute_capability | 6.0                                                                                                                                                                                                  |
| strict_readiness                 | 1                                                                                                                                                                                                    |
| exit_timeout                     | 30                                                                                                                                                                                                   |
+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

I0218 07:19:15.587533 1 grpc_server.cc:4820] Started GRPCInferenceService at 0.0.0.0:8001
I0218 07:19:15.592527 1 http_server.cc:3474] Started HTTPService at 0.0.0.0:8000
I0218 07:19:15.658575 1 http_server.cc:181] Started Metrics Service at 0.0.0.0:8002
```

### Check readiness
```
curl -v http://localhost:9000/v2/health/ready

*   Trying 127.0.0.1:9000...
* Connected to localhost (127.0.0.1) port 9000 (#0)
> GET /v2/health/ready HTTP/1.1
> Host: localhost:9000
> User-Agent: curl/7.79.1
> Accept: */*
>
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< Content-Length: 0
< Content-Type: text/plain
<
* Connection #0 to host localhost left intact
```

### Inference
```
curl -v http://localhost:9000/v2/models/identity/infer \
-H "Content-Type: application/json" \
-X POST \
-d '{"inputs":[{"name":"INPUT","shape":[5],"datatype":"UINT8","data":[0, 1, 2, 3, 4]}]}'

Note: Unnecessary use of -X or --request, POST is already inferred.
*   Trying 127.0.0.1:9000...
* Connected to localhost (127.0.0.1) port 9000 (#0)
> POST /v2/models/identity/infer HTTP/1.1
> Host: localhost:9000
> User-Agent: curl/7.79.1
> Accept: */*
> Content-Type: application/json
> Content-Length: 83
>
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< Content-Type: application/json
< Content-Length: 200
<
* Connection #0 to host localhost left intact
{"model_name":"identity","model_version":"1","parameters":{"sequence_id":0,"sequence_start":false,"sequence_end":false},"outputs":[{"name":"OUTPUT","datatype":"UINT8","shape":[5],"data":[0,1,2,3,4]}]}
```
