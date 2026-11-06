"""Bounded design experiment; does not encode or replace any media.

Uses only the independent implementation and original-pair experiment.
The scene projection below is a CPU prototype, not a CMIGuidedFilter replay.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('independent', type=Path)
    parser.add_argument('pair', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    old, pair, out = args.independent.resolve(), args.pair.resolve(), args.output.resolve()
    out.mkdir(exist_ok=False)
    spec = importlib.util.spec_from_file_location('independent_fit', old/'src/fit.py')
    fit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fit)
    collection = old/'verified-run/collection'
    model = old/'verified-run/model'
    source = json.loads((collection/'collection.json').read_text())
    paired = json.loads((pair/'verified-final/analysis/results.json').read_text())
    decoded = pair/'verified-final/decoded-isolated'
    w, h = source['width'], source['height']
    masks = np.load(model/'masks.npz')
    train, select, test = [masks[k] for k in ['training','validation','test']]
    confidence = masks['confidence']
    frame = paired['mainFrame']
    s = fit.load(collection/source['frames'][frame]['styled'],w,h)
    u = fit.load(collection/source['frames'][frame]['neutral'],w,h)
    target = fit.load(model/'target.f32',w,h)
    flow = np.fromfile(model/'flows/anchor-photo.f32',dtype='<f4').reshape(h,w,2)
    photo_sdr = fit.load(collection/'photo-sdr.f32',w,h)
    difference = fit.log(fit.luma(fit.warp(photo_sdr,flow)))-fit.log(fit.luma(s))
    center = np.median(difference[confidence>.5])
    weight = confidence*np.exp(-.5*((difference-center)/.45)**2)
    photo_scene = fit.load(decoded/'photo-linear-p3.f32',1024,768)
    yy,xx = np.mgrid[:h,:w]
    coordinates = [(yy+flow[...,1]+.5)*768/h-.5,(xx+flow[...,0]+.5)*1024/w-.5]
    photo_reference = np.stack([map_coordinates(photo_scene[...,c],coordinates,order=1,mode='nearest') for c in range(3)],axis=2)

    def area(a, width, height):
        ah,aw = a.shape[:2]
        assert aw % width == 0 and ah % height == 0
        return a.reshape(height,ah//height,width,aw//width,3).mean(axis=(1,3))

    def video_scene(index):
        codes = fit.load(decoded/f'video-codes-{index:04d}.f32',128,96).astype(float)
        r0,rt,c = -.05641088,.01,47.28711236
        toe = c*(rt-r0)**2
        inverse = np.where(codes>=toe,2**((codes-.69336945)/.08550479)-.00964052,np.sqrt(np.maximum(codes,0)/c)+r0)
        basis = np.array(paired['matrixRec2020ToP3'])
        pts = json.loads((decoded/'decoded.json').read_text())['thumbnails'][index]['pts']
        meta = next(f['style']['stored'] for f in source['frames'] if f['pts']['value']==pts['value'] and f['pts']['scale']==pts['scale'])
        raw = (inverse@basis)*(meta['h']/paired['photoBaseGain'])
        cy,cx = np.mgrid[:96,:128]
        cropx,cropy,cropw,croph = source['crop']
        co = [(cropy+(cy+.5)/96*croph)/source['codedHeight']*96-.5,
              (cropx+(cx+.5)/128*cropw)/source['codedWidth']*128-.5]
        return np.stack([map_coordinates(raw[...,k],co,order=1,mode='nearest') for k in range(3)],axis=2)

    a = video_scene(paired['thumbnailFrame'])
    # Make scene consistency explicit. The final implementation needs an
    # observation operator for the real spatial response, and native upsampling.
    positive_u = np.maximum(u,1e-5)
    g = fit.log(np.maximum(a,1e-5))-fit.log(area(positive_u,128,96))
    history=[]
    for iteration in range(21):
        scene = positive_u*np.exp2(fit.resize(g,w,h))
        low = area(scene,128,96)
        correction = fit.log(np.maximum(a,1e-5))-fit.log(low)
        mask = area(np.repeat(test[...,None],3,axis=2).astype(float),128,96)[...,0]>.5
        history.append(dict(iteration=iteration,sceneObservationMAEEV=float(np.mean(abs((fit.log(fit.luma(low))-fit.log(fit.luma(a)))[mask])))))
        if iteration<20:
            g += .8*correction

    def bridge_features(r):
        y = fit.log(fit.luma(r))
        columns = [np.ones_like(y),y]
        columns += [np.maximum(y-k,0) for k in [-11,-9,-7,-5,-3]]
        return np.stack(columns,axis=-1).astype(float)

    xphoto, xscene = bridge_features(photo_reference), bridge_features(scene)
    target_ratio = fit.log(target)-fit.log(photo_reference)
    candidates=[]
    for penalty in [.001,.01,.1]:
        beta = fit.fit_ridge(xphoto,target_ratio,weight*train,penalty)
        residual = fit.log(target)-fit.log(photo_reference)-xphoto@beta
        for sigma in [4,8,12]:
            local = fit.smooth_residual(residual,weight*train,sigma)
            prediction = np.maximum(scene,1e-5)*np.exp2(xscene@beta+local)
            score = fit.score(prediction,target,select)
            candidates.append((score['luma_mae_ev']+.3*score['chroma_mae'],penalty,sigma))
    _,penalty,sigma=min(candidates)
    beta=fit.fit_ridge(xphoto,target_ratio,weight*(train|select),penalty)
    residual=fit.log(target)-fit.log(photo_reference)-xphoto@beta
    local=fit.smooth_residual(residual,weight*(train|select),sigma)
    bridge=scene*np.exp2(xscene@beta+local)
    photo_oracle=photo_reference*np.exp2(xphoto@beta+local)
    existing=fit.load(old/f'verified-run/dynamic-hlg.mov.pixels/hdr-{frame:04d}.f32',w,h)
    metrics={
        'existing_rendered_linear_HDR':fit.score(existing,target,test),
        'scene_projection_then_photo_bridge':fit.score(bridge,target,test),
        'photo_scene_bridge_oracle_no_video_scene_error':fit.score(photo_oracle,target,test),
    }
    # A repair control: changing only scene decode/normalization, retaining the
    # old feature architecture. No scalar normalization can fix its design.
    x=fit.features(s,u,fit.resize(a,w,h))
    target_gain=np.clip(fit.log(target)-fit.log(s),-4,4)
    old_hyper=json.loads((model/'model.json').read_text())
    beta_old=fit.fit_ridge(x,target_gain,weight*(train|select),old_hyper['regularization'])
    local_old=fit.smooth_residual(target_gain-x@beta_old,weight*(train|select),old_hyper['spatialSigma'])
    repair=s*np.exp2(np.clip(fit.resize(fit.resize(x@beta_old+local_old,64,48),w,h),-3,3))
    metrics['corrected_scene_old_architecture_frozen_hyperparameters']=fit.score(repair,target,test)

    # Joint calibration reads the actual anchor's scene, neutral and styled
    # observations, rather than transferring a photo-scene-only curve blindly.
    scene_y=fit.log(fit.luma(scene))
    joint_x=np.concatenate([x,bridge_features(scene)[...,2:],
        np.stack([np.clip(fit.log(scene[...,c])-scene_y,-3,3)for c in [0,2]],axis=2)],axis=2)
    joint_selection=[]
    for carrier_name,carrier in [('styled',s),('neutral',u),('scene',scene)]:
        gain_target=fit.log(target)-fit.log(carrier)
        options=[]
        for regularization in [.001,.01,.1]:
            coefficients=fit.fit_ridge(joint_x,gain_target,weight*train,regularization)
            for smooth_sigma in [4,8,12]:
                spatial=fit.smooth_residual(gain_target-joint_x@coefficients,weight*train,smooth_sigma)
                gain_map=fit.resize(fit.resize(joint_x@coefficients+spatial,64,48),w,h)
                prediction=carrier*np.exp2(np.clip(gain_map,-6,6))
                selection_score=fit.score(prediction,target,select)
                options.append((selection_score['luma_mae_ev']+.3*selection_score['chroma_mae'],regularization,smooth_sigma))
        objective,regularization,smooth_sigma=min(options)
        coefficients=fit.fit_ridge(joint_x,gain_target,weight*(train|select),regularization)
        spatial=fit.smooth_residual(gain_target-joint_x@coefficients,weight*(train|select),smooth_sigma)
        gain_map=fit.resize(fit.resize(joint_x@coefficients+spatial,64,48),w,h)
        prediction=carrier*np.exp2(np.clip(gain_map,-6,6))
        metrics[f'joint_anchor_calibration_{carrier_name}_carrier']=fit.score(prediction,target,test)
        joint_selection.append(dict(carrier=carrier_name,regularization=regularization,residualSigma=smooth_sigma,validationObjective=objective))

    facts=json.loads((old/'verified-run/model/model.json').read_text())['frameFacts']
    confidences=np.array([v['flow_confidence']for v in facts])
    color_root=out.parent/'color-boundary-run-v2'
    if not color_root.exists():color_root=out.parent/'color-boundary-run'
    color=[]
    if (color_root/'facts.json').exists():
        cf=json.loads((color_root/'facts.json').read_text())
        for item in cf['modes']:
            if 'frames' not in item:
                color.append(dict(mode=item['mode'],unavailable=item.get('error',item.get('exception'))))
        for i in [0,44]:
            files=[color_root/f'{m}-{i:04d}-managed.f32' for m in ['auto-rgba-half','native-yuv']]
            half,yuv=[fit.load(p,w,h)for p in files]
            good=(fit.luma(yuv)>.003)&(fit.luma(yuv)<.9)
            delta=(fit.log(fit.luma(half))-fit.log(fit.luma(yuv)))[good]
            color.append(dict(frame=i,autoHalfVsNativeYUV_MAE_EV=float(np.mean(abs(delta))),medianSignedEV=float(np.median(delta))))
    result=dict(schema='scene-constrained-hdr-design-diagnostic-v1',
        scope='Anchor-only CPU design prototype; no native guided-filter validation or video output.',
        anchorFrame=frame,anchorPTS=paired['stillTime'],
        sceneProjectionHistory=history,anchorMetrics=metrics,
        bridge=dict(regularization=penalty,residualSigma=sigma,selection='Fixed spatial train/validation/test masks from independent implementation; prototype is exploratory.'),
        jointSelection=joint_selection,
        directAnchorTransport=dict(meanConfidenceQuantiles=np.percentile(confidences,[0,25,50,75,100]).tolist(),framesBelowPoint1=int((confidences<.1).sum()),total=len(facts),selected=[f for f in facts if f['frame']in [0,20,26,27,28,44,54]]),
        colorBoundary=color,
        supportedVideoUtilityConfiguration=source['utilityConfiguration'],
        inputs={str(p):sha(p)for p in [old/'src/native.m',old/'src/fit.py',collection/'collection.json',model/'model.json',pair/'verified-final/analysis/results.json',Path(__file__)]},
        limits=['No native HDR forward-style path is proved by this experiment.',
                'Photo-scene bridge uses sparse sampling from native photo thumbnail; primary photometric results remain the previous paired experiment.',
                'Scene projection uses positivity floor and bilinear interpolation; final implementation requires noise, clipping and gamut handling.',
                'Low-resolution observation closure alone is not independent scene-truth validation.'])
    (out/'diagnostics.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    np.savez_compressed(out/'anchor-prototype.npz',scene=scene,photo_scene=photo_reference,photo_hdr=target,predicted_hdr=bridge,test=test)
    print(json.dumps(dict(metrics=metrics,sceneProjectionStart=history[0],sceneProjectionEnd=history[-1],colorBoundary=color),indent=2))


if __name__=='__main__':
    main()
