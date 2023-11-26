import unittest
import os
import ctypes
import gpuctypes.hip as hip
from ctypes_helpers import to_char_p_p

def expectedFailureIf(condition):
  def wrapper(func):
    if condition: return unittest.expectedFailure(func)
    else: return func
  return wrapper

CI = os.getenv("CI", "") != ""

def check(status):
  if status != 0: raise RuntimeError(f"HIP Error {status}, {ctypes.string_at(hip.hipGetErrorString(status)).decode()}")

def get_hip_bytes(arg, get_sz, get_str) -> bytes:
  sz = ctypes.c_size_t()
  check(get_sz(arg, ctypes.byref(sz)))
  mstr = ctypes.create_string_buffer(sz.value)
  check(get_str(arg, mstr))
  return ctypes.string_at(mstr, size=sz.value)

class TestHIP(unittest.TestCase):
  def test_has_methods(self):
    assert hip.hipMalloc is not None
    assert hip.hiprtcCompileProgram is not None
    assert hip.hipGetDeviceProperties is not None

  @expectedFailureIf(CI)
  def test_malloc(self):
    ptr = ctypes.c_void_p()
    check(hip.hipMalloc(ctypes.byref(ptr), 100))
    assert ptr.value != 0
    check(hip.hipFree(ptr))

  @expectedFailureIf(CI)
  def test_get_device_properties(self) -> hip.hipDeviceProp_t:
    device_properties = hip.hipDeviceProp_t()
    check(hip.hipGetDeviceProperties(device_properties, 0))
    print(device_properties.gcnArchName)
    return device_properties

  @expectedFailureIf(CI)
  def test_compile_fail(self):
    prg = "void test() { {"
    prog = hip.hiprtcProgram()
    check(hip.hiprtcCreateProgram(ctypes.pointer(prog), prg.encode(), "<null>".encode(), 0, None, None))
    status = hip.hiprtcCompileProgram(prog, 0, None)
    assert status != 0
    print(f"compile fail returned {status}")
    log = get_hip_bytes(prog, hip.hiprtcGetProgramLogSize, hip.hiprtcGetProgramLog).decode()
    assert len(log) > 10
    print(log)

  @expectedFailureIf(CI)
  def test_compile(self):
    prg = "void test() { }"
    prog = hip.hiprtcProgram()
    check(hip.hiprtcCreateProgram(ctypes.pointer(prog), prg.encode(), "<null>".encode(), 0, None, None))
    options = [f'--offload-arch={self.test_get_device_properties().gcnArchName.decode()}']
    check(hip.hiprtcCompileProgram(prog, len(options), to_char_p_p(options)))
    code = get_hip_bytes(prog, hip.hiprtcGetCodeSize, hip.hiprtcGetCode)
    assert len(code) > 10

if __name__ == '__main__':
  unittest.main()