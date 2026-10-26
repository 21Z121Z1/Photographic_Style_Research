"""Reproducible synthetic source-to-writer and raw-parameter effect experiment.

Explicit experimental math is required on Linux. This CLI records model-only
outputs, unknowns and unselected errors; it does not run Apple code or certify
segmentation, Texture Styles placement, UI endpoints, or photographic accuracy.
"""
from __future__ import annotations
import argparse
from dataclasses import asdict
from enum import Enum
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import traceback
import numpy as np
from active_color import Color,replace_color
from complete_fixture import encode
from image_chain import BranchSelection,Numerics,SemanticMasks,run
from image_chain_metrics import compare_rgb
from synthetic_inputs import Pattern,MaskPattern,SyntheticSpec,make_context,describe

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]


def json_value(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,Enum):return x.value
    if isinstance(x,Path):return str(x)
    raise TypeError(type(x).__name__)


def encoded(value):
    return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False,default=json_value)+'\n').encode()


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def source_manifest():
    # Include the existing guided implementation imported from another directory
    # and all cross-imported semantic sources, not just this command's entry file.
    files=sorted({*ROOT.glob('*.py'),*(ROOT/'native-reference').glob('*.c'),
                  *(ROOT/'native-reference').glob('*.m'),*(ROOT.parent/'semantic-styles').glob('*.py'),
                  ROOT.parent/'hdr-native/guided_reference_v3.py'})
    return {str(p.relative_to(REPO)):sha(p) for p in files if p.is_file()}


def git_identity():
    def git(*args):
        p=subprocess.run(['git','-C',str(REPO),*args],text=True,capture_output=True,check=False)
        return p.stdout.strip() if p.returncode==0 else None
    return {'HEAD':git('rev-parse','HEAD'),'branch':git('branch','--show-current'),
            'worktree_status':git('status','--short'),
            'identity_note':'source hashes bind the executed worktree; a dirty tree does not inherit HEAD validation'}


def preview(path,array):
    """Direct clipped code-value PNG, deliberately without an ICC/color claim."""
    from PIL import Image
    a=np.asarray(array)[...,:3]
    if not np.isfinite(a).all():raise ValueError('Nonfinite preview refused')
    rgb=np.rint(np.clip(a,0,1)*255).astype('u1')
    Image.fromarray(rgb).resize((rgb.shape[1]*12,rgb.shape[0]*12),Image.Resampling.NEAREST).save(path)


def checkpoint_archive(path,result):
    arrays={};records=[]
    for cp in result.checkpoints:
        dtype='f2' if cp.value.precision=='h' else 'f4'
        arrays[cp.name+'__lo']=np.asarray(cp.value.lo,dtype=dtype)
        arrays[cp.name+'__hi']=np.asarray(cp.value.hi,dtype=dtype)
        records.append({'name':cp.name,'precision':cp.value.precision,'shape':list(cp.value.lo.shape),
                        'point':cp.value.point,'domain':cp.domain,'inputs':cp.inputs})
    if result.model.writer is not None:
        arrays['writer__written_mask']=result.model.writer.written_pixels
    np.savez_compressed(path,**arrays)
    return records


