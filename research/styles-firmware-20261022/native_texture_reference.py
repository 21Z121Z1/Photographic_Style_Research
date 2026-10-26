"""Align portable writer output with a specific native UnderEye final stage.

Placement after the writer and all edited images/masks/statistics are synthetic
caller choices. The camera producer, real segmentation and Apple order are not
recovered by this experiment.
"""
from __future__ import annotations

import base64
from dataclasses import asdict, dataclass
from enum import Enum
import hashlib
import json
from pathlib import Path

import numpy as np

from complete_fixture import encode
from image_chain import BranchSelection, Numerics, run
from image_chain_cli import encoded
from image_chain_metrics import compare_rgb
from synthetic_inputs import Pattern, SyntheticSpec, make_context
from texture_style_adapter import (ColorDomain, HalfMask, HalfRGB, TransferDomain,
                                   UnderEyeContext, UnderEyeMasks, UnderEyeParameters, apply_under_eye)

LIBRARY_SHA256 = '16a8a119e3e0ae1649d32b2bbc8ea9136cb757a8d1f3eb451025821901edff11'


class MaskMode(Enum):
    ZERO = 'zero'
    FULL = 'full-support-no-exclusion'
    SPATIAL = 'spatial'


@dataclass(frozen=True)
class NativeCase:
    masks: MaskMode
    brightness_mix: np.float32
    strength: np.float32

    def __post_init__(self):
        if type(self.masks) is not MaskMode:
            raise TypeError('Named synthetic mask mode required')
        UnderEyeParameters(self.brightness_mix, self.strength)


CASES = tuple(NativeCase(mode, np.float32(mix), np.float32(strength)) for mode,mix,strength in (
    (MaskMode.ZERO,1,1), (MaskMode.FULL,0,1), (MaskMode.FULL,.5,1), (MaskMode.FULL,1,1),
    (MaskMode.SPATIAL,0,1), (MaskMode.SPATIAL,.5,1), (MaskMode.SPATIAL,1,1),
    (MaskMode.SPATIAL,1,0), (MaskMode.SPATIAL,1,.5)))
DOMAIN = ColorDomain('ABI-supplied unidentified primaries', TransferDomain.NONLINEAR,
                     'AIR output transfer enum 3 (code3)', 'explicit synthetic post-writer placement')


def blob(array: np.ndarray) -> dict:
    raw = np.asarray(array, dtype='<f2').tobytes()
    return {'dtype':'<f2', 'shape':list(array.shape), 'sha256':hashlib.sha256(raw).hexdigest(),
            'base64':base64.b64encode(raw).decode()}


def unblob(record: dict) -> np.ndarray:
    raw = base64.b64decode(record['base64'], validate=True)
    if record['dtype'] != '<f2' or hashlib.sha256(raw).hexdigest() != record['sha256']:
        raise ValueError('Synthetic half-array identity mismatch')
    return np.frombuffer(raw,dtype='<f2').reshape(record['shape'])


def operands(source: HalfRGB, case: NativeCase) -> UnderEyeContext:
    h,w = source.values.shape[:2]
    y,x = np.mgrid[:h,:w]; u,v = (x+.5)/w,(y+.5)/h
    if case.masks is MaskMode.SPATIAL:
        arrays = {'face':.65+.25*(1-v), 'instance':.85+.1*u, 'hair':.08*v,
                  'lips':.06*(1-u), 'ears':.04*u, 'tattoo':.03*v,
                  'glasses':.02*(1-v), 'blend':.8-.2*v}
    else:
        arrays = {name:np.full((h,w), int(case.masks is MaskMode.FULL and name in ('face','instance','blend')))
                  for name in ('face','instance','hair','lips','ears','tattoo','glasses','blend')}
    masks = UnderEyeMasks(**{name:HalfMask(np.asarray(a,dtype='f2'),'analytic synthetic '+name)
                             for name,a in arrays.items()})
    edited = HalfRGB((source.values.astype('f8')*.95+.035).astype('f2'),source.domain)
    return UnderEyeContext(edited,masks,UnderEyeParameters(case.brightness_mix,case.strength))


