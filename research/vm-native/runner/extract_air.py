#!/usr/bin/env python3
"""Extract LLVM wrapper payloads on the runner; export text IR only."""
import pathlib,struct,re,json,subprocess,hashlib,sys,os
p=pathlib.Path('/System/Library/PrivateFrameworks/CMImaging.framework/Versions/A/Resources/default.metallib');data=p.read_bytes()
out=pathlib.Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
temp=pathlib.Path(os.environ['RUNNER_TEMP'])/'air-only';temp.mkdir(exist_ok=True)
llvm=pathlib.Path(subprocess.check_output(['brew','--prefix','llvm'],text=True).strip())/'bin/llvm-dis'
index=[]
for n,m in enumerate(re.finditer(b'\xde\xc0\x17\x0b',data)):
 start=m.start()
 if start+20>len(data):continue
 magic,version,offset,size,cpu=struct.unpack_from('<5I',data,start)
 raw=data[start+offset:start+offset+size]
 if raw[:4]!=b'BC\xc0\xde' or len(raw)!=size:continue
 row={'index':n,'wrapper_offset':start,'payload_offset':start+offset,'payload_size':size,'sha256':hashlib.sha256(raw).hexdigest()}
 interesting=any(t in raw for t in [b'StyleEngine',b'CMISmartStyleMetalRenderer',b'CMIGuidedFilter'])
 if interesting:
  bc=temp/f'{n:04d}.bc';bc.write_bytes(raw)
  target=out/f'{n:04d}.ll'
  result=subprocess.run([str(llvm),str(bc),'-o',str(target)],capture_output=True,text=True)
  row.update({'llvm_dis_rc':result.returncode,'stderr':result.stderr,'text_file':target.name})
  if target.exists():
   text=target.read_text();row['functions']=re.findall(r'^define .*?@(?:"([^"]+)"|([^ (]+))',text,re.M)
  bc.unlink()
 index.append(row)
(out/'index.json').write_text(json.dumps({'source_path':str(p),'source_size':len(data),'source_sha256':hashlib.sha256(data).hexdigest(),'llvm_version':subprocess.check_output([str(llvm),'--version'],text=True),'modules':index},indent=2)+'\n')
print('AIR wrappers',len(index),'selected',sum('llvm_dis_rc' in x for x in index),'successful',sum(x.get('llvm_dis_rc')==0 for x in index))
