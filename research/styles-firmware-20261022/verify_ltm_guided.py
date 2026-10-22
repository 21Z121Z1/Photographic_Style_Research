"""Synthetic full-set connection receipt; no additional native or GPU calls."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from leaf_numeric import V
from ltm_preprocess import Parameters as Pre
from ltm_gain import Parameters as Gain
from ltm_guided import forward
from semantic_tone import Curve1D


def check(output):
    if output.exists():raise FileExistsError(output)
    y,x=np.mgrid[:2,:3];primary=np.stack([.5+.03*x,.45+.02*y+.01*x,.4+.02*x],axis=2).astype('f2');linear=np.stack([.3+.02*x,.35+.02*y,.4+.01*x],axis=2).astype('f2');matte=np.full((2,3),.3,dtype='f2');guide=np.stack([.3+.02*x,.35+.03*y+.01*x,.4+.02*x],axis=2).astype('f2');semlo=[.6,.8,.7,1.2,.6,.3,.4];semhi=[.6,.8,.8,1.3,.6,.3,.4];s=lambda v:V.bounds(v,v);f=lambda v:V.bounds(v,v,'f');pre=Pre(f(.4),f(np.eye(3)),3,True,False);gain=Gain(f(np.eye(3)),f(1),V.bounds(semlo,semhi,'f'));curve=Curve1D(tuple(np.linspace(0,1,17)**.8),'synthetic AIR7 supplied curve');rows=[]
    for name,g in [('RGB-guide',guide),('scalar-guide',guide[...,:1])]:
        r=forward(s(primary),s(linear),s(matte),s(g),pre_parameters=pre,gain_parameters=gain,curve=curve,epsilon=f(.05),output_shape=(3,4),working_domain='Explicit sampled AIR7 colors /synthetic guided working domain',input_branch_decisions=('supplied semantic2 range .7..8 and semantic3 range1.2..1.3',))
        row={'case':name,'unknowns':r.unknowns,'input_branch_decisions':r.input_branch_decisions,'outputs':{}}
        for label,v in [('raw_BG',r.raw_bg),('raw_FG',r.raw_fg),('guided_BG',None if r.guided_bg is None else r.guided_bg['output']),('guided_FG',None if r.guided_fg is None else r.guided_fg['output'])]:
            row['outputs'][label]=None if v is None else {'shape':v.lo.shape,'is_point':v.point,'lower':v.lo.tolist(),'upper':v.hi.tolist(),'max_width':float(np.max(v.hi-v.lo))}
        rows.append(row)
    root=Path(__file__).parent;result={'scope':__doc__,'sampled_primary24':primary.tolist(),'sampled_linear98':linear.tolist(),'sampled_matte30':matte.tolist(),'supplied_guide':guide.tolist(),'semantic_lo':semlo,'semantic_hi':semhi,'SRL_parameter_f32':float(np.float32(.4)),'CCM0_and_CCM1':'explicit identity f32 columns','input_transfer_code':3,'useSRLBeforeStats':True,'epsilon_f32':float(np.float32(.05)),'curve_half_samples':curve.red_samples,'rows':rows,'source_sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest()for n in ['ltm_preprocess.py','ltm_gain.py','ltm_guided.py','guided_conditioned.py','verify_ltm_guided.py']},'native_calls':0,'GPU_executed':False,'source_2D_sampling_or_frame_identity_verified':False,'consumer_block290_ROI_sampling_included':False,'full_pipeline_verified':False}
    output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.output);print(json.dumps([{'case':x['case'],'unknowns':x['unknowns'],'widths':{k:None if v is None else v['max_width']for k,v in x['outputs'].items()}}for x in r['rows']]))
