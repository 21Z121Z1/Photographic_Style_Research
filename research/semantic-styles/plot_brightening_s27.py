"""Runner-only figures from already recorded synthetic ARM allocation curves.

The figure contains no photo-derived pixels. It does not infer IMG_2810's
brightening curve, j-to-EV amplitude, or the camera application coordinate.
"""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from semantic_curve_inverse import inverse_curve_pair

def plot(output):
 output=Path(output);output.mkdir(parents=True,exist_ok=True)
 source=Path('research/semantic-styles/evidence/allocation-curves-s19.synthetic.json')
 cases=json.loads(source.read_text());case=next(c for c in cases if (c['profile'],c['target'],c['budget'])==('uniform','dark',.25))
 x=np.linspace(0,1,len(case['baseline']));a=np.asarray(case['baseline']);b=np.asarray(case['beta'])
 observations=np.linspace(0,1,801,dtype='f4')
 result=inverse_curve_pair(observations,x,b,a,storage='float32',forward_error_abs=2**-22)
 fig,axes=plt.subplots(1,3,figsize=(14,4.1),layout='constrained')
 axes[0].plot(x,a,label='C_without (synthetic statistics)');axes[0].plot(x,b,label='C_with (beta=25/128)')
 axes[0].plot([0,1],[0,1],':',color='.55');axes[0].set(title='1. Replayed camera allocator',xlabel='Declared synthetic curve coordinate',ylabel='Curve output');axes[0].legend(fontsize=8)
 valid=result['valid_observation_mask'];axes[1].fill_between(observations[valid],result['neutral_lower'][valid],result['neutral_upper'][valid],alpha=.35,label='Conditional set inverse')
 axes[1].plot(observations[valid],result['minimax_estimate'][valid],lw=1,label='C_without(C_with^-1(y))');axes[1].plot([0,1],[0,1],':',color='.55');axes[1].set(title='2. Remove only supplied brightening curve',xlabel='Observed curve output y',ylabel='Counterfactual neutral output');axes[1].legend(fontsize=8)
 A=np.linspace(1/255,1,1500);T=.12
 for l,label in [(1.,'Local mixture neutral: l=1'),(.79,'BG l=0.790'),(.624692142,'Person l=0.625')]:
  z=np.minimum(A,l*A+(1-l)*T)
  axes[2].plot(A,z,label=label)
 axes[2].axvline(T,color='.5',ls=':',lw=1);axes[2].set(title='3. Styles local component (continuous)',xlabel='Primary A, fixed anchor T=0.12',ylabel='Z=min(A, l*A+(1-l)*T)');axes[2].legend(fontsize=8)
 for ax in axes:ax.grid(alpha=.2);ax.set_xlim(0,1);ax.set_ylim(0,1)
 fig.suptitle('Conditional operator diagrams; NOT the actual IMG_2810 camera curve',fontsize=12)
 file=output/'brightening-and-local-curves-s27.png';fig.savefig(file,dpi=160);plt.close(fig)
 q={'source_run':39183348891,'source_artifact':12157286597,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'synthetic_case':{k:case[k] for k in ['profile','target','budget']},'figure_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'camera_amplitude_identified':False,'sample_actual_curves_available':False,'inverse_formula':'C_without o set_inverse(C_with)','curve_inverse_module_sha256':hashlib.sha256(Path('research/semantic-styles/semantic_curve_inverse.py').read_bytes()).hexdigest(),'panel3_scope':'Continuous consumer branch with fixed T, HR=1, A>=half(1/255); diagram, not a new native half-equivalence test','display_transform':'Scientific axes, no image display transform; no photo pixels used'}
 (output/'figure-provenance.json').write_text(json.dumps(q,indent=2)+'\n')
 return q
if __name__=='__main__':plot(sys.argv[1])
