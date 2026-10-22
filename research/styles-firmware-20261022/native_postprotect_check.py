"""Small original502..566 comparison, including exact f32 threshold neighbors."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import native_neutral_leaves_check as base
from leaf_numeric import V
from pixel_postprotect import forward
from pixel_neutral_root import NeutralStats
from cast_values import CastValues
from postprotect_host import build


def cases(name=None):
    for rgb in [[.2,.4,.8],[.7,.45,.3],[.4,.4,.4],[0,0,0]]:
        for present,amount,width in [(True,.4,100),(False,.4,100),(True,-.4,100)]:
            yield np.r_[np.array([*rgb,.8,.2,.1],dtype='f2').astype('f4'),int(present),np.array([amount,width,.6,.4,.2],dtype='f4')].astype('f4')
    threshold=np.float32(.01)
    for amount in [np.nextafter(threshold,np.float32(0)),threshold,np.nextafter(threshold,np.float32(1))]:
        yield np.r_[np.array([.2,.4,.8,.8,.2,.1],dtype='f2').astype('f4'),1,np.array([amount,100,.6,.4,.2],dtype='f4')].astype('f4')


def model(name,data,point):
    h=lambda x:V.value(x)if point else V.bounds(x,x)
    f=lambda x:V.value(x,'f')if point else V.bounds(x,x,'f')
    raw=np.zeros(34,dtype='f4');raw[31:33]=data[7:9]
    return forward(h(data[:3]),h(data[3:6]),CastValues(f(raw)),NeutralStats(*(f(x)for x in data[9:12])),texture10_present=bool(data[6]))


def check(source,output):
    previous=base.cases,base.model,base.build
    try:base.cases=cases;base.model=model;base.build=build;r=base.check(source,output,['psrPostProtect'])
    finally:base.cases,base.model,base.build=previous
    r['reference_Lab_is_supplied']=False;r['original_bodies_modified']='main slice alpha-renamed and metadata/call attributes removed; arithmetic and control flow unchanged'
    r['declared_case_and_model_provider']={'module':'native_postprotect_check','only_new_postprotect_cases':True,'source_sha256':{n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest()for n in ['native_postprotect_check.py','postprotect_host.py','pixel_postprotect.py','pixel_warmth.py']},'explicit_context':['RGB501','color476','texture10 presence','cast fields19/20 f32','SSRStats groups2/3/4 field4 f32'],'threshold':'f32 amount < .01 skips, equality active; no abs','protect_ignore_chroma':True}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.output);print(json.dumps(r['metrics']))
