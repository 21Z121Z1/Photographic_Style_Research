"""Measure the frozen joint candidate's change and regression footprints."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import tempfile

import numpy as np

from . import blind, corpus, isolate, native
from .texture import measurement_host
from .tone_attribution import render

JOINT = {**blind.DEFAULT, 'baseline_scale': 0.75, 'gain_scale': 0.75,
         'histogram_light_maps': True}


def footprint(mask):
    """Eight-connected components using row runs; boxes have exclusive ends."""
    height, width = mask.shape
    parents, sizes, boxes = [], [], []

    def find(i):
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i

    def merge(a, b):
        a, b = find(a), find(b)
        if a != b:
            parents[b] = a
            sizes[a] += sizes[b]
            boxes[a] = [min(boxes[a][0], boxes[b][0]), min(boxes[a][1], boxes[b][1]),
                        max(boxes[a][2], boxes[b][2]), max(boxes[a][3], boxes[b][3])]
        return a

    previous = []
    for y, row in enumerate(mask):
        edges = np.flatnonzero(np.diff(np.r_[False, row, False].astype('i1')))
        current, cursor = [], 0
        for start, end in edges.reshape(-1, 2):
            start, end = int(start), int(end)
            i = len(parents)
            parents.append(i); sizes.append(end-start); boxes.append([start, y, end, y+1])
            while cursor < len(previous) and previous[cursor][1] < start:
                cursor += 1
            q = cursor
            while q < len(previous) and previous[q][0] <= end:
                i = merge(i, previous[q][2]); q += 1
            current.append((start, end, i))
        previous = current
    roots = [i for i in range(len(parents)) if parents[i] == i]
    largest = max(roots, key=lambda i: sizes[i]) if roots else None
    count = int(mask.sum())
    return {'pixels': count, 'area_pct': 100*count/mask.size,
            'components_8_connected': len(roots),
            'largest_component_pixels': sizes[largest] if largest is not None else 0,
            'largest_component_area_pct': 100*sizes[largest]/mask.size if largest is not None else 0.,
            'largest_component_box_xyxy': boxes[largest] if largest is not None else None,
            'width': width, 'height': height}


def display_projection(rgb, headroom):
    """Fixed shared exposure and Display P3 transfer; diagnostic, not Photos HDR."""
    linear = np.clip(rgb.astype('f8') / headroom, 0., 1.)
    return np.where(linear <= .0031308, 12.92*linear,
                    1.055*np.power(linear, 1/2.4)-.055)


def spatial(reference, baseline, candidate):
    if (reference.shape != baseline.shape or reference.shape != candidate.shape
            or reference.ndim != 3 or reference.shape[2] != 3
            or not all(np.isfinite(x).all() for x in (reference, baseline, candidate))):
        raise ValueError('matching finite RGB images required')
    reference, baseline, candidate = (x.astype('f8') for x in (reference, baseline, candidate))
    change = np.max(np.abs(candidate-baseline), axis=-1)
    old = np.max(np.abs(baseline-reference), axis=-1)
    new = np.max(np.abs(candidate-reference), axis=-1)
    regression = new-old
    return {'error_definition': 'per-pixel max absolute RGB channel error to reference',
            'candidate_change_max': float(change.max()),
            'regression_max': float(regression.max()),
            'change_quantiles_p50_p95_p99_p999': np.quantile(change, [.5,.95,.99,.999]).tolist(),
            'regression_quantiles_p50_p95_p99_p999': np.quantile(regression, [.5,.95,.99,.999]).tolist(),
            'thresholds': {f'{t:g}': {
                'changed': footprint(change > t),
                'worse': footprint(regression > t),
                'better': footprint(regression < -t)} for t in (.005,.01,.02)}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('adapter','generator','research-root','output'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--input', type=Path, action='append', required=True)
    parser.add_argument('--holdout', type=Path, action='append', default=[])
    parser.add_argument('--max-edge', type=int, default=2048)
    args = parser.parse_args(argv)
    if args.max_edge <= 0:
        parser.error('--max-edge must be positive')
    if {p.resolve() for p in args.input} & {p.resolve() for p in args.holdout}:
        parser.error('calibration and holdout overlap')
    args.output.mkdir(parents=True, exist_ok=False)
    report = {'schema':'styles-joint-spatial-v1','passed':False,'cases':[],
              'joint_calibration':JOINT,'max_edge':args.max_edge,
              'oracle_resources_used_for_generation':False,'product_defaults_changed':False,
              'scope':'PISemanticStyleFilter useStyleEngine=NO; scaled native renders, not full-resolution or real-display visibility',
              'projection':'RGB / measured source headroom, clipped to [0,1], then Display P3 transfer; identical mapping for all variants'}
    try:
        report['host'] = measurement_host(args.adapter)
        report['experiment_sha256'] = isolate.sha(Path(__file__).read_bytes())
        with tempfile.TemporaryDirectory(prefix='joint-spatial-',dir=args.output) as temp:
            work = Path(temp)
            renderer, _, compatibility, report['renderer'] = blind.prepare_renderer(
                args.research_root,work,capture_pixel_limit=4_000_000)
            for index, source in enumerate([*args.input,*args.holdout]):
                source = source.resolve()
                if corpus.inspect_bytes(source.read_bytes())['standard_semantic_state'] is not True:
                    raise ValueError('Standard reference required')
                root = work/str(index); root.mkdir()
                equivalence = native.check_case(args.adapter,source,root)
                if not equivalence['passed']:
                    raise ValueError('native source isolation failed')
                isolate.write_case(source,root/'producer')
                case = {'name':source.name,'source_sha256':isolate.sha(source.read_bytes()),
                        'evaluation_split':'holdout' if source in {p.resolve() for p in args.holdout} else 'calibration',
                        'native_equivalence':equivalence,'generation':{},'edits':[]}
                headroom = equivalence['reference_headroom']
                for label, calibration in [('default',blind.DEFAULT),('joint',JOINT)]:
                    output = root/(label+'.heic')
                    case['generation'][label] = blind.regenerate(args.generator,args.adapter,
                        root/'producer/input.heic',output,headroom,calibration,verify_pixels=True)
                    blind.extract(compatibility,output,root/label)
                # Reference resources never enter either generator.
                blind.extract(compatibility,source,root/'reference')
                report['cases'].append(case)
                for tone,color in [(-.5,0.),(0.,0.),(.5,0.),(0.,-.5),(0.,.5)]:
                    images = [render(renderer,source,root/label,root/f'{label}-{tone}-{color}',
                                     tone,color,max_edge=args.max_edge)
                              for label in ('reference','default','joint')]
                    item = {'tone':tone,'color':color,'width':images[0].shape[1],
                            'height':images[0].shape[0],
                            'metrics':{k:blind.score(images[0],a) for k,a in zip(('default','joint'),images[1:])},
                            'linear':spatial(*images),
                            'display_projection':spatial(*(display_projection(x,headroom) for x in images)),
                            'projection_headroom':headroom,
                            'projection_clipped_channel_pct':{k:100*float(np.mean((a<0)|(a>headroom)))
                                for k,a in zip(('reference','default','joint'),images)}}
                    case['edits'].append(item)
                    (args.output/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
                if isolate.sha(source.read_bytes()) != case['source_sha256']:
                    raise ValueError('source changed')
            report['passed'] = bool(report['cases'])
    except (ValueError,RuntimeError,OSError,KeyError,subprocess.TimeoutExpired) as error:
        report['error'] = str(error)
    finally:
        (args.output/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'passed':report['passed'],'cases':len(report['cases']),'error':report.get('error')}))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
