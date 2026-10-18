"""Discovery-only arithmetic lowering selection, then independent full frames."""
from pathlib import Path
import argparse,hashlib,itertools,json,os,sys,time
import numpy as np
from air_numpy import Module,Type,V
from forward import Capture
from precision import setup,LookupExecutor
HERE=Path(__file__).resolve().parent
PHOTOS=['IMG_2600','IMG_2604','IMG_2608','IMG_0032','IMG_0033']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def metric(x,y):
 d=x.astype('f8')-y.astype('f8');mse=float(np.mean(d*d));return {'half_differing_components':int(np.count_nonzero(x.view('u2')!=y.view('u2'))),'max_abs':float(np.max(abs(d))),'mae':float(np.mean(abs(d))),'psnr_peak1_db':-10*np.log10(mse)if mse else'inf'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--captures',type=Path,required=True);p.add_argument('--math',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--msl-root-checkpoints',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);air=HERE/'0010.ll';trials=[]
 def configure():setup(HERE/'unary-output.f16',a.math/'atan-scalar',a.math/'pow',a.math/'half-extra/extra-output.f16',cache_mb=256)
 for r,g,f32 in itertools.product([0,1],[1,3,0,2],[1,2]):
  os.environ['V10_R_FMA']=str(r);os.environ['V10_GB_FMA']=str(g);os.environ['V10_F32_FUSION']=str(f32);configure();c=Capture(a.captures/'IMG_2600/tone-0/renderer-0',air);begin=time.time();actual=c.execute(stop=4096,chunk=4096);m=metric(actual.reshape(-1,4)[:4096,:3],c.expected.reshape(-1,4)[:4096,:3]);row={'r_fma':r,'gb_fma':g,'float32_fusion':f32,'pow_table':True,'half_extra':True,'pixels':4096,'full_frame':False,**m,'seconds':time.time()-begin};trials.append(row);print('NUMPY-DISCOVERY',row,flush=True)
  if m['half_differing_components']==0:break
 (a.out/'discovery-trials.json').write_text(json.dumps(trials,indent=2)+'\n');selected=next((r for r in trials if r['half_differing_components']==0),None)
 freeze={'frozen_unix_time':time.time(),'selected':selected,'selection_inputs':['IMG_2600 first4096 discovery pixels'],'heldout_numpy_not_run_before_selection':['IMG_0032','IMG_0033'],'air_sha256':sha(air),'files':[{'file':n,'sha256':sha(HERE/n)}for n in ['forward.py','air_numpy.py','precision.py','cpu_probe.py']],'primitive_manifest_sha256':{'atan':sha(a.math/'atan-scalar/manifest.json'),'pow':sha(a.math/'pow/manifest.json'),'extra':sha(a.math/'half-extra/metadata.json')},'formula':'Fixed AIR algebra; generic contraction choices only; no image/output-specific correction table'};(a.out/'candidate-selected-freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
 if selected is None:
  # Raw root checkpoints are indirect Apple-compatible references only when
  # this exact MSL complete output was first proven native bit-exact.
  if a.msl_root_checkpoints and a.msl_root_checkpoints.exists():
   best=min(trials,key=lambda v:v['half_differing_components']);os.environ['V10_R_FMA']=str(best['r_fma']);os.environ['V10_GB_FMA']=str(best['gb_fma']);os.environ['V10_F32_FUSION']=str(best['float32_fusion']);configure();c=Capture(a.captures/'IMG_2600/tone-0/renderer-0',air);c.execute(stop=4096,chunk=4096);cp=np.fromfile(a.msl_root_checkpoints,'<f4').reshape(4096,17,4);rows=[]
   for j,k in enumerate([196,211,214,286,347,350,352,354,374,393,408,409,413,476,501,567,600]):
    x=c.last_checkpoints.get('%'+str(k))
    if x is None:continue
    if x.ndim==1:x=x[:,None]
    y=cp[:,j,:x.shape[1]];bad=np.flatnonzero(np.any(x!=y,axis=1));rows.append({'ssa':k,'different_components':int(np.count_nonzero(x!=y)),'indices_first30':bad[:30].tolist(),'examples':[{'index':int(i),'numpy':x[i].astype(float).tolist(),'rebuilt_msl':y[i].astype(float).tolist()}for i in bad[:5]]})
   (a.out/'root-checkpoint-diagnostic.json').write_text(json.dumps({'best_discovery':best,'scope':'Rebuilt MSL checkpoint; native equivalence must be checked separately','checkpoints':rows},indent=2)+'\n')
  (a.out/'summary.json').write_text(json.dumps({'numpy_half_bit_exact':False,'full_five_photo_validation':False,'reason':'No discovery candidate meets unchanged bit-exact gate','trials':trials},indent=2)+'\n');return 1
 results=[]
 for stem in PHOTOS:
  begin=time.time();c=Capture(a.captures/stem/'tone-0/renderer-0',air);actual=c.execute(chunk=4096);pred=a.out/(stem+'.npy');np.save(pred,actual);m=metric(actual[...,:3],c.expected[...,:3]);row={'photo':stem,'capture':f'runs/39111905092/artifacts/vm-native-text/acceptance-v6/native/{stem}/tone-0/renderer-0','os_build':'26A434','shape':list(actual.shape),'full_frame':True,'compared_pixels':c.h*c.w,'model_freeze_sha256':sha(a.out/'candidate-selected-freeze.json'),'native_output_sha256':sha(c.root/'_outputImageTexture.bin'),'output_sha256':sha(pred),**m,'seconds':time.time()-begin};(a.out/(stem+'.json')).write_text(json.dumps(row,indent=2)+'\n');results.append(row);print('NUMPY-FULL',stem,m,flush=True)
 c=Capture(a.captures/'IMG_2600/tone-0/renderer-0',air);c.expected=np.zeros_like(c.expected);out=c.execute(stop=4096,chunk=4096);prior=np.load(a.out/'IMG_2600.npy',mmap_mode='r');leak=metric(out.reshape(-1,4)[:4096,:3],prior.reshape(-1,4)[:4096,:3]);summary={'numpy_half_bit_exact':all(r['half_differing_components']==0 for r in results),'full_five_photo_validation':True,'profiles':results,'oracle_replacement_control':leak};(a.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');return 0 if summary['numpy_half_bit_exact']and leak['half_differing_components']==0 else 1
if __name__=='__main__':raise SystemExit(main())
