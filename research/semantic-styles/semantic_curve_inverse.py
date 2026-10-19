"""Conditional inverse for supplied monotone local/global/semantic curves.

No j-to-EV or scene-domain calibration is inferred. Call once per operator,
with the actual curve pair and its input domain. Keep GTM/LTM/semantic stages
separate. Array work and large batches belong on the macOS runner.
"""
import numpy as np
from fractions import Fraction
from bisect import bisect_left,bisect_right

def inverse_curve_pair(observed,knots,applied,neutral,*,storage='float32',forward_error_abs=0.0):
 """Global set inverse of a clamped, piecewise-linear monotone curve pair.

 Values outside the knot domain use edge clamp, matching the replayed ARM
 interpolate helper. Endpoint plateaus therefore have unbounded *input*
 intervals. The neutral curve is clamped in the same way. This is a
 conditional curve model, never a certified inverse of the complete camera.
 ``forward_error_abs`` must bound the supplied implementation's interpolation
 error; it is not an image-acceptance tolerance.
 """
 x=np.asarray(knots,dtype='f8');f=np.asarray(applied,dtype='f8');g=np.asarray(neutral,dtype='f8');y=np.asarray(observed,dtype='f8')
 if len(x)<2 or x.ndim!=1 or f.shape!=x.shape or g.shape!=x.shape:raise ValueError('Supply matching one-dimensional knot/curve tables')
 if not (np.isfinite(x).all() and np.isfinite(f).all() and np.isfinite(g).all()):raise ValueError('Curve tables must be finite')
 if not ((np.diff(x)>0).all() and (np.diff(f)>=0).all() and (np.diff(g)>=0).all()):raise ValueError('Curves must be monotone and knots strictly increasing')
 if not np.isfinite(forward_error_abs) or forward_error_abs<0:raise ValueError('Supply a finite nonnegative implementation-error bound')
 if y.size>65536:raise ValueError('Process chunks of at most65536; use the runner for images')
 if storage not in ['float16','float32','exact']:raise ValueError('storage must be float16, float32 or exact')
 valid=np.isfinite(y)
 # Exact rational interpolation of the dyadic supplied tables, with directed
 # conversion of each final bound. This avoids treating one final nextafter
 # as proof for an entire float64 calculation.
 Q=Fraction.from_float;X=list(map(Q,x));F=list(map(Q,f));G=list(map(Q,g));E=Q(float(forward_error_abs))
 lower_x=np.empty_like(y);upper_x=np.empty_like(y);lower_y=np.empty_like(y);upper_y=np.empty_like(y);estimate=np.empty_like(y);exact_radius=np.full_like(y,np.inf);guaranteed=np.zeros_like(y,dtype=bool)
 def directed(value,up):
  v=float(value);actual=Q(v)
  if (up and actual<value) or (not up and actual>value):v=float(np.nextafter(v,np.inf if up else -np.inf))
  return v
 def inverse(v,right):
  if v<F[0]:return X[0]
  if v>F[-1]:return X[-1]
  i=bisect_right(F,v) if right else bisect_left(F,v)
  if i==0:return X[0]
  if i==len(F):return X[-1]
  return X[i-1]+(v-F[i-1])*(X[i]-X[i-1])/(F[i]-F[i-1])
 def evaluate(v):
  i=bisect_right(X,v)
  if i==0:return G[0]
  if i==len(X):return G[-1]
  return G[i-1]+(v-X[i-1])*(G[i]-G[i-1])/(X[i]-X[i-1])
 if storage in ['float16','float32']:
  q=y.astype(storage);previous=np.nextafter(q,np.array(-np.inf,dtype=storage),dtype=np.dtype(storage)).astype('f8');following=np.nextafter(q,np.array(np.inf,dtype=storage),dtype=np.dtype(storage)).astype('f8');quantized=q.astype('f8')
  valid&=np.isfinite(quantized)
 flat_values=[F[i] for i in range(len(F)-1) if F[i]==F[i+1]];plateau=np.zeros_like(y,dtype=bool);endpoint_low=np.zeros_like(y,dtype=bool);endpoint_high=np.zeros_like(y,dtype=bool)
 for i in range(y.size):
  if not valid.flat[i]:
   lower_x.flat[i]=upper_x.flat[i]=lower_y.flat[i]=upper_y.flat[i]=np.nan;continue
  if storage=='exact':ql=Q(float(y.flat[i]))-E;qh=Q(float(y.flat[i]))+E
  else:
   # End representable types may have infinite neighbors. The supplied finite
   # curve range clips these infinite quantization cells conservatively.
   ql=(Q(float(previous.flat[i]))+Q(float(quantized.flat[i])))/2-E if np.isfinite(previous.flat[i]) else F[0]-1
   qh=(Q(float(following.flat[i]))+Q(float(quantized.flat[i])))/2+E if np.isfinite(following.flat[i]) else F[-1]+1
  if qh<F[0] or ql>F[-1]:
   valid.flat[i]=False;lower_x.flat[i]=upper_x.flat[i]=lower_y.flat[i]=upper_y.flat[i]=np.nan;continue
  plateau.flat[i]=any(ql<=v<=qh for v in flat_values);endpoint_low.flat[i]=ql<=F[0];endpoint_high.flat[i]=qh>=F[-1]
  xl=inverse(max(ql,F[0]),False);xh=inverse(min(qh,F[-1]),True);gl=evaluate(xl)-E;gh=evaluate(xh)+E
  lower_x.flat[i]=directed(xl,False);upper_x.flat[i]=directed(xh,True);lower_y.flat[i]=directed(gl,False);upper_y.flat[i]=directed(gh,True)
  chosen=2*gl*gh/(gl+gh) if gl*gh>0 else (gl+gh)/2;estimate.flat[i]=float(chosen)
  if gl>0:
   radius=(gh-gl)/(gh+gl);exact_radius.flat[i]=directed(radius,True);actual=Q(float(estimate.flat[i]));guaranteed.flat[i]=max(abs(actual-gl)/gl,abs(actual-gh)/gh)<=Fraction(1,1000)
 positive=lower_y>0
 radius=exact_radius
 lower_x=np.where(endpoint_low,-np.inf,lower_x);upper_x=np.where(endpoint_high,np.inf,upper_x)
 for a in [estimate,lower_y,upper_y,lower_x,upper_x]:a[~valid]=np.nan
 guaranteed=valid&positive&guaranteed
 return {'candidate':np.where(guaranteed,estimate,np.nan),'minimax_estimate':estimate,'neutral_lower':lower_y,'neutral_upper':upper_y,'input_lower':lower_x,'input_upper':upper_x,'valid_observation_mask':valid,'plateau_mask':plateau,'endpoint_low_mask':endpoint_low,'endpoint_high_mask':endpoint_high,'near_black_mask':y<=1/255,'relative_minimax_radius':radius,'guaranteed_1e3_mask':guaranteed,'camera_inverse_verified':False,'domain':'Caller-supplied curve coordinate; not automatically scene-linear P3','storage':storage,'forward_error_abs':forward_error_abs,'bound_arithmetic':'Exact rational dyadic tables and cells; final endpoints rounded outward'}
