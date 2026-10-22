"""New haze root cases with explicit 8-field haze context and guide211."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import native_neutral_leaves_check as base
from leaf_numeric import V
from pixel_haze import Parameters,forward


def cases(name=None):
    profiles=[[.05,.8,.6,.1,-.1,.5,.1,.1],[.1,.7,.9,-.1,.2,.2,-.1,.15]]
    for rgb in [[.2,.4,.8],[.7,.45,.3],[.4,.4,.4],[0,0,0]]:
        for guide,person in [(.1,.2),(.8,.8)]:
            for fields in profiles:yield np.r_[np.array([*rgb,guide,person],dtype='f2').astype('f4'),np.array(fields,dtype='f4')].astype('f4')
    for fields in [[.05,0,.6,.1,-.1,.5,.1,.1],[.8,.8,.6,.1,-.1,.5,.1,.1]]:yield np.r_[np.array([.2,.4,.8,.4,.5],dtype='f2').astype('f4'),np.array(fields,dtype='f4')].astype('f4')


def model(name,data,point):
    h=lambda x:V.value(x)if point else V.bounds(x,x)
    f=lambda x:V.value(x,'f')if point else V.bounds(x,x,'f')
    return forward(h(data[:3]),h(data[3]),h(data[4]),Parameters(f(data[5:13]),True))


def check(source,output):
    previous=base.cases,base.model
    try:base.cases=cases;base.model=model;r=base.check(source,output,['renderVideoHazeCorrection'])
    finally:base.cases,base.model=previous
    r['declared_case_and_model_provider']={'module':'native_haze_check','only_new_haze_cases':True,'source_sha256':{n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest()for n in ['native_haze_check.py','pixel_haze.py','pixel_remaining.py','bgfg_tone.py']},'explicit_haze_fields':'SSRHazeAdjustment fields1..8','guide_source':'original texture guide211, not mixed guide350'}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.output);print(json.dumps(r['metrics']))
