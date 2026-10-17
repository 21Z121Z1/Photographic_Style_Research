import pathlib,subprocess,os,json,hashlib,sys
root=pathlib.Path.cwd();src=root/'research/vm-native/runner';out=root/'out/native';out.mkdir(parents=True,exist_ok=True)
rows=[]
def run(args,log,env=None):
 with open(log,'w') as f:
  try:r=subprocess.run([str(x) for x in args],stdout=f,stderr=subprocess.STDOUT,timeout=240,env=env);rc=r.returncode
  except subprocess.TimeoutExpired:rc='timeout'
  except OSError as error:f.write(str(error));rc='spawn-error'
 rows.append({'args':[str(x) for x in args],'log':str(log.relative_to(root)),'returncode':rc});return rc
flags=['clang','-fobjc-arc','-O1','-framework','Foundation','-framework','CoreImage','-framework','CoreMedia','-framework','ImageIO','-framework','Metal','-Wl,-undefined,dynamic_lookup']
for name in ['native_thumbnail_stage','native_renderer_trace','reverse_main','resolve_calls','arithmetic','readback_main','contrast_probe']:
 run(flags+[src/(name+'.m'),'-o','/tmp/'+name],out/(name+'-build.log'))
# Selector and arithmetic discovery results are already archived.
# Do not repeat the independent contrast control.
# Arithmetic evidence is preserved in run 39054842867; no repeat here.
# First native consumer evaluation of the two held-out photos, after model freeze.
for stem in ['IMG_0032','IMG_0033']:
 photo=root/'Apple_Native_Samples'/(stem+'.HEIC');resources=pathlib.Path(os.environ['RUNNER_TEMP'])/'photo-resources'/stem
 rc=run(['python3',root/'research/vm-native/extract_inputs.py',photo,resources],out/(stem+'-extract.log'))
 if rc!=0:continue
 case=out/stem;case.mkdir(exist_ok=True)
 run(['/tmp/native_thumbnail_stage',resources,case/'thumbnail'],case/'thumbnail.log')
 if True:
  env=os.environ.copy();env['VM_DISABLE_RESIDENCY_SETS']='1'
  run(['/tmp/reverse_main',photo,resources,'2048'],case/'reverse.log',env)
  run(['log','show','--last','2m','--style','compact','--predicate','process == "reverse_main"'],case/'unified.log')
 for diagnostic in ['memory-descriptor.json','reverse-settings.json','setup-processor.json','runtime-override.txt']:
  if (resources/diagnostic).exists():(resources/diagnostic).replace(case/diagnostic)
 for p in resources.glob('*.f32'):p.replace(case/p.name)
 for p in resources.glob('*.bin'):p.replace(case/p.name)
 if (resources/'reverse.json').exists():(resources/'reverse.json').replace(case/'reverse.json')
 for tone in [0,.35]:
  env=os.environ.copy();env.update({'VM_CONSUMER_MSL':str(src/'consumer-model.metal'),'XD_TONE_THUMB_MODE':'native-stage-mirror','XD_TONE_BIAS':str(tone),'XD_TONE_MAX_EDGE':'512','XD_TONE_GUIDED_REPLAY':'0'})
  run(['/tmp/native_renderer_trace',photo,resources,case/('tone-'+str(tone))],case/('tone-'+str(tone)+'.log'),env)
 # Preserve shape/dtype even when a stage fails.
 for p in case.glob('*.f32'):
  meta={};f=case/'reverse.json'
  if f.exists():
   j=json.loads(f.read_text());key={'unstyled.f32':'unstyled','original_hdr.f32':'original_hdr','original_sdr.f32':'unstyled','thumbnail_codes.f32':'thumbnail'}.get(p.name)
   if key:meta={'shape':[j[key]['height'],j[key]['width'],4],'dtype':'<f4','colour_space':'extended-linear Display P3' if key!='thumbnail' else 'unmanaged'}
  if meta:(case/(p.name+'.json')).write_text(json.dumps(meta,indent=2)+'\n')
(out/'status.json').write_text(json.dumps(rows,indent=2)+'\n')
print('Probe commands',len(rows),'nonzero',sum(x['returncode']!=0 for x in rows))

sys.exit(1 if any(x["returncode"]!=0 for x in rows) else 0)
