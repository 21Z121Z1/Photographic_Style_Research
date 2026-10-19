"""Runner text-only extraction. Apple binaries/captures never leave backend directory."""
from pathlib import Path
import sys,subprocess,json,hashlib,struct,os
B=Path(sys.argv[1]);O=Path(sys.argv[2]);O.mkdir(parents=True,exist_ok=True);B.mkdir(parents=True,exist_ok=True)
report={'binary_exported':False,'tools':{},'operations':[],'air':[]}
def cmd(args,label,timeout=90):
 p=O/(label+'.log')
 try:
  with p.open('wb') as f:r=subprocess.run(list(map(str,args)),stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
  rc=r.returncode
 except (subprocess.TimeoutExpired,OSError) as e:rc=-1;p.write_text(type(e).__name__+'\n')
 report['operations'].append({'label':label,'returncode':rc})
 return rc
for t in ['metal-lipo','metal-source','metal-objdump','metal','llvm-objdump','otool','nm']:
 q=subprocess.run(['xcrun','--find',t],capture_output=True,text=True)
 report['tools'][t]={'available':q.returncode==0,'path':q.stdout.strip() if q.returncode==0 else ''}
 if q.returncode==0 and t in ['metal-objdump','metal-source','metal-lipo']:cmd(['xcrun',t,'--help'],'help-'+t)
archive=B/'original-derived.binary.metallib'
if archive.exists():
 with archive.open('rb') as f:report['archive']={'size':archive.stat().st_size,'sha256':hashlib.file_digest(f,'sha256').hexdigest()}
 if report['tools']['metal-lipo']['available']:cmd(['xcrun','-sdk','macosx','metal-lipo',archive,'-archs'],'archive-architectures')
 if report['tools']['metal-source']['available']:cmd(['xcrun','metal-source','-flatbuffers=json',archive,'-o',B/'extracted'],'metal-source-extract')
 # LLVM wrappers exported only as human-readable IR. Not machine-code disassembly.
try:import llvmlite.binding as llvm;report['llvmlite']=__import__('llvmlite').__version__
except ImportError:llvm=None;report['llvmlite']='unavailable'
# Structural identification of the original constexpr sampler integer. Each helper
# declares exactly one explicit sampler; matching integers is recorded, not guessed.
source='''#include <metal_stdlib>
using namespace metal;
kernel void sampler_linear_norm(texture2d<half,access::sample> a [[texture(0)]],device half4*o [[buffer(0)]],uint i [[thread_position_in_grid]]){constexpr sampler s(coord::normalized,address::clamp_to_edge,filter::linear);o[i]=a.sample(s,float2(i+.5f)/16.0f);}
kernel void sampler_nearest_norm(texture2d<half,access::sample> a [[texture(0)]],device half4*o [[buffer(0)]],uint i [[thread_position_in_grid]]){constexpr sampler s(coord::normalized,address::clamp_to_edge,filter::nearest);o[i]=a.sample(s,float2(i+.5f)/16.0f);}
kernel void sampler_linear_pixel(texture2d<half,access::sample> a [[texture(0)]],device half4*o [[buffer(0)]],uint i [[thread_position_in_grid]]){constexpr sampler s(coord::pixel,address::clamp_to_edge,filter::linear);o[i]=a.sample(s,float2(i+.5f));}
'''
(B/'sampler_controls.metal').write_text(source)
if False:cmd(['xcrun','-sdk','macosx','metal','-c','-ffast-math',B/'sampler_controls.metal','-o',B/'sampler_controls.air'],'compile-sampler-controls')
if llvm:
 files=([archive] if archive.exists() else [])+([B/'sampler-runtime.binary.metallib'] if (B/'sampler-runtime.binary.metallib').exists() else [])
 for f in files:
  data=f.read_bytes();offset=0;seen=set();n=0
  while True:
   k=data.find(b'\xde\xc0\x17\x0b',offset)
   if k<0:break
   offset=k+4
   if k+20>len(data):continue
   magic,ver,off,size,cpu=struct.unpack_from('<5I',data,k);raw=data[k+off:k+off+size]
   if not raw.startswith(b'BC\xc0\xde') or len(raw)!=size:continue
   sha=hashlib.sha256(raw).hexdigest()
   if sha in seen:continue
   seen.add(sha)
   try:ir=str(llvm.parse_bitcode(raw))
   except Exception as e:report['air'].append({'container':f.name,'offset':k,'error':str(e)[:300]});continue
   if 'renderFinalAdjustments' not in ir and not any(k in ir for k in ['@norm_', '@pixel_linear', '@runtime_linear']):continue
   n+=1;name=f.stem+f'-{n:03}.ll';(O/name).write_text(ir)
   report['air'].append({'container':f.name,'wrapper_offset':k,'raw_size':size,'raw_sha256':sha,'text_file':name,'text_sha256':hashlib.sha256(ir.encode()).hexdigest(),'classification':'AIR IR, not proof of final backend machine instructions'})
 # Some toolchains emit raw bitcode instead of a wrapper.
 p=B/'sampler_controls.air'
 if p.exists() and p.read_bytes().startswith(b'BC\xc0\xde'):
  raw=p.read_bytes();ir=str(llvm.parse_bitcode(raw));(O/'sampler-controls-raw.ll').write_text(ir);report['air'].append({'container':p.name,'text_file':'sampler-controls-raw.ll','raw_sha256':hashlib.sha256(raw).hexdigest(),'classification':'own explicit sampler helper AIR'})
if (B/'original.gputrace').exists():report['capture_files']=[{'path':str(p.relative_to(B)),'size':p.stat().st_size} for p in sorted((B/'original.gputrace').rglob('*')) if p.is_file()]
if archive.exists():cmd(['file',archive],'archive-file-kind');cmd(['xcrun','llvm-objdump','--macho','--universal-headers',archive],'archive-universal-headers')
if (B/'extracted').exists():report['metal_source_extracted_file_metadata']=[{'path':str(p.relative_to(B)),'size':p.stat().st_size} for p in sorted((B/'extracted').rglob('*')) if p.is_file()]
# No opaque/base64 code, binary archive, AIR bitcode or gputrace is published.
report['global_interval_certified']=False
(O/'backend-inspection.json').write_text(json.dumps(report,indent=2)+'\n')
