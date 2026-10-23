"""Exact finite canonical-f32 sets with retained binary endpoint geometry.

Inclusive uint32 first/last are authoritative. No real continuum or tolerance
matching is implied; all endpoints are exactly representable binary f32.
"""
from dataclasses import dataclass
import math
import numpy as np

LAST=0x3ec00000


def raw(x):return int(np.float32(x).view('u4'))
def real(bits):return float(np.array(bits,dtype='u4').view('f4'))


@dataclass(frozen=True)
class Interval:
    first:int
    last:int
    lower:float
    upper:float
    lower_closed:bool
    upper_closed:bool

    def __post_init__(self):
        if type(self.first)is not int or type(self.last)is not int or not 0<=self.first<=self.last<=LAST:raise ValueError('Canonical finite research-domain inclusive raw f32 endpoints required')
        if type(self.lower_closed)is not bool or type(self.upper_closed)is not bool:raise TypeError('Exact endpoint inclusion booleans required')
        if any(type(x)not in(int,float)or not math.isfinite(x)or not 0<=x<=.375 or float(np.float32(x))!=x for x in [self.lower,self.upper]):raise ValueError('Exact binary-f32 real endpoints in the fixed domain required')
        lo=raw(self.lower)if self.lower_closed else raw(np.nextafter(np.float32(self.lower),np.float32(np.inf)))
        hi=raw(self.upper)if self.upper_closed else raw(np.nextafter(np.float32(self.upper),np.float32(-np.inf)))
        if (lo,hi)!=(self.first,self.last):raise ValueError('Raw endpoints disagree with real geometry/closure')

    @property
    def population(self):return self.last-self.first+1

    @classmethod
    def read(cls,d):
        result=cls(d['first_f32_bits'],d['last_f32_bits'],d['lower_real'],d['upper_real'],d['lower_closed'],d['upper_closed'])
        if 'f32_population'in d and (type(d['f32_population'])is not int or d['f32_population']!=result.population):raise ValueError('Interval population differs from exact raw endpoints')
        return result

    def record(self):
        return {'first_f32_bits':self.first,'last_f32_bits':self.last,'first_f32_hex':f'0x{self.first:08x}','last_f32_hex':f'0x{self.last:08x}','lower_real':self.lower,'upper_real':self.upper,'lower_closed':self.lower_closed,'upper_closed':self.upper_closed,'f32_population':self.population,'membership':'inclusive raw uint32 interval interpreted as canonical nonnegative f32; no continuum or nearest-value claim'}


def intersect_one(a:Interval,b:Interval):
    lo=max(a.first,b.first);hi=min(a.last,b.last)
    if lo>hi:return None
    lower=max(a.lower,b.lower);upper=min(a.upper,b.upper)
    lc=(a.lower_closed and b.lower_closed)if a.lower==b.lower else(a.lower_closed if a.lower>b.lower else b.lower_closed)
    uc=(a.upper_closed and b.upper_closed)if a.upper==b.upper else(a.upper_closed if a.upper<b.upper else b.upper_closed)
    return Interval(lo,hi,lower,upper,lc,uc)


def normalize(intervals):
    values=tuple(intervals)
    if any(not isinstance(a,Interval)for a in values):raise TypeError('Typed intervals required')
    ordered=sorted(values,key=lambda a:(a.first,a.lower,not a.lower_closed,a.last));out=[]
    for b in ordered:
        if not isinstance(b,Interval):raise TypeError('Typed intervals required')
        if not out or b.first>out[-1].last+1:out.append(b);continue
        a=out.pop();lower=min(a.lower,b.lower);upper=max(a.upper,b.upper)
        lc=(a.lower_closed or b.lower_closed)if a.lower==b.lower else(a.lower_closed if a.lower<b.lower else b.lower_closed)
        uc=(a.upper_closed or b.upper_closed)if a.upper==b.upper else(a.upper_closed if a.upper>b.upper else b.upper_closed)
        out.append(Interval(min(a.first,b.first),max(a.last,b.last),lower,upper,lc,uc))
    return tuple(out)


def intersection(left,right):
    a=normalize(left);b=normalize(right);out=[];i=j=0
    while i<len(a)and j<len(b):
        c=intersect_one(a[i],b[j])
        if c is not None:out.append(c)
        if a[i].last<b[j].last:i+=1
        else:j+=1
    return normalize(out)


def difference(left,right):
    out=[];cuts=normalize(right)
    for a in normalize(left):
        current=a
        for b in cuts:
            if current is None:break
            overlap=intersect_one(current,b)
            if overlap is None:continue
            if current.first<overlap.first:out.append(Interval(current.first,overlap.first-1,current.lower,overlap.lower,current.lower_closed,not overlap.lower_closed))
            current=Interval(overlap.last+1,current.last,overlap.upper,current.upper,not overlap.upper_closed,current.upper_closed)if overlap.last<current.last else None
        if current is not None:out.append(current)
    return normalize(out)


def intersect_all(sets):
    if not sets:raise ValueError('Explicit nonempty list of sets required')
    result=normalize(sets[0])
    for s in sets[1:]:result=intersection(result,s)
    return result


def population(intervals):return sum(a.population for a in normalize(intervals))
def records(intervals):return [a.record()for a in normalize(intervals)]
def same_members(left,right):return [(a.first,a.last)for a in normalize(left)]==[(a.first,a.last)for a in normalize(right)]
