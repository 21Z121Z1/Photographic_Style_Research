"""Typed half/f32 arithmetic backends for independent small pixel operators.

Point mode rounds every declared operation. Box mode uses outward 2u arithmetic
and explicit 4u pow/sqrt assumptions; none is an Apple GPU accuracy proof.
"""
from dataclasses import dataclass
import struct
import numpy as np


class DomainUnknown(ValueError):pass


def hc(bits):return float(np.array([int(bits,16)],dtype='u2').view('f2')[0])
def fc(bits):return struct.unpack('>d',bytes.fromhex(bits))[0]


@dataclass(frozen=True)
class Truth:
    yes: np.ndarray
    no: np.ndarray


@dataclass(frozen=True)
class V:
    lo: np.ndarray
    hi: np.ndarray
    precision: str='h'
    point: bool=True

    @classmethod
    def value(cls,x,precision='h',point=True):
        a=np.asarray(x,dtype='f2'if precision=='h'else'f4').astype('f8');return cls(a,a,precision,point)

    @classmethod
    def bounds(cls,lo,hi,precision='h'):
        dtype='f2'if precision=='h'else'f4';a=np.asarray(lo,dtype=dtype).astype('f8');b=np.asarray(hi,dtype=dtype).astype('f8')
        return cls(a,b,precision,False)

    def __post_init__(self):
        if self.precision not in ('h','f')or not np.isfinite(self.lo).all()or not np.isfinite(self.hi).all()or np.any(np.asarray(self.lo)>self.hi):raise DomainUnknown('Nonfinite/unordered typed value')
        if self.point and np.any(np.asarray(self.lo)!=self.hi):raise DomainUnknown('A range cannot be labeled as a point')

    def cast(self,precision):
        dtype='f2'if precision=='h'else'f4'
        return V(np.asarray(self.lo,dtype=dtype).astype('f8'),np.asarray(self.hi,dtype=dtype).astype('f8'),precision,self.point)

    def h(self):return self.cast('h')
    def f(self):return self.cast('f')

    def box(self,x):
        if not isinstance(x,V):return V.value(x,self.precision,self.point)
        if x.precision!=self.precision or x.point!=self.point:raise TypeError('Explicit precision conversion and matching point/set backends required')
        return x

    def rounded(self,lo,hi,*,transcendental=False):
        lo=np.asarray(lo,dtype='f8');hi=np.asarray(hi,dtype='f8')
        if self.point:
            a=np.asarray(lo,dtype='f2'if self.precision=='h'else'f4').astype('f8');return V(a,a,self.precision,True)
        u=2**(-11 if self.precision=='h'else-24);tiny=2**(-24 if self.precision=='h'else-149)
        e=(4 if transcendental else 2)*u*np.maximum(abs(lo),abs(hi))+tiny
        a=np.nextafter(lo-e,-np.inf);b=np.nextafter(hi+e,np.inf)
        # Correctly rounded finite positive/negative arithmetic preserves sign.
        a=np.where(lo>=0,np.maximum(a,0),a);b=np.where(hi<=0,np.minimum(b,0),b)
        limit=65504 if self.precision=='h'else np.finfo('f4').max
        if np.any(abs(a)>limit)or np.any(abs(b)>limit):raise DomainUnknown('Finite arithmetic budget exceeded')
        return V(a,b,self.precision,False)

    def __add__(self,x):b=self.box(x);return self.rounded(self.lo+b.lo,self.hi+b.hi)
    __radd__=__add__
    def __neg__(self):return V(-self.hi,-self.lo,self.precision,self.point)
    def __sub__(self,x):return self+-self.box(x)
    def __rsub__(self,x):return self.box(x)+-self
    def __mul__(self,x):
        b=self.box(x);a=np.array([self.lo*b.lo,self.lo*b.hi,self.hi*b.lo,self.hi*b.hi]);return self.rounded(np.min(a,axis=0),np.max(a,axis=0))
    __rmul__=__mul__
    def __truediv__(self,x):
        b=self.box(x)
        if np.any((b.lo<=0)&(b.hi>=0)):raise DomainUnknown('Division interval includes zero')
        a=np.array([self.lo/b.lo,self.lo/b.hi,self.hi/b.lo,self.hi/b.hi]);return self.rounded(np.min(a,axis=0),np.max(a,axis=0))
    def __rtruediv__(self,x):return self.box(x)/self
    def __getitem__(self,index):return V(np.asarray(self.lo[index]),np.asarray(self.hi[index]),self.precision,self.point)

    def minimum(self,x):b=self.box(x);return V(np.minimum(self.lo,b.lo),np.minimum(self.hi,b.hi),self.precision,self.point)
    def maximum(self,x):b=self.box(x);return V(np.maximum(self.lo,b.lo),np.maximum(self.hi,b.hi),self.precision,self.point)
    def clamp(self,lo=0,hi=1):return self.maximum(lo).minimum(hi)
    def abs(self):return V(np.where((self.lo<=0)&(self.hi>=0),0,np.minimum(abs(self.lo),abs(self.hi))),np.maximum(abs(self.lo),abs(self.hi)),self.precision,self.point)
    def min_channels(self):return V(np.min(self.lo),np.min(self.hi),self.precision,self.point)
    def max_channels(self):return V(np.max(self.lo),np.max(self.hi),self.precision,self.point)
    def sum_channels(self):return (self[0]+self[1])+self[2]
    def sqrt(self):
        if np.any(self.lo<0):raise DomainUnknown('sqrt interval crosses negative domain')
        return self.rounded(np.sqrt(self.lo),np.sqrt(self.hi),transcendental=True)
    def pow(self,x):
        b=self.box(x)
        if np.any(self.lo<0)or np.any((self.lo==0)&(b.lo<0)):raise DomainUnknown('Unproven pow domain')
        with np.errstate(divide='ignore',invalid='ignore',over='ignore'):
            a=np.array([np.power(self.lo,b.lo),np.power(self.lo,b.hi),np.power(self.hi,b.lo),np.power(self.hi,b.hi)])
        return self.rounded(np.min(a,axis=0),np.max(a,axis=0),transcendental=True)
    def lt(self,x):b=self.box(x);return Truth(self.hi<b.lo,self.lo>=b.hi)
    def gt(self,x):b=self.box(x);return Truth(self.lo>b.hi,self.hi<=b.lo)


def select(condition: Truth,yes: V,no: V):
    if yes.precision!=no.precision or yes.point!=no.point:raise TypeError('Matching typed branches required')
    lo=np.where(condition.yes,yes.lo,np.where(condition.no,no.lo,np.minimum(yes.lo,no.lo)))
    hi=np.where(condition.yes,yes.hi,np.where(condition.no,no.hi,np.maximum(yes.hi,no.hi)))
    return V(lo,hi,yes.precision,yes.point)


def lazy_select(condition: Truth,yes,no):
    if np.all(condition.yes):return yes()
    if np.all(condition.no):return no()
    return select(condition,yes(),no())


def mix(a: V,b,w):b=a.box(b);return a+(b-a)*w
def vec(values):
    first=values[0];return V(np.array([x.lo for x in values]),np.array([x.hi for x in values]),first.precision,first.point)
def exterior(rgb: V):return (rgb.minimum(0)-1)+rgb.maximum(1)
def smoothstep(x: V):return x*x*(3-2*x)
