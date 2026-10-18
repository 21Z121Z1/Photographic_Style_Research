#!/usr/bin/env python3
"""Conditional inverse with explicit information-loss masks and interval bounds.

Full-render inversion is conditional on captured maps, thumbnail, masks, stats,
LUTs and tuning remaining fixed. It does not invert their capture-time producer.
The native conformance of forward.py is a separate acceptance gate.
"""
from pathlib import Path
import argparse,json
import numpy as np
from forward import Capture,linear_thumbnail,A,B,C

def inverse_thumbnail(linear,gain,lo,hi,code_uncertainty=.5/1023):
 x=np.asarray(linear,dtype=np.float64);valid=np.isfinite(x)&(x>lo)&(x<hi)&(gain*x+B>0)
 code=np.full_like(x,np.nan);code[valid]=C+A*np.log2(gain*x[valid]+B)
 lower=linear_thumbnail(code-code_uncertainty,gain,lo,hi);upper=linear_thumbnail(code+code_uncertainty,gain,lo,hi)
 return {'code':code,'mask':valid,'lower':lower,'upper':upper,'absolute_error_bound':np.maximum(x-lower,upper-x)}

def inverse_gtc(y,nodes,domain=(1e-4,.9999)):
 """Inverse of continuous piecewise-linear CI GTC; flat/endpoint values excluded.

Native finite-precision sampler plateaus need inverse_gtc_interval, not a unique
point claim. Input nodes must be monotone; no extrapolation is performed.
"""
 nodes=np.asarray(nodes,dtype=np.float64).reshape(-1)
 if np.any(np.diff(nodes)<0):raise ValueError('Nonmonotone GTC')
 y=np.asarray(y,dtype=np.float64);grid=np.linspace(0,1,len(nodes));x=np.interp(y,nodes,grid)
 left=np.searchsorted(nodes,y,side='left');right=np.searchsorted(nodes,y,side='right')
 flat=(right-left)>1;mask=np.isfinite(y)&(y>nodes[0])&(y<nodes[-1])&~flat&(x>domain[0])&(x<domain[1])
 return x,mask

def inverse_gtc_interval(y,table,precision='float32',x_domain=(0.,1.)):
 """Certified monotone table inverse on the supplied discrete x lattice.

`table` is (x_samples, actual_forward_samples), so precision/clamp behavior is
part of the supplied oracle. This routine never claims an uncaptured native
sampler convention. Plateau intervals include both ends conservatively.
"""
 x,f=map(lambda z:np.asarray(z,dtype=np.float64),table);y=np.asarray(y,dtype=np.float64)
 if np.any(np.diff(x)<=0) or np.any(np.diff(f)<0):raise ValueError('Need ordered x and monotone forward samples')
 dtype=np.float16 if precision=='half' else np.float32;rounded=y.astype(dtype)
 tolerance=np.maximum(np.spacing(rounded).astype(float)*.5,np.finfo(dtype).smallest_subnormal*.5)
 a=np.searchsorted(f,y-tolerance,side='left');b=np.searchsorted(f,y+tolerance,side='right')
 lower=x[np.clip(a-1,0,len(x)-1)];upper=x[np.clip(b,0,len(x)-1)]
 lower=np.where(a==0,x_domain[0],lower);upper=np.where(b==len(x),x_domain[1],upper)
 return {'lower':lower,'upper':upper,'midpoint':(lower+upper)/2,'absolute_error_bound':(upper-lower)/2,'mask':(a>0)&(b<len(x))&(a<b),'endpoint_mask':(a==0)|(b==len(x))}

def semantic_primary_forward(primary, anchor, person, nodes, params):
 """Continuous semantic-tone component, with all external context fixed.

This algebra removes a ratio only for primary >= 1/255. It keeps the native
near-black branch separately. Half rounding is provided by forward.py AIR.
 """
 from forward import semantic_tone
 return semantic_tone(np.asarray(anchor),np.asarray(primary),np.asarray(person),nodes,params)

