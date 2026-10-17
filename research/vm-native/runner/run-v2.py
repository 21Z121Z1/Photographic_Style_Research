import pathlib,subprocess,os,json
root=pathlib.Path.cwd();src=root/'research/vm-native/runner';out=root/'out/native';out.mkdir(parents=True,exist_ok=True);rows=[]
def run(args,log,env=None):
 with log.open('w') as f:
  try:rc=subprocess.run([str(x) for x in args],stdout=f,stderr=subprocess.STDOUT,timeout=600,env=env).returncode
  except subprocess.TimeoutExpired:rc='timeout'
  except OSError as e:f.write(str(e));rc='spawn-error'
 rows.append({'args':[str(x) for x in args],'returncode':rc,'log':str(log.relative_to(root))});return rc
flags=['clang','-fobjc-arc','-O1','-framework','Foundation','-framework','CoreImage','-framework','CoreMedia','-framework','ImageIO','-framework','Metal','-Wl,-undefined,dynamic_lookup']
if run(flags+[src/'native_renderer_trace_v2.m','-o','/tmp/renderer-v2'],out/'renderer-v2-build.log')==0:
 stem='IMG_2600';photo=root/'research/vm-native/samples'/(stem+'.HEIC');resources=pathlib.Path(os.environ['RUNNER_TEMP'])/'v2-resources'/stem
 if run(['python3',root/'research/vm-native/extract_inputs.py',photo,resources],out/'extract.log')==0:
  for tone in [0,.35,-.35]:
   case=out/stem/('tone-'+str(tone));case.parent.mkdir(parents=True,exist_ok=True);env=os.environ.copy();env.update({'VM_CONSUMER_MSL':str(src/'consumer-model.metal'),'XD_TONE_THUMB_MODE':'native-stage-mirror','XD_TONE_BIAS':str(tone),'XD_TONE_MAX_EDGE':'512','XD_TONE_GUIDED_REPLAY':'0','VM_EXACT_INVERSE_LIMIT':'4096','VM_SKIP_MSL':'1'})
   run(['/tmp/renderer-v2',photo,resources,case],case.parent/('tone-'+str(tone)+'.log'),env)
if run(['clang','-fobjc-arc','-O1','-framework','Foundation','-framework','Metal',src/'atan2_table_v2.m','-o','/tmp/atan2-table-v2'],out/'atan2-table-v2-build.log')==0:
 run(['/tmp/atan2-table-v2',out/'atan2-table-v2'],out/'atan2-table-v2.log')
(out/'status.json').write_text(json.dumps(rows,indent=2)+'\n');raise SystemExit(1 if any(x['returncode']!=0 for x in rows) else 0)