def execute(output:Path,*,patterns:tuple[Pattern,...],height:int,width:int,
            mask_pattern:MaskPattern,missing_masks:tuple[str,...],values:tuple[np.float32,...],
            numerics:Numerics,selection:BranchSelection,threshold:float,command:tuple[str,...]=()):
    """Persist source/input/checkpoint hashes and parameter deltas in a new dir."""
    if output.exists():raise FileExistsError('Output must be a new directory: '+str(output))
    if not patterns or not values:raise ValueError('At least one scene and raw control value required')
    if any(type(v)is not np.float32 or not np.isfinite(v)or not 0<=v<=1 for v in values):
        raise TypeError('Explicit finite raw internal color f32 values in[0,1] required')
    if not np.isfinite(threshold) or threshold<0:raise ValueError('Finite nonnegative diagnostic threshold required')
    if any(n not in ('person','skin','sky')for n in missing_masks):raise ValueError('Only named semantic masks may be omitted')
    specs=tuple(SyntheticSpec(p,height,width,mask_pattern)for p in patterns)
    # Validate configurations before creating any artifact directory.
    before=source_manifest();identity=git_identity();output.mkdir(parents=True)
    rows=[];deltas=[];started=time.perf_counter()
    for spec in specs:
        base=make_context(spec);reference=None
        for index,value in enumerate(values):
            case=output/(spec.pattern.value+'-'+str(index));case.mkdir()
            c=replace_color(base,Color(value));raw=encoded(encode(c));(case/'context.json').write_bytes(raw)
            input_sha=hashlib.sha256(raw).hexdigest()
            request={'input_context_sha256':input_sha,'numerics':numerics.value,'selection':selection.value,
                     'missing_masks':missing_masks,'context_json_is_before_declared_overrides':True,
                     'effective_raw_arrays_hash_in_result':'provenance.raw_input_sha256',
                     'point':True,'reference_kind':'none; parameter effect only'}
            request_raw=encoded(request);(case/'run-request.json').write_bytes(request_raw)
            request_sha=hashlib.sha256(request_raw).hexdigest()
            record={'id':case.name,'spec':describe(spec),'raw_field3':Color(value).record(),
                    'input_context_sha256':input_sha,'input_request_sha256':request_sha,'run_request':request,'evidence_level':'model_only',
                    'native_reference_compared':False,'Apple_accuracy_validated':False}
            masks=None
            if missing_masks:
                masks=SemanticMasks(**{name:None if name in missing_masks else c.images[i]
                                      for name,i in [('person',6),('skin',7),('sky',8)]})
            t=time.perf_counter()
            try:
                result=run(c,numerics=numerics,selection=selection,masks=masks)
                record.update(status=result.status,evidence_level=result.evidence_level,
                              branches=[asdict(b)for b in result.branches],provenance=result.provenance,
                              gaps=result.gaps,pixel_unknowns=result.model.pixel_unknowns,
                              internal_unknowns=result.model.internal_unknowns,
                              checkpoints=checkpoint_archive(case/'checkpoints.npz',result))
                if result.model.writer is not None:
                    pixels=result.model.writer.output.pixels.lo.astype('f2')
                    written=result.model.writer.written_pixels
                    preview(case/'writer-diagnostic.png',pixels)
                    record['writer_sha256']=hashlib.sha256(pixels.tobytes()).hexdigest()
                    record['written_pixels']=int(written.sum())
                    if reference is None:
                        reference=(record['id'],input_sha,pixels,written,request_sha)
                    else:
                        common=written & reference[3]
                        if common.any():
                            deltas.append({'scene':spec.pattern.value,'reference_case':reference[0],
                                           'actual_case':record['id'],'reference_input_sha256':reference[1],
                                           'actual_input_sha256':input_sha,'reference_request_sha256':reference[4],
                                           'actual_request_sha256':request_sha,'comparison_kind':'raw parameter effect; not accuracy',
                                           'threshold':threshold,'metric':compare_rgb(pixels,reference[2],pixel_mask=common,threshold=threshold).record()})
                preview(case/'source-diagnostic.png',c.images[0])
            except (ValueError,TypeError,RuntimeError) as exc:
                record.update(status='blocked_or_unknown',error_type=type(exc).__name__,error=str(exc))
                (case/'error.log').write_text(traceback.format_exc())
            record['elapsed_seconds']=time.perf_counter()-t
            record['files_sha256']={p.name:sha(p)for p in sorted(case.iterdir())if p.is_file()}
            (case/'result.json').write_bytes(encoded(record));rows.append(record)
    after=source_manifest()
    changes=sorted(k for k in before.keys()|after.keys()if before.get(k)!=after.get(k))
    report={'scope':__doc__,'command':command,'git':identity,
            'runtime':{'system':platform.system(),'machine':platform.machine(),'release':platform.release(),
                       'python':sys.version,'numpy':np.__version__},
            'numerics':numerics.value,'selection':selection.value,'missing_masks':missing_masks,
            'preview_contract':'12x nearest-neighbor, clamp raw output code values to[0,1], 8-bit diagnostic PNG; no ICC/ACES/color accuracy claim',
            'raw_control_contract':'SSRParams.color field3 byte12 f32; no UI mapping; [0,1] means model field range, not Apple UI endpoints',
            'source_sha256_before':before,'source_sha256_after':after,
            'source_changes_during_run':changes,'source_snapshot_stable':not changes,
            'evidence_level':'model_only','native_calls':0,'GPU_calls':0,'Apple_pipeline_verified':False,
            'elapsed_seconds':time.perf_counter()-started,'runs':rows,'parameter_effects':deltas,
            'summary':{'cases':len(rows),'writers':sum('writer_sha256'in r for r in rows),
                       'blocked_or_unknown':sum(r['status']!='model_source_to_writer_complete'for r in rows),
                       'internal_unknown_cases':sum(bool(r.get('internal_unknowns'))for r in rows),
                       'parameter_comparisons':len(deltas)},
            'status':('model_diagnostics_with_unknowns' if any(r['status']!='model_source_to_writer_complete'for r in rows)
                      else 'model_diagnostic_outputs') if not changes else 'source_changed_unbound_results'}
    (output/'summary.json').write_bytes(encoded(report))
    return report


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--patterns',nargs='+',choices=[v.value for v in Pattern],default=['gradient','exposure','colors','edges'])
    p.add_argument('--height',type=int,default=8);p.add_argument('--width',type=int,default=12)
    p.add_argument('--mask-pattern',choices=[v.value for v in MaskPattern],default='spatial')
    p.add_argument('--missing-masks',nargs='+',choices=['person','skin','sky'],default=[])
    p.add_argument('--values',type=float,nargs='+',default=[0,.125,.375,1])
    p.add_argument('--numerics',choices=['strict-host','experimental-portable'],required=True)
    p.add_argument('--selection',choices=['context','experimental-bright16'],default='context')
    p.add_argument('--threshold',type=float,default=1e-3)
    a=p.parse_args(argv)
    result=execute(a.output,patterns=tuple(Pattern(x)for x in a.patterns),height=a.height,width=a.width,
                   mask_pattern=MaskPattern(a.mask_pattern),missing_masks=tuple(a.missing_masks),
                   values=tuple(np.float32(v)for v in a.values),
                   numerics=Numerics.STRICT_HOST_POINT if a.numerics=='strict-host'else Numerics.EXPERIMENTAL_PORTABLE_POINT,
                   selection=BranchSelection.CONTEXT if a.selection=='context'else BranchSelection.EXPERIMENTAL_BRIGHT16,
                   threshold=a.threshold,command=tuple(sys.argv if argv is None else argv))
    print(json.dumps({'status':result['status'],'evidence_level':'model_only',**result['summary'],
                      'summary':str(a.output/'summary.json')}))
    return 3 if not result['source_snapshot_stable'] else 2 if result['summary']['blocked_or_unknown'] else 0


if __name__=='__main__':raise SystemExit(main())
