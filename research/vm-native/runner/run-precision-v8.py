from pathlib import Path
import subprocess,json,os,time,sys
root=Path.cwd();src=root/'research/vm-native/runner';model=root/'research/vm-native/model-v8';out=root/'out/precision-v8';out.mkdir(parents=True,exist_ok=True);rows=[];start=time.time()
def save():(out/'status.json').write_text(json.dumps({'rows':rows,'elapsed_seconds':time.time()-start},indent=2)+'\n')
def command(args,log,timeout=300,env=None):
 log.parent.mkdir(parents=True,exist_ok=True)
 with log.open('w')as f:
  try:rc=subprocess.run([str(x)for x in args],stdout=f,stderr=subprocess.STDOUT,timeout=timeout,env=env).returncode
  except subprocess.TimeoutExpired:rc='timeout'
 rows.append({'args':[str(x)for x in args],'returncode':rc,'log':str(log.relative_to(root))});save();return rc
build=subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()
if build!='26A434':
 (out/'wrong-build.json').write_text(json.dumps({'actual':build,'required':'26A434','acceptance_complete':False}));sys.exit(1)
prior=Path(os.environ['RUNNER_TEMP'])/'precision-v8-prior'
if command(['gh','run','download','39111905092','--repo','21Z121Z1/Photographic_Style_Research','--name','vm-native-text','--dir',prior],out/'download-prior.log',timeout=600)!=0:sys.exit(1)
candidates=list(prior.rglob('acceptance-v6/native'));assert len(candidates)==1;c=candidates[0]
flags=['clang','-fobjc-arc','-O2','-framework','Foundation','-framework','Metal','-lz']
math_ok=True
for name,source,subdir in [('pow','pow_lut_v8.m','pow'),('atan','atan_scalar_v8.m','atan-scalar'),('extra','half_extra_v8.m','half-extra')]:
 exe=Path('/tmp')/f'precision-v8-{name}'
 if command([*flags,src/source,'-o',exe],out/f'build-{name}.log')!=0:math_ok=False;continue
 if command([exe,out/'math'/subdir],out/f'math-{name}.log',timeout=600)!=0:math_ok=False
variants=[{'name':'structured-fast','source':str(src/'consumer-structured-v8.metal'),'fast_math':True},{'name':'structured-uninit-fast','source':str(src/'consumer-structured-uninit-v8.metal'),'fast_math':True}]
(out/'variants.json').write_text(json.dumps(variants,indent=2)+'\n');(out/'layout.json').write_bytes((model/'layout.json').read_bytes());msl=[]
exe=Path('/tmp/precision-v8-context')
if command([*flags,src/'context_precision_v8.m','-o',exe],out/'build-context.log')==0:
 for stem in ['IMG_2600','IMG_2604','IMG_2608','IMG_0032','IMG_0033']:
  for tone in ['tone-0','tone-0.35','tone--0.35']:
   dest=out/'msl'/stem/tone;zero=c/stem/'tone-0/renderer-0/_paramsBuf.bin'if stem=='IMG_2600'and tone!='tone-0'else''
   rc=command([exe,c/stem/tone/'renderer-0',out/'variants.json',dest,zero],out/'msl-logs'/f'{stem}-{tone}.log',timeout=180)
   f=dest/'model-comparisons.json';control=dest/'native-hydration-control.json';comparisons=json.loads(f.read_text())if f.exists()else[];hydration=json.loads(control.read_text())if control.exists()else None
   row={'photo':stem,'tone':tone,'returncode':rc,'native_hydration':hydration,'comparisons':comparisons};msl.append(row);print('MSL',stem,tone,[(r['variant'],r.get('half_differing_components','compile-error'))for r in comparisons],flush=True)
   (out/'msl-summary.json').write_text(json.dumps(msl,indent=2)+'\n')
else:msl=[]
common=[]
for variant in variants:
 name=variant['name'];matches=[next((r for r in item['comparisons']if r['variant']==name),{})for item in msl]
 if len(matches)==15 and all(x.get('pixels')==196608 and x.get('half_differing_components',-1)==0 for x in matches)and all(x['native_hydration']and x['native_hydration']['half_differing_components']==0 for x in msl):common.append(name)
numpy_rc='not-run'
if math_ok:
 env=os.environ.copy();env.update({'OPENBLAS_NUM_THREADS':'1','MALLOC_ARENA_MAX':'2','AIR_FUSION':'1','AIR_NATIVE_LOWERING':'1','AIR_TEX_HALF_UP':'1','AIR_DOT_EQUAL':'0'})
 numpy_rc=command([sys.executable,model/'cpu_probe.py','--captures',c,'--math',out/'math','--out',out/'numpy'],out/'numpy.log',timeout=2100,env=env)
np_summary=json.loads((out/'numpy/summary.json').read_text())if(out/'numpy/summary.json').exists()else None
summary={'os_build':build,'prior_native_capture_run':'39111905092','common_full_15_bit_exact_msl_variants':common,'numpy_half_bit_exact':bool(np_summary and np_summary.get('numpy_half_bit_exact')),'math_generation_succeeded':math_ok,'numpy_returncode':numpy_rc,'scope':'Consumer full captured 512x384 frames. R2/SDR evidence is maintained in their separate archived runs. No physical scene/RAW equivalence is inferred.'}
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');save();print(json.dumps(summary),flush=True);sys.exit(0 if common and summary['numpy_half_bit_exact']else 1)
