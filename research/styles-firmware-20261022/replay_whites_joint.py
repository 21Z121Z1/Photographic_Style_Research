"""Only original S14C case0: product/quotient proof and next actual failure."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from leaf_numeric import V,DomainUnknown
import typed_bgfg
from native_main_pre393_check import fixtures,model
from main_pre393_host import OBSERVATIONS


def encode(v):return {'lo':v.lo.tolist(),'hi':v.hi.tolist(),'max_width':float(np.max(v.hi-v.lo))}if isinstance(v,V)else v


def check(native,output):
    if output.exists():raise FileExistsError(output)
    if hashlib.sha256(native.read_bytes()).hexdigest()!='af5656e829016d0f14d4346ade2ccdd6eb8072cb7686290dcb1c0e704457f573':raise ValueError('Original S14C receipt required')
    names=['shadows','contrast','whites_curve','airy','mids','smooth_sat','local_contrast','gamma_contrast','under_grass','lighten','negative_lighten','rich_sat','tonal_contrast','under_tone','smart_contrast','highlight_neg'];old={n:getattr(typed_bgfg,n)for n in names};rows=[];active=[];olddiv=V.__truediv__
    def divide(a,b):
        try:return olddiv(a,b)
        except DomainUnknown as e:
            if active:active[-1].setdefault('division_failures',[]).append({'numerator':encode(a),'denominator':encode(a.box(b)),'reason':str(e)})
            raise
    def wrapper(name,fn):
        def run(*args,**kwargs):
            row={'leaf':name,'input':encode(args[0]),'other_numeric_inputs':[encode(a)for a in args[1:]if isinstance(a,V)]};rows.append(row);obs={};active.append(row)
            try:
                result=fn(*args,**kwargs,observations=obs)if name=='whites_curve'else fn(*args,**kwargs);row.update(status='known',output=encode(result));return result
            except DomainUnknown as e:row.update(status='unknown',reason=str(e));raise
            finally:
                if obs:row['whites_observations']={k:encode(v)for k,v in obs.items()}
                active.pop()
        return run
    for n,fn in old.items():setattr(typed_bgfg,n,wrapper(n,fn))
    V.__truediv__=divide
    try:r=model(next(fixtures()),False)
    finally:
        for n,fn in old.items():setattr(typed_bgfg,n,fn)
        V.__truediv__=olddiv
    saved=json.loads(native.read_text());actual=np.array(next(v for v in saved['rows']if v['case']==0)['native_output_half_bits'],dtype='u2').view('f2');offset=0;coverage={}
    for name,ssa,count in OBSERVATIONS:
        target=actual[offset:offset+count];offset+=count
        if name in r.observations:
            v=r.observations[name];coverage[name]={'covered':bool(np.all(target>=v.lo)and np.all(target<=v.hi)),**encode(v)}
    out={'scope':__doc__,'native_receipt_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'new_original_host_calls':0,'leaf_trace':rows,'unknown_stage':r.unknown_operator,'unknown_reason':r.unknown_reason,'first_unhandled_leaf':next((v for v in rows if v['status']=='unknown'),None),'known_prefix_coverage':coverage,'BG352_conditional_set_produced':'BG352'in r.observations,'FG354_conditional_set_produced':'FG354'in r.observations,'pre393_conditional_set_complete':r.unknown_operator is None,'complete_BG_runtime_verified':False,'GPU_verified':False};output.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print(json.dumps({'sequence':[(v['leaf'],v['status'],v.get('output',{}).get('max_width'))for v in rows],'unknown_stage':r.unknown_operator,'unknown_reason':r.unknown_reason}))
    if any(not v['covered']for v in coverage.values()):raise AssertionError('Known range excludes original S14C observation')
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('native',type=Path);p.add_argument('output',type=Path);a=p.parse_args();check(a.native,a.output)
