"""Separate the two positive-tone operators; preserve AIR five-term algebra."""
from pathlib import Path
import argparse,hashlib,json,re
from generate_candidates_v9 import body_transform
HELPERS='\nhalf3 hradd(half3 a,half3 b){volatile half3 t=a+b;return t;}\nhalf3 hrfma(half3 a,half3 b,half3 c){volatile half3 t=fma(a,b,c);return t;}\n'
TERMS={32:(86,['v82','v68','v58','v74','v80','v73','v69']),33:(101,['v97','v83','v75','v89','v95','v88','v84']),34:(99,['v95','v80','v72','v86','v92','v85','v81'])}
def canonical(v,mode):
 a,b,x,c,d,g,gx=v;return f'hradd(hradd(hradd({a},{b}),{x}),'+(f'hrfma({g},{gx},{d})'if mode else f'hradd({c},{d})')+')'
def replace_sum(text,n,expr):
 key=TERMS[n][0]
 def change(body):
  body,count=re.subn(r'^v'+str(key)+r'=.*?;$','v'+str(key)+'='+expr+';',body,flags=re.M);assert count==1;return body
 return body_transform(text,n,change)
def trees(items):
 if len(items)==1:return [items[0]]
 out=set();first=items[0];rest=items[1:]
 for mask in range(1<<len(rest)):
  left=(first,)+tuple(x for k,x in enumerate(rest)if mask&(1<<k));right=tuple(x for k,x in enumerate(rest)if not mask&(1<<k))
  if not right:continue
  for a in trees(left):
   for b in trees(right):out.add('hradd('+a+','+b+')')
 return sorted(out)
def main():
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--search-function',type=int,choices=[32,34]);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);original=a.source.read_text();base=original.replace('using namespace metal;','using namespace metal;'+HELPERS);base=replace_sum(base,33,canonical(TERMS[33][1],1));variants=[]
 def add(name,text,**extras):
  f=a.out/(name+'.metal');f.write_text(text);variants.append({'name':name,'source':str(f),'source_sha256':hashlib.sha256(text.encode()).hexdigest(),'fast_math':True,**extras})
 if a.search_function:
  n=a.search_function;terms=TERMS[n][1];all_trees=trees(('A','B','X','C','D'));assert len(all_trees)==105
  for k,tree in enumerate(all_trees):
   expr=tree
   for s,v in zip(['A','B','X','C','D'],terms[:5]):expr=re.sub(r'\b'+s+r'\b',v,expr)
   add(f'positive-f{n}-tree{k:03d}',replace_sum(base,n,expr),positive_function=n,tree=tree)
 else:
  add('negative-fma-only',base)
  for n in [32,34]:
   for mode in [0,1]:add(f'positive-f{n}-canonical-{mode}',replace_sum(base,n,canonical(TERMS[n][1],mode)),positive_function=n)
  # Root-only observations change no helper signature or arithmetic. Compare
  # its full output against Apple before accepting its internal observations.
  frozen=a.source.parent/'consumer-model.metal';text=frozen.read_text().replace('di<512','di<4096');assert text!=frozen.read_text();add('root-diagnostic-4096',text,capture_checkpoints=True,checkpoint_pixels=4096,checkpoint_stride=17)
 (a.out/'variants.json').write_text(json.dumps(variants,indent=2)+'\n');print('generated',len(variants))
if __name__=='__main__':main()
