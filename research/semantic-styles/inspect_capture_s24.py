"""Runner-only capture classification. Never export raw capture/library/resource bytes."""
from pathlib import Path
import sys,re,json,subprocess,hashlib,struct,plistlib
import llvmlite.binding as llvm
B=Path(sys.argv[1]);O=Path(sys.argv[2]);O.mkdir(parents=True,exist_ok=True);C=B/'original.gputrace';rows=[];irs=[]
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for p in sorted(C.iterdir()) if C.exists() else []:
 if not p.is_file() or re.match(r'(IOSurface|MTLHeap|MTLTexture)-',p.name):continue
 if p.stat().st_size>20_000_000:continue
 kind=subprocess.run(['file','-b',str(p)],capture_output=True,text=True).stdout.strip();row={'name':p.name,'size':p.stat().st_size,'sha256':sha(p),'file_kind':kind};rows.append(row)
 data=p.read_bytes();recognized=data[:4] in [b'MTLB',b'\xcf\xfa\xed\xfe',b'\xce\xfa\xed\xfe',b'\xca\xfe\xba\xbe',b'\xde\xc0\x17\x0b']
 row['recognized_code_container']=recognized
 # Prohibit publishing unknown capture payload or binary/Base64 as text.
 if recognized:
  with (O/(p.name+'-headers.log')).open('w') as f:row['objdump_headers_rc']=subprocess.run(['xcrun','llvm-objdump','--macho','--private-headers',str(p)],stdout=f,stderr=subprocess.STDOUT).returncode
  start=0;seen=set()
  while True:
   k=data.find(b'\xde\xc0\x17\x0b',start)
   if k<0:break
   start=k+4
   if k+20>len(data):continue
   magic,ver,off,size,cpu=struct.unpack_from('<5I',data,k);raw=data[k+off:k+off+size]
   if len(raw)!=size or not raw.startswith(b'BC\xc0\xde'):continue
   digest=hashlib.sha256(raw).hexdigest()
   if digest in seen:continue
   seen.add(digest)
   try:ir=str(llvm.parse_bitcode(raw))
   except Exception:continue
   if not re.search(r'define .*@renderFinalAdjustments\(',ir):continue
   name=p.name+f'-{len(irs):03}-renderFinalAdjustments.ll';(O/name).write_text(ir);irs.append({'capture_file':p.name,'wrapper_offset':k,'raw_size':size,'raw_sha256':digest,'text_file':name,'text_sha256':hashlib.sha256(ir.encode()).hexdigest(),'type':'AIR IR, not final backend ISA'})
  row['LLVM_wrapper_count']=len(seen)
 # Only key names from plist/JSON metadata. No arbitrary printable buffers.
 if p.name in ['metadata','index']:
  try:obj=plistlib.loads(data);row['metadata_type']='plist';row['metadata_top_keys']=list(obj) if isinstance(obj,dict) else type(obj).__name__
  except Exception:
   try:obj=json.loads(data);row['metadata_type']='json';row['metadata_top_keys']=list(obj) if isinstance(obj,dict) else type(obj).__name__
   except Exception:row['metadata_type']='opaque/unparsed'
report={'raw_capture_exported':False,'raw_Apple_binary_exported':False,'photo_resource_files_excluded':True,'capture_files_total':sum(p.is_file() for p in C.iterdir()) if C.exists() else 0,'non_resource_files':rows,'consumer_AIR':irs,'backend_machine_code_authenticated':False,'scope':'Recognized capture library containers and selected consumer AIR only; metadata names/file types/headers do not by themselves prove absence of hidden final code or equivalence to S5 PSO.'}
(O/'capture-inspection.json').write_text(json.dumps(report,indent=2)+'\n')
