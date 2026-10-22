"""New small mixed-activation host check of complete original BG/FG helpers.

No placeholder leaves; all transitive original bodies are linked. This tests
conditional helper composition, not semantic producer/outer pixel pipeline.
"""
import argparse,ctypes,hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from leaf_host import build,MATH_C
from leaf_numeric import V,DomainUnknown
from bgfg_fixed import ExactHelperFields,forward as fixed_forward
from semantic_tone import I,Curve1D
from bgfg_tone import run,PixelContext
from all_pixel_leaves import models
from tone_interface import ConsumerFields,ScaledControls,ResolvedSceneType


BG_POS={0:.12,1:.08,2:.18,3:.12,4:.08,5:.07,7:.06,8:.9,9:.12,10:.2,11:.9}
BG_NEG={0:-.08,1:-.07,2:-.1,3:-.08,4:-.05,5:-.06,7:-.04,8:.92,9:-.12,10:-.2,11:1.1}
FG_POS={0:.35,2:.04,3:.12,4:.1,5:.9,6:.08,7:.05,8:.12,11:.15,14:.2,15:.15}
FG_NEG={0:.35,2:-.04,3:-.12,4:-.08,5:1.1,6:-.08,7:-.05,8:-.12,11:-.1,14:-.2,15:-.15}


def packet(block,profile):
    p=np.zeros(40,dtype='f4');p[8]=p[11]=p[22]=1
    start=0 if block=='bg'else 17
    for key,value in profile.items():p[start+key]=value
    return ConsumerFields(ScaledControls(np.float32(.5),np.float32(.3),np.float32(0),ResolvedSceneType(4)),'synthetic_mixed_connection_check',p,np.zeros(40))


def cases(block):
    for profile_name,profile in [('positive',BG_POS if block=='bg'else FG_POS),('negative',BG_NEG if block=='bg'else FG_NEG)]:
        for color in [[.2,.4,.8],[.8,.2,.1],[.4,.4,.4]]:
            for guide,person,skin in [(.05,.2,.1),(.9,.9,.8)]:
                yield profile_name,packet(block,profile),np.array([*color,guide,person,skin,*[.3,.5,.7]],dtype='f2').astype('f4')


def check(source,output):
    if output.exists():raise FileExistsError(output)
    ir,original=build(source.read_text(),['renderBGAdjustments','renderFGAdjustments'])
    curve=Curve1D(tuple(np.linspace(0,1,17)**.8),'supplied whites working coordinate');tex=np.r_[np.array([17],dtype='u4').view('f4'),np.array(curve.red_samples,dtype='f4')];providers=models(curve)
    inputs=hashlib.sha256();outputs=[];rows=[]
    with tempfile.TemporaryDirectory(prefix='psr-bgfg-complete-')as t:
        w=Path(t);(w/'full.ll').write_text(ir);(w/'math.c').write_text(MATH_C)
        c=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',str(w/'full.ll'),str(w/'math.c'),'-o',str(w/'full.dylib')],capture_output=True,text=True,timeout=60)
        if c.returncode:raise RuntimeError(c.stderr[:6000])
        lib=ctypes.CDLL(str(w/'full.dylib'))
        for index,block in enumerate(['bg','fg']):
            fn=getattr(lib,f'psr_leaf_{index}');fn.argtypes=[ctypes.c_void_p]*3;fn.restype=None
            for profile,fields,data in cases(block):
                start=0 if block=='bg'else 17;n=17 if block=='bg'else 16
                raw=np.r_[data,fields.values[start:start+n]].astype('f4');out=np.zeros(3,dtype='f4');fn(raw.ctypes.data,tex.ctypes.data,out.ctypes.data);outputs.append(out.copy());inputs.update(block.encode()+raw.tobytes()+tex.tobytes())
                r=run(block,I.point(data[:3]),fields,PixelContext(*[float(x)for x in data[3:6]]),semantic_rgb=I.point(data[6:9]),leaf_models=providers)
                row={'block':block,'profile':profile,'input':data.tolist(),'field_values':fields.values[start:start+n].tolist(),'native_nonfinite_values':int(np.count_nonzero(~np.isfinite(out))),'set_status':r.status,'missing_operator':r.missing_operator,'range_covered':None,'max_output_box_width':None,'native_output_half':out.tolist(),'trace':r.trace}
                try:
                    exact=ExactHelperFields(block,raw[9:].copy(),'explicit synthetic f32 helper arguments')
                    point=fixed_forward(V.value(data[:3]),V.value(data[6:9]),exact,guide=V.value(data[3]),person=V.value(data[4]),skin=V.value(data[5]),whites=curve)
                    row['point_unknown']=None;row['point_half_bit_mismatches']=int(np.count_nonzero(out.astype('f2').view('u2')!=point.lo.astype('f2').view('u2')));row['point_max_absolute_error']=float(np.max(abs(out.astype('f8')-point.lo)))
                except DomainUnknown as error:row['point_unknown']=str(error);row['point_half_bit_mismatches']=None;row['point_max_absolute_error']=None
                if r.output is not None:
                    row['range_covered']=bool(np.isfinite(out).all()and np.all(out>=r.output.lo)and np.all(out<=r.output.hi));row['max_output_box_width']=float(np.max(r.output.hi-r.output.lo))
                rows.append(row)
    root=Path(__file__).parent
    metrics={b:{'calls':sum(r['block']==b for r in rows),'computed_sets':sum(r['block']==b and r['range_covered']is not None for r in rows),'unknown':sum(r['block']==b and r['range_covered']is None for r in rows),'range_violations':sum(r['block']==b and r['range_covered']is False for r in rows),'known_point_calls':sum(r['block']==b and r['point_unknown']is None for r in rows),'point_half_bit_mismatches':sum(r['point_half_bit_mismatches']or 0 for r in rows if r['block']==b),'point_max_absolute_error':max([r['point_max_absolute_error']for r in rows if r['block']==b and r['point_max_absolute_error']is not None],default=None),'max_box_width':max([r['max_output_box_width']for r in rows if r['block']==b and r['max_output_box_width']is not None],default=None)}for b in ['bg','fg']}
    result={'scope':__doc__,'reference_model':'iPhone17,3','OS_build':'24A446','metrics':metrics,'original_complete_function_sha256':original,'original_bodies_modified':False,'placeholder_leaves':False,'host_fragment_sha256':hashlib.sha256(ir.encode()).hexdigest(),'host_math_sha256':hashlib.sha256(MATH_C.encode()).hexdigest(),'input_sha256':inputs.hexdigest(),'native_output_sha256':hashlib.sha256(np.array(outputs,dtype='f4').tobytes()).hexdigest(),'source_sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest()for n in ['leaf_host.py','leaf_numeric.py','pixel_leaves.py','pixel_tonal.py','pixel_lighten.py','pixel_color.py','pixel_remaining.py','all_pixel_leaves.py','bgfg_tone.py','bgfg_fixed.py','native_bgfg_complete_check.py']},'point_contract':'Explicit synthetic exact f32 fields only; no uncertain producer centers','set_contract':'2u arithmetic and 4u transcendentals; normalized-to-pixel 1D linear clamp sampler are host assumptions','full_camera_pipeline_verified':False,'GPU_executed':False,'accepted_native_batches_repeated':False,'rows':rows}
    output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    if any(m['range_violations']for m in metrics.values()):raise AssertionError('Original complete helper outside model output set; receipt retained')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.output);print(json.dumps(r['metrics']))
