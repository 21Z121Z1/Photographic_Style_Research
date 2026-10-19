"""Classify code candidates from the actual original initializer, export text only."""
from pathlib import Path
import hashlib,json,re,subprocess,struct,sys
import llvmlite.binding as llvm
B=Path(sys.argv[1]);O=Path(sys.argv[2]);O.mkdir(parents=True,exist_ok=True);rows=[];modules=[]
for p in sorted(B.glob('original-*.bin')):
 row={'name':p.name,'size':p.stat().st_size,'file_kind':subprocess.check_output(['file','-b',str(p)],text=True).strip()}
 with p.open('rb') as f:row['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
 data=p.read_bytes();row['recognized_container']=data[:4] in [b'MTLB',b'\xcf\xfa\xed\xfe',b'\xce\xfa\xed\xfe',b'\xca\xfe\xba\xbe',b'\xde\xc0\x17\x0b'];rows.append(row)
 if not row['recognized_container']:continue
 with (O/(p.stem+'-headers.log')).open('w') as f:row['objdump_header_rc']=subprocess.run(['xcrun','llvm-objdump','--macho','--private-headers',str(p)],stdout=f,stderr=subprocess.STDOUT).returncode
 offset=0;seen=set()
 while True:
  k=data.find(b'\xde\xc0\x17\x0b',offset)
  if k<0:break
  offset=k+4
  if k+20>len(data):continue
  _,v,off,n,cpu=struct.unpack_from('<5I',data,k);raw=data[k+off:k+off+n]
  if len(raw)!=n or not raw.startswith(b'BC\xc0\xde'):continue
  h=hashlib.sha256(raw).hexdigest()
  if h in seen:continue
  seen.add(h)
  try:t=str(llvm.parse_bitcode(raw))
  except Exception as e:row.setdefault('parse_errors',[]).append(str(e)[:200]);continue
  if not re.search(r'define .*@renderFinalAdjustments\(',t):continue
  name=p.stem+f'-{len(modules):02}-consumer.ll';(O/name).write_text(t);modules.append({'file':name,'container':p.name,'bc_sha256':h,'text_sha256':hashlib.sha256(t.encode()).hexdigest(),'stage':'Actual constructor object code candidate; AIR text is still not final device ISA'})
(O/'variant-inspection.json').write_text(json.dumps({'raw_Apple_binaries_uploaded':False,'raw_people_pixels_uploaded':False,'actual_initializer_code_candidates':rows,'consumer_AIR_modules':modules,'final_original_backend_ISA_authenticated':False},indent=2)+'\n')
