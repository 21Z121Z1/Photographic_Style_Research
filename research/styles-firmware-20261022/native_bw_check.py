"""New BW root checks with explicit curve and separate stark/tonal observations."""
import argparse,ctypes,hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from leaf_numeric import V,DomainUnknown
from bw_host import build,MATH_C
from pixel_bw import Parameters,forward
from semantic_tone import Curve1D


def cases():
    for rgb in [[.2,.4,.8],[.7,.45,.3],[.4,.4,.4],[0,0,0]]:
        for cast in [0,4,15]:
            for tuning in [2,5]:
                for guide,person,parameter2 in [(.1,.2,-.3),(.8,.8,.3)]:
                    yield np.r_[np.array([*rgb,guide,person],dtype='f2').astype('f4'),np.array([parameter2,.4,.3,cast,tuning],dtype='f4')].astype('f4')


def model(data,curve,point):
    h=lambda x:V.value(x)if point else V.bounds(x,x)
    f=lambda x:V.value(x,'f')if point else V.bounds(x,x,'f')
    p=Parameters(f(data[5]),f(data[6]),f(data[7]),int(data[8]),int(data[9]))
    return forward(h(data[:3]),h(data[3]),h(data[4]),p,curve)


def check(source,output):
    if output.exists():raise FileExistsError(output)
    ir,functions=build(source.read_text());curve=Curve1D(tuple(np.linspace(0,1,17)**.8),'explicit whites curve working coordinate');tex=np.r_[np.array([17],dtype='u4').view('f4'),np.array(curve.red_samples,dtype='f4')];ih=hashlib.sha256();outputs=[];rows=[]
    with tempfile.TemporaryDirectory(prefix='psr-bw-')as t:
        w=Path(t);(w/'source.ll').write_text(ir);(w/'math.c').write_text(MATH_C)
        c=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',str(w/'source.ll'),str(w/'math.c'),'-o',str(w/'helper.dylib')],capture_output=True,text=True,timeout=60)
        if c.returncode:raise RuntimeError(c.stderr[:4000])
        lib=ctypes.CDLL(str(w/'helper.dylib'));fn=lib.psr_leaf_0;fn.argtypes=[ctypes.c_void_p]*3
        for data in cases():
            native=np.zeros(3,dtype='f4');fn(data.ctypes.data,tex.ctypes.data,native.ctypes.data);trace=np.ctypeslib.as_array((ctypes.c_float*6).in_dll(lib,'psr_bw_trace')).copy()
            observed={'stark12':trace[:3],'tonal67':trace[3:],'output477':native};outputs.append(np.r_[trace,native]);ih.update(data.tobytes()+tex.tobytes());row={'input':data.tolist(),'observed':{k:v.tolist()for k,v in observed.items()}}
            for point in [True,False]:
                m=model(data,curve,point)
                for name,actual in observed.items():
                    value=getattr(m,name);entry=row.setdefault(name,{})
                    if point:
                        entry['point_unknown']=value is None
                        entry['half_bit_mismatches']=None if value is None else int(np.count_nonzero(actual.astype('f2').view('u2')!=value.lo.astype('f2').view('u2')))
                        entry['max_absolute_error']=None if value is None else float(np.max(abs(actual-value.lo)))
                    else:
                        entry['set_unknown']=value is None;entry['range_covered']=None if value is None else bool(np.isfinite(actual).all()and np.all(actual>=value.lo)and np.all(actual<=value.hi))
                        entry['max_box_width']=None if value is None else float(np.max(value.hi-value.lo))
                row['point_reasons'if point else'set_reasons']=m.unknowns
            rows.append(row)
    metrics={}
    for name in ['stark12','tonal67','output477']:
        a=[r[name]for r in rows];metrics[name]={'calls':len(a),'point_unknown':sum(x['point_unknown']for x in a),'set_unknown':sum(x['set_unknown']for x in a),'half_bit_mismatches_known':sum(x['half_bit_mismatches']or 0 for x in a),'max_absolute_error_known':max((x['max_absolute_error']for x in a if x['max_absolute_error']is not None),default=None),'range_violations_known':sum(x['range_covered']is False for x in a),'max_known_box_width':max((x['max_box_width']for x in a if x['max_box_width']is not None),default=None)}
    root=Path(__file__).parent;r={'reference_model':'iPhone17,3','build':'24A446','metrics':metrics,'original_complete_functions_sha256':functions,'original_arithmetic_or_predicates_changed':False,'observation_stores_added':['stark12','tonal67'],'curve_is_explicit_not_recovered':True,'curve_half_sha256':hashlib.sha256(np.array(curve.red_samples,dtype='f2').tobytes()).hexdigest(),'raw_cast_SSRParams0_distinct_from_resolved245':True,'source_sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest()for n in ['native_bw_check.py','bw_host.py','pixel_bw.py','outer_cast.py','leaf_host.py','leaf_numeric.py','leaf_domains.py','pixel_leaves.py']},'host_ir_sha256':hashlib.sha256(ir.encode()).hexdigest(),'host_math_sha256':hashlib.sha256(MATH_C.encode()).hexdigest(),'input_sha256':ih.hexdigest(),'output_sha256':hashlib.sha256(np.array(outputs,dtype='f4').tobytes()).hexdigest(),'rows':rows,'old_batches_repeated':False,'GPU_executed':False,'full_pipeline_verified':False}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    if any(m['range_violations_known']for m in metrics.values()):raise AssertionError('Original BW value outside model set; receipt retained')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.output);print(json.dumps(r['metrics']))
