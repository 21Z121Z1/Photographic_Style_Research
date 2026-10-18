"""Photo-independent primitive tables, discovery-only selection, then full frames."""
from pathlib import Path
import argparse,hashlib,json,math,sys,time,resource
import numpy as np
from air_numpy import Module,Type,V
from forward import Capture
from precision import setup,LookupExecutor
HERE=Path(__file__).resolve().parent
PHOTOS=['IMG_2600','IMG_2604','IMG_2608','IMG_0032','IMG_0033']
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def metric(x,y):
 x=np.asarray(x);y=np.asarray(y);d=x.astype('f8')-y.astype('f8');mse=float(np.mean(d*d))
 return {'half_differing_components':int(np.count_nonzero(x.view('u2')!=y.view('u2'))),'max_abs':float(np.max(np.abs(d))),'mae':float(np.mean(np.abs(d))),'psnr_peak1_db':float(-10*np.log10(mse))if mse else'inf'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--captures',type=Path,required=True);p.add_argument('--math',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 unary=HERE/'unary-output.f16';assert sha(unary)=='b9ffb796564d09064243df4f0f714b66a1eca54d47ab45759014181826105af0'
 air=HERE/'0010.ll';extra=a.math/'half-extra/extra-output.f16';atan=a.math/'atan-scalar';pow_path=a.math/'pow';m=Module(air)
 def configure(pow_enabled,extra_enabled):return setup(unary,atan,pow_path if pow_enabled else None,extra if extra_enabled else None,cache_mb=512)
 configure(True,True)
 # Signed normal/subnormal/zero controls extend the old positive-only test.
 inp=np.fromfile(a.math/'half-extra/pairs-input.f16','<f2').reshape(-1,2);expected=np.fromfile(a.math/'half-extra/pairs-output.f16','<f2');e=LookupExecutor(m,len(inp));t=Type('half');e.return_type=t
 with np.errstate(all='ignore'):actual=e.call('air.atan2.f16',[V(t,inp[:,0]),V(t,inp[:,1])],np.ones(len(inp),bool)).d
 ib=inp.view('u2');exponents=(ib>>10)&31;regions={'all':np.ones(len(inp),bool),'both_normal':np.all((exponents>0)&(exponents<31),axis=1),'has_subnormal_nonzero':np.any((exponents==0)&((ib&1023)!=0),axis=1),'axis':np.any(inp==0,axis=1)}
 controls={name:metric(actual[mask],expected[mask])for name,mask in regions.items()if mask.any()};(a.out/'primitive-controls.json').write_text(json.dumps({'atan2':controls,'counts':dict(LookupExecutor.counts),'scope':'Independent signed finite half inputs, not photo outputs'},indent=2)+'\n')
 del inp,expected,actual,e
 trials=[]
 for pow_enabled,extra_enabled in [(True,True),(False,True),(True,False),(False,False)]:
  configure(pow_enabled,extra_enabled);c=Capture(a.captures/'IMG_2600/tone-0/renderer-0',air);begin=time.time();out=c.execute(stop=4096,chunk=1024);row={'pow_table':pow_enabled,'half_extra':extra_enabled,'scope':'Only the first 4096 IMG_2600 discovery pixels','pixels':4096,**metric(out.reshape(-1,4)[:4096,:3],c.expected.reshape(-1,4)[:4096,:3]),'seconds':time.time()-begin,'primitive_counts':dict(LookupExecutor.counts),'pow_counts':dict(LookupExecutor.pow_table.counts)if LookupExecutor.pow_table else None};trials.append(row)
  if row['half_differing_components']==0:break
 (a.out/'discovery-trials.json').write_text(json.dumps(trials,indent=2)+'\n')
 selected=next((r for r in trials if r['half_differing_components']==0),None)
 freeze={'frozen_unix_time':time.time(),'selected':selected,'selection_inputs':['IMG_2600 first4096 only'],'heldout_numpy_not_run_before_selection':['IMG_0032','IMG_0033'],'air_sha256':sha(air),'files':[{'file':p.name,'sha256':sha(p)}for p in [HERE/'forward.py',HERE/'air_numpy.py',HERE/'precision.py',Path(__file__)]],'primitive_manifest_sha256':{'atan':sha(atan/'manifest.json'),'pow':sha(pow_path/'manifest.json'),'extra':sha(a.math/'half-extra/metadata.json')},'formula':'Original frozen AIR algebra, new separately versioned precision backend; no image/output-specific correction table'}
 (a.out/'candidate-selected-freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
 if selected is None:
  (a.out/'summary.json').write_text(json.dumps({'numpy_half_bit_exact':False,'full_five_photo_validation':False,'reason':'Discovery prefix still fails unchanged bit-exact gate','trials':trials},indent=2)+'\n');return 1
 configure(selected['pow_table'],selected['half_extra']);results=[]
 for stem in PHOTOS:
  begin=time.time();capture=a.captures/stem/'tone-0/renderer-0';c=Capture(capture,air);n=c.h*c.w;actual=c.execute(chunk=4096);np.save(a.out/(stem+'.npy'),actual)
  row={'photo':stem,'capture':f'runs/39111905092/artifacts/vm-native-text/acceptance-v6/native/{stem}/tone-0/renderer-0','air_sha256':sha(air),'shape':list(actual.shape),'compared_pixels':n,'full_frame':True,**metric(actual[...,:3],c.expected[...,:3]),'output_sha256':sha(a.out/(stem+'.npy')),'native_output_sha256':sha(capture/'_outputImageTexture.bin'),'model_freeze_sha256':sha(a.out/'candidate-selected-freeze.json'),'precision_backend':{'pow_table':selected['pow_table'],'half_extra':selected['half_extra'],'primitive_counts':dict(LookupExecutor.counts),'pow_counts':dict(LookupExecutor.pow_table.counts)if LookupExecutor.pow_table else None},'os_build':'26A434','elapsed_seconds':time.time()-begin}
  (a.out/(stem+'.json')).write_text(json.dumps(row,indent=2)+'\n');results.append(row);print(stem,row['half_differing_components'],flush=True)
 # Replacing Capture.expected must not change the prediction. This is an
 # oracle-dependence control, and it never becomes a solver/forward seed.
 c=Capture(a.captures/'IMG_2600/tone-0/renderer-0',air);c.expected=np.zeros_like(c.expected);out=c.execute(stop=4096,chunk=1024);prior=np.load(a.out/'IMG_2600.npy',mmap_mode='r');leak=metric(out.reshape(-1,4)[:4096,:3],prior.reshape(-1,4)[:4096,:3])
 result={'numpy_half_bit_exact':len(results)==5 and all(r['half_differing_components']==0 for r in results),'full_five_photo_validation':True,'profiles':results,'oracle_replacement_control':leak,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin'else 1024),'scope':'Full captured 512x384 native consumer frames, not original 12/24MP scene outputs'}
 (a.out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');return 0 if result['numpy_half_bit_exact']and leak['half_differing_components']==0 else 1
if __name__=='__main__':raise SystemExit(main())