def prepare(output: Path) -> tuple[Path, dict]:
    output.mkdir(parents=True,exist_ok=False)
    manifest = {'width':12,'height':8,'cases':[]}
    evidence = {'schema':'psr-aligned-under-eye-inputs-v1','domain':{**asdict(DOMAIN),'transfer':DOMAIN.transfer.value},
                'placement':'after experimental portable writer; Apple order unverified',
                'upstream_native_verified':False, 'segmentation_verified':False,
                'contexts':{},'cases':[]}
    for pattern in (Pattern.GRADIENT,Pattern.EDGES):
        context = make_context(SyntheticSpec(pattern,8,12))
        context_raw = encoded(encode(context))
        result = run(context,numerics=Numerics.EXPERIMENTAL_PORTABLE_POINT,
                     selection=BranchSelection.EXPERIMENTAL_BRIGHT16)
        writer = result.model.writer
        if writer is None:
            raise RuntimeError('Predeclared portable source has no writer: '+pattern.value)
        coordinates = np.argwhere(writer.written_pixels)
        y0,x0 = coordinates.min(axis=0); y1,x1 = coordinates.max(axis=0)+1
        if not writer.written_pixels[y0:y1,x0:x1].all() or int(writer.written_pixels.sum()) != 96:
            raise RuntimeError('Complete aligned 8x12 written ROI required')
        source = HalfRGB(np.asarray(writer.output.pixels.lo[y0:y1,x0:x1,:3],dtype='f2'),DOMAIN)
        evidence['contexts'][pattern.value] = {'context':json.loads(context_raw),
            'context_sha256':hashlib.sha256(context_raw).hexdigest(),
            'written_roi_yxyx':[int(y0),int(x0),int(y1),int(x1)],
            'writer':blob(np.asarray(writer.output.pixels.lo,dtype='f2')),
            'upstream_native_calls':0}
        for i,case in enumerate(CASES):
            name = pattern.value+'-'+str(i)
            operands_context = operands(source,case)
            expected = apply_under_eye(source,operands_context)
            arrays = {n:getattr(operands_context.masks,n).values for n in operands_context.masks.__dict__}
            def rgba(rgb):
                return np.concatenate((rgb,np.ones(rgb.shape[:2]+(1,),dtype='f2')),axis=-1)
            arrays.update(source=rgba(source.values),edited=rgba(operands_context.edited.values))
            files = {}
            for key,a in arrays.items():
                file = name+'-'+key+'.f16'; files[key] = file
                (output/file).write_bytes(np.asarray(a,dtype='<f2').tobytes())
            row = {'name':name, 'pattern':pattern.value, 'mask_mode':case.masks.value,
                   'brightness_mix':float(case.brightness_mix), 'strength':float(case.strength)}
            manifest['cases'].append({**row,'files':files})
            evidence['cases'].append({**row,'inputs':{n:blob(a) for n,a in arrays.items()},
                                      'model_output':blob(expected.output.values)})
    path = output/'manifest.json'; path.write_bytes(encoded(manifest))
    evidence['input_manifest_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    return path,evidence


def compare_native(raw: dict, inputs: dict) -> dict:
    if raw.get('status') != 'native_under_eye_final_mix_completed':
        return {'status':'blocked_or_incomplete','native_error':raw.get('error'),
                'GPU_dispatches':raw.get('GPU_dispatches',0),'accuracy_verified':False}
    if raw.get('library_sha256') != LIBRARY_SHA256 or not raw.get('library_unchanged'):
        raise ValueError('Native library identity changed')
    if raw.get('input_manifest_sha256') != inputs['input_manifest_sha256']:
        raise ValueError('Actual native input manifest differs')
    expected = inputs['cases']; captured = raw['rows']
    probes = raw.get('weight_probe_dispatches',0)
    if probes not in (0,len(expected)) or len(captured) != len(expected) or raw['GPU_dispatches'] != len(expected)+probes:
        raise ValueError('Missing or extra native dispatches')
    if probes:
        for key,value in (('weight_probe_source_sha256',0),('weight_probe_edited_sha256',1)):
            if raw.get(key) != hashlib.sha256(np.full((8,12,4),value,dtype='<f2').tobytes()).hexdigest():
                raise ValueError('Native weight probe inputs differ from 0/1')
    rows = []
    for actual,reference in zip(captured,expected):
        if actual['name'] != reference['name'] or actual['command_status'] != 4:
            raise ValueError('Ordered completed native command required')
        hashes = {name:record['sha256'] for name,record in reference['inputs'].items()}
        if actual['input_sha256'] != hashes:
            raise ValueError('Native kernel received changed input bytes')
        params = np.zeros(13,dtype='<f4'); params[2] = reference['brightness_mix']
        stats = np.zeros(12,dtype='<f4'); stats[3] = reference['strength']
        if actual['params_sha256'] != hashlib.sha256(params.tobytes()).hexdigest() or actual['stats_sha256'] != hashlib.sha256(stats.tobytes()).hexdigest():
            raise ValueError('Native parameter/statistics bytes differ')
        output_bytes = base64.b64decode(actual['output_f16_base64'],validate=True)
        if hashlib.sha256(output_bytes).hexdigest() != actual['output_sha256'] or len(output_bytes) != 8*12*8:
            raise ValueError('Native output byte identity or geometry differs')
        native = np.frombuffer(output_bytes,dtype='<f2').reshape(8,12,4)
        if np.any(native[...,:3] == -99):
            raise ValueError('Unwritten native RGB sentinel remains')
        rows.append({k:reference[k] for k in ('name','pattern','mask_mode','brightness_mix','strength')})
        rows[-1]['native_minus_model'] = compare_rgb(native[...,:3],unblob(reference['model_output'])).record()
        rows[-1]['native_effect_from_input'] = compare_rgb(native,unblob(reference['inputs']['source'])).record()
    return {'status':'aligned_native_final_stage_observed','GPU_dispatches':len(rows)+probes, 'rows':rows,
            'all_observed_RGB_half_bits_match_continuous_model':all(r['native_minus_model']['half_bit_mismatches'] == 0 for r in rows),
            'Apple_capture_order_verified':False,'full_Texture_pipeline_verified':False,
            'real_segmentation_verified':False,'upstream_native_verified':False}


def bit_mismatch_examples(raw: dict, inputs: dict) -> dict:
    """Retain actual bit failures even when all errors are below 1e-3."""
    if raw.get('status') != 'native_under_eye_final_mix_completed':
        return {}
    result = {}
    for actual,reference in zip(raw['rows'],inputs['cases']):
        data=base64.b64decode(actual['output_f16_base64'],validate=True)
        native=np.frombuffer(data,dtype='<f2').reshape(8,12,4)[...,:3]
        model=unblob(reference['model_output'])
        mismatches=np.argwhere(native.view('u2') != model.view('u2'))
        result[actual['name']] = [
            {'y':int(y),'x':int(x),'channel':int(c),
             'native_half_bits':int(native[y,x,c].view('u2')),
             'model_half_bits':int(model[y,x,c].view('u2')),
             'native':float(native[y,x,c]),'model':float(model[y,x,c])}
            for y,x,c in mismatches[:16]]
    return result


def weight_diagnostics(raw: dict, inputs: dict) -> dict:
    """Use native 0/1 observations to locate error, never to feed the main model."""
    if not raw.get('weight_probe_dispatches'):
        return {'status':'not_collected','native_weight_used_by_main_model':False}
    rows=[]
    for actual,reference in zip(raw['rows'],inputs['cases']):
        data=base64.b64decode(actual['weight_f16_base64'],validate=True)
        if hashlib.sha256(data).hexdigest() != actual['weight_sha256'] or len(data) != 8*12*8:
            raise ValueError('Native weight byte identity differs')
        native_weight=np.frombuffer(data,dtype='<f2').reshape(8,12,4)[...,:3]
        if not np.isfinite(native_weight).all() or np.any(native_weight<0) or np.any(native_weight>1) or not np.all(native_weight==native_weight[...,:1]):
            raise ValueError('Invalid native scalar weight observation')
        m={k:unblob(reference['inputs'][k]).astype('f8') for k in ('face','instance','hair','lips','ears','tattoo','glasses','blend')}
        continuous=np.clip((m['face']-(m['lips']+m['ears']+m['tattoo']+m['glasses']+m['hair']))*m['instance'],0,1)*m['blend']*reference['brightness_mix']*reference['strength']
        expected=np.repeat(continuous[...,None],3,axis=-1).astype('f2')
        x=unblob(reference['inputs']['source'])[...,:3].astype('f8')
        e=unblob(reference['inputs']['edited'])[...,:3].astype('f8')
        observed=np.frombuffer(base64.b64decode(actual['output_f16_base64']),dtype='<f2').reshape(8,12,4)[...,:3]
        diagnostic=((e-x)*native_weight.astype('f8')+x).astype('f2')
        rows.append({'name':actual['name'], 'native_weight_minus_continuous_model':compare_rgb(native_weight,expected).record(),
                     'native_image_minus_continuous_mix_with_observed_weight':compare_rgb(observed,diagnostic).record()})
    return {'status':'native_0_1_weight_diagnostics','rows':rows,
            'native_weight_used_by_main_model':False,'sampler_or_compiler_equivalence_proved':False}
