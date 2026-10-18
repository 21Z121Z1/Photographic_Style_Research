#!/usr/bin/env python3
"""Build 26A434 consumer replay and independently readable constituent formulas.

The complete pixel program is the pinned AIR SSA in 0010.ll. NumPy executes its
42 functions using captured textures, color transforms, ROI, tuning and stats.
This is a consumer model; it is not asserted to equal the iOS capture producer.
"""
from pathlib import Path
import argparse,json,re,hashlib,time
import numpy as np
from air_numpy import Module,Executor,Type,V,Pointer,Texture

A=.08550479; B=.00964052; C=.69336945
BASIS_NAMES=['1','R','G','B','R2','RG','RB','G2','GB','B2']

def linear_thumbnail(code,gain,range_min,range_max):
 return np.clip((np.exp2((np.asarray(code,dtype=np.float64)-C)/A)-B)/gain,range_min,range_max)

def style_basis(rgb):
 r,g,b=np.moveaxis(np.asarray(rgb),-1,0)
 return np.stack([np.ones_like(r),r,g,b,r*r,r*g,r*b,g*g,g*b,b*b],axis=-1)

def load_key1(path,spotlights=(12,9),planes=8):
 x=np.fromfile(path,dtype='<f2');shape=(*spotlights,planes,10,3)
 if x.size!=np.prod(shape):raise ValueError('Coefficient size disagrees with supplied configuration')
 return x.reshape(shape) # AIR 0187: x-major spotlight index x*height+y.

def coefficient_bitmap_size(n,half=True):
 align=32 if half else 16;w=(int(np.sqrt(np.float32(n)))+align-1)//align*align
 return w,(n+w-1)//w

def make_weight_planes(rgb,planes=8,sigma=2.5,input_is_linear=False):
 h=np.asarray(rgb,dtype=np.float16)
 if input_is_linear:h=(np.sign(h)*np.sqrt(np.abs(h))).astype(np.float16)
 mean=((h[...,0]+h[...,1]).astype(np.float16)+h[...,2]).astype(np.float16)*np.float16(1/3)
 level=((mean+np.max(h,axis=-1)).astype(np.float16)*np.float16(.5)).astype(np.float16)
 centers=(np.arange(1,planes+1,dtype=np.float16)/np.float16(planes+1)).astype(np.float16)
 delta=((level[...,None]-centers).astype(np.float16)*np.float16(planes)).astype(np.float16)
 square=(delta*delta).astype(np.float16).astype(np.float32)
 return np.exp(-square/max(2*np.float32(sigma)**2,np.float32(2**-23))).astype(np.float16)

