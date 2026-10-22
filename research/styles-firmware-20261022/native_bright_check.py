"""New small original bright helper host check with explicit raw stats values."""
import argparse,ctypes,hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from leaf_host import build,MATH_C
from leaf_numeric import V,DomainUnknown
from pixel_bright import BrightStats,forward


def cases():
    for rgb in [[.2,.4,.8],[.7,.45,.3],[.4,.4,.4],[0,0,0]]:
        for person,skin in [(.2,.1),(.9,.8)]:
            for exposure,stats in [(1,[.3,.2,.2,.45,.4]),(8,[.8,.1,.8,.8,.1])]:
                yield np.r_[np.array([*rgb,person,skin,exposure,.1,.2,.4],dtype='f2').astype('f4'),np.array(stats,dtype='f4')].astype('f4')
    yield np.array([0,0,0,.5,.5,0,0,0,0,.3,.2,.2,.45,.4],dtype='f4')
    yield np.array([.2,.4,.8,.5,.5,1,.1,.2,.4,.3,.2,1.2,.45,.4],dtype='f4')


def model(data,point):
    h=lambda x:V.value(x)if point else V.bounds(x,x)
    f=lambda x:V.value(x,'f')if point else V.bounds(x,x,'f')
    stats=BrightStats(*[f(x)for x in data[9:14]])
    return forward(h(data[:3]),h(data[6:9]),h(data[3]),h(data[4]),h(data[5]),stats)


def check(source,output):
    if output.exists():raise FileExistsError(output)
    ir,original=build(source.read_text(),['renderBrightAndContrast']);rows=[];inputs=hashlib.sha256();outputs=[]
    with tempfile.TemporaryDirectory(prefix='psr-bright-')as t:
        w=Path(t);(w/'source.ll').write_text(ir);(w/'math.c').write_text(MATH_C)
        c=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',str(w/'source.ll'),str(w/'math.c'),'-o',str(w/'helper.dylib')],capture_output=True,text=True,timeout=60)
        if c.returncode:raise RuntimeError(c.stderr[:4000])
        lib=ctypes.CDLL(str(w/'helper.dylib'));fn=lib.psr_leaf_0;fn.argtypes=[ctypes.c_void_p]*3;tex=np.zeros(1,dtype='f4')
        for data in cases():
            native=np.zeros(3,dtype='f4');fn(data.ctypes.data,tex.ctypes.data,native.ctypes.data);outputs.append(native.copy());inputs.update(data.tobytes());row={'input':data.tolist(),'native_half_output':native.tolist(),'native_nonfinite':int(np.count_nonzero(~np.isfinite(native)))}
            for point in [True,False]:
                try:
                    v=model(data,point)
                    if point:row.update(point_unknown=None,half_bit_mismatches=int(np.count_nonzero(native.astype('f2').view('u2')!=v.lo.astype('f2').view('u2'))),max_absolute_error=float(np.max(abs(native-v.lo))))
                    else:row.update(set_unknown=None,range_covered=bool(np.isfinite(native).all()and np.all(native>=v.lo)and np.all(native<=v.hi)),max_box_width=float(np.max(v.hi-v.lo)))
                except DomainUnknown as error:
                    if point:row.update(point_unknown=str(error),half_bit_mismatches=None,max_absolute_error=None)
                    else:row.update(set_unknown=str(error),range_covered=None,max_box_width=None)
            rows.append(row)
    metrics={'calls':len(rows),'point_unknown':sum(r['point_unknown']is not None for r in rows),'set_unknown':sum(r['set_unknown']is not None for r in rows),'half_bit_mismatches_known':sum(r['half_bit_mismatches']or 0 for r in rows),'max_absolute_error_known':max((r['max_absolute_error']for r in rows if r['max_absolute_error']is not None),default=None),'range_violations_known':sum(r['range_covered']is False for r in rows),'max_known_box_width':max((r['max_box_width']for r in rows if r['max_box_width']is not None),default=None)}
    root=Path(__file__).parent;r={'reference_model':'iPhone17,3','build':'24A446','metrics':metrics,'original_complete_functions_sha256':original,'original_bodies_modified':False,'stats_field_indices':[[2,4],[3,4],[5,0],[6,6],[6,4]],'stats_reconstructed_from_photo':False,'source_sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest()for n in ['pixel_bright.py','pixel_skin.py','pixel_color.py','pixel_leaves.py','leaf_domains.py','leaf_numeric.py','leaf_host.py','native_bright_check.py']},'host_ir_sha256':hashlib.sha256(ir.encode()).hexdigest(),'host_math_sha256':hashlib.sha256(MATH_C.encode()).hexdigest(),'input_sha256':inputs.hexdigest(),'output_sha256':hashlib.sha256(np.array(outputs,dtype='f4').tobytes()).hexdigest(),'rows':rows,'GPU_executed':False,'old_batches_repeated':False,'full_pipeline_verified':False,'set_error_allowances_are_host_assumptions':True}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    if metrics['range_violations_known']:raise AssertionError('Original helper output outside model set; receipt retained')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.output);print(json.dumps(r['metrics']))
