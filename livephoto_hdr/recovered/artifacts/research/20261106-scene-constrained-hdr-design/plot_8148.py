from pathlib import Path
import json,os
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/scene-design-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

r=Path(__file__).resolve().parent
d=json.loads((r/'IMG_8148-diagnosis.json').read_text())
sd=json.loads((r/'IMG_8148-sdr-audit/audit.json').read_text())
native=json.loads((r/'IMG_8148-reference-decoded/decoded.json').read_text())
fig,axs=plt.subplots(2,2,figsize=(13,8),constrained_layout=True)
main=[f['pts']['seconds']for f in sd['frames']]
aux=[f['pts']['seconds']for f in native['thumbnails']]
axs[0,0].scatter(main,[1]*len(main),marker='|',s=160,label='56 main frames')
axs[0,0].scatter(aux,[0]*len(aux),marker='|',s=160,label='28 scene thumbnails')
gap=d['maxAuxiliaryGap']
axs[0,0].axvspan(gap['start'],gap['end'],alpha=.13,color='red',label='0.567 s auxiliary gap')
axs[0,0].axvline(d['stillTime']['seconds'],color='black',ls='--',label='Still exposure time')
axs[0,0].set(yticks=[0,1],yticklabels=['Scene','Main'],xlabel='PTS (seconds)',title='IMG_8148: actual presentation times',ylim=(-.5,1.5))
axs[0,0].legend(fontsize=8,loc='upper left')
late=[f for f in d['frames']if 'patternTranslation'in f]
axs[0,1].plot([f['pts']for f in late],[5*f['patternTranslation']['sdrDx']for f in late],label='SDR structure')
axs[0,1].plot([f['pts']for f in late],[5*f['patternTranslation']['gainDx']for f in late],label='HDR gain pattern')
axs[0,1].set(xlabel='PTS (seconds)',ylabel='Horizontal displacement (1920 coded pixels)',title='Independently registered pattern motion')
axs[0,1].grid(alpha=.2);axs[0,1].legend()
y=np.array([.22897456,.69173855,.07928691])
for ax,index in zip(axs[1],[30,55]):
 s=np.fromfile(r/f'IMG_8148-sdr-audit/decoded-{index:04d}.f32',dtype='<f4').reshape(288,384,4)[...,:3]
 h=np.fromfile(r/f'IMG_8148-hdr-audit/decoded-{index:04d}.f32',dtype='<f4').reshape(288,384,4)[...,:3]
 gain=np.log2(np.maximum(h@y,1e-5)/np.maximum(s@y,1e-5))
 im=ax.imshow(gain,vmin=-1.6,vmax=1.6,cmap='RdBu_r')
 ax.set(title=f'Decoded HDR / original SDR gain: frame {index}',xlabel='384-pixel analysis x',ylabel='Analysis y')
fig.colorbar(im,ax=axs[1,:],label='Luminance gain (EV)',shrink=.8)
fig.suptitle('Motion alignment and sparse scene observations; no per-frame exposure normalization')
fig.savefig(r/'IMG_8148-analysis.png',dpi=170)
fig.savefig(r/'IMG_8148-analysis.svg')
