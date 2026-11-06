"""Validate the final, independently decoded package and the fitted look."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from fit import load, luma, log, score

def run(collection: Path, model: Path, video: Path, audit: Path, package_report: Path, output: Path):
    c = json.loads((collection / 'collection.json').read_text())
    m = json.loads((model / 'model.json').read_text())
    a = json.loads((audit / 'audit.json').read_text())
    render = json.loads(Path(str(video) + '.json').read_text())
    package = json.loads(package_report.read_text())
    w, h = c['width'], c['height']; anchor = m['anchorFrame']
    # Masks and target depend solely on the fitted model's original SDR registration.
    original_model = model if (model / 'masks.npz').exists() else model.parent / 'model-v1'
    masks = np.load(original_model / 'masks.npz')
    target = load(original_model / 'target.f32', w, h)
    decoded = load(audit / f'decoded-{anchor:04d}.f32', w, h)
    encoded_metrics = score(decoded, target, masks['test'])
    baseline = m['independentTestMetrics']['stationary_photo_gain']
    rounds = []; peaks = []; gains = []; finite = True
    for i, row in enumerate(a['frames']):
        actual = load(audit / row['file'], w, h)
        prediction = load(Path(str(video) + '.pixels') / f'hdr-{i:04d}.f32', w, h)
        styled = load(collection / c['frames'][i]['styled'], w, h)
        valid = (luma(prediction) > .005) & (luma(styled) > .005)
        finite &= bool(np.isfinite(actual).all())
        rounds.append(score(actual, prediction, valid)['luma_mae_ev'])
        peaks.append(float(luma(actual).max()))
        gains.append(float(np.median((log(luma(actual)) - log(luma(styled)))[valid])))
    statuses = all(f['reverseStatus'] == 0 and f['guidedStatuses'] == [0, 0, 0] for f in render['frames'])
    pts_match = [f['pts'] for f in a['frames']] == [f['pts'] for f in c['frames']]
    format = a['mainFormat']
    checks = dict(allNativeStagesSucceeded=statuses, exactFramePTS=pts_match,
                  frameCountMatches=len(a['frames']) == len(c['frames']) == len(render['frames']),
                  nativeHDRRecognition=a['containsHDRVideo'], allPixelsFinite=finite,
                  retainsExtendedHighlights=max(peaks) > 1,
                  nativeHLGSignaling=format['CVImageBufferTransferFunction'] == 'ITU_R_2100_HLG',
                  nominalAmbientMatches=format.get('AmbientViewingEnvironment', {}).get('hex') == m['ambientViewingEnvironmentHex'],
                  CLLIExplicitlyUnknown=format.get('ContentLightLevelInfo', {}).get('hex') == '00000000',
                  anchorHeldoutLumaImproves=encoded_metrics['luma_mae_ev'] < .8 * baseline['luma_mae_ev'],
                  anchorHeldoutChromaDoesNotRegress=encoded_metrics['chroma_mae'] <= baseline['chroma_mae'],
                  HLGDecodeRoundtripAcceptable=max(rounds) < .06,
                  mainPresentationTimesPreserved=package['mainPTSMatch'],
                  allOtherTracksPreserved=all(t['identical'] for t in package['preservedTracks']),
                  photoOnlyUUIDChanged=package['photoOnlyUUIDChanged'])
    result = dict(schema='independent-native-hdr-validation-v1', overallPass=all(checks.values()), checks=checks,
                  anchorFrame=anchor, anchorPTS=m['anchorPTS'],
                  heldoutRegionPixels=encoded_metrics['pixels'], encodedAnchor=encoded_metrics,
                  independentlyBuiltStationaryBaseline=baseline,
                  lumaErrorReduction=float(1 - encoded_metrics['luma_mae_ev'] / baseline['luma_mae_ev']),
                  HLGDecodeRoundtripMeanEV=float(np.mean(rounds)), HLGDecodeRoundtripWorstFrameEV=max(rounds),
                  decodedLumaPeak=max(peaks), medianGainSequenceEV=gains,
                  maximumMedianGainStepEV=float(np.max(np.abs(np.diff(gains)))),
                  motionConfidenceAtFirstFrame=m['frameFacts'][0]['flow_confidence'],
                  package=package, sourceCodeHashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in Path(__file__).parent.glob('*') if p.suffix in ['.m', '.py']},
                  limits=m['limits'] + ['Photos import, physical HDR display appearance, and editing/save-reopen have not been exercised.'])
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({k:result[k] for k in ['overallPass', 'checks', 'encodedAnchor', 'lumaErrorReduction', 'HLGDecodeRoundtripWorstFrameEV', 'maximumMedianGainStepEV']}, indent=2))
    assert result['overallPass'], 'Final validation failed; inspect the named checks.'

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['collection', 'model', 'video', 'audit', 'package_report', 'output']: p.add_argument(key, type=Path)
    a = p.parse_args(); run(a.collection, a.model, a.video, a.audit, a.package_report, a.output)
