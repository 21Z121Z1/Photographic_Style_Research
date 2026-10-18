"""Build/device-specific numerical primitives for the unchanged AIR algebra.

Tables enumerate complete primitive input domains, independently of photographs.
Unsupported active inputs retain the baseline formula and are counted; no
primitive exactness is claimed for them. Full image conformance is measured.
"""
from pathlib import Path
from collections import OrderedDict,Counter
import hashlib,json,os,zlib
import numpy as np
from air_numpy import Executor,V

class AtanTable:
 def __init__(self,path,cache_mb=96):
  self.root=Path(path);self.meta=json.loads((self.root/'manifest.json').read_text());self.rows={(r['delta_exponent'],r['quadrant']):r for r in self.meta['rows']};self.cache=OrderedDict();self.cached_bytes=0;self.max_bytes=cache_mb*1024*1024
 def load(self,key):
  if key in self.cache:self.cache.move_to_end(key);return self.cache[key]
  while self.cache and self.cached_bytes+2*1024*1024>self.max_bytes:
   _,old=self.cache.popitem(last=False);self.cached_bytes-=old.nbytes
  row=self.rows[key];data=(self.root/row['file']).read_bytes();assert hashlib.sha256(data).hexdigest()==row['compressed_sha256'];raw=zlib.decompress(data);first=np.frombuffer(raw,'<u2',1024);delta=np.frombuffer(raw,row['delta_dtype'],offset=2048).reshape(1024,1024)
  out=np.empty((1024,1024),'<u2');np.cumsum(delta,axis=1,dtype=np.int64,out=out);out+=first[:,None]
  assert hashlib.sha256(memoryview(out)).hexdigest()==row['raw_f16_sha256'];self.cache[key]=out;self.cached_bytes+=out.nbytes;return out
 def __getitem__(self,indices):
  delta,ia,ib,q=np.broadcast_arrays(*indices);out=np.empty(delta.shape,'<f2')
  for code in np.unique(delta*4+q):
   at=delta*4+q==code;key=(int(code)//4-29,int(code)%4);plane=self.load(key);out[at]=plane[ia[at],ib[at]].view('<f2')
  return out

class PowTable:
 def __init__(self,path,cache_mb=128):
  self.root=Path(path);self.meta=json.loads((self.root/'manifest.json').read_text());self.rows={(r['power_bits'],r['input_unbiased_exponent']):r for r in self.meta['rows']};self.cache=OrderedDict();self.max_bytes=cache_mb*1024*1024;self.cached_bytes=0;self.counts=Counter();self.specials={}
  for r in self.meta['specials']:
   for p,value in zip(self.meta['powers'],r['output_bits']):self.specials[(p,r['input_bits'])]=value
 def load(self,key):
  if key in self.cache:self.cache.move_to_end(key);return self.cache[key]
  row=self.rows[key];needed=row['n']*4
  while self.cache and self.cached_bytes+needed>self.max_bytes:
   _,old=self.cache.popitem(last=False);self.cached_bytes-=old.nbytes
  raw=(self.root/row['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==row['compressed_sha256']
  delta=np.frombuffer(zlib.decompress(raw),dtype='i1');assert len(delta)==row['n']and delta[0]==0
  out=np.empty(len(delta),dtype='<u4');np.cumsum(delta,dtype=np.int64,out=out);out+=np.uint32(row['first_output_bits'])
  assert hashlib.sha256(memoryview(out)).hexdigest()==row['raw_f32_sha256']
  self.cache[key]=out;self.cached_bytes+=out.nbytes;return out
 def evaluate(self,x,p,mask):
  x,p=np.broadcast_arrays(np.asarray(x,dtype='<f4'),np.asarray(p,dtype='<f4'));bits=np.ascontiguousarray(x).view('<u4');powers=np.ascontiguousarray(p).view('<u4');active=np.broadcast_to(mask.reshape((len(mask),)+(1,)*(x.ndim-1)),x.shape)
  with np.errstate(all='ignore'):out=np.power(x.astype('f8'),p.astype('f8')).astype('<f4')
  ob=out.view('<u4');covered=np.zeros(x.shape,bool);exponents=((bits>>23)&255).astype('i4')-127;mantissas=bits&0x7fffff
  for power in np.unique(powers[active]):
   at_power=powers==power
   for exponent in np.unique(exponents[at_power&active]):
    at=at_power&(exponents==exponent)&((bits>>31)==0);key=(int(power),int(exponent))
    if key in self.rows:
     values=self.load(key);ob[at]=values[mantissas[at]];covered|=at;self.counts['normal_lookups']+=int(np.count_nonzero(at&active))
   for (pbits,xbits),value in self.specials.items():
    if pbits==int(power):at=at_power&(bits==xbits);ob[at]=value;covered|=at
   # x**1 is an explicit identity lowering, not a fitted primitive table.
   if int(power)==0x3f800000:ob[at_power]=bits[at_power];covered|=at_power
  missing=active&~covered;self.counts['uncovered_active_components']+=int(np.count_nonzero(missing))
  if missing.any():
   for power,exponent in set(zip(powers[missing].tolist(),exponents[missing].tolist())):self.counts[f'missing_p{power:08x}_e{exponent}']+=1
  return out

class LookupExecutor(Executor):
 unary=None;atan=None;extra=None;pow_table=None;counts=Counter()
 def call(self,name,args,mask):
  rt=self.return_type;dt=rt.dtype()if rt.dtype()is not None else(rt.fields[0].dtype()if rt.kind=='vector'else None);op=name.split('.')[1].removeprefix('fast_')if name.startswith('air.')else''
  if name.startswith('air.fast_pow.')and dt==np.dtype('f4')and self.pow_table is not None:return self.cast(rt,self.pow_table.evaluate(args[0].d,args[1].d,mask))
  if dt==np.dtype('f2'):
   a=np.asarray(args[0].d,dtype='<f2');index={'sqrt':1,'sin':2,'cos':3,'log2':4,'exp2':5}
   if op in index and self.unary is not None:
    self.counts[op]+=int(np.count_nonzero(mask))*int(np.prod(a.shape[1:])or 1);return self.cast(rt,self.unary[np.ascontiguousarray(a).view('<u2'),index[op]])
   if self.extra is not None and op in ('exp','log','pow'):
    ai=np.ascontiguousarray(a).view('<u2')
    if op in ('exp','log'):return self.cast(rt,self.extra[ai,4 if op=='exp'else 5])
    b=np.asarray(args[1].d,dtype='<f2');x,p=np.broadcast_arrays(a,b);out=np.power(x.astype('f8'),p.astype('f8')).astype('<f2');out=np.where(p==np.float16(.5),self.extra[np.ascontiguousarray(x).view('<u2'),6],out);out=np.where(p==np.float16(1),self.extra[np.ascontiguousarray(x).view('<u2'),7],out);return self.cast(rt,out)
   if op=='atan2'and self.atan is not None:
    b=np.asarray(args[1].d,dtype='<f2');aa=np.abs(a.astype('f4'));bb=np.abs(b.astype('f4'));ma,ea=np.frexp(aa);mb,eb=np.frexp(bb);delta=ea.astype('i4')-eb.astype('i4');valid=np.isfinite(aa)&np.isfinite(bb)&(aa>0)&(bb>0)&(delta>=-29)&(delta<=29)
    ia=np.clip(np.rint(ma*2048-1024).astype('i4'),0,1023);ib=np.clip(np.rint(mb*2048-1024).astype('i4'),0,1023);quad=np.signbit(a).astype('i4')+2*np.signbit(b).astype('i4')
    out=self.atan[np.clip(delta+29,0,58),ia,ib,quad];fallback=np.arctan2(a.astype('f8'),b.astype('f8')).astype('f2');out=np.where(valid,out,fallback);axes=np.zeros(valid.shape,bool)
    if self.extra is not None:
     ai=np.ascontiguousarray(a).view('<u2');bi=np.ascontiguousarray(b).view('<u2');bz=b==0;az=a==0
     out=np.where(bz,self.extra[ai,np.where(np.signbit(b),2,0)],out);out=np.where(az&~bz,self.extra[bi,np.where(np.signbit(a),3,1)],out);axes=az|bz
    active=np.broadcast_to(mask.reshape(mask.shape+(1,)*(valid.ndim-1)),valid.shape);self.counts['atan2_canonical']+=int(np.count_nonzero(valid&active));self.counts['atan2_axes']+=int(np.count_nonzero(axes&active));self.counts['atan2_fallback']+=int(np.count_nonzero(~(valid|axes)&active));return self.cast(rt,out)
  return super().call(name,args,mask)

def setup(unary_path,atan_path,pow_path=None,extra_path=None,cache_mb=128):
 LookupExecutor.unary=np.memmap(unary_path,dtype='<f2',mode='r',shape=(65536,8));LookupExecutor.atan=AtanTable(atan_path,cache_mb)if Path(atan_path).is_dir()else np.memmap(atan_path,dtype='<f2',mode='r',shape=(59,1024,1024,4));LookupExecutor.extra=np.memmap(extra_path,dtype='<f2',mode='r',shape=(65536,8))if extra_path else None;LookupExecutor.counts=Counter();LookupExecutor.pow_table=PowTable(pow_path,cache_mb)if pow_path else None
 import forward
 forward.Executor=LookupExecutor
 return LookupExecutor
