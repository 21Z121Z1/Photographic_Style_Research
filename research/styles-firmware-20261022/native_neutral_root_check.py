"""New root-only cases through the shared full-original helper host checker."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import native_neutral_leaves_check as base
from leaf_numeric import V
from cast_values import CastValues
from pixel_neutral_root import NeutralStats,forward


def cases(name=None):
    for rgb in [[.2,.4,.8],[.8,.3,.15],[.4,.4,.4],[0,0,0]]:
        for profile in [{27:.2},{27:.2,28:.3},{27:.2,28:.3,29:.2,30:.2}]:
            for use_skin in [False,True]:
                raw=np.zeros(34,dtype='f4')
                for key,value in profile.items():raw[key]=value
                yield np.r_[np.array([*rgb,.7,.4,1,int(use_skin)],dtype='f2').astype('f4'),np.array([.7,.45,.3],dtype='f4'),raw].astype('f4')
    raw=np.zeros(34,dtype='f4');raw[27:31]=.3
    yield np.r_[np.array([.2,.4,.8,.7,.4,0,1],dtype='f2').astype('f4'),np.array([.7,.45,.3],dtype='f4'),raw].astype('f4')


def model(name,data,point):
    h=lambda x:V.value(x)if point else V.bounds(x,x)
    f=lambda x:V.value(x,'f')if point else V.bounds(x,x,'f')
    stats=NeutralStats(*[f(x)for x in data[7:10]])
    return forward(h(data[:3]),enabled=bool(data[5]),cast=CastValues(f(data[10:44])),skin=h(data[3]),person=h(data[4]),use_skin=bool(data[6]),stats=stats)


def check(source,output):
    previous=base.cases,base.model
    try:base.cases=cases;base.model=model;r=base.check(source,output,['renderNeutralizingAdjustments'])
    finally:base.cases,base.model=previous
    r['declared_case_and_model_provider']={'module':'native_neutral_root_check','only_root_cases_executed':True,'source_sha256':{n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest()for n in ['native_neutral_root_check.py','pixel_neutral_root.py','cast_values.py']},'full_cast_fields_required':34,'root_stats_fields':[[2,4],[3,4],[4,4]],'skinWarmth_caller_mode':1}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.output);print(json.dumps(r['metrics']))
