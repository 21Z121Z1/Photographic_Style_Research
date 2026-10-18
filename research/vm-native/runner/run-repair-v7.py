from pathlib import Path
import subprocess,json,os,time,sys
root=Path.cwd();src=root/'research/vm-native/runner';out=root/'out/native-repair-v7';out.mkdir(parents=True,exist_ok=True);rows=[];start=time.time()
def save():(out/'status.json').write_text(json.dumps({'rows':rows,'elapsed_seconds':time.time()-start},indent=2)+'\n')
def command(args,log,env=None,timeout=480):
 with log.open('w')as f:
  try:rc=subprocess.run([str(x)for x in args],stdout=f,stderr=subprocess.STDOUT,env=env,timeout=timeout).returncode
  except subprocess.TimeoutExpired:rc='timeout'
 rows.append({'args':[str(x)for x in args],'returncode':rc,'log':str(log.relative_to(root))});save();return rc
flags=['clang','-fobjc-arc','-O1','-framework','Foundation','-framework','CoreImage','-framework','CoreMedia','-framework','ImageIO','-framework','Metal','-Wl,-undefined,dynamic_lookup']
if command(flags+[src/'native_renderer_trace_v7.m','-o','/tmp/renderer-v7'],out/'build.log')!=0:sys.exit(1)
stem='IMG_2600';photo=root/'research/vm-native/samples'/f'{stem}.HEIC';resources=Path(os.environ['RUNNER_TEMP'])/'repair-v7'/stem
if command(['python3',root/'research/vm-native/extract_inputs.py',photo,resources],out/'extract.log')!=0:sys.exit(1)
case=out/stem/'tone--0.35';case.parent.mkdir(exist_ok=True);env=os.environ.copy();env.update({'VM_CONSUMER_MSL':str(src/'consumer-nodebug-v7.metal'),'XD_TONE_THUMB_MODE':'native-stage-mirror','XD_TONE_BIAS':'-0.35','XD_TONE_MAX_EDGE':'512','XD_TONE_GUIDED_REPLAY':'0','VM_EXACT_INVERSE_LIMIT':'196608','VM_SKIP_MSL':'0','VM_INVERSE_SEED_PATH':str(root/'research/vm-native/inverse-seeds-v7/IMG_2600-tone--0.35.f32')})
rc=command(['/tmp/renderer-v7',photo,resources,case],out/'renderer.log',env)
p=case/'renderer-0/native-inverse.json';j=json.loads(p.read_text())if p.exists()else None
summary={'scope':'Only the one unresolved V6 native profile is repaired; other 14 validated profiles are not recomputed','complete_acceptance':False,'profile':'IMG_2600 tone=-0.35 full 512x384','native_roundtrip_passed':bool(j and j['full_frame']and j['failed_eligible_pixels']==0 and j['max_relative_error_in_mask']<=.001),'native_inverse':j,'msl_nodebug':json.loads((p.parent/'model-precision-v2.json').read_text())if(p.parent/'model-precision-v2.json').exists()else None}
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items()if k!='native_inverse'}));save();sys.exit(0 if rc==0 and summary['native_roundtrip_passed']else 1)
