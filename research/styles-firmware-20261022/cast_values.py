"""Typed raw SSRCastAdjustments storage: 34 f32 scalars / 136 bytes.

This is the renderer block, not the 12-scalar cast prior matrix. Caller must
supply its actual values; no table/name-based reconstruction is assumed.
"""
from dataclasses import dataclass
import numpy as np
from leaf_numeric import V


@dataclass(frozen=True)
class CastValues:
    raw: V

    def __post_init__(self):
        if not isinstance(self.raw,V)or self.raw.precision!='f'or np.shape(self.raw.lo)!=(34,):raise TypeError('Full explicit 34-field f32 renderer block required')

    def scalar(self,index):
        offsets={0:0,1:1,2:2,3:3,4:4,5:5,9:15,10:16,11:17,15:27,16:28,17:29,18:30,19:31,20:32,21:33}
        if index not in offsets:raise ValueError('Scalar struct index required')
        return self.raw[offsets[index]]

    def array(self,index):
        start={6:6,7:9,8:12,12:18,13:21,14:24}.get(index)
        if start is None:raise ValueError('Three-scalar struct array index required')
        return self.raw[slice(start,start+3)]
