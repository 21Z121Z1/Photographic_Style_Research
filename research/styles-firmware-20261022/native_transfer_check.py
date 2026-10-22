"""New CMI transfer branches; branch3 reuses accepted encode/decode, no rerun."""
import argparse,hashlib,json,re
from pathlib import Path
import numpy as np
import native_neutral_leaves_check as base
from leaf_numeric import V
from pixel_transfer import forward


def cases(name=None):
    for rgb in [[.2,.4,.8],[-.1,.05,1],[0,0,0],[.0001,-.0002,.0003]]:
        for code in [0,1,2,4,5,6,7,8,9]:yield np.array([*rgb,code,0,0],dtype='f2').astype('f4')


def model(name,data,point):return forward(V.value(data[:3])if point else V.bounds(data[:3],data[:3]),int(data[3]),to_linear='linearFromCurved'in name)


def check(source,output):
    names=re.findall(r'^define[^\n]*@([^ (]*(?:linearFromCurved|curvedFromLinear)[^ (]*)\(',source.read_text(),re.M)
    previous=base.cases,base.model
    try:base.cases=cases;base.model=model;r=base.check(source,output,names)
    finally:base.cases,base.model=previous
    r['reference_Lab_is_supplied']=False;r['declared_case_and_model_provider']={'module':'native_transfer_check','raw_enum_without_ICC_name_assumption':True,'branch3_arithmetic_reused_and_not_rerun':True,'source_sha256':{n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest()for n in ['native_transfer_check.py','pixel_transfer.py']}}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.output);print(json.dumps(r['metrics']))
