"""New extracted outer arithmetic checks, conditional on a supplied BW result."""
import argparse,ctypes,hashlib,json
from pathlib import Path
import numpy as np
import native_neutral_leaves_check as base
from leaf_numeric import V,DomainUnknown
from outer_cast import forward
from outer_cast_host import build as outer_build


def build(source,names):
    ir,metadata=outer_build(source)
    ir+='\ndefine void @psr_leaf_0(ptr %input,ptr %texture,ptr %output){\ncall void @psr_outer(ptr %input,ptr %output)\nret void\n}\n'
    return ir,metadata


def cases(name=None):
    for rgb in [[.2,.4,.8],[.4,.4,.4]]:
        for code in [2,3,4,16]:
            for tuning,parameter2,person in [(2,-.3,.3),(5,.4,.8)]:
                values=np.array([*rgb,.25,.45,.65,person,parameter2,.4,.25,.75,tuning,code,.6,.3,.2],dtype='f4')
                values[:7]=values[:7].astype('f2').astype('f4');values[13:16]=values[13:16].astype('f2').astype('f4');yield values


def result(data,point):
    h=lambda x:V.value(x)if point else V.bounds(x,x)
    f=lambda x:V.value(x,'f')if point else V.bounds(x,x,'f')
    return forward(h(data[:3]),h(data[3:6]),h(data[6]),f(data[7]),f(data[8]),f(data[9]),f(data[10]),tuning_type415=int(data[11]),raw_cast_type245=int(data[12]),bw477=h(data[13:16]))


def model(name,data,point):
    r=result(data,point)
    if r.output492 is None:raise DomainUnknown(str(r.unknowns))
    return r.output492


def check(source,output):
    def observe(lib,name,data,native):
        tonal=np.ctypeslib.as_array((ctypes.c_float*3).in_dll(lib,'psr_outer_tonal')).copy();p=result(data,True).tonal468;b=result(data,False).tonal468
        return {'native_tonal468':tonal.tolist(),'tonal_point_unknown':p is None,'tonal_half_bit_mismatches':None if p is None else int(np.count_nonzero(tonal.astype('f2').view('u2')!=p.lo.astype('f2').view('u2'))),'tonal_max_absolute_error':None if p is None else float(np.max(abs(tonal-p.lo))),'tonal_set_unknown':b is None,'tonal_range_covered':None if b is None else bool(np.all(tonal>=b.lo)and np.all(tonal<=b.hi))}
    previous=base.cases,base.model,base.build
    try:base.cases=cases;base.model=model;base.build=build;r=base.check(source,output,['conditional_outer_cast'],observe_native=observe)
    finally:base.cases,base.model,base.build=previous
    r['original_bodies_modified']='Extracted SSA414..492: BW477 call replaced by explicit input; SSA alpha-renamed; metadata/call attributes removed; arithmetic preserved'
    r['BW_algorithm_verified']=False;r['conditional_on_explicit_BW477']=True
    r['tonal_set_unknown_calls']=sum(result(data,False).tonal468 is None for data in cases())
    r['tonal_metrics']={'calls':len(r['rows']),'point_unknown':sum(x['tonal_point_unknown']for x in r['rows']),'half_bit_mismatches_known':sum(x['tonal_half_bit_mismatches']or 0 for x in r['rows']),'max_absolute_error_known':max((x['tonal_max_absolute_error']for x in r['rows']if x['tonal_max_absolute_error']is not None),default=None),'range_violations_known':sum(x['tonal_range_covered']is False for x in r['rows'])}
    r['declared_case_and_model_provider']={'module':'native_outer_cast_check','no_previous_batches_repeated':True,'source_sha256':{n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest()for n in ['native_outer_cast_check.py','outer_cast.py','outer_cast_host.py']}}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    if r['tonal_metrics']['range_violations_known']:raise AssertionError('Observed tonal468 outside model set; receipt retained')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.output);print(json.dumps({'metrics':r['metrics'],'tonal_metrics':r['tonal_metrics'],'tonal_set_unknown_calls':r['tonal_set_unknown_calls']}))
