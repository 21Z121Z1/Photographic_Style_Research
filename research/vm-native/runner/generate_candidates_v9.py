"""Versioned compiler/rounding candidates; no photograph-specific corrections."""
from pathlib import Path
import argparse,re,json,hashlib

def body_transform(source,n,fn):
 m=re.search(r'^half3 f'+str(n)+r'\([^\n]*\) \{',source,re.M);assert m,n
 begin=m.end();depth=1;end=begin
 while depth:
  if source[end]=='{':depth+=1
  elif source[end]=='}':depth-=1
  end+=1
 return source[:begin]+fn(source[begin:end-1])+source[end-1:]

def main():
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);base=a.source.read_text();variants=[]
 def add(name,text,**options):
  file=a.out/(name+'.metal');file.write_text(text);variants.append({'name':name,'source':str(file),'source_sha256':hashlib.sha256(text.encode()).hexdigest(),'fast_math':True,**options})
 # End-to-end oracle checks determine whether a compiler choice is admissible.
 for attr,functions in [('noinline',[32,33,34]),('always_inline',list(range(2,42))),('noinline',list(range(2,42))),('optnone',[32,33,34])]:
  text=base
  for n in functions:text=re.sub(r'^half3 f'+str(n)+r'\(',f'__attribute__(({attr})) half3 f{n}(',text,flags=re.M)
  add(attr+('-all'if len(functions)>3 else'-tone'),text)
 for option in ['contract(off) reassociate(off)','contract(fast) reassociate(on)','contract(on) reassociate(off)']:
  text=base
  for n in [32,33,34]:text=body_transform(text,n,lambda b:'\n#pragma clang fp '+option+'\n'+b)
  add('pragma-'+option.split('(')[1].split(')')[0]+'-'+option.rsplit('(',1)[1].split(')')[0],text)
 for mode,functions in [('relaxed','fast'),('fast','precise')]:add('math-'+mode+'-'+functions,base,math_mode=mode,math_functions=functions)
 add('optimization-size',base,optimization_level='size')
 # These trees contain exactly the AIR five terms. Volatile half temporaries
 # delimit rounding; explicit fma candidates change contraction, not algebra.
 helpers='\nhalf3 hradd(half3 a,half3 b){volatile half3 t=a+b;return t;}\nhalf3 hrfma(half3 a,half3 b,half3 c){volatile half3 t=fma(a,b,c);return t;}\n'
 trees=[lambda a,b,v,c,d,g,x:f'hradd(hradd(hradd({a},{b}),{v}),hradd({c},{d}))',lambda a,b,v,c,d,g,x:f'hradd(hradd(hradd({a},{b}),{v}),hrfma({g},{x},{d}))',lambda a,b,v,c,d,g,x:f'hradd(hradd({a},{v}),hradd(hradd({b},{c}),{d}))',lambda a,b,v,c,d,g,x:f'hradd(hradd(hradd(hradd({a},{v}),{c}),{b}),{d})']
 for k,tree in enumerate(trees):
  text=base.replace('using namespace metal;','using namespace metal;'+helpers)
  for n,key,terms in [(32,86,['v82','v68','v58','v74','v80','v73','v69']),(33,101,['v97','v83','v75','v89','v95','v88','v84']),(34,99,['v95','v80','v72','v86','v92','v85','v81'])]:
   def change(b,key=key,terms=terms):
    match=re.search(r'^v'+str(key)+r'=.*?;$',b,re.M);assert match
    return b[:match.start()]+'v'+str(key)+'='+tree(*terms)+';'+b[match.end():]
   text=body_transform(text,n,change)
  add('half-sum-tree-'+str(k),text)
 # Instrument only the final smoothSat call. Its full-frame output must still
 # match the original library before its intermediate buffers are trusted.
 m=re.search(r'^half3 f27\([^\n]*\) \{',base,re.M);start=m.start();depth=1;end=m.end()
 while depth:
  if base[end]=='{':depth+=1
  elif base[end]=='}':depth-=1
  end+=1
 clone=base[start:end].replace('f27(half3 v0,half v1)','f27debug(half3 v0,half v1,device float4* dbg,uint di)',1)
 checkpoints=[('input','float4(float3(v0),float(v1))'),('12','float4(v12,0)'),('15','float4(v15,0)'),('24','float4(v24,0)'),('25','float4(float3(v25),0)'),('37','float4(float(v34),float(v36),float(v37),0)'),('47','float4(float3(v47),0)'),('55','float4(v55,0)'),('58','float4(v58,0)'),('67','float4(v67,0)'),('68','float4(float3(v68),0)'),('75','float4(float3(v75),0)')]
 clone=clone.replace('{','{\nif(di<4096)dbg[di*20]='+checkpoints[0][1]+';',1)
 for i,(key,expr)in enumerate(checkpoints[1:],1):
  pattern=r'^(v'+key+r'=.*?;)$';clone,count=re.subn(pattern,lambda m:m[0]+'\nif(di<4096)dbg[di*20+'+str(i)+']='+expr+';',clone,flags=re.M);assert count==1,key
 decl='half3 f27debug(half3,half,device float4*,uint);\n'
 text=base.replace('half3 f27(half3 v0,half v1);',decl+'half3 f27(half3 v0,half v1);',1)
 text,n=re.subn(r'v372=f27\(v354,v364\);','v372=f27debug(v354,v364,dbg,uint(v21.y)*v14.get_width()+uint(v21.x));',text);assert n==1
 text+='\n'+clone+'\n';add('smooth-diagnostic',text,capture_checkpoints=True,checkpoint_stride=20,checkpoint_pixels=4096)
 (a.out/'smooth-checkpoint-layout.json').write_text(json.dumps(checkpoints,indent=2)+'\n');(a.out/'variants.json').write_text(json.dumps(variants,indent=2)+'\n');print('variants',len(variants))
if __name__=='__main__':main()
