"""Locate the remaining first RichSat set failure, without changing its domain."""
import argparse,hashlib,json,sys
from pathlib import Path
import numpy as np
import pixel_color,pre_skin_color
from leaf_numeric import V,DomainUnknown
from complete_fixture import decode
from complete_forward import forward


def encode(v):return {'lo':np.asarray(v.lo).tolist(),'hi':np.asarray(v.hi).tolist(),'max_width':float(np.max(v.hi-v.lo))}


def check(contexts_file,analysis_file,output):
    if output.exists():raise FileExistsError(output)
    contexts=json.loads(contexts_file.read_text());analysis=json.loads(analysis_file.read_text());index=analysis['auxiliary_shared_semantic']['active_context_index'];c=decode(contexts['rows'][index]['context']);records=[];active=[]
    old_rich=pre_skin_color.rich_sat;old_to=pixel_color.to_polar;old_from=pixel_color.from_polar;old_dot=pixel_color.dot;old_div=V.__truediv__
    def rich(rgb,gain,strength):
        row={'input_FG354':encode(rgb),'gain':encode(gain),'strength':encode(strength)};records.append(row);active.append(row)
        try:return old_rich(rgb,gain,strength)
        finally:active.pop()
    def polar(rgb):
        r=old_to(rgb)
        if active:active[-1]['polar']={n:encode(v)for n,v in zip(['light','angle','radius'],r)}
        return r
    def inverse(*a,**k):
        r=old_from(*a,**k)
        if active:active[-1]['work_after_original_clamp']=encode(r)
        return r
    def dot(*a,**k):
        r=old_dot(*a,**k)
        if active:active[-1].setdefault('dot_calls',[]).append({'input':encode(a[0]),'result':encode(r)})
        return r
    def divide(a,b):
        try:return old_div(a,b)
        except DomainUnknown as ex:
            if active:
                caller=sys._getframe(1);active[-1]['first_failed_division']={'numerator':encode(a),'denominator':encode(a.box(b)),'caller':caller.f_code.co_name,'file':Path(caller.f_code.co_filename).name,'line':caller.f_lineno,'reason':str(ex)}
            raise
    pre_skin_color.rich_sat=rich;pixel_color.to_polar=polar;pixel_color.from_polar=inverse;pixel_color.dot=dot;V.__truediv__=divide
    try:result=forward(c,point=False,shared_semantic=True)
    finally:pre_skin_color.rich_sat=old_rich;pixel_color.to_polar=old_to;pixel_color.from_polar=old_from;pixel_color.dot=old_dot;V.__truediv__=old_div
    out={'scope':__doc__,'contexts_sha256':hashlib.sha256(contexts_file.read_bytes()).hexdigest(),'analysis_sha256':hashlib.sha256(analysis_file.read_bytes()).hexdigest(),'active_context_index':index,'shared_semantic_enabled':True,'first_pixel_RichSat':records[0],'recorded_pixels':len(records),'pixel_unknowns':result.pixel_unknowns,'writer_set_really_generated':result.writer is not None,'zero_denominator_joint_reachability':'not established; remaining polar/work/power-mean dependency loss; no center/clamp/epsilon change','new_native_calls':0,'GPU_verified':False}
    output.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print(json.dumps({'pixels':len(records),'first_failed_division':records[0].get('first_failed_division'),'work':records[0].get('work_after_original_clamp'),'writer_set':result.writer is not None}));return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('contexts',type=Path);p.add_argument('analysis',type=Path);p.add_argument('output',type=Path);a=p.parse_args();check(a.contexts,a.analysis,a.output)
