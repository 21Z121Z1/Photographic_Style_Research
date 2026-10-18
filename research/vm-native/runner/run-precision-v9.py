from pathlib import Path
import hashlib,json,os,subprocess,sys,time
ROOT=Path.cwd();SRC=ROOT/'research/vm-native/runner';OUT=ROOT/'out/precision-v9';OUT.mkdir(parents=True,exist_ok=True);rows=[];start=time.time()
def command(args,log,timeout=300,env=None):
 log.parent.mkdir(parents=True,exist_ok=True)
 with log.open('w')as f:
  try:rc=subprocess.run([str(v)for v in args],stdout=f,stderr=subprocess.STDOUT,timeout=timeout,env=env).returncode
  except subprocess.TimeoutExpired:rc='timeout'
 rows.append({'args':[str(v)for v in args],'returncode':rc,'log':str(log.relative_to(ROOT))});(OUT/'status.json').write_text(json.dumps({'elapsed_seconds':time.time()-start,'rows':rows},indent=2)+'\n');return rc
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def main():
 build=subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip();assert build=='26A434',build
 prior=Path(os.environ['RUNNER_TEMP'])/'precision-v9-prior';math_prior=Path(os.environ['RUNNER_TEMP'])/'precision-v9-primitives'
 for run,directory in [('39111905092',prior),('39118612970',math_prior)]:
  if command(['gh','run','download',run,'--repo','21Z121Z1/Photographic_Style_Research','--name','vm-native-text','--dir',directory],OUT/f'download-{run}.log',600)!=0:return 1
 captures=next(prior.rglob('acceptance-v6/native'));primitives=next(math_prior.rglob('precision-v8/math'))
 if command([sys.executable,SRC/'generate_candidates_v9.py','--source',SRC/'consumer-structured-v8.metal','--out',OUT/'msl-sources'],OUT/'generation.log')!=0:return 1
 exe=Path('/tmp/precision-context-v9')
 if command(['clang','-fobjc-arc','-O2','-framework','Foundation','-framework','Metal',SRC/'context_precision_v9.m','-o',exe],OUT/'build-context.log')!=0:return 1
 # SDK tool and compile option provenance only; no component is downloaded.
 with (OUT/'compiler-tool-availability.txt').open('w')as f:
  for name in ['metal','metal-objdump','metal-dis','metal-tt','metal-lipo','metallib','metal-ar']:
   subprocess.run(['xcrun','--find',name],stdout=f,stderr=subprocess.STDOUT)
 variants=OUT/'msl-sources/variants.json';discovery=[]
 for tone in ['tone-0','tone-0.35','tone--0.35']:
  dest=OUT/'msl/IMG_2600'/tone;rc=command([exe,captures/'IMG_2600'/tone/'renderer-0',variants,dest,''],OUT/f'discovery-{tone}.log',600);j=read(dest/'model-comparisons.json')if(dest/'model-comparisons.json').exists()else[];discovery.append({'tone':tone,'returncode':rc,'comparisons':j});print('DISCOVERY',tone,[(r['variant'],r.get('half_differing_components',r.get('error','error')))for r in j],flush=True)
 (OUT/'discovery.json').write_text(json.dumps(discovery,indent=2)+'\n')
 eligible=[]
 for variant in read(variants):
  cases=[next((r for r in d['comparisons']if r['variant']==variant['name']),{})for d in discovery]
  if len(cases)==3 and all(r.get('half_differing_components',-1)==0 for r in cases)and not variant.get('capture_checkpoints'):eligible.append(variant)
 freeze={'frozen_unix_time':time.time(),'selection_inputs':['IMG_2600 tone 0,+0.35,-0.35 full captured frames'],'heldout_not_validated_before_selection':['IMG_0032','IMG_0033'],'eligible_candidates':eligible,'os_build':build};(OUT/'selected-freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
 validated=[]
 if eligible:
  # Deterministic source order, selected before any other photo is run.
  selected=eligible[0];chosen=OUT/'selected-variant.json';chosen.write_text(json.dumps([selected],indent=2)+'\n')
  for stem in ['IMG_2604','IMG_2608','IMG_0032','IMG_0033']:
   for tone in ['tone-0','tone-0.35','tone--0.35']:
    dest=OUT/'msl'/stem/tone;rc=command([exe,captures/stem/tone/'renderer-0',chosen,dest,''],OUT/f'validate-{stem}-{tone}.log',180);j=read(dest/'model-comparisons.json')if(dest/'model-comparisons.json').exists()else[];validated.append({'photo':stem,'tone':tone,'returncode':rc,'comparisons':j});print('VALIDATE',stem,tone,[(r['variant'],r.get('half_differing_components','error'))for r in j],flush=True)
 diag=OUT/'msl/IMG_2600/tone-0/smooth-diagnostic.checkpoints.f32';env=os.environ.copy();env.update({'OPENBLAS_NUM_THREADS':'1','AIR_FUSION':'1','AIR_NATIVE_LOWERING':'1','AIR_TEX_HALF_UP':'1','AIR_DOT_EQUAL':'0'})
 if diag.exists():command([sys.executable,SRC/'cpu_trace_v9.py','--model',ROOT/'research/vm-native/model-v8','--math',primitives,'--capture',captures/'IMG_2600/tone-0/renderer-0','--msl',diag,'--out',OUT/'numpy-diagnostic'],OUT/'numpy-diagnostic.log',300,env)
 msl_pass=bool(eligible and len(validated)==12 and all(r.get('half_differing_components',-1)==0 for item in validated for r in item['comparisons']))
 summary={'os_build':build,'msl_full_15_bit_exact':msl_pass,'selected_variant':eligible[0]if eligible else None,'numpy_half_bit_exact':False,'numpy_scope':'Diagnostic only; no five-photo acceptance asserted','validation_profiles':validated,'scientific_scope':'Consumer captured 512x384 fixed contexts, separate from camera production and physical GTM/LTM decomposition'};(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items()if k!='validation_profiles'}),flush=True);return 0 if msl_pass else 1
if __name__=='__main__':raise SystemExit(main())
