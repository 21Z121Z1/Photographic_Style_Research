"""Fit the paired still's HDR look, then transport its residual with native flow.

The regression and confidence policy are this experiment's algorithm. Apple's
native calls provide style inversion, log decoding, flow, guided upsampling,
and HLG conversion; this does not reproduce Apple's capture ISP.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import plistlib
import subprocess
import struct
from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates

Y = np.array([0.22897456, 0.69173855, 0.07928691], dtype=np.float32)

def load(path: Path, w: int, h: int) -> np.ndarray:
    return np.fromfile(path, dtype='<f4').reshape(h, w, 4)[..., :3]

def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')

def luma(a: np.ndarray) -> np.ndarray:
    return np.maximum(a @ Y, 1e-5)

def log(a: np.ndarray) -> np.ndarray:
    return np.log2(np.maximum(a, 1e-5))

def warp(a: np.ndarray, flow: np.ndarray) -> np.ndarray:
    h, w = flow.shape[:2]
    yy, xx = np.mgrid[:h, :w]
    coordinates = [yy + flow[..., 1], xx + flow[..., 0]]
    if a.ndim == 2:
        return map_coordinates(a, coordinates, order=1, mode='nearest')
    return np.stack([map_coordinates(a[..., c], coordinates, order=1, mode='nearest')
                     for c in range(a.shape[2])], axis=-1)

def resize(a: np.ndarray, w: int, h: int) -> np.ndarray:
    ah, aw = a.shape[:2]
    yy, xx = np.mgrid[:h, :w]
    coords = [(yy + .5) * ah / h - .5, (xx + .5) * aw / w - .5]
    if a.ndim == 2:
        return map_coordinates(a, coords, order=1, mode='nearest')
    return np.stack([map_coordinates(a[..., c], coords, order=1, mode='nearest')
                     for c in range(a.shape[2])], axis=-1)

def flow_call(native: Path, source: Path, target: Path, output: Path, w: int, h: int) -> np.ndarray:
    if not output.exists():
        subprocess.run([str(native), 'flow', str(source), str(target), str(output), str(w), str(h)], check=True)
    return np.fromfile(output, dtype='<f4').reshape(h, w, 2)

def flow_confidence(f: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    h, w = f.shape[:2]
    yy, xx = np.mgrid[:h, :w]
    error = np.linalg.norm(f + warp(b, f), axis=2)
    inside = ((xx + f[..., 0] >= 2) & (xx + f[..., 0] < w - 2) &
              (yy + f[..., 1] >= 2) & (yy + f[..., 1] < h - 2))
    return inside * np.exp(-.5 * (error / 1.5) ** 2), error

def features(styled: np.ndarray, neutral: np.ndarray, scene: np.ndarray) -> np.ndarray:
    s, u, a = log(luma(styled)), log(luma(neutral)), log(luma(scene))
    # The scene/neutral relation changes spatially and with time. It is a
    # predictor, rather than an assumed inverse camera tone curve.
    columns = [np.ones_like(s), np.clip(a - u, -10, 10), s, np.clip(u - s, -3, 3)]
    columns += [np.maximum(s - knot, 0) for knot in [-7, -5, -3, -1.5]]
    columns += [np.clip(log(styled[..., c]) - s, -3, 3) for c in [0, 2]]
    return np.stack(columns, axis=-1).astype(np.float64)

def fit_ridge(x: np.ndarray, target: np.ndarray, weight: np.ndarray, penalty: float) -> np.ndarray:
    selected = weight > .01
    a, b, base = x[selected], target[selected], weight[selected]
    scale = np.sqrt(np.mean(a * a, axis=0)); scale[0] = 1; scale = np.maximum(scale, .1)
    a = a / scale
    regularizer = np.eye(a.shape[1]) * penalty * len(a); regularizer[0, 0] = 1e-8
    wr = base.copy()
    for _ in range(5):
        beta = np.linalg.solve((a * wr[:, None]).T @ a + regularizer,
                               (a * wr[:, None]).T @ b)
        residual = np.max(np.abs(a @ beta - b), axis=1)
        wr = base * np.minimum(1, .25 / np.maximum(residual, 1e-6))
    return beta / scale[:, None]

def score(prediction: np.ndarray, target: np.ndarray, mask: np.ndarray) -> dict:
    mask = mask & np.isfinite(prediction).all(axis=-1) & np.isfinite(target).all(axis=-1)
    ev = np.abs(log(luma(prediction))[mask] - log(luma(target))[mask])
    pc = prediction / luma(prediction)[..., None]
    tc = target / luma(target)[..., None]
    chroma = np.linalg.norm(pc[mask] - tc[mask], axis=-1)
    return dict(pixels=int(mask.sum()), luma_mae_ev=float(ev.mean()),
                luma_p90_ev=float(np.percentile(ev, 90)), chroma_mae=float(chroma.mean()))

def smooth_residual(residual: np.ndarray, weight: np.ndarray, sigma: float) -> np.ndarray:
    den = gaussian_filter(weight, sigma=sigma, mode='nearest')
    return np.stack([gaussian_filter(residual[..., c] * weight, sigma=sigma, mode='nearest') /
                     np.maximum(den, .002) for c in range(3)], axis=-1)

def run(args: argparse.Namespace) -> None:
    collection, output, native = args.collection.resolve(), args.output.resolve(), args.native.resolve()
    output.mkdir(exist_ok=False); flows = output / 'flows'; flows.mkdir()
    source = json.loads((collection / 'collection.json').read_text())
    w, h = source['width'], source['height']
    frame_times = np.array([f['pts']['seconds'] for f in source['frames']])
    anchor = int(np.argmin(np.abs(frame_times - source['stillTime']['seconds'])))
    s = load(collection / source['frames'][anchor]['styled'], w, h)
    u = load(collection / source['frames'][anchor]['neutral'], w, h)
    ps, ph = load(collection / 'photo-sdr.f32', w, h), load(collection / 'photo-hdr.f32', w, h)
    f = flow_call(native, collection / source['frames'][anchor]['styled'], collection / 'photo-sdr.f32',
                  flows / 'anchor-photo.f32', w, h)
    b = flow_call(native, collection / 'photo-sdr.f32', collection / source['frames'][anchor]['styled'],
                  flows / 'photo-anchor.f32', w, h)
    confidence, fb_error = flow_confidence(f, b)
    aligned_sdr, target = warp(ps, f), warp(ph, f)
    np.concatenate([target, np.ones((h, w, 1), np.float32)], axis=2).astype('<f4').tofile(output / 'target.f32')
    sdr_difference = log(luma(aligned_sdr)) - log(luma(s))
    center = np.median(sdr_difference[confidence > .5])
    photometric = np.exp(-.5 * ((sdr_difference - center) / .45) ** 2)
    weight = confidence * photometric
    valid = ((weight > .2) & (luma(s) > .003) & (luma(aligned_sdr) > .003) &
             (luma(s) < .98) & (np.max(s, axis=2) > .01))
    assert valid.mean() > .2, f'Insufficient valid anchor registration: {valid.mean():.3f}'
    yy, xx = np.mgrid[:h, :w]
    split = ((xx // 24) + 2 * (yy // 24)) % 5
    training, validation, test = valid & (split >= 2), valid & (split == 0), valid & (split == 1)
    np.savez(output / 'masks.npz', valid=valid, training=training, validation=validation, test=test,
             confidence=confidence, fb_error=fb_error)
    photo_style=plistlib.loads((collection.parent/'resources'/'styles.plist').read_bytes())
    photo_h=float(photo_style['h'])
    if not photo_h>0:raise ValueError('Invalid photo scene normalization h')
    scene_scales=[]
    for t in source['thumbnails']:
        j=int(np.argmin(abs(frame_times-t['pts']['seconds'])))
        video_h=float(source['frames'][j]['style']['stored']['h'])
        if not video_h>0:raise ValueError('Invalid per-frame video scene normalization h')
        scene_scales.append(video_h/photo_h)
    scenes = [load(collection / t['file'], t['width'], t['height'])*scale for t,scale in zip(source['thumbnails'],scene_scales)]
    thumbnail_times = np.array([t['pts']['seconds'] for t in source['thumbnails']])

    def scene_at(time: float) -> np.ndarray:
        j = int(np.searchsorted(thumbnail_times, time, side='right'))
        lo, hi = max(0, j - 1), min(j, len(scenes) - 1)
        fraction = 0 if lo == hi else (time - thumbnail_times[lo]) / (thumbnail_times[hi] - thumbnail_times[lo])
        a = np.exp2((1 - fraction) * log(scenes[lo]) + fraction * log(scenes[hi]))
        # All maps use the original coded canvas. The output keeps the same
        # canvas and its clean aperture instead of changing auxiliary geometry.
        cx, cy, cw, ch = source['crop']; sh, sw = a.shape[:2]
        coords = [(cy + (yy + .5) / h * ch) / source['codedHeight'] * sh - .5,
                  (cx + (xx + .5) / w * cw) / source['codedWidth'] * sw - .5]
        return np.stack([map_coordinates(a[..., c], coords, order=1, mode='nearest') for c in range(3)], axis=-1)

    x = features(s, u, scene_at(frame_times[anchor]))
    log_gain = np.clip(log(target) - log(s), -4, 4)
    candidates = []
    for penalty in [.0001, .001, .01, .1]:
        beta = fit_ridge(x, log_gain, weight * training, penalty)
        global_gain = x @ beta
        for sigma in [4, 8, 12]:
            residual = smooth_residual(log_gain - global_gain, weight * training, sigma)
            g = resize(resize(global_gain + residual, 64, 48), w, h)
            prediction = s * np.exp2(np.clip(g, -3, 3))
            metric = score(prediction, target, validation)
            objective = metric['luma_mae_ev'] + .3 * metric['chroma_mae']
            candidates.append((objective, penalty, sigma, metric))
    _, penalty, sigma, validation_metrics = min(candidates, key=lambda v: v[0])
    fit_weight = weight * (training | validation)
    beta = fit_ridge(x, log_gain, fit_weight, penalty)
    global_anchor = x @ beta
    residual = smooth_residual(log_gain - global_anchor, fit_weight, sigma)
    anchor_gain = resize(resize(global_anchor + residual, 64, 48), w, h)
    reconstructed = s * np.exp2(np.clip(anchor_gain, -3, 3))
    # An independently constructed stationary gain-map baseline; no earlier
    # implementation or results are read by this experiment.
    stationary = resize(resize(luma(ph), 32, 24) / np.maximum(resize(luma(ps), 32, 24), 1e-5), w, h)
    baseline = s * np.clip(stationary, 1, source['headroom'])[..., None]
    metrics = dict(input_sdr=score(s, target, test),
                   stationary_photo_gain=score(baseline, target, test),
                   fitted_hdr=score(reconstructed, target, test))
    map_stats = []
    for i, frame in enumerate(source['frames']):
        st = load(collection / frame['styled'], w, h)
        ut = load(collection / frame['neutral'], w, h)
        base = features(st, ut, scene_at(frame_times[i])) @ beta
        if i == anchor:
            transported, transport_confidence = residual, np.ones((h, w))
        else:
            to_anchor = flow_call(native, collection / frame['styled'], collection / source['frames'][anchor]['styled'],
                                  flows / f'{i:04d}-anchor.f32', w, h)
            from_anchor = flow_call(native, collection / source['frames'][anchor]['styled'], collection / frame['styled'],
                                    flows / f'anchor-{i:04d}.f32', w, h)
            transport_confidence, _ = flow_confidence(to_anchor, from_anchor)
            # Newly exposed or inconsistent content uses the fitted global
            # response; it receives no arbitrary photo-space correction.
            transported = warp(residual, to_anchor) * transport_confidence[..., None]
        gain = np.clip(resize(base + transported, 64, 48), -3, 3).astype('<f4')
        gain.tofile(output / f'gain-{i:04d}.f32')
        map_stats.append(dict(frame=i, pts=float(frame_times[i]),
                              flow_confidence=float(np.mean(transport_confidence)),
                              gain_ev_min=float(gain.min()), gain_ev_max=float(gain.max()),
                              gain_ev_mean=float(gain.mean())))
        if i % 10 == 0: print(f'fitted frame {i}/{len(frame_times)}', flush=True)
    plan = dict(schema='independent-native-dynamic-hdr-model-v1', collection=str(collection),
                mapWidth=64, mapHeight=48, anchorFrame=anchor, anchorPTS=float(frame_times[anchor]),
                stillTime=source['stillTime'], linearPeakCap=float(source['headroom'] * 1.05),
                regularization=penalty, spatialSigma=sigma, coefficients=beta.tolist(),
                registration=dict(validFraction=float(valid.mean()),
                                  forwardBackwardMedian=float(np.median(fb_error[valid])),
                                  normalizedSDRMedianDifferenceEV=float(center)),
                selectionValidation=validation_metrics, independentTestMetrics=metrics,
                dataPolicy='Photo HDR test blocks excluded from regression and spatial residual fitting; optical flow uses SDR only.',
                dynamicPolicy='Per-PTS scene/neutral/styled response plus bidirectionally checked transport of the fitted photo residual.',
                temporalPolicy='Interpolate scene thumbnails in log RGB at actual PTS after h_video/h_photo normalization. Residual transport is always from one anchor.',
                sceneNormalization=dict(formula='h_video/h_photo',photoBaseGain=photo_h,scales=scene_scales),
                reverseMode=source['reverseMode'],
                frameFacts=map_stats,
                ambientViewingEnvironmentHex=struct.pack('>IHH', 3140000, 15635, 16450).hex(),
                ambientMetadataSource='Nominal 314 lux / D65 mobile viewing target from Apple TN3145; an authoring assumption, not a measurement of the capture scene.',
                limits=['Estimated reconstruction, not original capture HDR or Apple ISP equivalence.',
                        'No unique recovery of clipped high-frequency highlights.',
                        'Only Smart Style version 16 with a complete paired resource set is tested.'])
    save_json(output / 'model.json', plan)
    save_json(output / 'fit-report.json', {k: plan[k] for k in ['anchorFrame', 'anchorPTS', 'registration', 'independentTestMetrics', 'regularization', 'spatialSigma']})
    print(json.dumps(plan['independentTestMetrics'], indent=2), flush=True)

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('collection', type=Path); p.add_argument('output', type=Path); p.add_argument('native', type=Path)
    run(p.parse_args())
