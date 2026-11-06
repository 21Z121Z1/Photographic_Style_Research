"""Independent pixel/timeline diagnosis of the supplied reconstructed PVT."""
from __future__ import annotations
from fractions import Fraction
import hashlib,json
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter,map_coordinates
from scipy.optimize import least_squares


ROOT=Path(__file__).resolve().parent
Y=np.array([.22897456,.69173855,.07928691])


def load(path,w=384,h=288):
    return np.fromfile(path,dtype='<f4').reshape(h,w,4)[...,:3].astype(float)


def log(a):return np.log2(np.maximum(a,1e-5))


def main():
    receipt_path=Path('/Users/retriedstormtrooper/Downloads/IMG_8148.pvt.receipt.json')
    receipt=json.loads(receipt_path.read_text());work=Path(receipt['work'])
    source=json.loads((work/'collection/collection.json').read_text())
    model=json.loads((work/'model/model.json').read_text())
    sd=json.loads((ROOT/'IMG_8148-sdr-audit/audit.json').read_text())
    hd=json.loads((ROOT/'IMG_8148-hdr-audit/audit.json').read_text())
    native=json.loads((ROOT/'IMG_8148-reference-decoded/decoded.json').read_text())
    def time(value):return Fraction(value['value'],value['scale'])
    mt=[time(f['pts'])for f in sd['frames']];at=[time(f['pts'])for f in native['thumbnails']]
    frames=[]
    basis=np.fromfile(ROOT/'IMG_8148-reference-decoded/rec2020-to-p3-basis.f32',dtype='<f4').reshape(3,4)[:,:3]
    scene_mirror=[]
    for i,entry in enumerate(native['thumbnails']):
        codes=load(ROOT/f'IMG_8148-reference-decoded/video-codes-{i:04d}.f32',128,96)
        toe=47.28711236*(.01+.05641088)**2
        linear=np.where(codes>=toe,2**((codes-.69336945)/.08550479)-.00964052,
                        np.sqrt(np.maximum(codes,0)/47.28711236)-.05641088)@basis
        stored=load(work/f'collection/scene-{i:04d}.f32',128,96)
        scene_mirror.append(float(np.max(abs(linear-stored))))
    sdr=[];gain=[];maps=[];clamps=[]
    for i,(s,h) in enumerate(zip(sd['frames'],hd['frames'])):
        assert s['pts']==h['pts']==source['frames'][i]['pts']
        a=load(ROOT/'IMG_8148-sdr-audit'/s['file']);b=load(ROOT/'IMG_8148-hdr-audit'/h['file'])
        g=log(b@Y)-log(a@Y)
        sdr.append(a);gain.append(g)
        m=np.fromfile(work/f'model/gain-{i:04d}.f32',dtype='<f4').reshape(48,64,3)
        maps.append(m.mean(axis=2))
        t=mt[i];lower=[j for j,x in enumerate(at)if x<=t];upper=[j for j,x in enumerate(at)if x>=t]
        left=max(lower)if lower else 0;right=min(upper)if upper else len(at)-1
        alpha=Fraction(0)if left==right else(t-at[left])/(at[right]-at[left])
        props=source['frames'][i]['style']['native'];scale=props['baseGain']*props['baselineExposure']
        clamps.append(float(np.mean(a*scale>=1)))
        frames.append(dict(frame=i,pts=float(t),ptsRational=str(t),
            sceneLeft=left,sceneRight=right,sceneGapSeconds=float(at[right]-at[left]),
            sceneAlpha=float(alpha),sceneExact=t in at,
            sdrMedianY=float(np.median(a@Y)),hdrMedianY=float(np.median(b@Y)),
            gainMedianEV=float(np.median(g)),guideSDRInputUpperClampFraction=clamps[-1],
            baseGain=props['baseGain'],baselineExposure=props['baselineExposure'],
            cachedPhotoResidualFlowConfidence=model['frameFacts'][i]['flow_confidence']))
    # Estimate scene and gain-pattern translations independently. This is a
    # descriptive image-registration diagnostic, not a claimed fixed time delay.
    anchor=model['anchorFrame'];yy,xx=np.mgrid[10:190,40:280]
    def structure(a):
        z=gaussian_filter(a,1)-gaussian_filter(a,6)
        return z/np.maximum(np.sqrt(gaussian_filter(z*z,6)),.03)
    reference_s=structure(log(sdr[anchor]@Y));reference_g=structure(gain[anchor])
    def shift(reference,current,start):
        objective=lambda p:(map_coordinates(reference,[yy+p[0],xx+p[1]],order=1,mode='nearest')-current[yy,xx]).ravel()
        fit=least_squares(objective,start,bounds=([-80,-100],[80,100]),loss='soft_l1',f_scale=.5,max_nfev=35)
        return fit.x, float(np.mean(abs(objective(fit.x))))
    start_s=np.zeros(2);start_g=np.zeros(2)
    for i in range(anchor,len(frames)):
        start_s,se=shift(reference_s,structure(log(sdr[i]@Y)),start_s)
        start_g,ge=shift(reference_g,structure(gain[i]),start_g)
        frames[i]['patternTranslation']=dict(sdrDx=float(-start_s[1]),sdrDy=float(-start_s[0]),gainDx=float(-start_g[1]),gainDy=float(-start_g[0]),sdrResidual=se,gainResidual=ge)
    gaps=[dict(left=j,right=j+1,start=float(a),end=float(b),duration=float(b-a),
        mainFramesStrictlyInside=[i for i,t in enumerate(mt)if a<t<b])for j,(a,b)in enumerate(zip(at,at[1:]))]
    inputs=[receipt_path,Path(sd['movie']),Path(hd['movie']),ROOT/'IMG_8148-reference-decoded/decoded.json',work/'collection/collection.json',work/'model/model.json',Path(__file__)]
    result=dict(schema='IMG-8148-independent-diagnosis-v1',
        mainFrames=len(mt),thumbnailFrames=len(at),stillTime=native['stillTime'],
        actualAnchorFrame=anchor,actualAnchorPTS=float(mt[anchor]),
        anchorOffsetFromStillSeconds=float(mt[anchor]-time(native['stillTime'])),
        maxAuxiliaryGap=max(gaps,key=lambda q:q['duration']),mainAndOutputPTSEqual=True,
        nativeDecodedSceneVsStoredMaxAbs=max(scene_mirror),
        sceneDecoderAlreadyCorrected=source['sceneDecoder'],
        sourceStyleBypassed=source['styleBypassed'],
        guideSDRUpperClampPercentiles=np.percentile(clamps,[0,25,50,75,100]).tolist(),
        inputHashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in inputs},
        frames=frames,gaps=gaps,
        limits=['Pixel/timeline evidence only; no physical HDR display or consumer-adaptation measurement.',
                'Registration describes pattern motion and does not uniquely identify an exposure delay.'])
    (ROOT/'IMG_8148-diagnosis.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k not in ['frames','gaps','inputHashes']},indent=2))
    print('late motion',[(f['frame'],f.get('patternTranslation'))for f in frames if f['frame']in [30,38,46,50,55]])


if __name__=='__main__':main()
