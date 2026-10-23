"""Isolated GTM/LTM/semantic/bright/Texture parameter effects in a supplied model.

Every case recomputes source -> producer -> guided -> consumer -> writer. The
optional UnderEye experiment follows the writer only because this caller asks
for that placement; neither Apple placement nor a full Texture chain is proved.
Unknown domains are retained. This command never executes target Apple code.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
from enum import Enum
import hashlib
import json
from pathlib import Path
import platform
import sys
import time
import traceback

import numpy as np

from complete_fixture import encode
from complete_forward import Context
from image_chain import BranchSelection, ImageChainResult, Numerics, run
from image_chain_cli import encoded, git_identity, sha, source_manifest
from image_chain_metrics import compare_rgb
from semantic_tone import Curve1D
from synthetic_inputs import MaskPattern, Pattern, SyntheticSpec, describe, make_context
from texture_style_adapter import (ColorDomain, HalfMask, HalfRGB, TransferDomain,
                                   UnderEyeContext, UnderEyeMasks, UnderEyeParameters,
                                   apply_under_eye)


class Intervention(Enum):
    BASELINE = 'baseline'
    GTC_IDENTITY = 'gtc-identity'
    GTC_WEIGHT_ZERO = 'gtc-weight-0'
    GTC_WEIGHT_ONE = 'gtc-weight-1'
    LTM_BG_NEUTRAL = 'ltm-bg-neutral'
    LTM_FG_NEUTRAL = 'ltm-fg-neutral'
    SKIN_THETA9 = 'skin-theta9-025'
    SKIN_THETA10 = 'skin-theta10-025'
    BRIGHT_EXPOSURE_ZERO = 'bright-exposure-0'
    BRIGHT_EXPOSURE_ONE = 'bright-exposure-1'
    PERSON_ZERO = 'person-mask-zero'
    SKIN_ZERO = 'skin-mask-zero'
    UNDER_EYE_ZERO = 'under-eye-0'
    UNDER_EYE_HALF = 'under-eye-05'
    UNDER_EYE_ONE = 'under-eye-1'


@dataclass(frozen=True)
class RawChange:
    path: str
    changed_components: int
    before_sha256: str
    after_sha256: str
    before_f32_bits: int | None = None
    after_f32_bits: int | None = None
    meaning: str = ''


@dataclass(frozen=True)
class AppliedIntervention:
    context: Context
    intervention: Intervention
    changes: tuple[RawChange, ...]
    permitted_paths: tuple[str, ...]
    texture_strength: np.float32 | None = None


PARAMETER_EDITS = {
    Intervention.GTC_WEIGHT_ZERO: (159, np.float32(0), 'AIR7 supplied GTC mix semantic7[4]; not a UI slider'),
    Intervention.GTC_WEIGHT_ONE: (159, np.float32(1), 'AIR7 supplied GTC mix semantic7[4]; not a UI slider'),
    Intervention.LTM_BG_NEUTRAL: (155, np.float32(1), 'semantic7[0] BG gain ratio -> 1; conditional LTM neutral mix'),
    Intervention.LTM_FG_NEUTRAL: (156, np.float32(1), 'semantic7[1] FG gain ratio -> 1; conditional LTM neutral mix'),
    Intervention.SKIN_THETA9: (148, np.float32(.25), 'FG theta9 supplied skin color coefficient; not a derived Tone setting'),
    Intervention.SKIN_THETA10: (149, np.float32(.25), 'FG theta10 supplied skin brightness coefficient; not a derived Tone setting'),
    Intervention.BRIGHT_EXPOSURE_ZERO: (7, np.float32(0), 'raw exposure399 input; zero may produce a selected unknown domain'),
    Intervention.BRIGHT_EXPOSURE_ONE: (7, np.float32(1), 'raw exposure399 input; not a camera EV calibration'),
}
TEXTURE_STRENGTHS = {Intervention.UNDER_EYE_ZERO: np.float32(0),
                     Intervention.UNDER_EYE_HALF: np.float32(.5),
                     Intervention.UNDER_EYE_ONE: np.float32(1)}


def _digest(a: np.ndarray) -> str:
    return hashlib.sha256(a.dtype.str.encode()+str(a.shape).encode()+a.tobytes()).hexdigest()


def _context_arrays(c: Context) -> dict[str, np.ndarray]:
    result = {f'images[{i}]': a for i, a in enumerate(c.images)}
    result.update({name: getattr(c, name) for name in ('management', 'stats', 'roi', 'srl', 'output_initial')})
    result.update({f'params[{i}]': c.params[i:i+1] for i in range(len(c.params))})
    result['gtc.red_samples'] = np.asarray(c.gtc.red_samples, dtype='f2')
    result['whites.red_samples'] = np.asarray(c.whites.red_samples, dtype='f2')
    return result


def _context_contract(c: Context) -> tuple:
    return (c.gtc.coordinate_space, c.whites.coordinate_space, c.producer_shape,
            int(np.asarray(c.epsilon).view('u4')), c.version, c.hardware, c.build)


def apply(context: Context, intervention: Intervention) -> AppliedIntervention:
    """Change only the declared raw ABI field, curve, mask or post-writer strength."""
    if not isinstance(context, Context) or type(intervention) is not Intervention:
        raise TypeError('Validated raw Context and an exact Intervention enum required')
    result = context; permitted: tuple[str, ...] = (); meaning = ''
    if intervention in PARAMETER_EDITS:
        index, value, meaning = PARAMETER_EDITS[intervention]
        p = context.params.copy(); p[index] = value
        result = replace(context, params=p); permitted = (f'params[{index}]',)
    elif intervention is Intervention.GTC_IDENTITY:
        result = replace(context, gtc=Curve1D(tuple(np.linspace(0, 1, len(context.gtc.red_samples))),
                                            context.gtc.coordinate_space))
        permitted = ('gtc.red_samples',); meaning = 'Identity table at the same supplied GTC coordinate and sample count'
    elif intervention in (Intervention.PERSON_ZERO, Intervention.SKIN_ZERO):
        index = 6 if intervention is Intervention.PERSON_ZERO else 7
        images = list(context.images); images[index] = np.zeros_like(images[index])
        result = replace(context, images=tuple(images)); permitted = (f'images[{index}]',)
        meaning = 'Program-supplied zero semantic weight; not a segmentation result or native nil-texture claim'
    elif intervention not in (Intervention.BASELINE, *TEXTURE_STRENGTHS):
        raise ValueError('Unknown intervention; no generic arbitrary buffer patching')
    before = _context_arrays(context); after = _context_arrays(result)
    if _context_contract(context) != _context_contract(result) or before.keys() != after.keys():
        raise RuntimeError('Intervention changed an undeclared raw input contract')
    changes = []
    for path in before:
        a, b = before[path], after[path]
        if a.shape != b.shape or a.dtype != b.dtype:
            raise RuntimeError('Intervention changed storage layout: '+path)
        if a.tobytes() == b.tobytes():
            continue
        if path not in permitted:
            raise RuntimeError('Intervention changed an undeclared input: '+path)
        scalar_f32 = a.shape == (1,) and a.dtype == np.dtype('f4')
        byte_mask = np.frombuffer(a.tobytes(), dtype='u1') != np.frombuffer(b.tobytes(), dtype='u1')
        count = int(np.count_nonzero(byte_mask.reshape(a.size, a.itemsize).any(axis=1)))
        changes.append(RawChange(path, count, _digest(a), _digest(b),
                                 int(a.view('u4')[0]) if scalar_f32 else None,
                                 int(b.view('u4')[0]) if scalar_f32 else None, meaning))
    return AppliedIntervention(result, intervention, tuple(changes), permitted,
                               TEXTURE_STRENGTHS.get(intervention))


def stage_difference(actual: np.ndarray, reference: np.ndarray, *, precision: str,
                     reference_name: str) -> dict:
    """Aligned per-component diagnostics for RGB, scalar masks and internal arrays."""
    a, b = np.asarray(actual), np.asarray(reference)
    if a.shape != b.shape or not a.size or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError('Finite nonempty aligned stage arrays required')
    if precision not in ('h', 'f', 'float64'):
        raise TypeError('Named half/f32/float64 stage precision required')
    error = np.abs(a.astype('f8')-b.astype('f8'))
    edges = (0, 1e-6, 1e-4, 1e-3, .01, .1, np.inf)
    dtype, bits = {'h': ('f2', 'u2'), 'f': ('f4', 'u4'), 'float64': ('f8', 'u8')}[precision]
    return {'status': 'compared', 'shape': list(a.shape), 'precision': precision,
            'reference': reference_name, 'components': int(a.size),
            'max_absolute_error': float(error.max()), 'rmse': float(np.sqrt(np.mean(error**2))),
            'mean_absolute_error': float(error.mean()),
            'storage_bit_mismatches': int(np.count_nonzero(a.astype(dtype).view(bits) != b.astype(dtype).view(bits))),
            'absolute_error_percentiles': {str(p): float(np.percentile(error, p)) for p in (0, 50, 90, 95, 99, 100)},
            'histogram': [{'lower_inclusive': float(lo), 'upper_exclusive': float(hi) if np.isfinite(hi) else None,
                           'count': int(np.count_nonzero((error >= lo) & (error < hi)))}
                          for lo, hi in zip(edges, edges[1:])]}


def _stage_comparisons(result: ImageChainResult, baseline: ImageChainResult) -> dict:
    current = {c.name: c for c in result.checkpoints}; base = {c.name: c for c in baseline.checkpoints}
    rows = {}
    for name in sorted(current.keys() | base.keys()):
        if name not in current or name not in base:
            rows[name] = {'status': 'actual_checkpoint_unavailable' if name not in current else 'baseline_checkpoint_unavailable'}
        else:
            rows[name] = stage_difference(current[name].value.lo, base[name].value.lo,
                                          precision=current[name].value.precision,
                                          reference_name='baseline.'+name)
    return rows


def under_eye_after_writer(result: ImageChainResult, *, strength: np.float32,
                          supplied_output_transfer_code: int):
    """Explicit caller-selected post-writer diagnostic with eight synthetic masks.

    Only the active rectangular written region is used; sentinel border storage
    never becomes Texture input. The edited image is an analytic test operand.
    """
    if type(strength) is not np.float32 or not np.isfinite(strength) or not 0 <= strength <= 1:
        raise TypeError('Explicit finite f32 UnderEye strength in [0,1] required')
    if type(supplied_output_transfer_code) is not int or supplied_output_transfer_code != 3:
        raise ValueError('This experiment requires explicitly supplied output transfer enum 3')
    if result.model.writer is None:
        raise ValueError('UnderEye requires a completed source-to-writer model, no injected writer')
    writer = result.model.writer; written = writer.written_pixels
    coordinates = np.argwhere(written)
    if not len(coordinates):
        raise ValueError('No written RGB is available for the Texture diagnostic')
    y0, x0 = coordinates.min(axis=0); y1, x1 = coordinates.max(axis=0)+1
    if not written[y0:y1, x0:x1].all() or int(written.sum()) != (y1-y0)*(x1-x0):
        raise ValueError('This synthetic placement adapter requires one rectangular written ROI')
    domain = ColorDomain('unidentified primaries supplied by ABI; no P3/sRGB assertion',
                         TransferDomain.NONLINEAR, 'AIR output transfer enum 3 (code3)',
                         'caller-selected post-writer experiment; Apple placement unverified')
    values = np.asarray(writer.output.pixels.lo[y0:y1, x0:x1, :3], dtype='f2')
    source = HalfRGB(values, domain)
    edited_values = (values.astype('f8')*.95 + .035).astype('f2')
    edited = HalfRGB(edited_values, domain)
    h, w = values.shape[:2]; y, x = np.mgrid[:h, :w]
    u, v = (x+.5)/w, (y+.5)/h
    operands = {'face': .65+.25*(1-v), 'instance': .85+.1*u, 'hair': .08*v,
                'lips': .06*(1-u), 'ears': .04*u, 'tattoo': .03*v,
                'glasses': .02*(1-v), 'blend': .8-.2*v}
    masks = UnderEyeMasks(**{name: HalfMask(np.asarray(a, dtype='f2'),
                                          'analytic synthetic '+name+' field; no real segmentation')
                             for name, a in operands.items()})
    context = UnderEyeContext(edited, masks, UnderEyeParameters(np.float32(.5), strength))
    texture = apply_under_eye(source, context)
    final = np.asarray(writer.output.pixels.lo, dtype='f2').copy()
    final[y0:y1, x0:x1, :3] = texture.output.values
    arrays = {c.name: c.values for c in texture.checkpoints}
    comparisons = {c.name: stage_difference(c.values,
                                            np.zeros_like(c.values) if c.name == 'weight' else source.values,
                                            precision='float64' if c.values.dtype == np.dtype('f8') else 'h',
                                            reference_name='explicit zero-intensity weight' if c.name == 'weight' else 'same-case pre-Texture writer RGB')
                   for c in texture.checkpoints}
    return final, {'placement': 'caller-selected after completed writer; not established Apple order',
                   'apple_order_verified': False, 'full_texture_pipeline_verified': False,
                   'source_domain': asdict(domain), 'written_roi_yxyx': [int(y0), int(x0), int(y1), int(x1)],
                   'brightness_mix_f32_bits': int(np.float32(.5).view('u4')),
                   'strength_f32_bits': int(strength.view('u4')),
                   'edited_formula': 'half(float64(source_writer_RGB)*.95+.035); synthetic external edit, no skin-edit producer claim',
                   'edited_sha256': _digest(edited.values),
                   'mask_sha256': {name: _digest(getattr(masks, name).values) for name in operands},
                   'checkpoint_differences': comparisons,
                   'texture_result_model_only': texture.model_only,
                   'native_half_or_sampler_verified': texture.native_half_or_sampler_verified}, arrays


def execute(output: Path, *, spec: SyntheticSpec,
            numerics: Numerics, selection: BranchSelection,
            interventions: tuple[Intervention, ...] = tuple(Intervention),
            command: tuple[str, ...] = ()) -> dict:
    """Write one auditable sensitivity experiment; existing output is never replaced."""
    if type(spec) is not SyntheticSpec or spec.pattern is not Pattern.GRADIENT:
        raise TypeError('The isolated experiment requires a typed synthetic gradient specification')
    if numerics is not Numerics.EXPERIMENTAL_PORTABLE_POINT or type(selection) is not BranchSelection:
        raise TypeError('Explicit experimental portable numerics and branch selection required')
    if type(interventions) is not tuple or not interventions or any(type(x) is not Intervention for x in interventions):
        raise TypeError('Nonempty tuple of exact intervention enums required')
    if len(set(interventions)) != len(interventions):
        raise ValueError('Duplicate interventions would conceal model-call costs')
    if output.exists():
        raise FileExistsError(output)
    cases = (Intervention.BASELINE,) + tuple(i for i in interventions if i is not Intervention.BASELINE)
    source_before = source_manifest(); git = git_identity(); output.mkdir(parents=True)
    original = make_context(spec); original_bytes = encoded(encode(original))
    original_sha = hashlib.sha256(original_bytes).hexdigest()
    (output/'baseline-context.json').write_bytes(original_bytes)
    baseline = None; rows = []; model_calls = 0; texture_calls = 0; started = time.perf_counter()
    for intervention in cases:
        case_dir = output/intervention.value; case_dir.mkdir()
        changed = apply(original, intervention)
        raw = encoded(encode(changed.context)); (case_dir/'context.json').write_bytes(raw)
        row = {'intervention': intervention.value, 'raw_changes': [asdict(c) for c in changed.changes],
               'permitted_raw_paths': list(changed.permitted_paths), 'only_declared_inputs_changed': True,
               'input_context_sha256': hashlib.sha256(raw).hexdigest(),
               'baseline_input_context_sha256': original_sha,
               'post_writer_texture_strength_f32_bits': int(changed.texture_strength.view('u4')) if changed.texture_strength is not None else None,
               'source_to_writer_model_calls': 1, 'texture_model_calls': 0,
               'target_Apple_native_calls': 0, 'GPU_calls': 0, 'evidence_level': 'model_only'}
        t = time.perf_counter(); model_calls += 1
        try:
            result = run(changed.context, numerics=numerics, selection=selection)
            if intervention is Intervention.BASELINE:
                baseline = result
            row.update(status=result.status, pixel_unknowns=result.model.pixel_unknowns,
                       internal_unknowns=result.model.internal_unknowns, gaps=result.gaps,
                       provenance=result.provenance, branches=[asdict(b) for b in result.branches],
                       stage_differences=_stage_comparisons(result, baseline) if baseline is not None else
                       {c.name: {'status': 'baseline_checkpoint_unavailable'} for c in result.checkpoints})
            arrays = {c.name+'__point': np.asarray(c.value.lo, dtype='f2' if c.value.precision == 'h' else 'f4')
                      for c in result.checkpoints}
            if result.model.writer is not None:
                final = np.asarray(result.model.writer.output.pixels.lo, dtype='f2')
                arrays['written_pixels'] = result.model.writer.written_pixels
                if changed.texture_strength is not None:
                    texture_calls += 1; row['texture_model_calls'] = 1
                    final, row['texture'], texture_arrays = under_eye_after_writer(
                        result, strength=changed.texture_strength,
                        supplied_output_transfer_code=int(changed.context.management.view('u4')[60]))
                    arrays.update({'texture.'+name: a for name, a in texture_arrays.items()})
                arrays['final_image'] = final
                row['final_image_sha256'] = _digest(final)
                if baseline is not None and baseline.model.writer is not None:
                    common = result.model.writer.written_pixels & baseline.model.writer.written_pixels
                    row['final_image_difference'] = {'comparison_kind': 'isolated raw/module parameter effect; not Apple accuracy',
                                                     **compare_rgb(final, baseline.model.writer.output.pixels.lo,
                                                                   pixel_mask=common).record()}
            else:
                row['final_image_difference'] = {'status': 'unavailable; selected upstream unknown preserved'}
            np.savez_compressed(case_dir/'checkpoints.npz', **arrays)
        except (ValueError, TypeError, RuntimeError, FloatingPointError) as exc:
            row.update(status='blocked_or_unknown', error_type=type(exc).__name__, error=str(exc))
            (case_dir/'error.log').write_text(traceback.format_exc())
        row['elapsed_seconds'] = time.perf_counter()-t
        row['files_sha256'] = {p.name: sha(p) for p in sorted(case_dir.iterdir()) if p.is_file()}
        (case_dir/'result.json').write_bytes(encoded(row)); rows.append(row)
    after = source_manifest()
    source_changes = sorted(p for p in source_before.keys() | after.keys() if source_before.get(p) != after.get(p))
    report = {'scope': __doc__, 'command': command, 'git': git, 'spec': describe(spec),
              'runtime': {'system': platform.system(), 'machine': platform.machine(), 'release': platform.release(),
                          'python': sys.version, 'numpy': np.__version__},
              'numerics': numerics.value, 'selection': selection.value,
              'baseline_context_sha256': original_sha,
              'source_sha256_before': source_before, 'source_sha256_after': after,
              'source_changes_during_run': source_changes, 'source_snapshot_stable': not source_changes,
              'source_to_writer_model_calls': model_calls, 'texture_model_calls': texture_calls,
              'target_Apple_native_calls': 0, 'GPU_calls': 0,
              'evidence_level': 'model_only', 'Apple_pipeline_verified': False,
              'Apple_Texture_placement_verified': False,
              'numeric_contract': 'Existing half/f32 V model plus explicit generic code3 NumPy output transfer; no target powf substitute certification',
              'parameter_contract': 'Raw ABI edits and supplied curves/masks; coefficients are not regenerated from UI controls or original frame stats',
              'cost_contract': 'Every listed case recomputes the source model once, including Texture cases; Texture adds one conditional continuous-model application',
              'status': 'model_sensitivity_observed' if not source_changes else 'source_changed_unbound_results',
              'elapsed_seconds': time.perf_counter()-started,
              'summary': {'cases': len(rows), 'completed_writers': sum('final_image_sha256' in r for r in rows),
                          'blocked_or_unknown': sum(r['status'] != 'model_source_to_writer_complete' for r in rows)},
              'runs': rows}
    (output/'summary.json').write_bytes(encoded(report))
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--height', type=int, default=8); parser.add_argument('--width', type=int, default=12)
    parser.add_argument('--mask-pattern', choices=[x.value for x in MaskPattern], default='spatial')
    parser.add_argument('--numerics', choices=['experimental-portable'], required=True)
    parser.add_argument('--selection', choices=['context', 'experimental-bright16'], required=True)
    parser.add_argument('--cases', nargs='+', choices=[x.value for x in Intervention], default=[x.value for x in Intervention])
    args = parser.parse_args(argv)
    report = execute(args.output,
                     spec=SyntheticSpec(Pattern.GRADIENT, args.height, args.width, MaskPattern(args.mask_pattern)),
                     numerics=Numerics.EXPERIMENTAL_PORTABLE_POINT,
                     selection=BranchSelection.CONTEXT if args.selection == 'context' else BranchSelection.EXPERIMENTAL_BRIGHT16,
                     interventions=tuple(Intervention(x) for x in args.cases),
                     command=tuple(sys.argv if argv is None else argv))
    print(json.dumps({'status': report['status'], **report['summary'],
                      'source_to_writer_model_calls': report['source_to_writer_model_calls'],
                      'texture_model_calls': report['texture_model_calls'],
                      'evidence_level': 'model_only', 'summary': str(args.output/'summary.json')}))
    return 3 if not report['source_snapshot_stable'] else 2 if report['summary']['blocked_or_unknown'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
