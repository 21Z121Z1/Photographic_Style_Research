"""Discovery-only precision diagnosis against a separately rebuilt MSL trace."""
from pathlib import Path
import argparse,json,sys,os
import numpy as np
def main():
 p=argparse.ArgumentParser();p.add_argument('--model',type=Path,required=True);p.add_argument('--math',type=Path,required=True);p.add_argument('--capture',type=Path,required=True);p.add_argument('--msl',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(a.model))
 from precision import setup,LookupExecutor
 import forward
 setup(a.model/'unary-output.f16',a.math/'atan-scalar',a.math/'pow',a.math/'half-extra/extra-output.f16',cache_mb=256)
 class Trace(LookupExecutor):
  instance=None
  def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.stack=[];self.smooth={};Trace.instance=self
  def run(self,name,args,active=None):
   target=name.startswith('_Z15smoothSatFilter')and self.stack and self.stack[-1]=='renderFinalAdjustments';self.stack.append(name);old_name=self.trace_function;old_checks=self.checkpoints
   if target:self.trace_function=name;self.checkpoints={};self.smooth_input=(args[0].d.copy(),args[1].d.copy())
   value=super().run(name,args,active)
   if target:self.smooth={k:v.copy()for k,v in self.checkpoints.items()};self.checkpoints=old_checks
   self.trace_function=old_name;self.stack.pop();return value
 forward.Executor=Trace;c=forward.Capture(a.capture,a.model/'0010.ll');output=c.execute(stop=4096,chunk=4096);e=Trace.instance;checks=e.smooth;layout=json.loads((a.msl.parent.parent.parent.parent/'msl-sources/smooth-checkpoint-layout.json').read_text())if False else ['input','12','15','24','25','37','47','55','58','67','68','75'];native=np.fromfile(a.msl,'<f4').reshape(4096,20,4);rows=[];arr={}
 for i,key in enumerate(layout):
  if key=='input':x=np.column_stack(e.smooth_input)
  elif key=='37':x=np.column_stack([checks['%34'],checks['%36'],checks['%37']])
  else:x=checks['%'+key]
  if x.ndim==1:x=x[:,None]
  y=native[:,i,:x.shape[1]];different=x.astype('f4')!=y;bad=np.flatnonzero(np.any(different,axis=1));rows.append({'ssa':key,'different_components':int(different.sum()),'max_abs':float(np.max(abs(x.astype('f8')-y))),'indices_first20':bad[:20].tolist(),'examples':[{'index':int(k),'numpy':x[k].astype(float).tolist(),'rebuilt_msl':y[k].astype(float).tolist()}for k in bad[:3]]});arr[key]=x
 np.savez(a.out/'numpy-checkpoints.npz',**arr)
 target=c.expected.reshape(-1,4)[:4096,:3];pred=output.reshape(-1,4)[:4096,:3]
 data={'scope':'4096 discovery pixels; internals are rebuilt MSL, not original Apple machine-code checkpoints','numpy_differing_components':int(np.count_nonzero(pred.view('u2')!=target.view('u2'))),'checkpoints':rows,'primitive_counts':dict(Trace.counts),'pow_counts':dict(Trace.pow_table.counts)};(a.out/'diagnostic.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data))
if __name__=='__main__':main()
