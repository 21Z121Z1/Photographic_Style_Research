"""Private real-photo native probes; all output is encrypted by the workflow."""
from pathlib import Path
import sys,os,json,hashlib,subprocess,plistlib
R=Path.cwd();W=Path(os.environ['W']);OUT=W/'out';OUT.mkdir(exist_ok=True);SRC=R/'research/semantic-styles';OLD=R/'research/vm-native/runner';RES=W/'res';PHOTO=W/'IMG_2810.HEIC'
sys.path.insert(0,str(R));sys.path.insert(0,str(R/'research/vm-native'))
from extract_inputs import extract
from tools.heif_dump import parse_heif,_payload_from_item_extents
from heif_standalone import standalone
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
assert hashlib.sha256(PHOTO.read_bytes()).hexdigest()=='52ea41f0dd16590cef83abfd8093ccf8082994113e0c2cee86f90c42f7ab21c2'
status=[]
def run(cmd,name,env=None,timeout=180):
 try:
  with (OUT/(name+'.log')).open('w')as log:rc=subprocess.run(list(map(str,cmd)),stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,**(env or{})),timeout=timeout).returncode
 except subprocess.TimeoutExpired:rc='timeout'
 status.append({'operation':name,'returncode':rc});(OUT/'status.json').write_text(json.dumps(status,indent=2)+'\n');return rc
extract(PHOTO,RES);data=PHOTO.read_bytes();h=parse_heif(data)
names={'nose':'noseMatte','skinv2':'skinMatteV2','nonfaceskin':'nonFaceSkinMatte','lips':'lipsMatte','teethv2':'teethMatteV2','person':'personMatte','glassesv2':'glassesMatteV2','eyebrows':'eyebrowsMatte','tattoo':'tattooMatte','hands':'handsMatte','ears':'earsMatte','faceskin':'faceSkinMatte','hair':'hairMatte'}
for item in h['items'].values():
 aux=item.get('aux_type','')
 for key,target in names.items():
  if aux.endswith('semantic'+key+'matte')or (key.endswith('v2')and aux.endswith('semantic'+key[:-2]+'mattev2')):(RES/(target+'.heic')).write_bytes(standalone(data,item['item_id']))
 if item.get('uri_type','').endswith('texture_styles'):(RES/'texture_styles.plist').write_bytes(_payload_from_item_extents(data,item))
choices={'inputSubjectMatteImage':'semanticpersonmatte','inputSkinMatteImage':'semanticskinmatte','inputSkyMatteImage':'semanticskymatte','inputGainMapImage':'hdrgainmap'}
for target,suffix in choices.items():
 matches=[i for i in h['items'].values()if i.get('aux_type','').endswith(suffix)]
 if matches:(RES/(target+'.heic')).write_bytes(standalone(data,matches[0]['item_id']))
flags=['clang','-fobjc-arc','-O1','-I'+str(OLD),'-I'+str(SRC),'-framework','Foundation','-framework','CoreImage','-framework','CoreMedia','-framework','ImageIO','-framework','Metal','-Wl,-undefined,dynamic_lookup']
executables={}
sources=[('thumbnail',OLD/'native_thumbnail_stage.m'),('texture',SRC/'semantic_texture_s2.m')]
if os.environ.get('SEMANTIC_PHASE')!='texture-fix':sources += [('face',SRC/'semantic_face_s2.m'),('resolve',OLD/'resolve_calls.m')]
for name,source in sources:
 exe=W/name
 if run(flags+[source,'-o',exe],'build-'+name)==0:executables[name]=exe
if 'resolve'in executables:run([executables['resolve'],SRC/'call-addresses-s2.json',OUT/'resolved-calls.json'],'resolve')
if 'thumbnail'in executables:run([executables['thumbnail'],RES,RES/'thumbnail'],'thumbnail')
if 'face'in executables:
 for label,j in [('actual',None),('j1','1'),('j1p2','1.2')]:
  env={'XD_TONE_MAX_EDGE':'512','XD_TONE_THUMB_MODE':'native-stage-mirror','XD_TONE_BIAS':'0'}
  if j:env['SEMANTIC_J']=j
  run([executables['face'],PHOTO,RES,OUT/('face-'+label)],'face-'+label,env)
if 'texture'in executables:run([executables['texture'],RES,OUT/'texture',PHOTO],'texture',timeout=240)
run([sys.executable,SRC/'extract_texture_air.py',OUT/'texture-air'],'texture-air',timeout=240)
run([sys.executable,SRC/'summarize_semantic_s2.py',OUT,RES],'metrics',timeout=180)
rows=[]
for p in sorted(OUT.rglob('*')):
 if p.is_file():
  a=hashlib.sha256()
  with p.open('rb')as f:
   for b in iter(lambda:f.read(1024*1024),b''):a.update(b)
  rows.append({'path':str(p.relative_to(OUT)),'size':p.stat().st_size,'sha256':a.hexdigest()})
(OUT/'manifest.json').write_text(json.dumps({'run_id':os.environ['GITHUB_RUN_ID'],'commit':os.environ['GITHUB_SHA'],'os_build':'26A434','files':rows},indent=2)+'\n')
print('Private semantic native probes finished. Outputs remain encrypted.')
