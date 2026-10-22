"""The actual renderer's adjusted-SRL-parameter branch, not a pixel gain.

iPhone17,3/24A446 CMImaging _getAdjustedSrlCurveParameter reads curve f32 at
self+0x598 and uint32 adjustment at self+0x5a0. Values outside the open (0,1)
interval, including NaNs, return -1. Otherwise uint32->f32 then f32 addition.
The meaning/producer of the adjustment field remains a separate dependency.
"""
from __future__ import annotations
import numpy as np


def adjust_parameter(curve: float, adjustment: int) -> np.float32:
    if not isinstance(adjustment,(int,np.integer)) or not 0<=int(adjustment)<=0xffffffff:
        raise ValueError('Adjustment must preserve its original uint32 type')
    x=np.float32(curve)
    if not (x>np.float32(0) and x<np.float32(1)):
        return np.float32(-1)
    return np.add(x,np.float32(int(adjustment)),dtype=np.float32)
