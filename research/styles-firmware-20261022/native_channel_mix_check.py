"""New channel-mix567 root cases, with explicit tone and stats inputs."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import native_neutral_leaves_check as base
from leaf_numeric import V
from pixel_channel_mix import forward
from pixel_neutral_root import NeutralStats


def cases(name=None):
    for rgb in [[.2,.4,.8],[.7,.45,.3],[.4,.4,.4],[0,0,0]]:
        for cast in [0,4,15]:
            for person,stats in [(.2,[.6,.4,.2]),(.8,[.4,.4,.4])]:
                yield np.r_[np.array([*rgb,person],dtype='f2').astype('f4'),cast,np.array([.3,.6,.1,*stats],dtype='f4')].astype('f4')


def model(name,data,point):
    h=lambda x:V.value(x)if point else V.bounds(x,x)
    f=lambda x:V.value(x,'f')if point else V.bounds(x,x,'f')
    return forward(h(data[:3]),h(data[3]),cast_type0=int(data[4]),tone17_19=f(data[5:8]),stats=NeutralStats(*(f(x)for x in data[8:11])))


def check(source,output):
    previous=base.cases,base.model
    try:base.cases=cases;base.model=model;r=base.check(source,output,['renderChannelMixForBWCasts'])
    finally:base.cases,base.model=previous
    r['reference_Lab_is_supplied']=False
    r['declared_case_and_model_provider']={'module':'native_channel_mix_check','only_new_channel_mix_cases':True,'source_sha256':{n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest()for n in ['native_channel_mix_check.py','pixel_channel_mix.py','pixel_neutral_root.py']},'explicit_context':['SSRParams0 uint32','SSRTone17..19 f32','SSRStats groups2/3/4 field4 f32','person96 half'],'black_cast15_unguarded_division_retained':True}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.output);print(json.dumps(r['metrics']))
