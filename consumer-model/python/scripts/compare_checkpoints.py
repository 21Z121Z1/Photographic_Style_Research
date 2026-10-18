#!/usr/bin/env python3
from pathlib import Path
import argparse,json,sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from forward import Capture
from scripts.air_to_msl import CHECKS
p=argparse.ArgumentParser();p.add_argument('run');p.add_argument('--out',type=Path,required=True);a=p.parse_args();rows=[]
for root in sorted((Path('runs')/a.run/'artifacts/vm-native-text/native').glob('*/tone-*/renderer-0')):
 if not(root/'msl-output.f16').exists():continue
 c=Capture(root,'runs/39052427081/artifacts/vm-native-text/air/0010.ll');m=np.fromfile(root/'msl-output.f16','<f2').reshape(c.expected.shape);diff=m[...,:3].astype(float)-c.expected[...,:3];r={'photo':root.parent.parent.name,'tone':root.parent.name,'msl_original':{'differing_components':int(np.count_nonzero(m[...,:3].view('u2')!=c.expected[...,:3].view('u2'))),'max_abs':float(np.max(abs(diff))),'psnr':float(-10*np.log10(np.mean(diff**2))) if np.any(diff) else 'inf'},'numpy_msl_checkpoints':[]}
 c.execute(stop=512,chunk=512);native=np.fromfile(root/'msl-checkpoints.f32','<f4').reshape(512,len(CHECKS),4)
 for j,k in enumerate(CHECKS):
  x=c.last_checkpoints.get('%'+str(k))
  if x is None:continue
  x=x[:,None] if x.ndim==1 else x;y=native[:,j,:x.shape[1]];d=x.astype(float)-y;bad=np.flatnonzero(np.any(d!=0,axis=1));r['numpy_msl_checkpoints'].append({'ssa':k,'differing_components':int(np.count_nonzero(d)),'max_abs':float(np.nanmax(abs(d))),'first_differing_pixel':int(bad[0]) if bad.size else None})
 rows.append(r);print(json.dumps(r,indent=2))
a.out.write_text(json.dumps(rows,indent=2)+'\n')
