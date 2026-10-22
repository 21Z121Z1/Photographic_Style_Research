"""Final code3 HOST point profile: system powf ->half, separate mul/add.

This models the persisted C shim's f32 math ABI and the observed final transfer
separate offset rounding. It is not a GPU profile or set arithmetic.
"""
import ctypes,platform
import numpy as np
from leaf_numeric import V,hc,select
from pixel_leaves import H


def runtime_contract():
    return {'system':platform.system(),'release':platform.release(),'machine':platform.machine(),'numpy':np.__version__,'powf_library':'/usr/lib/libSystem.B.dylib','powf_ABI':'float(float,float) then explicit IEEE half','offset':'separate half multiply SSA14 then half add SSA15; fused candidate rejected by observed checkpoints','scope':'current macOS host shim, no iOS/GPU or set guarantee'}


def forward(rgb:V):
    if not isinstance(rgb,V)or not rgb.point or rgb.precision!='h'or rgb.lo.shape!=(3,):raise TypeError('Final code3 half3 point only')
    if platform.system()!='Darwin'or platform.machine()!='arm64':raise ValueError('This host point profile requires Darwin arm64')
    lib=ctypes.CDLL('/usr/lib/libSystem.B.dylib');fn=lib.powf;fn.argtypes=[ctypes.c_float,ctypes.c_float];fn.restype=ctypes.c_float;a=rgb.abs();exponent=np.float32(hc('36aa'));p=np.array([fn(float(x),float(exponent))for x in a.lo],dtype='f4').astype('f2');power=V.value(p);offset=power*H(hc('3c38'),rgb)+H(hc('ab0a'),rgb);return select(a.gt(H(hc('1a69'),rgb)),offset,a*H(hc('4a76'),rgb))*rgb.sign()
