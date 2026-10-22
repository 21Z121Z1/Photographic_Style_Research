"""Small original complete skin/highlight helper host check; no old batches."""
import argparse,ctypes,hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from leaf_host import build,MATH_C
from leaf_numeric import V,DomainUnknown
import pixel_skin


def cases(name):
    for rgb in [[.2,.4,.8],[.7,.45,.3],[.4,.4,.4],[0,0,0]]:
        for guide,skin in [(.1,.2),(.7,.8)]:
            for t9,t10 in ([(.2,.3),(-.2,-.3),(5e-6,5e-6)]if name=='renderSkinAdjustments'else[(0,0)]):
                head=np.array([*rgb,guide,2,skin,0,0,0],dtype='f2').astype('f4');fields=np.zeros(16,dtype='f4');fields[9:11]=[t9,t10]
                yield np.r_[head,fields].astype('f4')


def model(name,data,point):
    h=lambda x:V.value(x)if point else V.bounds(x,x)
    f=lambda x:V.value(x,'f')if point else V.bounds(x,x,'f')
    if name=='renderSkinAdjustments':return pixel_skin.forward(h(data[:3]),h(data[5]),h(data[3]),f(data[18]),f(data[19]))
    return pixel_skin.highlight_recover(h(data[:3]),h(data[3]),h(data[4]))


def check(source,output):
    if output.exists():raise FileExistsError(output)
    names=['renderSkinAdjustments','highlightRecover'];ir,functions=build(source.read_text(),names);rows=[];ih=hashlib.sha256();outputs=[]
    with tempfile.TemporaryDirectory(prefix='psr-skin-highlight-')as t:
        w=Path(t);(w/'source.ll').write_text(ir);(w/'math.c').write_text(MATH_C);library=w/'helpers.dylib'
        c=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',str(w/'source.ll'),str(w/'math.c'),'-o',str(library)],capture_output=True,text=True,timeout=60)
        if c.returncode:raise RuntimeError(c.stderr[:4000])
        lib=ctypes.CDLL(str(library));tex=np.zeros(1,dtype='f4')
        for index,name in enumerate(names):
            fn=getattr(lib,f'psr_leaf_{index}');fn.argtypes=[ctypes.c_void_p]*3
            for data in cases(name):
                native=np.zeros(3,dtype='f4');fn(data.ctypes.data,tex.ctypes.data,native.ctypes.data);outputs.append(native.copy());ih.update(name.encode()+data.tobytes())
                row={'helper':name,'input':data.tolist(),'native_output_half':native.tolist(),'native_nonfinite':int(np.count_nonzero(~np.isfinite(native)))}
                for point in [True,False]:
                    try:
                        v=model(name,data,point)
                        if point:row.update(point_unknown=None,half_bit_mismatches=int(np.count_nonzero(native.astype('f2').view('u2')!=v.lo.astype('f2').view('u2'))),max_absolute_error=float(np.max(abs(native-v.lo))))
                        else:row.update(set_unknown=None,range_covered=bool(np.isfinite(native).all()and np.all(native>=v.lo)and np.all(native<=v.hi)),box_max_width=float(np.max(v.hi-v.lo)))
                    except DomainUnknown as error:
                        if point:row.update(point_unknown=str(error),half_bit_mismatches=None,max_absolute_error=None)
                        else:row.update(set_unknown=str(error),range_covered=None,box_max_width=None)
                rows.append(row)
    metrics={n:{'calls':sum(r['helper']==n for r in rows),'point_unknown':sum(r['helper']==n and r['point_unknown']is not None for r in rows),'set_unknown':sum(r['helper']==n and r['set_unknown']is not None for r in rows),'half_bit_mismatches_known':sum(r['half_bit_mismatches']or 0 for r in rows if r['helper']==n),'max_absolute_error_known':max((r['max_absolute_error']for r in rows if r['helper']==n and r['max_absolute_error']is not None),default=None),'range_violations_known':sum(r['helper']==n and r['range_covered']is False for r in rows)}for n in names}
    root=Path(__file__).parent;r={'reference_model':'iPhone17,3','OS_build':'24A446','metrics':metrics,'original_complete_function_sha256':functions,'original_function_bodies_modified':False,'source_sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest()for n in ['pixel_skin.py','pixel_remaining.py','pixel_leaves.py','leaf_domains.py','leaf_numeric.py','leaf_host.py','native_skin_highlight_check.py']},'host_ir_sha256':hashlib.sha256(ir.encode()).hexdigest(),'host_math_sha256':hashlib.sha256(MATH_C.encode()).hexdigest(),'input_sha256':ih.hexdigest(),'native_output_sha256':hashlib.sha256(np.array(outputs,dtype='f4').tobytes()).hexdigest(),'rows':rows,'GPU_executed':False,'old_batches_repeated':False,'error_allowances':'2u arithmetic / 4u transcendentals are declared host assumptions; not GPU proof','full_pipeline_verified':False}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    if any(x['range_violations_known']for x in metrics.values()):raise AssertionError('Host output outside conditional set; receipt retained')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.output);print(json.dumps(r['metrics']))
