"""Render standalone scientific plots of the frozen paired-thumbnail comparison."""
import argparse,json
from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analyze import Y,load,piecewise_inverse

def run(root,analysis):
    result=json.loads((analysis/'results.json').read_text());arrays=np.load(analysis/'comparison-arrays.npz');ref=arrays['photo_reference'];video=arrays['video'];mask=arrays['mask'];
    native_scale=result['primary']['scaleVideoToPhoto'];metadata_scale=result['metadataScaleHypothesis']['scale']
    raw=load(root/'decoded-isolated/video-codes-0022.f32',128,96);matrix=np.asarray(result['matrixRec2020ToP3']);piecewise=piecewise_inverse(raw)@matrix
    valid=np.isfinite(ref).all(axis=2);den=gaussian_filter(valid.astype(float),2)
    filtered_ref=np.stack([gaussian_filter(np.nan_to_num(ref[...,c]),2)/np.maximum(den,1e-6)for c in range(3)],axis=2)
    filtered_video=gaussian_filter(piecewise,sigma=(2,2,0))
    fig,axes=plt.subplots(2,2,figsize=(13,9),constrained_layout=True)
    for ax,src,target,scale,title in [(axes[0,0],video,ref,native_scale,'128 x 96: native private inverse'),(axes[0,1],filtered_video,filtered_ref,metadata_scale,'Matched low-frequency band: piecewise inverse')]:
        x=np.log2(np.maximum((src@Y)*scale,1e-8))[mask];y=np.log2(np.maximum(target@Y,1e-8))[mask]
        ax.hexbin(x,y,gridsize=65,mincnt=1,bins='log',cmap='viridis');lo=min(x.min(),y.min());hi=max(x.max(),y.max());ax.plot([lo,hi],[lo,hi],'r--',lw=1.2,label='identity');ax.set(xlabel='Video relative linear Y, log2 (scaled)',ylabel='Still relative linear Y, log2',title=title);ax.legend(loc='upper left');ax.grid(alpha=.15)
    names=['Codes as linear','Inverse sRGB','Native inverse','Piecewise inverse']
    keys=['codes_as_linear_Rec2020','inverse_sRGB_Rec2020','native_AppleLog_Rec2020_to_P3','piecewise_AppleLog_Rec2020']
    values=[result['controls'][k]['maeEV']for k in keys];ax=axes[1,0];ax.barh(names,values,color=['#999999','#777777','#3478a8','#21856a']);ax.invert_yaxis();ax.set(xlabel='Held-out mean absolute luminance error (EV)',title='Same frozen geometry, one exposure scalar')
    for i,v in enumerate(values):ax.text(v+.01,i,f'{v:.3f}',va='center',fontsize=10)
    err=np.log2(np.maximum((video@Y)*metadata_scale,1e-8))-np.log2(np.maximum(ref@Y,1e-8));err[~mask]=np.nan
    im=axes[1,1].imshow(err,origin='lower',vmin=-.5,vmax=.5,cmap='coolwarm');axes[1,1].set(title='Native inverse residual with metadata scale, no exposure fit',xlabel='Video thumbnail x',ylabel='Video thumbnail y');fig.colorbar(im,ax=axes[1,1],label='Video minus still (EV)')
    fig.suptitle('IMG_3673: still / video LinearThumbnail at PTS 881/600 s',fontsize=15)
    fig.savefig(analysis/'comparison.png',dpi=170);fig.savefig(analysis/'comparison.svg');plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('analysis',type=Path);a=p.parse_args();run(a.root,a.analysis)
