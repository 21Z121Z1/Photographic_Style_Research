from pathlib import Path
import subprocess,json,os,time,sys
root=Path.cwd();src=root/'research/vm-native/runner';out=root/'out/acceptance-v6';out.mkdir(parents=True,exist_ok=True);rows=[];start=time.time()
def save():
 (out/'status.json').write_text(json.dumps({'rows':rows,'elapsed_seconds':time.time()-start},indent=2)+'\n')
def command(args,log,env=None,timeout=900):
 with log.open('w')as f:
  try:rc=subprocess.run([str(x)for x in args],stdout=f,stderr=subprocess.STDOUT,env=env,timeout=timeout).returncode
  except subprocess.TimeoutExpired:rc='timeout'
 rows.append({'args':[str(x)for x in args],'returncode':rc,'log':str(log.relative_to(root))});save();return rc
flags=['clang','-fobjc-arc','-O1','-framework','Foundation','-framework','CoreImage','-framework','CoreMedia','-framework','ImageIO','-framework','Metal','-Wl,-undefined,dynamic_lookup']
if command(flags+[src/'native_renderer_trace_v6.m','-o','/tmp/renderer-v6'],out/'build.log')!=0:sys.exit(1)
# This compiler experiment is optional, and never substitutes the original
# framework oracle or changes the existing MSL/NumPy acceptance gates.
air_ok=command(['xcrun','metal','-c','-x','ir',root/'research/vm-native/model-v6/0010.ll','-o','/tmp/consumer-reassembled.air'],out/'air-compile.log',timeout=120)==0
if air_ok:air_ok=command(['xcrun','metallib','/tmp/consumer-reassembled.air','-o','/tmp/consumer-reassembled.metallib'],out/'air-link.log',timeout=120)==0
resources={}
def photo(stem):return root/('research/vm-native/samples'if stem.startswith('IMG_26')else'Apple_Native_Samples')/(stem+'.HEIC')
for stem in['IMG_2600','IMG_2604','IMG_2608','IMG_0032','IMG_0033']:
 resources[stem]=Path(os.environ['RUNNER_TEMP'])/'acceptance-v6'/stem
 if command(['python3',root/'research/vm-native/extract_inputs.py',photo(stem),resources[stem]],out/(stem+'-extract.log'))!=0:continue
 for tone in[0,.35,-.35]:
  if time.time()-start>38*60:
   rows.append({'phase':'deferred','photo':stem,'tone':tone,'reason':'Upload margin; incomplete validation'});save();continue
  case=out/'native'/stem/f'tone-{tone}';case.parent.mkdir(parents=True,exist_ok=True);env=os.environ.copy();env.update({'VM_CONSUMER_MSL':str(src/'consumer-model.metal'),'XD_TONE_THUMB_MODE':'native-stage-mirror','XD_TONE_BIAS':str(tone),'XD_TONE_MAX_EDGE':'512','XD_TONE_GUIDED_REPLAY':'0','VM_EXACT_INVERSE_LIMIT':'196608','VM_SKIP_MSL':'0'})
  seed=root/'research/vm-native/inverse-seeds-v6'/f'{stem}-tone-{tone}.f32'
  if seed.exists():env['VM_INVERSE_SEED_PATH']=str(seed)
  if air_ok:env['VM_REASSEMBLED_AIR_LIBRARY']='/tmp/consumer-reassembled.metallib'
  rc=command(['/tmp/renderer-v6',photo(stem),resources[stem],case],case.parent/f'tone-{tone}.log',env,timeout=720)
  p=case/'renderer-0/native-inverse.json'
  if p.exists():
   j=json.loads(p.read_text());row={'phase':'inverse','photo':stem,'tone':tone,**{k:j[k]for k in ['pixels','full_frame','native_forward_verified','failed_eligible_pixels','max_relative_error_in_mask','mask_coverage']}};rows.append(row);save();print(json.dumps(row),flush=True)
  else:rows.append({'phase':'missing-inverse','photo':stem,'tone':tone,'process_returncode':rc});save()
# Summary and any failures remain visible; no failing pixel or profile is dropped.
save();required=[r for r in rows if r.get('phase')=='inverse'];complete=len(required)==15 and all(r['failed_eligible_pixels']==0 and r['max_relative_error_in_mask']<=1e-3 for r in required)
summary={'native_roundtrip_all_15_passed':complete,'profiles':len(required),'scope':'Full 512x384 native consumer dispatches, not original 12/24MP resolution','threshold_unchanged':1e-3,'original_input_used_as_seed':False}
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)
sys.exit(0 if complete and all(r.get('returncode',0)==0 for r in rows if not str(r.get('log','')).endswith(('air-compile.log','air-link.log')))else 1)
