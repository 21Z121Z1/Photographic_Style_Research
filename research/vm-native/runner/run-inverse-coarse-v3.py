from pathlib import Path
import subprocess,json,os,time,sys
root=Path.cwd();src=root/'research/vm-native/runner';out=root/'out/native-inverse-coarse-v3';out.mkdir(parents=True,exist_ok=True);rows=[];start=time.time()
def save():
 (out/'status.json').write_text(json.dumps({'rows':rows,'elapsed_seconds':time.time()-start},indent=2)+'\n')
def command(args,log,env=None,timeout=900):
 with log.open('w')as f:
  try:rc=subprocess.run([str(x)for x in args],stdout=f,stderr=subprocess.STDOUT,env=env,timeout=timeout).returncode
  except subprocess.TimeoutExpired:rc='timeout'
 rows.append({'args':[str(x)for x in args],'returncode':rc,'log':str(log.relative_to(root))});save();return rc
flags=['clang','-fobjc-arc','-O1','-framework','Foundation','-framework','CoreImage','-framework','CoreMedia','-framework','ImageIO','-framework','Metal','-Wl,-undefined,dynamic_lookup']
if command(flags+[src/'native_renderer_trace_v3_coarse.m','-o','/tmp/renderer-coarse-v3'],out/'build.log')!=0:sys.exit(1)
resources={}
def photo(stem):return root/('research/vm-native/samples'if stem.startswith('IMG_26')else'Apple_Native_Samples')/(stem+'.HEIC')
def render(stem,tone,limit,phase):
 if stem not in resources:
  resources[stem]=Path(os.environ['RUNNER_TEMP'])/'inverse-v3-coarse'/stem
  if command(['python3',root/'research/vm-native/extract_inputs.py',photo(stem),resources[stem]],out/(stem+'-extract.log'))!=0:return None
 case=out/phase/stem/f'tone-{tone}';case.parent.mkdir(parents=True,exist_ok=True);env=os.environ.copy();env.update({'VM_CONSUMER_MSL':str(src/'consumer-model.metal'),'XD_TONE_THUMB_MODE':'native-stage-mirror','XD_TONE_BIAS':str(tone),'XD_TONE_MAX_EDGE':'512','XD_TONE_GUIDED_REPLAY':'0','VM_EXACT_INVERSE_LIMIT':str(limit),'VM_SKIP_MSL':'1'});rc=command(['/tmp/renderer-coarse-v3',photo(stem),resources[stem],case],case.parent/f'tone-{tone}.log',env)
 result=case/'renderer-0/native-inverse.json'
 if result.exists():
  j=json.loads(result.read_text());rows.append({'phase':phase,'photo':stem,'tone':tone,'pixels':j['pixels'],'full_frame':j['full_frame'],'failed_eligible':j['failed_eligible_pixels'],'max_relative':j['max_relative_error_in_mask'],'mask_coverage':j['mask_coverage']});save();print(phase,stem,tone,rows[-1],flush=True);return j
 return None
pilot=[render('IMG_2600',t,4096,'pilot')for t in[0,.35,-.35]]
# Capture previously missing nonzero-tone contexts even if the pilot still fails.
for stem,tones in[('IMG_2604',[.35,-.35]),('IMG_2608',[.35,-.35]),('IMG_0032',[-.35]),('IMG_0033',[-.35])]:
 for t in tones:render(stem,t,0,'contexts')
if all(j is not None and j['failed_eligible_pixels']==0 for j in pilot):
 for stem in['IMG_2600','IMG_2604','IMG_2608','IMG_0032','IMG_0033']:
  for t in[0,.35,-.35]:
   if time.time()-start>35*60:
    rows.append({'phase':'deferred','photo':stem,'tone':t,'reason':'Keep upload/archive margin before job timeout; this is incomplete validation'});save();continue
   render(stem,t,196608,'full512')
else:rows.append({'phase':'pilot-gate','pass':False,'reason':'4096 pixel pilot failed unchanged 1e-3 threshold; full-frame validation not promoted'})
save();sys.exit(1 if any(x.get('returncode',0)!=0 or x.get('failed_eligible',0)>0 or x.get('phase')in['deferred','pilot-gate']for x in rows)else 0)
