"""Run fresh, isolated real-photo tests. The workflow seals all private output."""
from pathlib import Path
import sys,os,json,hashlib,subprocess
R=Path.cwd();W=Path(os.environ['W']);O=W/'out';O.mkdir(exist_ok=True);SRC=R/'research/semantic-styles';OLD=R/'research/vm-native/runner';RES=W/'res';PHOTO=W/'IMG_2810.HEIC';GEN=W/'generated'
sys.path.insert(0,str(R));sys.path.insert(0,str(R/'research/vm-native'))
from extract_inputs import extract
from tools.heif_dump import parse_heif
from heif_standalone import standalone
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
assert hashlib.sha256(PHOTO.read_bytes()).hexdigest()=='52ea41f0dd16590cef83abfd8093ccf8082994113e0c2cee86f90c42f7ab21c2'
status=[]
def run(cmd,name,env=None,timeout=600):
 try:
  with (O/(name+'.log')).open('w') as log:rc=subprocess.run(list(map(str,cmd)),stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,**(env or{})),timeout=timeout).returncode
 except subprocess.TimeoutExpired:rc='timeout'
 status.append({'operation':name,'returncode':rc});(O/'status.json').write_text(json.dumps(status,indent=2)+'\n');return rc
extract(PHOTO,RES);data=PHOTO.read_bytes();h=parse_heif(data)
names={'nose':'noseMatte','skinv2':'skinMatteV2','nonfaceskin':'nonFaceSkinMatte','lips':'lipsMatte','teethv2':'teethMatteV2','person':'personMatte','glassesv2':'glassesMatteV2','eyebrows':'eyebrowsMatte','tattoo':'tattooMatte','hands':'handsMatte','ears':'earsMatte','faceskin':'faceSkinMatte'}
for item in h['items'].values():
 aux=item.get('aux_type','')
 for key,target in names.items():
  if aux.endswith('semantic'+key+'matte') or (key.endswith('v2') and aux.endswith('semantic'+key[:-2]+'mattev2')):(RES/(target+'.heic')).write_bytes(standalone(data,item['item_id']))
for target,suffix in {'inputSubjectMatteImage':'semanticpersonmatte','inputSkinMatteImage':'semanticskinmatte','inputSkyMatteImage':'semanticskymatte','inputGainMapImage':'hdrgainmap'}.items():
 matches=[i for i in h['items'].values() if i.get('aux_type','').endswith(suffix)]
 if matches:(RES/(target+'.heic')).write_bytes(standalone(data,matches[0]['item_id']))
assert run([sys.executable,SRC/'generate_semantic_s5.py',GEN],'generate')==0
flags=['clang','-fobjc-arc','-O2','-I'+str(OLD),'-I'+str(GEN),'-framework','Foundation','-framework','CoreImage','-framework','CoreMedia','-framework','ImageIO','-framework','Metal','-Wl,-undefined,dynamic_lookup']
exe=W/'semantic-consumer'
if run(flags+[SRC/'semantic_consumer_s5.m','-o',exe],'build-consumer')==0:
 for label,tone,inverse in [('tone0','0',False),('toneP035','0.35',True),('toneN035','-0.35',False)]:
  env={'XD_TONE_MAX_EDGE':'512','XD_TONE_THUMB_MODE':'native-stage-mirror','XD_TONE_BIAS':tone,'SEMANTIC_STAGE_MSL':str(GEN/'semantic_stage_s5.metal'),'SEMANTIC_RUN_INVERSE':str(int(inverse)),'VM_EXACT_INVERSE_LIMIT':'196608'}
  run([exe,PHOTO,RES,O/('consumer-'+label)],'consumer-'+label,env,timeout=900)
run([sys.executable,SRC/'analyze_semantic_s5.py',O],'analysis',timeout=600)
import shutil
shutil.copy2(GEN/'generated-source-sha256.json',O/'generated-source-sha256.json')
print('S5 private native probes finished; encrypted output only.')
