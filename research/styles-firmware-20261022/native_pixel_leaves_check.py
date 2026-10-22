"""Small, separately activated original leaf checks; no accepted batch reruns.

Every requested leaf has its original complete body and explicit host shims.
Unknown finite domains remain in the receipt and are not counted as passes.
"""
import argparse,ctypes,hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from leaf_host import build,MATH_C
from leaf_numeric import V,DomainUnknown
import pixel_leaves
from semantic_tone import Curve1D


def model(name,data,curve,*,point):
    make=lambda x:V.value(x,point=True)if point else V.bounds(x,x)
    rgb=make(data[:3]);guide=make(data[3]);amount=make(data[4]);mode=make(data[5])
    if name=='whitesCurve':return pixel_leaves.whites_curve(rgb,amount,curve,mode)
    if name in pixel_leaves.LEAVES:return pixel_leaves.LEAVES[name](rgb,amount)
    import pixel_tonal
    if name in pixel_tonal.FUNCTIONS:return pixel_tonal.FUNCTIONS[name](rgb,guide,amount)
    import pixel_lighten
    if name in pixel_lighten.FUNCTIONS:return pixel_lighten.FUNCTIONS[name](rgb,guide,amount)
    raise ValueError('Independent leaf model absent: '+name)


def cases(name):
    rgb=[[.2,.4,.8],[.4,.4,.4],[-.05,.6,1.1],[.001,.002,.003],[0,0,0]]
    amounts=[.7,1.3]if name=='airyFilter'else[-.25,.25,.75]
    guides=[.4]
    if name in ('ShadowsFilter','ShadowsNegativeFilter'):
        amounts=[.1,.5,.9]if name=='ShadowsFilter'else[-.1,-.5,-.9];guides=[.05,.4,.9]
    if name in ('lightenFilter','negativeLightenFilter'):
        amounts=[.1,.5,.9]if name=='lightenFilter'else[1.1,1.4,1.8];guides=[.05,.4,.9]
    modes=[0,1]if name=='whitesCurve'else[0]
    return [np.array([*color,guide,amount,mode],dtype='f2').astype('f4')for color in rgb for guide in guides for amount in amounts for mode in modes]


def check(source: Path,output: Path,names):
    if output.exists():raise FileExistsError(output)
    ir,functions=build(source.read_text(),names);curve=Curve1D(tuple(np.linspace(0,1,17)**.8),'supplied whites working coordinate');tex=np.r_[np.array([17],dtype='u4').view('f4'),np.array(curve.red_samples,dtype='f4')];rows=[];all_outputs=[];inputs_hash=hashlib.sha256()
    with tempfile.TemporaryDirectory(prefix='psr-pixel-leaves-')as t:
        w=Path(t);(w/'leaf.ll').write_text(ir);(w/'math.c').write_text(MATH_C);libpath=w/'leaves.dylib'
        c=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',str(w/'leaf.ll'),str(w/'math.c'),'-o',str(libpath)],capture_output=True,text=True,timeout=60)
        if c.returncode:raise RuntimeError(c.stderr[:6000])
        lib=ctypes.CDLL(str(libpath))
        for index,name in enumerate(names):
            fn=getattr(lib,f'psr_leaf_{index}');fn.argtypes=[ctypes.c_void_p]*3;fn.restype=None
            for data in cases(name):
                out=np.zeros(3,dtype='f4');fn(data.ctypes.data,tex.ctypes.data,out.ctypes.data);all_outputs.append(out.copy());inputs_hash.update(name.encode()+data.tobytes()+tex.tobytes())
                row={'leaf':name,'input_half_values':data.tolist(),'nonzero_parameter':bool(data[4]!=0),'native_nonfinite_values':int(np.count_nonzero(~np.isfinite(out)))}
                try:
                    point=model(name,data,curve,point=True);row['point_unknown']=None
                    row['half_bit_mismatches']=int(np.count_nonzero(out.astype('f2').view('u2')!=point.lo.astype('f2').view('u2')))
                    row['max_absolute_error']=float(np.max(abs(out.astype('f8')-point.lo)))if np.isfinite(out).all()else None
                except DomainUnknown as error:row.update(point_unknown=str(error),half_bit_mismatches=None,max_absolute_error=None)
                try:
                    bounds=model(name,data,curve,point=False);row['set_unknown']=None
                    row['range_covered']=bool(np.isfinite(out).all()and np.all(out>=bounds.lo)and np.all(out<=bounds.hi))
                except DomainUnknown as error:row.update(set_unknown=str(error),range_covered=None)
                rows.append(row)
    per={}
    for name in names:
        a=[r for r in rows if r['leaf']==name];per[name]={'cases':len(a),'nonzero_cases':sum(r['nonzero_parameter']for r in a),'point_unknown':sum(r['point_unknown']is not None for r in a),'set_unknown':sum(r['set_unknown']is not None for r in a),'half_bit_mismatches_in_known_point_domain':sum(r['half_bit_mismatches']or 0 for r in a),'max_absolute_error_in_known_point_domain':max([r['max_absolute_error']for r in a if r['max_absolute_error']is not None],default=None),'range_violations_in_known_set_domain':sum(r['range_covered']is False for r in a)}
    r={'scope':__doc__,'hardware_reference':'iPhone17,3','build':'24A446','leaves':per,'records':len(rows),'original_function_text_sha256':functions,'original_function_bodies_modified':False,'host_fragment_sha256':hashlib.sha256(ir.encode()).hexdigest(),'host_math_C_sha256':hashlib.sha256(MATH_C.encode()).hexdigest(),'model_sha256':hashlib.sha256(Path(pixel_leaves.__file__).read_bytes()).hexdigest(),'arithmetic_sha256':hashlib.sha256((Path(__file__).parent/'leaf_numeric.py').read_bytes()).hexdigest(),'host_builder_sha256':hashlib.sha256((Path(__file__).parent/'leaf_host.py').read_bytes()).hexdigest(),'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'input_sha256':inputs_hash.hexdigest(),'native_output_sha256':hashlib.sha256(np.asarray(all_outputs,dtype='f4').tobytes()).hexdigest(),'GPU_executed':False,'libm_sampler_and_2u_4u_allowances_are_assumptions':True,'unimplemented_placeholders':False,'unknown_cases_retained':True,'accepted_batches_repeated':False,'rows':rows}
    r['additional_model_sources']={name:hashlib.sha256((Path(__file__).parent/name).read_bytes()).hexdigest()for name in ['pixel_tonal.py','pixel_lighten.py']}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    if any(x['range_violations_in_known_set_domain']for x in per.values()):raise AssertionError('Leaf output outside declared box; receipt retained')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);p.add_argument('--leaf',action='append',required=True);a=p.parse_args();r=check(a.source,a.output,a.leaf);print(json.dumps(r['leaves']))