def inverse_semantic_primary(y,anchor,person,nodes,params,domain=(1/255,1.25)):
 """Exact piecewise-affine inverse of continuous semantic tone, conditional on S.

Foreground/background breakpoint candidates are checked before accepting a
solution. Zero slopes return an information-loss mask, not a fabricated RGB.
 """
 bg,fg,be,fe,g,hr,phr=np.asarray(params,dtype=float);anchor=np.asarray(anchor,dtype=float);y=np.asarray(y,dtype=float);m=np.asarray(person,dtype=float)[...,None]
 if any(v<0 or v>1 for v in [bg,fg,g,hr,phr]):raise ValueError('This monotone inverse requires LTM/GTC/HR amounts in [0,1]')
 def curve(exposure):
  x=np.minimum(exposure*anchor,1);return x+(np.interp(x,np.linspace(0,1,len(nodes)),nodes)-x)*g
 tb,tf=curve(be),curve(fe);out=np.full_like(y,np.nan);chosen_slope=np.zeros_like(y);matches=np.zeros_like(y,dtype=int)
 for above_bg in [False,True]:
  for above_fg in [False,True]:
   sb=bg if above_bg else bg+hr*(1-bg);ib=(1-bg)*tb*(1 if above_bg else 1-hr)
   sf=fg if above_fg else fg+phr*(1-fg);iff=(1-fg)*tf*(1 if above_fg else 1-phr)
   slope=(1-m)*sb+m*sf;intercept=(1-m)*ib+m*iff
   x=np.divide(y-intercept,slope,out=np.full_like(y,np.nan),where=slope>1e-10)
   good=np.isfinite(x)&(x>=domain[0])&(x<=domain[1])&((x>=tb) if above_bg else (x<tb))&((x>=tf) if above_fg else (x<tf))
   out[good]=x[good];chosen_slope[good]=np.broadcast_to(slope,y.shape)[good];matches+=good
 mask=np.all(matches==1,axis=-1);replayed=semantic_primary_forward(out,anchor,person,nodes,params);rel=np.max(np.abs(replayed-y)/np.maximum(abs(y),1e-6),axis=-1)
 scene_endpoint=np.any((be*anchor>=.9999)|(fe*anchor>=.9999)|(be*anchor<=1e-4)|(fe*anchor<=1e-4),axis=-1)
 return {'rgb':out,'mask':mask,'relative_error':rel,'slope':chosen_slope,'gtc_anchor_endpoint_mask':scene_endpoint,'note':'GTC endpoint flags information about S. It does not by itself invalidate the conditional A inverse.'}

def inverse_semantic_anchor(y,primary,person,nodes,params,domain=(0.,1.25),tolerance=1e-7):
 """Monotone interval solve for sampled S, conditional on A and all masks.

At LTM=1 the output loses S completely. HR=1 can create further plateaus. Both
are reported as broad preimage intervals even away from curve endpoints.
 """
 bg,fg,be,fe,g,hr,phr=np.asarray(params,dtype=float)
 if any(v<0 or v>1 for v in [bg,fg,g,hr,phr]):raise ValueError('Need monotone semantic-tone controls in [0,1]')
 y=np.asarray(y,dtype=float);primary=np.asarray(primary,dtype=float);lo,hi=domain
 def bound(upper):
  a=np.full_like(y,lo);b=np.full_like(y,hi)
  for _ in range(48):
   mid=(a+b)/2;f=semantic_primary_forward(primary,mid,person,nodes,params);left=(f<=y+tolerance) if upper else (f<y-tolerance);a=np.where(left,mid,a);b=np.where(left,b,mid)
  return (a+b)/2
 lower=bound(False);upper=bound(True);x=(lower+upper)/2;f=semantic_primary_forward(primary,x,person,nodes,params);relative=np.max(abs(f-y)/np.maximum(abs(y),1e-6),axis=-1)
 near_black=np.any(primary<np.float16(1/255),axis=-1);endpoint=np.any((lower<=lo+1e-6)|(upper>=hi-1e-6),axis=-1);plateau=np.any(upper-lower>1e-3,axis=-1);mask=~near_black&~endpoint&~plateau&np.isfinite(y).all(-1)
 return {'rgb':x,'mask':mask,'lower':lower,'upper':upper,'absolute_error_bound':(upper-lower)/2,'relative_error':relative,'near_black_mask':near_black,'endpoint_mask':endpoint,'plateau_mask':plateau,'unbounded_scene_ev_mask':np.any(lower<=0,axis=-1),'bound_is_conditional_on_domain':True}

