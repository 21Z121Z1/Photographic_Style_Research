"""Small model-only candidate screen before any new original host calls."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from active_color import Color,replace_color,half_cell
from complete_fixture import decode
from complete_forward import forward

CONTEXT_SHA='ffae597ca79f92447a2bdae45bbc007450be27ae9165bef78d0e6b3cb0932b11'


def check(context_file,output):
    if output.exists():raise FileExistsError(output)
    if hashlib.sha256(context_file.read_bytes()).hexdigest()!=CONTEXT_SHA:raise ValueError('Only frozen S15 raw source/ROI/auxiliary context')
    base=decode(json.loads(context_file.read_text()));colors=[np.float32(v)for v in [0,.01,.02,.03,.3]]+[np.nextafter(np.float32(.3),np.float32(np.inf))];rows=[];images={}
    for value in colors:
        control=Color(value);c=replace_color(base,control);result=forward(c,point=True);obs={n:v.lo.astype('f2')for n,v in result.observations.items()};row={'control':control.record(),'point_unknowns':result.pixel_unknowns,'internal_unknowns':result.internal_unknowns,'writer_known':result.writer is not None,'observation_sha256':{n:hashlib.sha256(a.tobytes()).hexdigest()for n,a in obs.items()}}
        if result.writer is not None:images[int(value.view('u4'))]=obs
        rows.append(row)
    pairs=[]
    for i,a in enumerate(rows):
        for b in rows[i+1:]:
            aa=images.get(a['control']['raw_f32_bits']);bb=images.get(b['control']['raw_f32_bits'])
            if aa is None or bb is None:continue
            differences={n:{'different_half_components':int(np.count_nonzero(v.view('u2')!=bb[n].view('u2'))),'max_absolute_difference':float(np.max(abs(v.astype('f8')-bb[n].astype('f8'))))}for n,v in aa.items()if n in bb}
            pairs.append({'a_raw_bits':a['control']['raw_f32_bits'],'b_raw_bits':b['control']['raw_f32_bits'],'differences':differences,'writer_equal':differences['writer']['different_half_components']==0,'classification':'model_only; original host not run'})
    result={'scope':__doc__,'base_context_sha256':CONTEXT_SHA,'control':'SSRParams.color field3 byte12, post-scene f32; UI mapping unverified','changed_raw_field_only':3,'rows':rows,'pairs':pairs,'half_cell_at_point3':half_cell(Color(np.float32(.3))),'selected_host_values':[float(v)for v in [np.float32(.01),np.float32(.02),np.float32(.3),np.nextafter(np.float32(.3),np.float32(np.inf))]],'native_calls':0,'GPU_verified':False,'global_injectivity_proved':False,'unknown_source_photo_inverse':False}
    output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({'model_rows':len(rows),'known_writers':sum(v['writer_known']for v in rows),'writer_equal_pairs':sum(v['writer_equal']for v in pairs),'host_values_selected':result['selected_host_values']}));return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('context',type=Path);p.add_argument('output',type=Path);a=p.parse_args();check(a.context,a.output)
