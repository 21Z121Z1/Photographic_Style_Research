"""New warmth root mixed-activation cases; no prior leaf batches repeated."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import native_neutral_leaves_check as base
from leaf_numeric import V
from cast_values import CastValues
from pixel_warmth import forward


def cases(name=None):
    profiles=[{0:.1,2:.1},{1:.1,3:.1},{4:.1,5:.1},{0:.1,1:-.1,2:.1,3:-.1,4:-.1,5:.1}]
    for rgb in [[.2,.4,.8],[.7,.45,.3],[.4,.4,.4],[0,0,0]]:
        for person in [.3,.8]:
            for profile in profiles:
                raw=np.zeros(34,dtype='f4');raw[6:9]=[-.5,1,2.3];raw[9:12]=[200,150,180];raw[12:15]=[.1,.2,.05]
                for key,value in profile.items():raw[key]=value
                yield np.r_[np.array([*rgb,person],dtype='f2').astype('f4'),raw].astype('f4')


def model(name,data,point):
    h=lambda x:V.value(x)if point else V.bounds(x,x)
    f=lambda x:V.value(x,'f')if point else V.bounds(x,x,'f')
    return forward(h(data[:3]),CastValues(f(data[4:38])),h(data[3]))


def check(source,output):
    previous=base.cases,base.model
    try:base.cases=cases;base.model=model;r=base.check(source,output,['renderWarmthCastAdjustments'])
    finally:base.cases,base.model=previous
    r['declared_case_and_model_provider']={'module':'native_warmth_root_check','only_new_warmth_root_cases':True,'source_sha256':{n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest()for n in ['native_warmth_root_check.py','pixel_warmth.py','cast_values.py']},'all_34_cast_fields_supplied':True}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.output);print(json.dumps(r['metrics']))
