"""Public, photograph-free runtime and resource discovery."""
from pathlib import Path
import hashlib,json,plistlib,subprocess,sys
ROOT=Path.cwd();OUT=ROOT/'out/semantic-s1';OUT.mkdir(parents=True,exist_ok=True);SRC=ROOT/'research/semantic-styles'
def command(args,name):
 with(OUT/name).open('w')as f:return subprocess.run([str(v)for v in args],stdout=f,stderr=subprocess.STDOUT).returncode
build=subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip();assert build=='26A434',build
command(['sw_vers'],'host.txt');command(['xcodebuild','-version'],'xcode.txt');exe=Path('/tmp/semantic-runtime-s1');rc=command(['clang','-fobjc-arc','-O1','-framework','Foundation','-framework','CoreImage','-framework','Metal',SRC/'semantic_runtime_s1.m','-o',exe],'build.log')
if not rc:rc=command([exe,OUT],'runtime.log')
resources=[]
for name in ['NeutrinoCore','PhotoImaging','CMImaging']:
 root=Path('/System/Library/PrivateFrameworks')/(name+'.framework/Resources')
 for p in sorted(root.rglob('*')):
  if not p.is_file()or p.suffix not in ['.plist','.metallib']:continue
  row={'framework':name,'path':str(p),'bytes':p.stat().st_size};h=hashlib.sha256()
  with p.open('rb')as f:
   for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
  row['sha256']=h.hexdigest()
  if p.suffix=='.plist'and p.stat().st_size<2*1024*1024:
   try:
    obj=plistlib.loads(p.read_bytes());row['root_keys']=list(obj)if isinstance(obj,dict)else None
    if any(s in str(p).lower()for s in ['texture','skin','person','style']):
     dest=OUT/'tuning'/(name+'-'+p.name+'.json');dest.parent.mkdir(exist_ok=True);dest.write_text(json.dumps(obj,indent=2,default=lambda x:{'bytes':len(x)}if isinstance(x,bytes)else str(x))+'\n')
   except Exception as e:row['parse_error']=str(e)
  resources.append(row)
(OUT/'resources.json').write_text(json.dumps(resources,indent=2)+'\n');(OUT/'status.json').write_text(json.dumps({'os_build':build,'runtime_returncode':rc,'resource_count':len(resources),'photographs_or_person_pixels_uploaded':False},indent=2)+'\n');print('Photograph-free semantic runtime preflight complete');raise SystemExit(rc)
