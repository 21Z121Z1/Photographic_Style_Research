"""Compare paired still/video scene thumbnails with SDR-frozen geometry.

Primary radiometric scoring fits one exposure scalar on training tiles. A
free log slope is diagnostic only and never used to correct scored pixels.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import plistlib
from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates
from scipy.optimize import least_squares
from PIL import Image, ImageDraw

Y=np.array([.2289745641,.6917385218,.0792869141])
def load(path,w,h):return np.fromfile(path,dtype='<f4').reshape(h,w,4)[...,:3].astype('f8')
def luminance(a):return a@Y
def area(a,w,h):
    ah,aw=a.shape[:2]
    if aw%w==0 and ah%h==0:return a.reshape(h,ah//h,w,aw//w,a.shape[2]).mean(axis=(1,3))
    return np.stack([np.array(Image.fromarray(a[...,c].astype('f4')).resize((w,h),Image.Resampling.BOX))for c in range(a.shape[2])],axis=2)
def structure(a):
    y=np.log2(np.maximum(luminance(a),1e-5));z=gaussian_filter(y,.7)-gaussian_filter(y,5)
    return z/np.maximum(np.sqrt(gaussian_filter(z*z,5)),.05)
def coords(p,h,w):
    yy,xx=np.mgrid[:h,:w].astype(float);cy,cx=(h-1)/2,(w-1)/2
    return [p[0]*(yy-cy)+p[1]*(xx-cx)+cy+p[4]*h,
            p[2]*(yy-cy)+p[3]*(xx-cx)+cx+p[5]*w]
def warp(a,p):
    h,w=a.shape[:2];co=coords(p,h,w)
    return np.stack([map_coordinates(a[...,c],co,order=1,mode='constant',cval=np.nan)for c in range(a.shape[2])],axis=2)
def register(source,target):
    s,t=structure(area(source,192,144)),structure(area(target,192,144));h,w=t.shape
    yy,xx=np.mgrid[:h,:w];m=(yy>=10)&(yy<h-10)&(xx>=10)&(xx<w-10)
    def residual(p):return (map_coordinates(s,coords(p,h,w),order=1,mode='nearest')-t)[m]
    fit=least_squares(residual,[1,0,0,1,0,0],bounds=([.75,-.12,-.12,.75,-.15,-.15],[1.25,.12,.12,1.25,.15,.15]),loss='soft_l1',f_scale=.5,diff_step=1e-4,max_nfev=100)
    p=fit.x
    return p,dict(parameters=p.tolist(),initialCorrelation=float(np.corrcoef(s[m],t[m])[0,1]),finalCorrelation=float(np.corrcoef(map_coordinates(s,coords(p,h,w),order=1,mode='nearest')[m],t[m])[0,1]),cost=float(fit.cost),geometrySource='SDR primary images only; no linear-thumbnail radiometry used')
def score(candidate,reference,mask,tile=8,offset=0,fixed_ev=None):
    cy,ry=luminance(candidate),luminance(reference)
    m=mask&np.isfinite(cy)&np.isfinite(ry)&(cy>1e-7)&(ry>1e-7)
    yy,xx=np.indices(m.shape);train=m&((((yy+offset)//tile+(xx+offset)//tile)%2)==0);test=m&~train
    sx=np.log2(np.maximum(cy,1e-30));rx=np.log2(np.maximum(ry,1e-30))
    ev=float(np.median((rx-sx)[train]))if fixed_ev is None else float(fixed_ev)
    e=(sx+ev-rx)[test];slope,intercept=np.polyfit(sx[train],rx[train],1)
    residual_curve=(slope*sx+intercept-rx)[test]
    return dict(trainPixels=int(train.sum()),testPixels=int(test.sum()),exposureFitEV=ev,scaleVideoToPhoto=float(2**ev),
                maeEV=float(np.mean(abs(e))),medianEV=float(np.median(abs(e))),p90EV=float(np.percentile(abs(e),90)),p99EV=float(np.percentile(abs(e),99)),
                logCorrelation=float(np.corrcoef(sx[test],rx[test])[0,1]),linearCorrelation=float(np.corrcoef(cy[test],ry[test])[0,1]),
                diagnosticLogSlope=float(slope),diagnosticCurveMAE=float(np.mean(abs(residual_curve))))
def native_inverse(c):return 2**((c-.69336945)/.08550479)-.00964052
def piecewise_inverse(c):
    r0=-.05641088;rt=.01;constant=47.28711236;pt=constant*(rt-r0)**2
    return np.where(c>=pt,native_inverse(c),np.sqrt(np.maximum(c,0)/constant)+r0)
def srgb_inverse(c):return np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
def preview(a,exposure=1):
    a=np.maximum(np.nan_to_num(a)*exposure,0);a=a/(1+np.max(a,axis=-1,keepdims=True));a=np.where(a<=.0031308,12.92*a,1.055*a**(1/2.4)-.055)
    return Image.fromarray(np.uint8(np.clip(a,0,1)*255+.5))
def run(root,out):
    out.mkdir(exist_ok=False);decoded=root/'decoded-isolated';facts=json.loads((decoded/'decoded.json').read_text());extract=json.loads((root/'resources-isolated/extract.json').read_text())
    photo_meta=plistlib.loads((root/'resources-isolated/styles.plist').read_bytes());enc=extract['encoding'];gain=enc['Gain']
    photo=load(decoded/'photo-linear-p3.f32',1024,768);codes=load(decoded/'photo-codes.f32',1024,768)
    mirror=np.clip(native_inverse(codes)/gain,enc['OriginalRangeMin'],enc['OriginalRangeMax'])
    decode_error=float(np.max(np.abs(mirror-photo)))
    photo_sdr=load(decoded/'photo-sdr.f32',384,288);still=facts['stillTime']['seconds']
    main=min(facts['nearbyMainFrames'],key=lambda f:abs(f['pts']['seconds']-still));video_sdr=load(decoded/main['full']['file'],384,288)
    geometry,geometry_report=register(photo_sdr,video_sdr)
    clean=load(decoded/main['clean']['file'],384,288);clean_geometry,clean_report=register(photo_sdr,clean)
    # Warp at the native still-thumbnail resolution before area reduction.
    # Reversing these operations introduces an extra low-resolution blur.
    reference=area(warp(photo,geometry),128,96);identity_reference=area(photo,128,96)
    anchor=min(facts['thumbnails'],key=lambda f:abs(f['pts']['seconds']-still));ai=anchor['index'];w,h=anchor['linear']['width'],anchor['linear']['height']
    assert(w,h)==(128,96)
    video=load(decoded/anchor['linear']['file'],w,h);raw=load(decoded/anchor['codes']['file'],w,h)
    basis=np.fromfile(decoded/'rec2020-to-p3-basis.f32',dtype='<f4').reshape(3,4)[:,:3]
    native_video_mirror=native_inverse(raw)@basis
    video_decode_error=float(np.max(np.abs(native_video_mirror-video)))
    yy,xx=np.mgrid[:h,:w]
    valid=np.isfinite(reference).all(axis=2)&np.isfinite(video).all(axis=2)&(luminance(reference)>1e-5)&(luminance(video)>1e-5)&(xx>=5)&(xx<w-5)&(yy>=5)&(yy<h-5)
    lo,hi=np.percentile(luminance(reference)[valid],[2,99.5]);mask=valid&(luminance(reference)>=lo)&(luminance(reference)<=hi)
    primary=score(video,reference,mask)
    adjacent=[]
    for f in facts['thumbnails']:
        if abs(f['pts']['seconds']-still)>.2:continue
        a=load(decoded/f['linear']['file'],w,h);adjacent.append(dict(index=f['index'],pts=f['pts'],offsetSeconds=f['pts']['seconds']-still,metrics=score(a,reference,mask)))
    controls={
      'native_AppleLog_Rec2020_to_P3':primary,
      'codes_as_linear_Rec2020':score(raw@basis,reference,mask),
      'inverse_sRGB_Rec2020':score(srgb_inverse(raw)@basis,reference,mask),
      'piecewise_AppleLog_Rec2020':score(piecewise_inverse(raw)@basis,reference,mask),
      'native_AppleLog_wrongly_P3':score(native_inverse(raw),reference,mask),
      'identity_geometry':score(video,identity_reference,mask&np.isfinite(identity_reference).all(axis=2)),
      'downsample_then_warp':score(video,warp(area(photo,128,96),geometry),mask),
      'clean_aperture_geometry':score(video,area(warp(photo,clean_geometry),128,96),mask),
    }
    vm=next(m['value']for m in facts['timedMetadata']if m['identifier'].endswith('smartstyle-info')and m['pts']['value']==anchor['pts']['value'])
    meta_scale=float(vm['h']/photo_meta['h']);metadata_score=score(video,reference,mask,fixed_ev=np.log2(meta_scale))
    splits=[score(video,reference,mask,tile,offset)for tile in [8,12,16]for offset in [0,4]]
    toe=47.28711236*(.01+.05641088)**2;non_toe=np.min(raw,axis=2)>=toe
    toe_diagnostics={}
    for name,m in [('all',mask),('above_toe_all_channels',mask&non_toe),('contains_toe_channel',mask&~non_toe)]:
        toe_diagnostics[name]=dict(pixels=int(m.sum()),native=score(video,reference,m),piecewise=score(piecewise_inverse(raw)@basis,reference,m))
    coarse=[]
    for cw,ch in [(64,48),(32,24)]:
        cp,cv=area(reference,cw,ch),area(video,cw,ch);yyc,xxc=np.mgrid[:ch,:cw]
        cm=np.isfinite(cp).all(axis=2)&(luminance(cp)>1e-5)&(luminance(cv)>1e-5)&(yyc>=2)&(yyc<ch-2)&(xxc>=2)&(xxc<cw-2)
        coarse.append(dict(size=[cw,ch],native=score(cv,cp,cm,tile=max(2,cw//16)),piecewise=score(area(piecewise_inverse(raw)@basis,cw,ch),cp,cm,tile=max(2,cw//16))))
    lowpass=[]
    available=np.isfinite(reference).all(axis=2)
    for sigma in [1,2]:
        denominator=gaussian_filter(available.astype(float),sigma)
        pr=np.stack([gaussian_filter(np.nan_to_num(reference[...,c]),sigma)/np.maximum(denominator,1e-6)for c in range(3)],axis=2)
        for name,pixels in [('native',video),('piecewise',piecewise_inverse(raw)@basis)]:
            filtered=gaussian_filter(pixels,sigma=(sigma,sigma,0))
            lowpass.append(dict(sigmaPixels=sigma,decoder=name,pixels=int(mask.sum()),
                                exposureFit=score(filtered,pr,mask),
                                fixedMetadataScale=score(filtered,pr,mask,fixed_ev=np.log2(meta_scale))))
    ranges=[]
    for lower,upper in [(2,25),(25,50),(50,75),(75,95),(95,99.5)]:
        l,u=np.percentile(luminance(reference)[valid],[lower,upper]);m=mask&(luminance(reference)>=l)&(luminance(reference)<u)
        ranges.append(dict(percentiles=[lower,upper],metrics=score(video,reference,m)))
    # RGB diagnostics share the luminance split; no per-pixel or local correction.
    color=[];train=mask&(((yy//8+xx//8)%2)==0);test=mask&~train
    for c,name in enumerate(['R','G','B']):
        v=np.maximum(video[...,c],1e-8);p=np.maximum(reference[...,c],1e-8);m=(v>1e-5)&(p>1e-5);ev=float(np.median((np.log2(p)-np.log2(v))[train&m]));e=(np.log2(v)+ev-np.log2(p))[test&m]
        color.append(dict(channel=name,exposureFitEV=ev,maeEV=float(np.mean(abs(e)))))
    output=dict(schema='paired-still-video-linear-thumbnail-v1',photoItem=extract['linearItem'],photoEncoding=enc,photoBaseGain=photo_meta['h'],videoBaseGain=vm['h'],
                stillTime=facts['stillTime'],mainFrame=main['index'],thumbnailFrame=ai,thumbnailPTS=anchor['pts'],exactStillPTSMatch=anchor['pts']==facts['stillTime'],
                commonSpace='extended-linear Display P3',resolution=[w,h],photoNativeMirrorMaxAbs=decode_error,videoNativeMirrorMaxAbs=video_decode_error,
                matrixRec2020ToP3=basis.tolist(),geometry=geometry_report,cleanGeometry=clean_report,
                frozenMask=dict(valid=int(valid.sum()),scored=int(mask.sum()),referenceYPercentiles=[lo,hi],tileSize=8),
                primary=primary,controls=controls,nearbyFrames=adjacent,splitSensitivity=splits,luminanceBands=ranges,rgbDiagnostics=color,
                toeDiagnostics=toe_diagnostics,coarseBandComparisons=coarse,
                symmetricLowPassComparisons=lowpass,
                toeDiagnosticsStatus='Added after initial all-pixel comparison to localize the observed decoder difference. Full-field primary result is retained.',
                metadataScaleHypothesis=dict(formula='video.h / photo.h',scale=meta_scale,fitScaleOverMetadataScale=primary['scaleVideoToPhoto']/meta_scale,metricsWithoutExposureFit=metadata_score),
                allNonblackUntrimmed=score(video,reference,valid),
                sourceHashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(facts.get('photoSourcePath','/Users/retriedstormtrooper/Downloads/IMG_3673.HEIC')),Path(facts.get('movieSourcePath','/Users/retriedstormtrooper/Downloads/IMG_3673.mov'))]},
                method='Geometry fitted on SDR primary images only. Single exposure scalar on alternating spatial tiles, opposite tiles score. Log slope diagnostic only. No tone curve, local gain, or RGB field fitted for primary result.')
    (out/'results.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
    np.savez_compressed(out/'comparison-arrays.npz',photo_reference=reference,video=video,mask=mask,valid=valid,geometry=geometry)
    thumb=[('Photo linear reference',reference),('Video x fitted scalar',video*primary['scaleVideoToPhoto']),('Video x metadata scalar',video*meta_scale)]
    canvas=Image.new('RGB',(3*384,320),'white');draw=ImageDraw.Draw(canvas)
    exposure=1/np.percentile(luminance(reference)[mask],95)
    for j,(name,a)in enumerate(thumb):canvas.paste(preview(a,exposure).resize((384,288)),(j*384,0));draw.text((j*384+8,296),name,fill='black')
    canvas.save(out/'paired-preview.png')
    print(json.dumps({k:output[k]for k in ['exactStillPTSMatch','photoNativeMirrorMaxAbs','videoNativeMirrorMaxAbs','geometry','primary','metadataScaleHypothesis','controls']},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('output',type=Path);a=p.parse_args();run(a.root,a.output)
