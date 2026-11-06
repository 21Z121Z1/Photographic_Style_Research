"""Audit exact PTS and test interpolation against held-out native thumbnails.

The interpolation test removes a native thumbnail and uses its neighbours.
Native Vision flow reads full-rate SDR only. No video/PVT is written.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter,map_coordinates


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['independent','pair','output']:parser.add_argument(name,type=Path)
    args=parser.parse_args()
    old,pair,out=[getattr(args,k).resolve()for k in ['independent','pair','output']]
    out.mkdir(exist_ok=False);(out/'flows').mkdir()
    spec=importlib.util.spec_from_file_location('independent_fit',old/'src/fit.py')
    fit=importlib.util.module_from_spec(spec);spec.loader.exec_module(fit)
    collection=old/'verified-run/collection'
    source=json.loads((collection/'collection.json').read_text())
    decoded=pair/'verified-final/decoded-isolated'
    facts=json.loads((decoded/'decoded.json').read_text())
    prior=json.loads((pair/'verified-final/analysis/results.json').read_text())
    times=[Fraction(f['pts']['value'],f['pts']['scale'])for f in source['frames']]
    thumb_times=[Fraction(f['pts']['value'],f['pts']['scale'])for f in facts['thumbnails']]
    exact={t:i for i,t in enumerate(times)}
    assert len(set(times))==len(times) and all(t in exact for t in thumb_times)
    timeline=[]
    for index,t in enumerate(times):
        lower=[i for i,s in enumerate(thumb_times)if s<=t]
        upper=[i for i,s in enumerate(thumb_times)if s>=t]
        left=max(lower)if lower else 0
        right=min(upper)if upper else len(thumb_times)-1
        alpha=Fraction(0)if left==right else(t-thumb_times[left])/(thumb_times[right]-thumb_times[left])
        is_exact=thumb_times[left]==t
        policy='exact'if is_exact else('interpolation'if lower and upper else'one_sided')
        timeline.append(dict(mainFrame=index,pts=source['frames'][index]['pts'],
            exactThumbnail=left if is_exact else None,left=left,right=right,policy=policy,
            alpha=dict(value=alpha.numerator,scale=alpha.denominator,decimal=float(alpha))))
    (out/'timeline.json').write_text(json.dumps(dict(mainFrames=len(times),thumbnailFrames=len(thumb_times),
        exactFrames=sum(i['exactThumbnail']is not None for i in timeline),
        interpolatedFrames=sum(i['policy']=='interpolation'for i in timeline),
        oneSidedFrames=sum(i['policy']=='one_sided'for i in timeline),
        mainPTSStrictlyIncreasing=all(a<b for a,b in zip(times,times[1:])),
        allThumbnailPTSMatchMain=True,frames=timeline),indent=2)+'\n')
    w,h=source['width'],source['height'];basis=np.array(prior['matrixRec2020ToP3'])
    yy,xx=np.mgrid[:96,:128];cx,cy,cw,ch=source['crop']
    coords=[(cy+(yy+.5)/96*ch)/source['codedHeight']*96-.5,
            (cx+(xx+.5)/128*cw)/source['codedWidth']*128-.5]
    def thumbnail(index):
        codes=fit.load(decoded/f'video-codes-{index:04d}.f32',128,96)
        toe=47.28711236*(.01+.05641088)**2
        linear=np.where(codes>=toe,2**((codes-.69336945)/.08550479)-.00964052,
                        np.sqrt(np.maximum(codes,0)/47.28711236)-.05641088)@basis
        frame=source['frames'][exact[thumb_times[index]]]
        linear*=frame['style']['stored']['h']/prior['photoBaseGain']
        return np.stack([map_coordinates(linear[...,c],coords,order=1,mode='nearest')for c in range(3)],axis=2)
    def area(a):return a.reshape(96,h//96,128,w//128,3).mean(axis=(1,3))
    def metrics(candidate,reference,mask):
        error=(fit.log(fit.luma(candidate))-fit.log(fit.luma(reference)))[mask]
        return dict(pixels=int(mask.sum()),maeEV=float(np.mean(abs(error))),
                    p90EV=float(np.percentile(abs(error),90)),signedMedianEV=float(np.median(error)))
    tests=[]
    cases=[('interpolation',j)for j in [2,6,10,13,14,18,22,25]]+[('one_sided',27)]
    for policy,j in cases:
        endpoint_indices=[j-1,j+1]if policy=='interpolation'else[j-1,j-1]
        target,left,right=[thumbnail(k)for k in [j,*endpoint_indices]]
        t=thumb_times[j]
        alpha=float((t-thumb_times[j-1])/(thumb_times[j+1]-thumb_times[j-1]))if policy=='interpolation'else 0.
        current=exact[t];endpoints=[exact[thumb_times[k]]for k in endpoint_indices]
        warped=[];confidence=[]
        for endpoint,view in zip(endpoints,[left,right]):
            paths=[collection/source['frames'][k]['neutral']for k in [current,endpoint]]
            forward=fit.flow_call(old/'verified-run/native',*paths,out/f'flows/{current:04d}-{endpoint:04d}.f32',w,h)
            backward=fit.flow_call(old/'verified-run/native',*paths[::-1],out/f'flows/{endpoint:04d}-{current:04d}.f32',w,h)
            c,_=fit.flow_confidence(forward,backward)
            warped.append(fit.warp(fit.resize(view,w,h),forward));confidence.append(c)
        c0,c1=confidence
        den=(1-alpha)*c0+alpha*c1
        motion=((1-alpha)*c0[...,None]*warped[0]+alpha*c1[...,None]*warped[1])/np.maximum(den[...,None],1e-5)
        fixed_linear=(1-alpha)*left+alpha*right
        fallback=fit.resize(fixed_linear,w,h)
        motion=np.where((den>.05)[...,None],motion,fallback)
        candidates=dict(fixed_coordinate_linear=fixed_linear,
            fixed_coordinate_log=np.exp2((1-alpha)*fit.log(left)+alpha*fit.log(right)),
            motion_compensated_linear=area(motion))
        ty=fit.luma(target);mask=(yy>=5)&(yy<91)&(xx>=5)&(xx<123)&(ty>1e-5)
        lo,hi=np.percentile(ty[mask],[2,99.5]);mask&=(ty>=lo)&(ty<=hi)
        scores={name:metrics(value,target,mask)for name,value in candidates.items()}
        low_target=gaussian_filter(target,sigma=(1,1,0))
        low={name:metrics(gaussian_filter(value,sigma=(1,1,0)),low_target,mask)for name,value in candidates.items()}
        tests.append(dict(policy=policy,heldoutThumbnail=j,heldoutMainFrame=current,pts=float(t),alpha=alpha,
            forwardBackwardConfidenceCoverage=float(np.mean(den>.05)),fullBand=scores,commonLowPassSigma1=low))
        print(json.dumps(tests[-1]),flush=True)
    result=dict(schema='scene-thumbnail-temporal-design-diagnostic-v1',tests=tests,
        policy='All methods score the same reference-defined mask. No exposure fit. Motion uses neutral full-rate main frames only. Both-sided invalid pixels use fixed-coordinate linear fallback and remain scored.',
        limitation='Leave-one-native-thumbnail-out doubles the interpolation interval; it is a stress test, not ground truth for the actual unsampled odd main frames.',
        inputs={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),old/'src/fit.py',collection/'collection.json',decoded/'decoded.json']})
    (out/'temporal-results.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
