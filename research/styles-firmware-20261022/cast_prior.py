"""Conditional CMImaging cast-table interpolation, iPhone17,3/24A446.

Inputs are normalized tone/color/intensity and an explicitly selected table,
startup and monochrome context. Cast-name/dictionary construction is separate.
The result is a three-by-four coefficient layout; the separately verified
enqueue packing transposes it into shader term-major order. It is not EV.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
import math
import numpy as np
from numpy.typing import NDArray
from gtc_texture import round_nonnegative_fraction_f32

F32=NDArray[np.float32]


def fused_f32(a: float,b: float,c: float) -> np.float32:
    """Reuse exact RN-even rounding from GTC; extend sign and exact-zero sign."""
    a,b,c=map(float,(np.float32(a),np.float32(b),np.float32(c)))
    if not all(map(math.isfinite,(a,b,c))):raise ValueError('Finite FMA operands required')
    value=Fraction(a)*Fraction(b)+Fraction(c)
    if not value:return np.float32(math.fma(a,b,c))
    sign=-1 if value<0 else 1
    return np.float32(sign*round_nonnegative_fraction_f32(abs(value)))


@dataclass(frozen=True)
class CastControls:
    tone: float
    color: float
    intensity: float
    prior_strength: float=1.

    def array(self) -> F32:
        x=np.array([self.tone,self.color,self.intensity,self.prior_strength],dtype='f4')
        # This finite budget is our declared model domain, not an Apple guard.
        if not np.isfinite(x).all() or np.max(np.abs(x[:3]))>16 or abs(float(x[3]))>8:
            raise ValueError('Finite controls budget: axes <=16, strength <=8')
        return x


@dataclass(frozen=True)
class CastTable:
    values: F32

    def __post_init__(self):
        a=np.array(self.values,dtype='f4',copy=True)
        if a.shape!=(5,5,2,3,4) or not np.isfinite(a).all() or np.max(abs(a))>64:
            raise ValueError('Need finite bounded [tone5,color5,intensity2,3,4] table')
        a.flags.writeable=False;object.__setattr__(self,'values',a)


@dataclass(frozen=True)
class PriorResult:
    memory_vectors: F32
    output_coefficients: F32
    lower_indices: tuple[int,int,int] | None
    fractions: tuple[float,float,float] | None
    native_GPU_verified: bool=False
    full_camera_inverse_verified: bool=False

    def shader_prior_matrix(self) -> F32:
        """enqueue 0x1d42e66cc..6704: row=g%3, column=g//3."""
        return self.output_coefficients.T.copy().reshape(12)


def base_memory(monochrome: bool) -> F32:
    standard=np.zeros((3,4),dtype='f4')
    if monochrome:standard[:,1:]=np.float32(1/3)
    else:standard[:,1:]=np.eye(3,dtype='f4')
    return standard.T.copy().reshape(3,4)


def convert_memory(memory: F32,monochrome: bool) -> F32:
    """Complete _ssccmpg_float3x4FromMatrix arithmetic and lane ordering."""
    columns=np.asarray(memory,dtype='f4').reshape(4,3).copy()
    if monochrome:
        for i,column in enumerate(columns):
            scaled=np.multiply(column,np.float32(1/3),dtype=np.float32)
            mean=np.add(np.add(scaled[0],scaled[1],dtype=np.float32),scaled[2],dtype=np.float32)
            columns[i]=mean
    return columns.T.copy()


def interpolate(controls: CastControls,table: CastTable | None,*,monochrome: bool=False) -> PriorResult:
    tone,color,intensity,strength=controls.array()
    base=base_memory(monochrome)
    if table is None:
        # The actual no-table branch returns the base without strength blending.
        return PriorResult(base,convert_memory(base,monochrome),None,None)
    tc=np.minimum(np.maximum(np.array([tone,color],dtype='f4'),np.float32(-1)),np.float32(1))
    normalized=np.multiply(np.add(tc,np.float32(1),dtype=np.float32),np.float32(.5),dtype=np.float32)
    coordinate=np.r_[np.multiply(normalized,np.float32(4),dtype=np.float32),np.minimum(np.maximum(intensity,np.float32(0)),np.float32(1))].astype('f4')
    lower=np.floor(coordinate).astype('i4');upper=np.minimum(lower+1,[4,4,1])
    fractions=np.minimum(np.subtract(coordinate,lower.astype('f4'),dtype=np.float32),np.float32(float.fromhex('0x1.fffffep-1')))
    def mix(a,b,w):
        delta=np.subtract(b,a,dtype=np.float32)
        return np.array([fused_f32(d,w,x)for d,x in zip(delta.flat,a.flat)],dtype='f4').reshape(a.shape)
    # The original FMA order is intensity, then color, then tone.
    a=[]
    for ti in (lower[0],upper[0]):
        colors=[mix(table.values[ti,ci,lower[2]],table.values[ti,ci,upper[2]],fractions[2]) for ci in (lower[1],upper[1])]
        a.append(mix(colors[0],colors[1],fractions[1]))
    sampled=mix(a[0],a[1],fractions[0]);blended=mix(base,sampled,strength)
    return PriorResult(blended,convert_memory(blended,monochrome),tuple(map(int,lower)),tuple(map(float,fractions)))
