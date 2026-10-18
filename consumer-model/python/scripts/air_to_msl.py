#!/usr/bin/env python3
"""Translate the bounded 26A434 consumer AIR SSA to inspectable MSL for diagnosis.

This is a newly compiled research model, NOT Apple's original executable. The
original pipeline remains the conformance oracle. Numeric fusion may differ.
"""
from pathlib import Path
import sys,re,struct,json,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from air_numpy import Module,Type,split,clean

CHECKS=[196,211,214,286,347,350,352,354,374,393,408,409,413,476,501,567,600]
class Translator:
 def __init__(self,path):
  self.m=Module(path);self.names={n:'f'+str(i) for i,n in enumerate(self.m.functions) if not n.startswith('_GLOBAL')};self.meta={};self.kind={};self.types={};self.records={};self.structs={};self.globals={}
  for line in self.m.text.splitlines():
   q=re.match(r'!\d+ = !\{i32 (\d+), (.*)',line)
   if q and '!"air.arg_name"' in line:
    i=int(q[1]);s=q[2];loc=re.search(r'!"air.location_index", i32 (\d+)',s);name=re.search(r'!"air.arg_name", !"([^"]+)"',s)
    self.meta[i]={'kind':'texture' if '!"air.texture"' in s else 'buffer' if '!"air.buffer"' in s else 'builtin','slot':int(loc[1]) if loc else None,'name':name[1],'write':'!"air.write"' in s}
  self.infer()
 def infer(self):
  for n,f in self.m.functions.items():
   if n not in self.names:continue
   ts={k:t for k,t in f['params']};self.types[n]=ts
   if n=='renderFinalAdjustments':
    for k,t in f['params']:
     z=self.meta.get(int(k[1:]),{})
     if z.get('kind')=='texture':self.kind[n,k]='write' if z['write'] else 'sample'
   records=[]
   for label,lines in f['blocks'].items():
    for raw in lines:
     line=re.split(r', ![A-Za-z]',raw)[0];key=None
     if line.startswith('%'):key,line=line.split(' = ',1)
     op,body=(line.split(' ',1)+[''])[:2];records.append((label,key,op,body,line))
     if key:
      if op in ('fcmp','icmp'):
       t,_=self.m.type(clean(body).split(' ',1)[1]);ts[key]=Type('vector',(Type('i1'),),t.count) if t.kind=='vector' else Type('i1')
      elif op in ('getelementptr','alloca','bitcast') and not (op=='bitcast' and ' to ptr' not in body):ts[key]=Type('ptr')
      elif op in ('fpext','fptrunc','zext','sext','trunc','uitofp','sitofp','fptoui','fptosi','bitcast'):ts[key]=self.m.type(body.rsplit(' to ',1)[1])[0]
      elif op=='call' or op=='tail':ts[key]=self.m.type(clean(line[line.index('call ')+5:]))[0]
      elif op=='select':ts[key]=self.m.type(split(clean(body))[1])[0]
      elif op=='extractelement':ts[key]=self.m.type(split(body)[0])[0].fields[0]
      elif op=='extractvalue':
       v,*ii=split(body);t,_=self.m.type(v)
       for i in ii:t=t.fields[int(i)] if t.kind=='struct' else t.fields[0]
       ts[key]=t
      elif op=='shufflevector':
       v,_,ii=split(body);t,_=self.m.type(v);it,_=self.m.type(ii);ts[key]=Type('vector',(t.fields[0],),it.count)
      else:ts[key]=self.m.type(clean(body))[0]
   self.records[n]=records
  for _ in range(6):
   for n,records in self.records.items():
    for _,key,op,body,line in records:
     if op in ('call','tail'):
      q=clean(line[line.index('call ')+5:]);t,rest=self.m.type(q);mt=re.match(r'@([^ (]+)\((.*)\)(?: #\d+.*)?$',rest);cn,argv=mt.groups();argv=split(argv) if argv else []
      if cn.startswith('air.') and any(x in cn for x in ['sample_texture','get_width_texture','get_height_texture','is_null_texture','write_texture']):
       _,k=self.m.type(argv[0]);self.kind[n,clean(k)]='write' if 'write_texture' in cn else 'sample'
      elif cn in self.names:
       for a,(p,_) in zip(argv,self.m.functions[cn]['params']):
        _,k=self.m.type(a);k=clean(k)
        if (cn,p) in self.kind:self.kind[n,k]=self.kind[cn,p]
        if (n,k) in self.kind:self.kind[cn,p]=self.kind[n,k]
 def ctype(self,t):
  if t.kind=='ptr':return 'device uchar*'
  if t.kind=='vector':return self.ctype(t.fields[0])+str(t.count)
  if t.kind=='array':return 'array<'+self.ctype(t.fields[0])+','+str(t.count)+'>'
  if t.kind=='struct':
   if t not in self.structs:
    name='S'+str(len(self.structs));self.structs[t]=name
    for f in t.fields:self.ctype(f)
   return self.structs[t]
  return {'i1':'bool','i8':'uchar','i16':'ushort','i32':'uint','i64':'ulong'}.get(t.kind,t.kind)
 def var(self,k):return 'v'+k[1:] if k.startswith('%') else k
 def value(self,t,s):
  s=clean(s)
  if s.startswith('%'):return self.var(s)
  if s.startswith('@'):
   if 'sampler' in s:return 's_pixel' if s=='@__air_sampler_state' else 's_norm'
   if 'useSrlVersion' in s:return '(device uchar*)0' # global loads special-cased
   return '(device uchar*)0'
  ct=self.ctype(t)
  if t.kind=='ptr':return '(device uchar*)nullptr'
  if s in ('undef','poison','zeroinitializer','null'):return ct+'{}' if t.kind not in ('half','float','double') else ct+'(0)'
  if s.startswith('splat ('):return ct+'('+self.typed(s[7:-1])[1]+')'
  if s.startswith('<') or s.startswith('['):return ct+'('+','.join(self.typed(x)[1] for x in split(s[1:-1]))+')'
  if s.startswith('0xH'):number=struct.unpack('>e',bytes.fromhex(s[3:]))[0];s=repr(number)
  elif s.startswith('f0x'):s=repr(struct.unpack('>f',bytes.fromhex(s[3:]))[0])
  elif s.startswith('0x'):s=repr(struct.unpack('>d',bytes.fromhex(s[2:]))[0])
  if s in ('true','false'):return s
  return ct+'('+s+')'
 def typed(self,s):
  t,r=self.m.type(s);return t,self.value(t,r)
 def gepexpr(self,body):
  a,b,*indices=split(clean(body));t,_=self.m.type(a);_,p=self.typed(b);off=[];cur=t
  for j,z in enumerate(indices):
   it,iv=self.typed(z)
   if j==0:off.append(f'({iv})*{cur.size()}')
   elif cur.kind=='struct':
    _,i=self.m.type(z);i=int(clean(i));off.append(str(cur.offsets()[i]));cur=cur.fields[i]
   else:off.append(f'({iv})*{cur.fields[0].size()}');cur=cur.fields[0]
  return p+' + '+' + '.join(off)
 def signature(self,n):
  f=self.m.functions[n];prefix=f['prefix'].replace('internal ','');rt,_=self.m.type(clean(prefix));out=[]
  for k,t in f['params']:
   if n=='renderFinalAdjustments':
    meta=self.meta[int(k[1:])]
    if int(k[1:])==0:continue
    attr=meta['kind'];slot=meta['slot']
    if attr=='texture':ct='texture2d<half'+(',access::write' if meta['write'] else '')+'>';suffix=f' [[texture({slot})]]'
    elif attr=='buffer':ct='device uchar*';suffix=f' [[buffer({slot})]]'
    else:ct=self.ctype(t);suffix={'gridPos':' [[thread_position_in_grid]]','tgPos':' [[thread_position_in_threadgroup]]','tgSize':' [[threads_per_threadgroup]]'}[meta['name']]
   else:
    kind=self.kind.get((n,k));ct=('texture2d<half'+(',access::write' if kind=='write' else '')+'>') if kind else self.ctype(t);suffix=''
   out.append(ct+' '+self.var(k)+suffix)
  if n=='renderFinalAdjustments':out.append('device float4* dbg [[buffer(30)]]')
  return ('kernel void' if n=='renderFinalAdjustments' else self.ctype(rt))+' '+self.names[n]+'('+','.join(out)+')'
 def translate_function(self,n):
  f=self.m.functions[n];ts=self.types[n];kinds={};decl=[];lines=[]
  for k,t in ts.items():
   if any(k==p for p,_ in f['params']):continue
   kt=self.kind.get((n,k));ct='texture2d<half>' if kt else self.ctype(t)
   # Pointer derived from a local alloca stays thread address-space.
   if t.kind=='ptr':
    record=next(r for r in self.records[n] if r[1]==k)
    if record[2]=='alloca':kinds[k]='thread'
    elif record[2] in ('getelementptr','bitcast'):
     ks=re.findall(r'%[0-9]+',record[3]);kinds[k]='thread' if any(kinds.get(z)=='thread' for z in ks) else 'device'
    if kinds.get(k)=='thread':ct='thread uchar*'
   decl.append(ct+' '+self.var(k)+'{};')
  if n=='renderFinalAdjustments':decl.append('uint di=uint(v21.y)*v14.get_width()+uint(v21.x); if(di<512)dbg[di*17]=float4(float(v21.x),float(v21.y),17,19);')
  for label,raws in f['blocks'].items():
   lines.append('case '+label+': {')
   for _,key,op,body,line in (r for r in self.records[n] if r[0]==label):
    expr=None;statement=None;t=ts.get(key);ct=self.ctype(t) if t else None
    if op in ('fadd','fsub','fmul','fdiv','add','sub','mul','and','or','xor','udiv','urem','shl','lshr'):
     tt,r=self.m.type(clean(body));a,b=split(r);a=self.value(tt,a);b=self.value(tt,b);symbol={'fadd':'+','fsub':'-','fmul':'*','fdiv':'/','add':'+','sub':'-','mul':'*','and':'&','or':'|','xor':'^','udiv':'/','urem':'%','shl':'<<','lshr':'>>'}[op];expr=f'({a}) {symbol} ({b})'
    elif op=='fneg':tt,r=self.m.type(clean(body));expr='-('+self.value(tt,r)+')'
    elif op in ('fpext','fptrunc','zext','sext','trunc','uitofp','sitofp','fptoui','fptosi','bitcast'):
     a,_=body.rsplit(' to ',1);_,v=self.typed(a);expr=v if t.kind=='ptr' else ct+'('+v+')'
    elif op in ('fcmp','icmp'):
     q=clean(body);cond,q=q.split(' ',1);tt,r=self.m.type(q);a,b=split(r);a=self.value(tt,a);b=self.value(tt,b);cond=cond[1:] if cond[0] in 'ous' else cond;symbol={'eq':'==','ne':'!=','lt':'<','le':'<=','gt':'>','ge':'>='}[cond];expr=f'({a}) {symbol} ({b})'
    elif op=='select':
     a,b,c=split(clean(body));ta,va=self.typed(a);_,vb=self.typed(b);_,vc=self.typed(c);expr=f'select({vc},{vb},{va})' if ta.kind=='vector' else f'({va}) ? ({vb}):({vc})'
    elif op in ('insertelement','insertvalue'):
     a,b,c=split(body);_,v=self.typed(a);_,x=self.typed(b);i=self.typed(c)[1] if op=='insertelement' else c;statement=f'{self.var(key)}={v};{self.var(key)}[{i}]={x};'
    elif op in ('extractelement','extractvalue'):
     a,*ii=split(body);tt,v=self.typed(a)
     for i in ii:
      index=self.typed(i)[1] if op=='extractelement' else i
      v+='.'+'f'+i if tt.kind=='struct' else '['+index+']';tt=tt.fields[int(i)] if tt.kind=='struct' else tt.fields[0]
     expr=v
    elif op=='shufflevector':
     a,b,ii=split(body);at,av=self.typed(a);bt,bv=self.typed(b);it,ir=self.m.type(ii);entries=['i32 0']*it.count if ir=='zeroinitializer' else split(ir.strip('<> '));vals=[]
     for z in entries:
      _,num=self.m.type(z);idx=0 if num in ('poison','undef') else int(num);vals.append((av+'['+str(idx)+']') if idx<at.count else bv+'['+str(idx-at.count)+']')
     expr=ct+'('+','.join(vals)+')'
    elif op=='getelementptr':expr=self.gepexpr(body)
    elif op=='alloca':
     tt,_=self.m.type(split(body)[0]);decl.append(f'alignas(16) uchar local{key[1:]}[{tt.size()}]={{0}};');expr='local'+key[1:]
    elif op=='load':
     a,b,*_=split(body);tt,_=self.m.type(a);pt,pr=self.m.type(b);_,p=self.typed(b)
     if pr.startswith('@'):
      expr='0' # FCs fixed to texture path, SRL0; capture has inactive SRL.
     else:
      kind='thread' if kinds.get(pr)=='thread' else 'device';expr=f'*(({kind} {self.ctype(tt)}*)({p}))'
    elif op=='store':
     a,b,*_=split(body);tt,v=self.typed(a);_,p=self.typed(b);_,pr=self.m.type(b);kind='thread' if kinds.get(pr)=='thread' else 'device';statement=f'*(({kind} {self.ctype(tt)}*)({p}))={v};'
    elif op=='phi':
     tt,r=self.m.type(clean(body));choices=re.findall(r'\[\s*(.*?)\s*,\s*%([\w.]+)\s*\]',r);expr=' : '.join(f'(pred=={parent}) ? ({self.value(tt,v)})' for v,parent in choices)+' : '+self.value(tt,'zeroinitializer')
    elif op in ('call','tail'):
     q=clean(line[line.index('call ')+5:]);tt,rest=self.m.type(q);cn,ps=re.match(r'@([^ (]+)\((.*)\)(?: #\d+.*)?$',rest).groups();args=[self.typed(x) for x in split(ps)] if ps else [];aa=[v for t,v in args]
     if cn in self.names:expr=self.names[cn]+'('+','.join(aa)+')'
     elif cn.startswith('llvm.lifetime') or cn=='llvm.assume':statement=''
     elif cn.startswith('llvm.memset'):statement=f'for(uint zz=0;zz<{aa[2]};++zz){aa[0]}[zz]=uchar({aa[1]});'
     elif cn.startswith('air.'):
      base=cn.split('.')[1]
      if base=='sample_texture_2d':expr=ct+'{'+aa[0]+'.sample('+aa[1]+','+aa[2]+'),0}'
      elif base=='write_texture_2d':statement=f'{aa[0]}.write({aa[2]},uint2({aa[1]}));'
      elif base=='is_null_texture_2d':expr='is_null_texture('+aa[0]+')'
      elif base=='get_width_texture_2d':expr=aa[0]+'.get_width()'
      elif base=='get_height_texture_2d':expr=aa[0]+'.get_height()'
      elif base.startswith('convert'):expr=ct+'('+aa[0]+')'
      elif base=='imageblock_data':expr='nullptr'
      elif base in ('wg','write_imageblock_slice_to_texture_2d'):statement=''
      else:
       base=base.removeprefix('fast_');base={'fmax':'max','fmin':'min','fmax3':'max3','fmin3':'min3'}.get(base,base);expr=base+'('+','.join(aa)+')'
     else:raise NotImplementedError(cn)
    elif op=='br':
     if body.startswith('label'):statement=f'pred={label};pc={body.split("%")[1]};continue;'
     else:
      a,b,c=split(body);_,cond=self.typed(a);statement=f'pred={label};pc=({cond}) ? {b.split("%")[1]}:{c.split("%")[1]};continue;'
    elif op=='switch':
     first,cases=body.split('[',1);v,default=split(first);_,x=self.typed(v);choices=re.findall(r'(i\d+ -?\d+), label %([\w.]+)',cases);expr2=' : '.join(f'({x}=={self.typed(z)[1]}) ? {parent}' for z,parent in choices)+' : '+default.split('%')[1].strip();statement=f'pred={label};pc={expr2};continue;'
    elif op=='ret':statement='return;' if body=='void' else 'return '+self.typed(body)[1]+';'
    else:raise NotImplementedError(op)
    if expr is not None:statement=self.var(key)+'='+expr+';'
    if statement is not None:lines.append(statement)
    if n=='renderFinalAdjustments' and key and int(key[1:]) in CHECKS:
     ix=CHECKS.index(int(key[1:]));val=self.var(key);v='float4(float3('+val+'),1)' if t.kind=='vector' else 'float4(float('+val+'),0,0,1)';lines.append(f'if(di<512)dbg[di*{len(CHECKS)}+{ix}]={v};')
   lines.append('}')
  return self.signature(n)+' {\n'+'\n'.join(decl)+f'\nuint pc={f["first"]},pred=0;while(true){{switch(pc){{\n'+'\n'.join(lines)+'\ndefault:return'+(';' if n=='renderFinalAdjustments' else ' {};')+'}}}\n'
 def write(self,out):
  signatures=[self.signature(n)+';' for n in self.names];functions=[self.translate_function(n) for n in self.names]
  definitions=[]
  # Struct fields first; recursive dependencies emitted before parents.
  done=set()
  def emit(t):
   if t.kind=='struct':
    if t in done:return
    for f in t.fields:emit(f)
    definitions.append('struct '+self.structs[t]+' {'+';'.join(self.ctype(f)+' f'+str(i) for i,f in enumerate(t.fields))+';};');done.add(t)
   elif t.kind=='array':emit(t.fields[0])
  for t in list(self.structs):emit(t)
  source='#include <metal_stdlib>\nusing namespace metal;\ntemplate<typename T>T max3(T a,T b,T c){return max(max(a,b),c); }\ntemplate<typename T>T min3(T a,T b,T c){return min(min(a,b),c); }\nconstexpr sampler s_norm(coord::normalized,address::clamp_to_edge,filter::linear);\nconstexpr sampler s_pixel(coord::pixel,address::clamp_to_edge,filter::linear);\n'+'\n'.join(definitions+signatures+functions)
  source+='\nkernel void sentinel(texture2d<half,access::write> out [[texture(13)]],device float4* dbg [[buffer(30)]],uint2 xy [[thread_position_in_grid]]){out.write(half4(.25h,.5h,.75h,1.h),xy);uint i=xy.y*out.get_width()+xy.x;if(i<512)dbg[i*17]=float4(xy.x,xy.y,17,19); }\n'
  Path(out).write_text(source);Path(out).with_suffix('.json').write_text(json.dumps({'air_sha256':hashlib.sha256(self.m.path.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'checkpoints':CHECKS,'function':'f1','scope':'newly compiled SSA model; original native output remains oracle','constants':{'useImageBlock':0,'useSrlVersion':0}},indent=2)+'\n')
if __name__=='__main__':Translator(sys.argv[1]).write(sys.argv[2])
