"""Exact conditional retarget of a spatial mixture of supplied scalar curves.

Use only when the actual operator is known to blend these curves with fixed,
nonnegative spatial weights in one identified scalar coordinate. This is not
a model of the entire consumer, its half arithmetic, or a calibrated camera.
Call on the macOS runner for images. This small scalar API permits auditing
one pixel's complete curve preimage without constructing image-size arrays.
"""
from fractions import Fraction
from bisect import bisect_left,bisect_right
import math

def _q(value):
 if isinstance(value,Fraction):return value
 return Fraction.from_float(float(value))

def _outward(value,up):
 result=float(value);delta=Fraction.from_float(result)-value
 return math.nextafter(result,math.inf if up else -math.inf) if (up and delta<0) or (not up and delta>0) else result

def _inverse(table,knots,value,right):
 index=(bisect_right if right else bisect_left)(table,value)
 if index==0:return knots[0]
 if index==len(table):return knots[-1]
 return knots[index-1]+(value-table[index-1])*(knots[index]-knots[index-1])/(table[index]-table[index-1])

def _evaluate(table,knots,value):
 index=bisect_right(knots,value)
 if index==0:return table[0]
 if index==len(knots):return table[-1]
 return table[index-1]+(value-knots[index-1])*(table[index]-table[index-1])/(knots[index]-knots[index-1])

def retarget_curve_point(observed,knots,applied_curves,neutral_curves,weights,*,coordinate_space,storage='exact',forward_error_abs=0):
 """Return the entire scalar input/neutral-output interval, blend FIRST.

 Supplied dyadic floats (or Fractions) are treated as exact real values.
 Curves share knots and clamp at the outer edges. ``forward_error_abs`` must
 bound actual evaluation error for both supplied models; no native Metal
 error contract is inferred. A candidate is emitted only when the exact
 interval permits a maximum relative error <=1/1000. Endpoint clamp can leave
 the original input unbounded even when the neutral output stays bounded.
 """
 if not coordinate_space or not isinstance(coordinate_space,str):raise ValueError('An identified application coordinate is required')
 if storage not in ('exact','float16','float32'):raise ValueError('Unknown observation storage')
 if not math.isfinite(float(observed)):return {'valid':False,'reason':'nonfinite observation; no finite-path assumption'}
 X=list(map(_q,knots));W=list(map(_q,weights));E=_q(forward_error_abs)
 if len(X)<2 or any(b<=a for a,b in zip(X,X[1:])):raise ValueError('Strictly increasing common knots required')
 if E<0 or any(w<0 for w in W) or not W or sum(W)<=0:raise ValueError('Nonnegative weights and error bound required')
 if len(applied_curves)!=len(W) or len(neutral_curves)!=len(W):raise ValueError('One paired curve per fixed spatial weight required')
 def blend(tables):
  Q=[list(map(_q,row)) for row in tables]
  if any(len(row)!=len(X) or any(b<a for a,b in zip(row,row[1:])) for row in Q):raise ValueError('Matching finite monotone curve tables required')
  return [sum((w*row[k] for w,row in zip(W,Q)),Fraction()) for k in range(len(X))]
 F=blend(applied_curves);G=blend(neutral_curves);Y=_q(observed)
 if storage=='exact':ql,qh=Y-E,Y+E
 else:
  import numpy as np
  dtype=np.dtype(storage);v=np.array(float(observed),dtype=dtype)
  if not np.isfinite(v):return {'valid':False,'reason':'observation overflow in declared storage'}
  lo=np.nextafter(v,np.array(-np.inf,dtype=dtype));hi=np.nextafter(v,np.array(np.inf,dtype=dtype));q=_q(float(v))
  ql=(_q(float(lo))+q)/2-E if np.isfinite(lo) else F[0]-1-E
  qh=(_q(float(hi))+q)/2+E if np.isfinite(hi) else F[-1]+1+E
 if qh<F[0] or ql>F[-1]:return {'valid':False,'reason':'observation outside declared curve range'}
 low_edge=ql<=F[0];high_edge=qh>=F[-1]
 xl=_inverse(F,X,max(F[0],ql),False);xh=_inverse(F,X,min(F[-1],qh),True)
 gl=_evaluate(G,X,xl)-E;gh=_evaluate(G,X,xh)+E
 estimate=2*gl*gh/(gl+gh) if gl*gh>0 else (gl+gh)/2
 # Test the actual exported float candidate, not only the exact minimax root.
 chosen=float(estimate);actual=_q(chosen);guaranteed=gl>0 and max(abs(actual-gl)/gl,abs(actual-gh)/gh)<=Fraction(1,1000)
 radius=(gh-gl)/(gh+gl) if gl>0 else None
 return {'valid':True,'input_lower':-math.inf if low_edge else _outward(xl,False),'input_upper':math.inf if high_edge else _outward(xh,True),'neutral_lower':_outward(gl,False),'neutral_upper':_outward(gh,True),'candidate':chosen if guaranteed else None,'minimax_estimate':chosen,'guaranteed_1e3':guaranteed,'relative_minimax_radius_upper':_outward(radius,True) if radius is not None else None,'plateau':any(a==b and ql<=a<=qh for a,b in zip(F,F[1:])),'endpoint_low':low_edge,'endpoint_high':high_edge,'coordinate_space':coordinate_space,'weights_exact_sum':str(sum(W)),'camera_inverse_verified':False,'full_consumer_domain_certified':False,'scope':'Exact rational conditional scalar curve mixture; actual native weights/curves/domain/evaluation bound must be supplied'}
