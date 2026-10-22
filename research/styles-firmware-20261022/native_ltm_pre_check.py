"""New AIR7 SRL/transfer/CCM composition, sampled primary/matte explicit."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import native_ltm_gain_check as base
from leaf_numeric import V,vec
from ltm_preprocess import Parameters,forward
from air7_pre_host import build


def cases():
    c=np.array([[1,.02,0],[.01,1,.03],[0,-.01,1]],dtype='f4')
    for rgb in [[.2,.4,.8],[.7,.45,.3],[0,0,0]]:
        for code,srl,use,mode in [(3,.4,False,False),(3,.4,True,False),(3,2.4,True,False),(6,-1,False,False),(6,-1,False,True)]:yield np.r_[np.array([*rgb,.3],dtype='f2').astype('f4'),np.float32(srl),int(use),code,c.flat,int(mode)].astype('f4')


def model(data,unused,point):
    h=lambda x:V.value(x)if point else V.bounds(x,x)
    f=lambda x:V.value(x,'f')if point else V.bounds(x,x,'f')
    r=forward(h(data[:3]),h(data[3]),Parameters(f(data[4]),f(data[7:16].reshape(3,3)),int(data[6]),bool(data[5]),bool(data[16])))
    return vec([r.reference96[i]for i in range(3)]+[r.linear37[i]for i in range(3)]+[r.post_srl34[i]for i in range(3)])


def check(source,output):
    previous=base.cases,base.model,base.build
    try:base.cases=cases;base.model=model;base.build=build;r=base.check(source,output)
    finally:base.cases,base.model,base.build=previous
    r.pop('curve_half_samples',None);r.pop('upstream_reference96_linear98_CCM_scale_semantic_are_supplied',None)
    r['scope']=__doc__;r['actual_model_provider']={'module':'native_ltm_pre_check','source_sha256':{n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest()for n in ['ltm_preprocess.py','air7_pre_host.py','native_ltm_pre_check.py','pixel_transfer.py','leaf_host.py']},'inputs':['primary24 half','matte30 half','SRL f32','exact useSRL flag','transfer uint32','input CCM f32 columns','exact gamma mode flag'],'not_recovered_from_final_photo':True}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.output);print(json.dumps(r['metrics']))
