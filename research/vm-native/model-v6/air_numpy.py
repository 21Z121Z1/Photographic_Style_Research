#!/usr/bin/env python3
"""A deliberately bounded NumPy executor for the captured AIR SSA.

This executes the supplied text, not an inferred c/d ratio formula. Only normal
texture compute paths are supported: tile imageblocks and SIMD reductions must
be captured/replayed as separate upstream operators. Unsupported instructions
raise. The module hash and all bindings belong in the result provenance.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re,struct,json,math,os
import numpy as np


def split(s):
 out=[];start=0;stack=[];quoted=False;escaped=False
 for i,c in enumerate(s):
  if escaped:escaped=False;continue
  if c=='\\' and quoted:escaped=True;continue
  if c=='"':quoted=not quoted;continue
  if quoted:continue
  if c in '([{<':stack.append(c)
  elif c in ')]}>':
   if stack:stack.pop()
  elif c==',' and not stack:out.append(s[start:i].strip());start=i+1
 out.append(s[start:].strip());return out

@dataclass(frozen=True)
class Type:
 kind:str
 fields:tuple=()
 count:int=0
 packed:bool=False
 def dtype(self):
  return {'half':np.dtype('<f2'),'float':np.dtype('<f4'),'double':np.dtype('<f8'),'i1':np.dtype('?'),'i8':np.dtype('u1'),'i16':np.dtype('<u2'),'i32':np.dtype('<u4'),'i64':np.dtype('<u8')}.get(self.kind)
 def align(self):
  if self.dtype() is not None:return self.dtype().itemsize
  if self.kind=='ptr':return 8
  if self.kind=='vector':return (4 if self.count==3 else self.count)*self.fields[0].align()
  if self.kind=='array':return self.fields[0].align()
  return 1 if self.packed else max((t.align() for t in self.fields),default=1)
 def size(self):
  if self.dtype() is not None:return self.dtype().itemsize
  if self.kind=='ptr':return 8
  if self.kind=='vector':return self.align()
  if self.kind=='array':return self.count*self.fields[0].size()
  n=0
  for t in self.fields:
   a=1 if self.packed else t.align();n=(n+a-1)//a*a+t.size()
  a=self.align();return (n+a-1)//a*a
 def offsets(self):
  n=0;out=[]
  for t in self.fields:
   a=1 if self.packed else t.align();n=(n+a-1)//a*a;out.append(n);n+=t.size()
  return out
 def shape(self):
  if self.kind in ('vector','array'):return (self.count,)+self.fields[0].shape()
  return ()

@dataclass
class V:
 t:Type
 d:object
 product:object=None

@dataclass
class Pointer:
 memory:object
 offset:object=0

@dataclass
class Texture:
 data:object
 name:str=''
 output:bool=False

FLAGS=re.compile(r'^(?:(?:fast|reassoc|nnan|ninf|nsz|arcp|contract|afn|nuw|nsw|exact|inbounds|noundef|nonnull|readonly|readnone|writeonly|zeroext|signext|nocapture|immarg|inreg|returned|swiftself|byval|fastcc|coldcc|tail|musttail)\s+|(?:align|dereferenceable)\s*(?:\(\d+\)|\d+)\s*|captures\([^)]*\)\s*|"[^"]+"\s*)+')
def clean(s):
 while True:
  n=FLAGS.sub('',s.strip(),count=1)
  if n==s.strip():return n
  s=n

class Module:
 def __init__(self,path):
  self.path=Path(path);self.text=self.path.read_text();self.named={};self.functions={};self.globals={};self.cache={}
  self.structtext=dict(re.findall(r'^(%(?:"[^"]+"|[^ ]+)) = type (.+)$',self.text,re.M))
  for name in self.structtext:self.named_type(name)
  for m in re.finditer(r'^(@(?:"[^"]+"|[^ ]+)) = (.+)$',self.text,re.M):self.globals[m[1]]=m[2]
  for m in re.finditer(r'^define (.+?) @((?:"[^"]+")|[^ (]+)\(([^\n]*)\)[^\n]*\{\n(.*?)^}',self.text,re.M|re.S):
   prefix,name,args,body=m.groups();params=[]
   for arg in split(args):
    if not arg:continue
    t,rest=self.type(arg);key=re.search(r'(%(?:\d+|[A-Za-z_][\w.]*))$',rest.strip())
    if key:params.append((key.group(1),t))
   first=str(max([int(k[1:]) for k,t in params if k[1:].isdigit()]+[-1])+1);blocks={first:[]};label=first;pending=''
   for line in body.splitlines():
    line=line.split(';')[0].strip()
    if not line:continue
    match=re.match(r'([\w.]+):',line)
    if match:label=match[1];blocks[label]=[];continue
    if pending:
     pending+=' '+line
     if line==']':blocks[label].append(pending);pending=''
     continue
    if line.startswith('switch '):pending=line;continue
    blocks[label].append(line)
   self.functions[name.strip('"')]={'params':params,'blocks':blocks,'first':first,'prefix':prefix}
 def named_type(self,name):
  if name not in self.named:self.named[name]=self.type(self.structtext[name])[0]
  return self.named[name]
 def type(self,s):
  s=s.strip();key=s
  if key in self.cache:return self.cache[key]
  if s.startswith('ptr'):
   m=re.match(r'ptr(?: addrspace\(\d+\))?',s);r=(Type('ptr'),s[m.end():].strip())
  elif s.startswith('%'):
   m=re.match(r'%(?:"[^"]+"|[^ ,)]+)',s);r=(self.named_type(m.group()),s[m.end():].strip())
  elif s.startswith('<{') or s.startswith('{'):
   packed=s.startswith('<{');op=2 if packed else 1;end='}>' if packed else '}';depth=1;i=op
   while i<len(s):
    if s[i]=='{':depth+=1
    if s[i]=='}':
     depth-=1
     if depth==0:break
    i+=1
   fields=tuple(self.type(x)[0] for x in split(s[op:i]));r=(Type('struct',fields,packed=packed),s[i+len(end):].strip())
  elif s.startswith('<') or s.startswith('['):
   kind='vector' if s[0]=='<' else 'array';close='>' if kind=='vector' else ']';depth=1;i=1
   while depth:
    if s[i]==s[0]:depth+=1
    if s[i]==close:depth-=1
    i+=1
   m=re.match(r'(\d+) x (.*)',s[1:i-1]);r=(Type(kind,(self.type(m.group(2))[0],),int(m.group(1))),s[i:].strip())
  else:
   m=re.match(r'(void|half|float|double|i\d+|label)\b',s)
   if not m:raise ValueError('TYPE '+s[:200])
   r=(Type(m.group(1)),s[m.end():].strip())
  self.cache[key]=r;return r

class Executor:
 def __init__(self,module,n,function_constants=None):
  self.m=module;self.n=n;self.fc=function_constants or {};self.global_memory={};self.opcount=0;self.texture_calls=0;self.checkpoints={};self.trace_function=os.environ.get('AIR_TRACE_FUNCTION','renderFinalAdjustments');self.fusion=int(os.environ.get('AIR_FUSION','1'))
 def array(self,t,x):
  a=np.asarray(x,dtype=t.dtype() if t.dtype() is not None else (t.fields[0].dtype() if t.kind in ('vector','array') else None))
  return np.broadcast_to(a,(self.n,)+a.shape)
 def const(self,t,s,env):
  s=clean(s).strip()
  if s.startswith('%'):return env[s]
  if s.startswith('@'):
   if s not in self.global_memory:
    desc=self.m.globals.get(s,'');match=re.search(r'(?:global|constant) (.*?)(?:, (?:align|section)|$)',desc)
    gt,gs=self.m.type(match.group(1)) if match else (Type('i32'),'0')
    if s in self.fc:raw=self.fc[s]
    elif '.MTL_FC_INIT_' in s:raw=self.fc.get(s.split('.MTL_FC_INIT_')[0],0)
    elif 'useImageBlock' in s:raw=0
    elif 'useSrlVersion' in s:raw=0
    else:
     desc=self.m.globals.get(s,'');match=re.search(r'(?:global|constant) (.*?)(?:, (?:align|section)|$)',desc)
     if match:
      gt,gs=self.m.type(match.group(1));raw=self.const(gt,gs,{}).d[0]
     else:raise ValueError('GLOBAL '+s)
    if isinstance(raw,(int,float,np.number)):buf=np.asarray([raw],dtype=gt.dtype() or np.uint8).tobytes()
    else:buf=np.asarray(raw).tobytes()
    self.global_memory[s]=np.frombuffer(buf,dtype=np.uint8).copy()
   return V(t,Pointer(self.global_memory[s]))
  if t.kind=='ptr':return V(t,None)
  if t.kind=='struct':
   if s in ('undef','poison','zeroinitializer'):return V(t,tuple(self.const(q,'zeroinitializer' if s=='zeroinitializer' else 'undef',env) for q in t.fields))
   q=s.strip('{} ');return V(t,tuple(self.typed(x,env) for x in split(q)))
  if s in ('zeroinitializer','null'):return V(t,self.array(t,np.zeros(t.shape(),dtype=t.dtype() or t.fields[0].dtype())))
  if s in ('undef','poison'):return V(t,self.array(t,np.full(t.shape(),np.nan if (t.dtype() or t.fields[0].dtype()).kind=='f' else 0)))
  if s.startswith('splat ('):
   v=self.typed(s[7:-1],env);return V(t,np.broadcast_to(v.d.reshape(self.n,1),(self.n,t.count)))
  if s.startswith('<') or s.startswith('['):
   vals=[self.typed(x,env).d for x in split(s[1:-1])];return V(t,np.stack(vals,axis=1))
  if s in ('true','false'):x=int(s=='true')
  elif re.match(r'f0x[0-9A-Fa-f]+$',s):x=struct.unpack('>f',bytes.fromhex(s[3:].zfill(8)))[0]
  elif s.startswith('0xH'):x=np.frombuffer(bytes.fromhex(s[3:]),dtype='>f2')[0]
  elif s.startswith('0x'):x=struct.unpack('>d',bytes.fromhex(s[2:].zfill(16)))[0] if (t.dtype() or np.dtype(float)).kind=='f' else int(s,16)
  else:x=float(s) if '.' in s or 'e' in s.lower() else int(s)
  if (t.dtype() or np.dtype('f')).kind=='u':x=int(x)%(1<<(8*t.dtype().itemsize))
  return V(t,self.array(t,x))
 def typed(self,s,env):
  t,r=self.m.type(s);return self.const(t,r,env)
 def cast(self,t,data):
  if t.kind=='ptr':return V(t,data)
  dt=t.dtype() if t.dtype() is not None else t.fields[0].dtype()
  return V(t,np.asarray(data).astype(dt))
 def gep(self,t,p,indices):
  off=p.offset;cur=t
  for j,v in enumerate(indices):
   index=int(v.d[0]) if np.all(v.d==v.d[0]) else v.d.astype(np.int64)
   if j==0:off=off+index*cur.size()
   elif cur.kind=='struct':
    if not isinstance(index,int):raise ValueError('Divergent struct index')
    off=off+cur.offsets()[index];cur=cur.fields[index]
   elif cur.kind in ('array','vector'):off=off+index*cur.fields[0].size();cur=cur.fields[0]
   else:off=off+index*cur.size()
  return Pointer(p.memory,off)
 def load(self,t,p):
  if t.kind=='struct':return V(t,tuple(self.load(q,Pointer(p.memory,np.asarray(p.offset)+o)) for q,o in zip(t.fields,t.offsets())))
  if t.kind in ('array','vector'):
   stride=t.fields[0].size() if t.kind=='array' else t.fields[0].dtype().itemsize
   vals=[self.load(t.fields[0],Pointer(p.memory,np.asarray(p.offset)+i*stride)).d for i in range(t.count)]
   return V(t,np.stack(vals,axis=1))
  dt=t.dtype();mem=p.memory;offset=np.asarray(p.offset)
  if mem.ndim==1:
   vals=np.frombuffer(mem.data,dtype=dt,count=len(mem)//dt.itemsize)
   if np.any(offset%dt.itemsize):raise ValueError('Unaligned load')
   a=vals[(offset//dt.itemsize).astype(np.int64)];return V(t,np.broadcast_to(a,(self.n,)))
  off=np.broadcast_to(offset,(self.n,)).astype(np.int64)
  raw=mem[np.arange(self.n)[:,None],off[:,None]+np.arange(dt.itemsize)[None,:]].copy();return V(t,raw.view(dt).reshape(self.n))
 def store(self,value,p,mask):
  t=value.t
  if t.kind=='struct':
   for q,o in zip(value.d,t.offsets()):self.store(q,Pointer(p.memory,np.asarray(p.offset)+o),mask)
   return
  if t.kind in ('array','vector'):
   stride=t.fields[0].size() if t.kind=='array' else t.fields[0].dtype().itemsize
   for i in range(t.count):self.store(V(t.fields[0],value.d[:,i]),Pointer(p.memory,np.asarray(p.offset)+i*stride),mask)
   return
  dt=t.dtype();mem=p.memory;off=np.asarray(p.offset);raw=np.ascontiguousarray(value.d).view(np.uint8).reshape(self.n,dt.itemsize)
  if mem.ndim==1:
   v=value.d[mask]
   if not np.all(v==v[0]):raise ValueError('Divergent global buffer store')
   i=int(off.flat[0]);mem[i:i+dt.itemsize]=raw[np.flatnonzero(mask)[0]]
  else:
   indices=np.flatnonzero(mask);o=np.broadcast_to(off,(self.n,))[mask].astype(np.int64);mem[indices[:,None],o[:,None]+np.arange(dt.itemsize)]=raw[mask]
 def call(self,name,args,mask):
  if name in self.m.functions:return self.run(name,args,mask)
  if name.startswith('llvm.lifetime') or name=='llvm.assume':return None
  if name.startswith('llvm.memset'):
   ptr=args[0].d;count=int(args[2].d[0]);byte=int(args[1].d[0]);off=int(np.asarray(ptr.offset).flat[0])
   if ptr.memory.ndim==2:ptr.memory[mask,off:off+count]=byte
   else:ptr.memory[off:off+count]=byte
   return None
  if not name.startswith('air.'):raise NotImplementedError(name)
  a=[v.d for v in args];base=name.split('.')[1];rt=self.return_type
  if base in ('is_null_texture_2d','is_null_texture_3d'):return self.cast(rt,np.full(self.n,a[0] is None))
  if base.startswith('get_width_texture'):return self.cast(rt,np.full(self.n,a[0].data.shape[1]))
  if base.startswith('get_height_texture'):return self.cast(rt,np.full(self.n,a[0].data.shape[0]))
  if base=='sample_texture_2d':
   self.texture_calls+=1;tex=a[0];state=args[1].d
   v=np.frombuffer(state.memory,dtype='<u8')[0];normalized=(int(v)&32768)==0
   xy=a[2].astype(np.float32);data=tex.data
   wh=np.array([data.shape[1],data.shape[0]],np.float32);pos=xy*wh-.5 if normalized else xy-.5
   i=np.floor(pos).astype(np.int64);f=pos-i
   # Apple normalized texture interpolation uses finite fractional weights.
   f=np.rint(f*256)/256
   x0=np.clip(i[:,0],0,data.shape[1]-1);x1=np.clip(i[:,0]+1,0,data.shape[1]-1);y0=np.clip(i[:,1],0,data.shape[0]-1);y1=np.clip(i[:,1]+1,0,data.shape[0]-1)
   q00=data[y0,x0].astype(np.float32);q10=data[y0,x1].astype(np.float32);q01=data[y1,x0].astype(np.float32);q11=data[y1,x1].astype(np.float32)
   if q00.ndim==1:q00=q00[:,None];q10=q10[:,None];q01=q01[:,None];q11=q11[:,None]
   top=q00+(q10-q00)*f[:,0,None];bot=q01+(q11-q01)*f[:,0,None];sample_raw=top+(bot-top)*f[:,1,None];sample=sample_raw.astype(np.float16)
   if os.environ.get('AIR_TEX_HALF_UP','1')=='1':
    up=np.nextafter(sample,np.float16(np.inf));tie=(sample_raw==(sample.astype(np.float64)+up.astype(np.float64))*.5)&(sample_raw>sample);sample=np.where(tie,up,sample)
   rgba=np.zeros((self.n,4),np.float16);rgba[:,3]=1;rgba[:,:sample.shape[1]]=sample
   return V(rt,(V(rt.fields[0],rgba),V(rt.fields[1],np.zeros(self.n,np.uint8))))
  if base=='write_texture_2d':
   tex=a[0];xy=a[1].astype(np.int64);vals=a[2];good=mask&(xy[:,0]<tex.data.shape[1])&(xy[:,1]<tex.data.shape[0]);tex.data[xy[good,1],xy[good,0]]=vals[good];return None
  if base=='wg':return None
  if base.startswith('convert'):return self.cast(rt,a[0])
  if base=='normalize_function_constant_predicate':return self.cast(rt,a[0]!=0)
  if base in ('all','any'):return self.cast(rt,np.all(a[0],axis=-1) if base=='all' else np.any(a[0],axis=-1))
  op=base.removeprefix('fast_')
  if op=='mix':
   dt=rt.dtype() if rt.dtype() is not None else rt.fields[0].dtype();u=a[0].astype(np.float64);v=a[1].astype(np.float64);t=a[2].astype(np.float64);first=(-u*t+u).astype(dt).astype(np.float64);z=v*t+first
  elif op=='dot':
   dt=rt.dtype();x=a[0].astype(np.float64);y=a[1].astype(np.float64);z=(x[:,0]*y[:,0]).astype(dt)
   for j in range(1,x.shape[1]):z=(x[:,j]*y[:,j]+z.astype(np.float64)).astype(dt)
   dotmode=int(os.environ.get('AIR_DOT_EQUAL','0'))
   if dotmode and np.all(y==y[:,:1]):
    if dotmode==1:
     z=x[:,0].astype(dt)
     for j in range(1,x.shape[1]):z=(z+x[:,j]).astype(dt)
     z=z.astype(np.float64)*y[:,0]
    elif dotmode==2:z=np.sum(x,axis=1)*y[:,0]
    elif dotmode==3:
     products=(x*y).astype(dt);z=products[:,0]
     for j in range(1,x.shape[1]):z=(z+products[:,j]).astype(dt)
    elif dotmode==4:z=np.sum((x*y).astype(dt).astype(np.float64),axis=1)

  elif op in ('fmax','max'):z=np.maximum(a[0],a[1])
  elif op in ('fmin','min'):z=np.minimum(a[0],a[1])
  elif op=='fmax3':z=np.maximum(np.maximum(a[0],a[1]),a[2])
  elif op=='fmin3':z=np.minimum(np.minimum(a[0],a[1]),a[2])
  elif op=='clamp':z=np.minimum(np.maximum(a[0],a[1]),a[2])
  elif op=='saturate':z=np.clip(a[0],0,1)
  elif op in ('pow','powr'):z=np.power(a[0].astype(np.float64),a[1].astype(np.float64))
  elif op=='atan2':z=np.arctan2(a[0].astype(np.float64),a[1].astype(np.float64))
  elif op=='fmod':z=np.fmod(a[0],a[1])
  elif op=='fma':z=a[0].astype(np.float64)*a[1].astype(np.float64)+a[2].astype(np.float64)
  elif op in ('fabs','sqrt','exp','exp2','log','log2','sin','cos','sign','floor','ceil','round','trunc'):
   z={'fabs':np.abs,'round':np.rint}.get(op,getattr(np,op,None))(a[0].astype(np.float64))
  else:raise NotImplementedError(name)
  return self.cast(rt,z)
 def run(self,name,args,active=None):
  fun=self.m.functions[name]
  if 'uses' not in fun:
   uses={}
   for block in fun['blocks'].values():
    for line in block:
     for k in re.findall(r'%[0-9]+',line.split(' = ',1)[-1]):uses[k]=uses.get(k,0)+1
   fun['uses']=uses
  uses=fun['uses']
  env={k:v for (k,t),v in zip(fun['params'],args)};queue=[(fun['first'],np.ones(self.n,bool) if active is None else active,'entry')];ret=None;steps=0
  while queue:
   label,mask,pred=queue.pop(0)
   if not mask.any():continue
   steps+=1
   if steps>10000:raise RuntimeError('Unbounded CFG '+name)
   for raw in fun['blocks'][label]:
    self.opcount+=1;key=None;line=re.split(r", ![a-zA-Z]",raw)[0]
    if line.startswith('%'):key,line=line.split(' = ',1)
    op,body=(line.split(' ',1)+[''])[:2];value=None
    try:
     if op=='phi':
      t,rest=self.m.type(clean(body));options=re.findall(r'\[\s*(.*?)\s*,\s*%([\w.]+)\s*\]',rest)
      chosen=next((v for v,parent in options if parent==pred),None)
      if chosen is None:raise ValueError(('PHI',pred,raw))
      value=self.const(t,chosen,env)
     elif op in ('fadd','fsub','fmul','fdiv','add','sub','mul','and','or','xor','udiv','urem','shl','lshr'):
      t,rest=self.m.type(clean(body));l,r=split(rest);vx=self.const(t,l,env);vy=self.const(t,r,env);x=vx.d;y=vy.d
      calc={'fadd':np.add,'fsub':np.subtract,'fmul':np.multiply,'fdiv':np.divide,'add':np.add,'sub':np.subtract,'mul':np.multiply,'and':np.bitwise_and,'or':np.bitwise_or,'xor':np.bitwise_xor,'udiv':np.floor_divide,'urem':np.remainder,'shl':np.left_shift,'lshr':np.right_shift}
      value=self.cast(t,calc[op](x,y))
      if op=='fmul' and ('fast' in body or 'contract' in body):value.product=(x.astype(np.float64),y.astype(np.float64))
      if self.fusion and op in ('fadd','fsub') and ('fast' in body or 'contract' in body):
       left_ok=vx.product is not None and (self.fusion>=3 or uses.get(l,0)==1)
       right_ok=vy.product is not None and (self.fusion>=3 or uses.get(r,0)==1)
       prefer_right=self.fusion in (2,4)
       if right_ok and (prefer_right or not left_ok):
        a,b=vy.product;value=self.cast(t,x.astype(np.float64)+(a*b if op=='fadd' else -a*b))
       elif left_ok:
        a,b=vx.product;value=self.cast(t,a*b+(y.astype(np.float64) if op=='fadd' else -y.astype(np.float64)))
     elif op=='fneg':t,rest=self.m.type(clean(body));value=self.cast(t,-self.const(t,rest,env).d)
     elif op in ('fpext','fptrunc','zext','sext','trunc','uitofp','sitofp','fptoui','fptosi','bitcast','freeze'):
      if op=='freeze':value=self.typed(body,env)
      else:
       left,right=body.rsplit(' to ',1);src=self.typed(left,env);t,_=self.m.type(right)
       value=V(t,src.d) if t.kind=='ptr' else self.cast(t,src.d)
     elif op in ('fcmp','icmp'):
      q=clean(body);cond,q=q.split(' ',1);t,rest=self.m.type(q);l,r=split(rest);x=self.const(t,l,env).d;y=self.const(t,r,env).d
      suffix=cond[1:] if cond[0] in 'ous' and cond not in ('ord','uno') else cond
      fn={'eq':np.equal,'ne':np.not_equal,'lt':np.less,'le':np.less_equal,'gt':np.greater,'ge':np.greater_equal}
      z=fn[suffix](x,y) if suffix in fn else (np.isfinite(x)&np.isfinite(y) if cond=='ord' else np.isnan(x)|np.isnan(y))
      if cond.startswith('u') and op=='fcmp':z=z|np.isnan(x)|np.isnan(y)
      value=V(Type('vector',(Type('i1'),),t.count) if t.kind=='vector' else Type('i1'),z)
     elif op=='select':
      a,b,c=split(clean(body));cond=self.typed(a,env);x=self.typed(b,env);y=self.typed(c,env);cd=cond.d.reshape(cond.d.shape+(1,)*(x.d.ndim-cond.d.ndim));value=V(x.t,np.where(cd,x.d,y.d))
     elif op=='insertelement':
      a,b,c=split(body);v=self.typed(a,env);x=self.typed(b,env);index=int(self.typed(c,env).d[0]);d=v.d.copy();d[:,index]=x.d;value=V(v.t,d)
     elif op=='extractelement':
      a,b=split(body);v=self.typed(a,env);i=self.typed(b,env).d.astype(np.int64);value=V(v.t.fields[0],v.d[np.arange(self.n),i])
     elif op=='shufflevector':
      a,b,c=split(body);x=self.typed(a,env);y=self.typed(b,env);idx=self.typed(c,env);indices=idx.d[0].astype(int);d=np.concatenate([x.d,y.d],axis=1);indices=np.minimum(indices,d.shape[1]-1);value=V(Type('vector',(x.t.fields[0],),len(indices)),d[:,indices])
     elif op=='extractvalue':
      a,*indices=split(body);value=self.typed(a,env)
      for i in indices:value=value.d[int(i)] if value.t.kind=='struct' else V(value.t.fields[0],value.d[:,int(i)])
     elif op=='insertvalue':
      a,b,*indices=split(body);v=self.typed(a,env);x=self.typed(b,env);d=list(v.d);d[int(indices[0])]=x;value=V(v.t,tuple(d))
     elif op=='getelementptr':
      a,b,*ind=split(clean(body));t,_=self.m.type(a);p=self.typed(b,env);value=V(Type('ptr'),self.gep(t,p.d,[self.typed(x,env) for x in ind]))
     elif op=='load':
      a,b,*_=split(body);t,_=self.m.type(a);p=self.typed(b,env);value=self.load(t,p.d)
     elif op=='store':
      a,b,*_=split(body);self.store(self.typed(a,env),self.typed(b,env).d,mask)
     elif op=='alloca':
      t,_=self.m.type(split(body)[0]);value=V(Type('ptr'),Pointer(np.zeros((self.n,t.size()),np.uint8)))
     elif op in ('call','tail'):
      q=line[line.index('call ')+5:];q=clean(q);t,rest=self.m.type(q);m=re.match(r'@("[^"]+"|[^ (]+)\((.*)\)(?: #\d+.*)?$',rest)
      if not m:raise ValueError('CALL '+rest)
      cn,params=m.groups();self.return_type=t;value=self.call(cn.strip('"'),[self.typed(x,env) for x in split(params)] if params else [],mask)
     elif op=='br':
      if body.startswith('label '):queue.append((body.split('%')[1],mask,label))
      else:
       c,a,b=split(body);v=self.typed(c,env).d;queue.append((a.split('%')[1],mask&v,label));queue.append((b.split('%')[1],mask&~v,label))
      break
     elif op=='switch':
      first,cases=body.split('[',1);v,default=split(first);x=self.typed(v,env).d;remaining=mask.copy()
      for ct,label2 in re.findall(r'(i\d+ -?\d+), label %([\w.]+)',cases):
       z=self.typed(ct,env).d;yes=remaining&(x==z);queue.append((label2,yes,label));remaining=remaining&~yes
      queue.append((default.split('%')[1].strip(),remaining,label));break
     elif op=='ret':
      if body!='void':
       v=self.typed(body,env)
       if ret is None:ret=V(v.t,np.zeros_like(v.d))
       ret.d[mask]=v.d[mask]
      break
     else:raise NotImplementedError(op)
     # 26A434 PVG contrast lowering: measured reassociation, same five terms.
     # Provenance: results/contrast-sum-trees*.json; validated independently on
     # the randomized native arithmetic fixture before held-out photographs.
     if os.environ.get('AIR_NATIVE_LOWERING','1')=='1' and name.startswith('_Z14contrastFilter') and key=='%52':
      a=env['%29'].d[:,None];b=env['%34'].d;v=env['%23'].d;c=env['%40'].d;d=env['%46'].d
      value=self.cast(value.t,(((a+b).astype(np.float16)+v).astype(np.float16)+(c+d).astype(np.float16)))
     if key and value is not None:
      if key in env and isinstance(value.d,np.ndarray) and not mask.all():
       d=env[key].d.copy();d[mask]=value.d[mask];env[key]=V(value.t,d)
      else:env[key]=value
      if name==self.trace_function and isinstance(value.d,np.ndarray) and (name!='renderFinalAdjustments' or int(key[1:]) in {196,211,214,286,347,350,352,354,374,393,408,409,413,476,501,567,600}):self.checkpoints[key]=env[key].d.copy()
    except Exception as e:
     raise RuntimeError(f'{name}, block {label}, {raw}: {e}') from e
  return ret
