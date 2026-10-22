"""One post-scene internal SSRParams.color f32 control, never a UI mapping."""
from dataclasses import dataclass,replace
import numpy as np
from complete_forward import Context

INDEX=3
BYTE_OFFSET=12


@dataclass(frozen=True)
class Color:
    raw: np.float32

    def __post_init__(self):
        if type(self.raw)is not np.float32 or not np.isfinite(self.raw)or not 0<=self.raw<=1:raise TypeError('Explicit finite post-scene f32 color in[0,1] required; no UI calibration')

    @property
    def half(self):return np.float16(self.raw)

    @property
    def gain(self):return np.float16(np.float16(self.half*self.half)+np.float16(1))

    def record(self):return {'raw_f32':float(self.raw),'raw_f32_bits':int(self.raw.view('u4')),'half357':float(self.half),'half357_bits':int(self.half.view('u2')),'gain364':float(self.gain),'gain364_bits':int(self.gain.view('u2')),'branch':'RichSat'if self.half>0 else'smoothSat'}


def replace_color(base,color):
    if not isinstance(base,Context)or not isinstance(color,Color):raise TypeError('Validated raw context and internal color required')
    p=base.params.copy();p[INDEX]=color.raw
    return replace(base,params=p)


def half_cell(color):
    """Exact round-to-nearest-even f32 preimage of a normal positive half."""
    h=color.half;bits=int(h.view('u2'))
    if not 0x400<bits<0x3bff:raise ValueError('Normal positive interior half bin required')
    lower=(float(np.nextafter(h,np.float16(-np.inf)))+float(h))/2;upper=(float(h)+float(np.nextafter(h,np.float16(np.inf))))/2;closed=bits%2==0
    first=np.float32(lower)if closed else np.nextafter(np.float32(lower),np.float32(np.inf));last=np.float32(upper)if closed else np.nextafter(np.float32(upper),np.float32(-np.inf))
    return {'lower_real':lower,'upper_real':upper,'lower_closed':closed,'upper_closed':closed,'first_f32_bits':int(first.view('u4')),'last_f32_bits':int(last.view('u4')),'f32_values':int(last.view('u4'))-int(first.view('u4'))+1,'same_half_bits':bits,'assumption':'IEEE round-to-nearest-even f32 to half; static callsites plus finite host witnesses, not GPU certification'}
