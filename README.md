## gpuctypes (a low level GPU library for Python)

Do you wish that there were simple wrappers for GPU libraries in Python? Like not pyopencl, pycuda, and (HIP library someday?) here, but just raw access to the APIs?

That's what gpuctypes does! While high level libraries have their place, the world needs more low level libraries. Like gpuctypes. Welcome home.

### Installation

```sh
pip install gpuctypes
```

### Usage

```py
import gpuctypes.hip as hip
import gpuctypes.cuda as cuda
import gpuctypes.opencl as opencl
```

### Current versions

* ROCm 5.7.1
* CUDA 11.5
* OpenCL whatever is in Ubuntu 22.04