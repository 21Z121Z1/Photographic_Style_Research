from pathlib import Path
import hashlib,json,os,subprocess,sys,time
ROOT=Path.cwd();SRC=ROOT/'research/vm-native/runner';OUT=ROOT/'out/precision-v10';OUT.mkdir(parents=True,exist_ok=True);rows=[];start=time.time()
def command(args,log,timeout=300,env=None):
 log.parent.mkdir(parents=True,exist_ok=True)
 with log.open('w')as f:
  try:rc=subprocess.run([str(v)for v in args],stdout=f,stderr=subprocess.STDOUT,timeout=timeout,env=env).returncode
  except subprocess.TimeoutExpired:rc='timeout'
 rows.append({'args':[str(v)for v in args],'returncode':rc,'log':str(log.relative_to(ROOT))});(OUT/'status.json').write_text(json.dumps({'elapsed_seconds':time.time()-start,'rows':rows},indent=2)+'\n');return rc
def read(p):return json.loads(Path(p).read_text())
def main():
 build=subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip();assert build=='26A434';prior=Path(os.environ['RUNNER_TEMP'])/'precision-v10-prior';math_prior=Path(os.environ['RUNNER_TEMP'])/'precision-v10-math'
 for run,directory in [('39111905092',prior),('39118612970',math_prior)]:
  if command(['gh','run','download',run,'--repo','21Z121Z1/Photographic_Style_Research','--name','vm-native-text','--dir',directory],OUT/f'download-{run}.log',600)!=0:return 1
 captures=next(prior.rglob('acceptance-v6/native'));primitives=next(math_prior.rglob('precision-v8/math'));exe=Path('/tmp/precision-context-v10')
 if command(['clang','-fobjc-arc','-O2','-framework','Foundation','-framework','Metal',SRC/'context_precision_v10.m','-o',exe],OUT/'build-context.log')!=0:return 1
 source=SRC/'consumer-structured-v8.metal';generator=SRC/'generate_candidates_v10.py';first=OUT/'msl-sources/initial';assert command([sys.executable,generator,'--source',source,'--out',first],OUT/'generate-initial.log')==0
 def evaluate(variants,stem,tone,dest):
  rc=command([exe,captures/stem/tone/'renderer-0',variants,dest,''],dest.with_suffix('.log'),900);f=dest/'model-comparisons.json';data=read(f)if f.exists()else[];print('MSL',stem,tone,[(r['variant'],r.get('half_differing_components','error'))for r in data],flush=True);return data
 initial={}
 for tone in ['tone-0','tone-0.35','tone--0.35']:initial[tone]=evaluate(first/'variants.json','IMG_2600',tone,OUT/'initial/IMG_2600'/tone)
 specs=read(first/'variants.json');candidates=[]
 for spec in specs:
  if spec.get('capture_checkpoints'):continue
  positive=next((v for v in initial['tone-0.35']if v['variant']==spec['name']),{})
  if positive.get('half_differing_components')==0:candidates.append(spec)
 searches=[]
 if not candidates:
  # Each function is changed separately. No per-photo selection is allowed.
  for n in [34,32]:
   directory=OUT/f'msl-sources/search-f{n}';assert command([sys.executable,generator,'--source',source,'--out',directory,'--search-function',n],OUT/f'generate-search-f{n}.log')==0
   dest=OUT/f'search-f{n}/IMG_2600/tone-0.35';metrics=evaluate(directory/'variants.json','IMG_2600','tone-0.35',dest);lookup={r['name']:r for r in read(directory/'variants.json')}
   scores=sorted([r for r in metrics if'half_differing_components'in r],key=lambda r:r['half_differing_components']);searches.append({'function':n,'best':scores[:5]})
   candidates.extend(lookup[r['variant']]for r in scores if r['half_differing_components']==0)
   if candidates:break
 (OUT/'search-summary.json').write_text(json.dumps(searches,indent=2)+'\n')
 # Recheck all three discovery tones for the single best common source,
 # then seal it before exposing the four remaining validation photographs.
 selected=None
 for spec in candidates[:1]:
  spec['keep_output']=True;chosen=OUT/'discovery-candidate.json';chosen.write_text(json.dumps([spec],indent=2)+'\n');cases=[]
  for tone in ['tone-0','tone-0.35','tone--0.35']:
   data=evaluate(chosen,'IMG_2600',tone,OUT/'msl/IMG_2600'/tone);cases.extend(data)
  if len(cases)==3 and all(r.get('half_differing_components',-1)==0 for r in cases):selected=spec
 (OUT/'selected-freeze.json').write_text(json.dumps({'os_build':build,'frozen_unix_time':time.time(),'selected':selected,'selection_inputs':['IMG_2600 three complete captured tone contexts'],'heldout_not_used_before_selection':['IMG_0032','IMG_0033'],'source_sha256':selected['source_sha256']if selected else None},indent=2)+'\n')
 validated=[]
 if selected:
  chosen=OUT/'selected-variant.json';chosen.write_text(json.dumps([selected],indent=2)+'\n')
  for stem in ['IMG_2604','IMG_2608','IMG_0032','IMG_0033']:
   for tone in ['tone-0','tone-0.35','tone--0.35']:
    data=evaluate(chosen,stem,tone,OUT/'msl'/stem/tone);validated.extend({'photo':stem,'tone':tone,**v}for v in data)
 # NumPy selection is independent of MSL success and remains on discovery.
 rootcp=OUT/'initial/IMG_2600/tone-0/root-diagnostic-4096.checkpoints.f32';control=next((r for r in initial['tone-0']if r['variant']=='root-diagnostic-4096'),{})
 args=[sys.executable,ROOT/'research/vm-native/model-v10/cpu_probe.py','--captures',captures,'--math',primitives,'--out',OUT/'numpy']
 if control.get('half_differing_components')==0:args+=['--msl-root-checkpoints',rootcp]
 env=os.environ.copy();env.update({'OPENBLAS_NUM_THREADS':'1','AIR_FUSION':'1','AIR_NATIVE_LOWERING':'1','AIR_TEX_HALF_UP':'1','AIR_DOT_EQUAL':'0'});rc=command(args,OUT/'numpy.log',2100,env);ns=read(OUT/'numpy/summary.json')if(OUT/'numpy/summary.json').exists()else{}
 summary={'os_build':build,'msl_full_15_bit_exact':bool(selected and len(validated)==12 and all(v['half_differing_components']==0 for v in validated)),'selected_msl':selected,'numpy_half_bit_exact':bool(ns.get('numpy_half_bit_exact')),'numpy_returncode':rc,'root_diagnostic_native_bit_exact':control.get('half_differing_components')==0,'validation_profiles':validated,'scope':'Consumer complete 512x384 captured contexts. Original-resolution and physical scene GTM/LTM remain separate.'};(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items()if k!='validation_profiles'}),flush=True);return 0 if summary['msl_full_15_bit_exact']and summary['numpy_half_bit_exact']else 1
if __name__=='__main__':raise SystemExit(main())