def integration_coordinates(pixel,extent,spotlight_count):
 """AIR 0186 default full learning/zoom ROI, identity transform, no GDC."""
 extent=np.asarray(extent,dtype=np.int64);count=np.asarray(spotlight_count,dtype=np.int64)
 pitch=((extent+count-1)//count+1)&~1;first=(pitch//2-1);last=first+pitch*(count-1)
 p=np.clip(np.asarray(pixel),first,last)-first
 uv=(.5+p*(count-1)/np.maximum(pitch*(count-1),1))/count
 return uv

def semantic_tone(rgb_linear_anchor,rgb_display_linear,person,gtc,params):
 """Readable float formula for AIR 0010 renderSemanticToneAdjustments.

Use the AIR executor for actual half precision and sampler behavior. params is
(bgLTM,fgLTM,bgExposureGain,fgExposureGain,GTC,HR,personHR).
"""
 bg,fg,be,fe,g,hr,phr=np.asarray(params)
 def branch(exposure,ltm,recover):
  x=np.minimum(exposure*rgb_linear_anchor,1)
  curved=np.interp(x,np.linspace(0,1,len(gtc)),gtc)
  z=x+(curved-x)*g
  ratio=np.divide(z,rgb_display_linear,out=np.zeros_like(z),where=rgb_display_linear>=np.float16(1/255))
  a=ratio+(1-ratio)*ltm;a=a+(np.minimum(a,1)-a)*recover
  return a*rgb_display_linear
 a=branch(be,bg,hr);b=branch(fe,fg,phr)
 return a+(b-a)*person[...,None]

def c_d_scalar(c,d,bg_ltm,fg_ltm,person):
 bg=d+(c-d)*bg_ltm;fg=d+(c-d)*fg_ltm
 return bg+(fg-bg)*person

class Capture:
 def __init__(self,directory,air_path):
  self.root=Path(directory);self.module=Module(air_path);self.trace=json.loads((self.root/'trace.json').read_text());self.dispatches=json.loads((self.root/'dispatches.json').read_text())
  matches=[(i,d) for i,d in enumerate(self.dispatches) if d.get('textures',{}).get('13',{}).get('ivar')=='_outputImageTexture']
  if len(matches)!=1:raise ValueError(f'Expected one final-render dispatch, found {len(matches)}')
  self.index,self.dispatch=matches[0];self.textures={};self.expected=None
  for slot,row in self.dispatch['textures'].items():
   name=row['ivar'];layout=self.trace['textures'].get(name)
   data=None
   if layout and layout.get('file'):
    shape=layout.get('shape',[layout['height'],layout['width'],layout['channels']]);data=np.memmap(self.root/layout['file'],dtype=layout['dtype'],mode='r',shape=tuple(shape))
   if slot=='13':self.expected=data;data=np.zeros_like(data)
   self.textures[slot]=Texture(data,name,slot=='13')
  self.h,self.w=self.expected.shape[:2]
  self.argmeta={}
  for line in self.module.text.splitlines():
   m=re.match(r'!\d+ = !\{i32 (\d+), (.*)\}',line)
   if not m or '!"air.arg_name"' not in line:continue
   arg=int(m.group(1));tail=m.group(2);kind='texture' if '!"air.texture"' in tail else 'buffer' if '!"air.buffer"' in tail else 'builtin'
   location=re.search(r'!"air.location_index", i32 (\d+)',tail);name=re.search(r'!"air.arg_name", !"([^"]+)"',tail)
   self.argmeta[arg]={'kind':kind,'slot':location.group(1) if location else None,'name':name.group(1)}
 def execute(self,start=0,stop=None,chunk=2048):
  stop=stop or self.h*self.w
  for begin in range(start,stop,chunk):
   end=min(begin+chunk,stop);n=end-begin;idx=np.arange(begin,end);xy=np.stack([idx%self.w,idx//self.w],axis=-1).astype(np.uint16)
   e=Executor(self.module,n);args=[]
   for k,t in self.module.functions['renderFinalAdjustments']['params']:
    meta=self.argmeta[int(k[1:])];slot=meta['slot'];name=meta['name']
    if meta['kind']=='texture':args.append(V(t,self.textures.get(slot)))
    elif meta['kind']=='buffer':
     if slot in self.dispatch['bytes']:raw=np.frombuffer((self.root/self.dispatch['bytes'][slot]).read_bytes(),np.uint8).copy()
     elif slot=='1':raw=np.frombuffer((self.root/'_paramsBuf.bin').read_bytes(),np.uint8).copy()
     elif slot=='3':raw=np.frombuffer((self.root/'_statsBuf.bin').read_bytes(),np.uint8).copy()
     else:raise ValueError('Uncaptured buffer '+slot)
     args.append(V(t,Pointer(raw)))
    elif name=='gridPos':args.append(V(t,xy))
    elif name=='tgPos':args.append(V(t,xy%np.array(self.dispatch['group'][:2],np.uint16)))
    elif name=='tgSize':args.append(V(t,np.broadcast_to(np.array(self.dispatch['group'][:2],np.uint16),(n,2))))
    else:args.append(e.const(t,'zeroinitializer',{}))
   with np.errstate(all='ignore'):e.run('renderFinalAdjustments',args)
   self.last_checkpoints=e.checkpoints
  return self.textures['13'].data

def main():
 p=argparse.ArgumentParser();p.add_argument('--capture',type=Path,required=True);p.add_argument('--air',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--chunk',type=int,default=2048);p.add_argument('--limit',type=int,default=0,help='Development only: never counts as full validation');a=p.parse_args()
 t=time.time();c=Capture(a.capture,a.air);n=a.limit or c.h*c.w;actual=c.execute(stop=n,chunk=a.chunk);a.out.parent.mkdir(parents=True,exist_ok=True);np.save(a.out,actual)
 x=actual.reshape(-1,4)[:n,:3];y=c.expected.reshape(-1,4)[:n,:3];diff=x.astype(float)-y.astype(float);mse=np.mean(diff**2)
 result={'capture':str(a.capture),'air_path':str(a.air),'air_sha256':hashlib.sha256(a.air.read_bytes()).hexdigest(),'shape':list(actual.shape),'compared_pixels':n,'full_frame':n==c.w*c.h,'half_differing_components':int(np.count_nonzero(x.view('u2')!=y.view('u2'))),'max_abs':float(np.max(np.abs(diff))),'mse':float(mse),'psnr_peak1_db':float(-10*np.log10(mse)) if mse else 'inf','elapsed_seconds':time.time()-t,'precision':'AIR half ops rounded by NumPy; fast-math fusion and transcendental approximation need native validation'}
 a.out.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