def fixed_context_inverse(capture,target,indices,iterations=8,domain=(0.,1.25),relative_threshold=1e-3):
 """Damped finite-difference Newton solve of the complete NumPy AIR consumer.

The initial guess is target RGB. No original input RGB enters the solver. Mask
eligibility is fixed before solving: positive target and finite target. Numerical
Jacobian singularities are diagnostic flags; they do not remove failed pixels. Failures remain in eligible_mask; pass_mask is separate.
Absolute bounds are conservative domain-width bounds, not local-Jacobian claims.
"""
 ids=np.asarray(indices,dtype=np.int64);target=np.asarray(target,dtype=np.float64).reshape(-1,3)
 lo,hi=domain;x=np.clip(target,lo,hi);eligible=np.isfinite(target).all(1)&(target.min(1)>1/255);singular=np.zeros(len(ids),bool)
 input_texture=capture.textures['0'];original_data=input_texture.data;work=np.array(original_data,copy=True);input_texture.data=work
 def forward(v):
  flat=work.reshape(-1,work.shape[-1]);flat[ids,:3]=v.astype(np.float16)
  # Points are independent only for the recorded one-to-one input/output ROI.
  # execute uses contiguous chunks; retain groups so no pixels are silently lost.
  for start in range(0,len(ids),1024):
   group=ids[start:start+1024]
   if np.any(np.diff(group)!=1):raise ValueError('Inverse needs contiguous pixel groups')
   capture.execute(start=int(group[0]),stop=int(group[-1])+1,chunk=len(group))
  return capture.textures['13'].data.reshape(-1,4)[ids,:3].astype(np.float64)
 try:
  for step_index in range(iterations):
   f=forward(x);r=target-f
   if np.all(np.max(np.abs(r)/np.maximum(np.abs(target),1e-6),axis=1)[eligible]<=relative_threshold):break
   step=np.maximum(.004,np.abs(x)*.01);jac=np.empty((len(ids),3,3))
   for c in range(3):
    v=x.copy();v[:,c]=np.minimum(v[:,c]+step[:,c],hi);plus=forward(v);actual_step=v[:,c]-x[:,c]
    jac[:,:,c]=(plus-f)/np.maximum(actual_step[:,None],1e-12)
   sv=np.linalg.svd(jac,compute_uv=False);bad=(sv[:,-1]<.02)|~np.isfinite(sv).all(1);singular|=bad
   delta=np.einsum('nij,nj->ni',np.linalg.pinv(jac,rcond=.02),r)
   x=np.clip(x+np.clip(delta,-.1,.1),lo,hi)
  f=forward(x);relative=np.max(np.abs(f-target)/np.maximum(np.abs(target),1e-6),axis=1)
  return {'rgb':x,'eligible_mask':eligible,'pass_mask':eligible&(relative<=relative_threshold),'full_rank_observed_mask':~singular,'relative_error':relative,'near_black_mask':target.min(1)<=1/255,'singular_mask':singular,'domain_boundary_mask':np.any((x<=lo)|(x>=hi),axis=1),'absolute_error_bound':np.full_like(x,hi-lo),'unbounded_ev_mask':np.any(x<=0,axis=1),'forward_conformance_required':True}
 finally:input_texture.data=original_data

def main():
 p=argparse.ArgumentParser();p.add_argument('--capture',type=Path,required=True);p.add_argument('--air',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--limit',type=int,default=0,help='Development subset; full validation must omit');a=p.parse_args()
 c=Capture(a.capture,a.air);n=a.limit or c.h*c.w;target=np.array(c.expected.reshape(-1,4)[:n,:3]);r=fixed_context_inverse(c,target,np.arange(n));a.out.parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(a.out,**{k:v for k,v in r.items() if isinstance(v,np.ndarray)})
 mask=r['eligible_mask'];report={'pixels':n,'full_frame':n==c.w*c.h,'mask_coverage':float(mask.mean()),'max_relative_error_in_mask':float(r['relative_error'][mask].max()) if mask.any() else None,'failed_eligible_pixels':int(np.count_nonzero(mask&~r['pass_mask'])),'native_forward_verified':False,'singular_fraction':float(r['singular_mask'].mean()),'solver_scope':'conditional numerical experiment; failure is not evidence of noninvertibility','bound':'Input restricted to [0,1.25]: conservative absolute RGB error bound 1.25; no finite EV bound at zero or outside a bounded input domain.'};a.out.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
