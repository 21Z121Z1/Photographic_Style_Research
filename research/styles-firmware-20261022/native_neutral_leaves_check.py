"""Small activated original neutralizing leaf checks, supplied reference Lab."""
import argparse,ctypes,hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from leaf_host import build,MATH_C
from leaf_numeric import V,DomainUnknown
from pixel_neutral import de_red,de_yellow,red_neutral_only,skin_warmth_positive


def cases(name=None):
    for rgb in [[.2,.4,.8],[.8,.3,.15],[.4,.4,.4],[0,0,0]]:
        for amount in [-.3,.3]:
            for ref in [[.65,.1,.05],[.65,0,0]]:
                yield np.array([*rgb,.7,amount,.4,*ref,1 if name=='skinWarmthFilter'else .8],dtype='f2').astype('f4')


def model(name,data,point):
    v=lambda x:V.value(x)if point else V.bounds(x,x)
    rgb=v(data[:3]);mask=v(data[3]);amount=v(data[4]);other=v(data[5]);ref=v(data[6:9])
    if name=='deRed':return de_red(rgb,mask,other,ref,amount)
    if name=='deYellow':return de_yellow(rgb,mask,ref,amount)
    if name=='skinWarmthFilter':return skin_warmth_positive(rgb,mask,other,ref,v(data[9]),amount)
    return red_neutral_only(rgb,mask,ref,amount,other,v(data[9]))


def check(source,output,names=None,observe_native=None):
    if output.exists():raise FileExistsError(output)
    names=names or['deRed','deYellow','deRedNeutralOnly'];ir,original=build(source.read_text(),names);rows=[];ih=hashlib.sha256();outputs=[]
    with tempfile.TemporaryDirectory(prefix='psr-neutral-leaves-')as t:
        w=Path(t);(w/'source.ll').write_text(ir);(w/'math.c').write_text(MATH_C)
        c=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',str(w/'source.ll'),str(w/'math.c'),'-o',str(w/'helper.dylib')],capture_output=True,text=True,timeout=60)
        if c.returncode:raise RuntimeError(c.stderr[:4000])
        lib=ctypes.CDLL(str(w/'helper.dylib'));tex=np.zeros(1,dtype='f4')
        for index,name in enumerate(names):
            fn=getattr(lib,f'psr_leaf_{index}');fn.argtypes=[ctypes.c_void_p]*3
            for data in cases(name):
                native=np.zeros(3,dtype='f4');fn(data.ctypes.data,tex.ctypes.data,native.ctypes.data);outputs.append(native.copy());ih.update(name.encode()+data.tobytes());row={'helper':name,'input':data.tolist(),'native_half_output':native.tolist(),'native_nonfinite':int(np.count_nonzero(~np.isfinite(native)))}
                if observe_native is not None:row.update(observe_native(lib,name,data,native))
                for point in [True,False]:
                    try:
                        value=model(name,data,point)
                        if point:row.update(point_unknown=None,half_bit_mismatches=int(np.count_nonzero(native.astype('f2').view('u2')!=value.lo.astype('f2').view('u2'))),max_absolute_error=float(np.max(abs(native-value.lo))))
                        else:row.update(set_unknown=None,range_covered=bool(np.isfinite(native).all()and np.all(native>=value.lo)and np.all(native<=value.hi)))
                    except DomainUnknown as error:
                        if point:row.update(point_unknown=str(error),half_bit_mismatches=None,max_absolute_error=None)
                        else:row.update(set_unknown=str(error),range_covered=None)
                rows.append(row)
    metrics={n:{'calls':sum(r['helper']==n for r in rows),'point_unknown':sum(r['helper']==n and r['point_unknown']is not None for r in rows),'set_unknown':sum(r['helper']==n and r['set_unknown']is not None for r in rows),'half_bit_mismatches_known':sum(r['half_bit_mismatches']or 0 for r in rows if r['helper']==n),'max_absolute_error_known':max((r['max_absolute_error']for r in rows if r['helper']==n and r['max_absolute_error']is not None),default=None),'range_violations_known':sum(r['helper']==n and r['range_covered']is False for r in rows)}for n in names}
    root=Path(__file__).parent;r={'model':'iPhone17,3','OS_build':'24A446','metrics':metrics,'original_complete_function_sha256':original,'original_bodies_modified':False,'reference_Lab_is_supplied':True,'old_batches_repeated':False,'GPU_executed':False,'host_bool_shim':'float!=0 (explicit assumption), not fptoui i1','host_fmod_shim':'C fmodf then half','source_sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest()for n in ['pixel_neutral.py','pixel_color.py','pixel_skin.py','leaf_domains.py','leaf_numeric.py','leaf_host.py','native_neutral_leaves_check.py']},'host_ir_sha256':hashlib.sha256(ir.encode()).hexdigest(),'host_math_sha256':hashlib.sha256(MATH_C.encode()).hexdigest(),'input_sha256':ih.hexdigest(),'output_sha256':hashlib.sha256(np.array(outputs,dtype='f4').tobytes()).hexdigest(),'rows':rows,'full_pipeline_verified':False,'set_error_budget_is_host_assumption':True}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    if any(m['range_violations_known']for m in metrics.values()):raise AssertionError('Original leaf outside set; receipt retained')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);p.add_argument('--leaf',action='append');a=p.parse_args();r=check(a.source,a.output,a.leaf);print(json.dumps(r['metrics']))
