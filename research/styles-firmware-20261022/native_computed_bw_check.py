"""New original outer+actual BW cases, with three independent internal outputs."""
import argparse,ctypes,hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from leaf_numeric import V
from computed_bw_host import build,MATH_C
from computed_bw_outer import forward
from pixel_bw import Parameters
from semantic_tone import Curve1D


def cases():
    for rgb in [[.2,.4,.8],[.7,.45,.3],[.4,.4,.4]]:
        for cast0,cast245,tuning in [(4,2,5),(4,4,2),(15,2,5),(15,3,2),(0,4,5),(0,3,2)]:
            data=np.array([*rgb,.25,.45,.65,.6,.3,.3,.25,.75,tuning,cast245,.4,cast0,.4],dtype='f4');data[:7]=data[:7].astype('f2').astype('f4');data[13]=np.float16(data[13]);yield data


def model(data,curve,point):
    h=lambda x:V.value(x)if point else V.bounds(x,x)
    f=lambda x:V.value(x,'f')if point else V.bounds(x,x,'f')
    p=Parameters(f(data[7]),f(data[15]),f(data[8]),int(data[14]),int(data[11]))
    return forward(h(data[:3]),h(data[3:6]),h(data[13]),h(data[6]),f(data[9]),f(data[10]),parameters=p,raw_cast_type245=int(data[12]),whites=curve)


def check(source,output):
    if output.exists():raise FileExistsError(output)
    ir,metadata=build(source.read_text());curve=Curve1D(tuple(np.linspace(0,1,17)**.8),'supplied whites working curve');tex=np.r_[np.array([17],dtype='u4').view('f4'),np.array(curve.red_samples,dtype='f4')];rows=[];ih=hashlib.sha256();outputs=[]
    with tempfile.TemporaryDirectory(prefix='psr-computed-bw-')as t:
        w=Path(t);(w/'source.ll').write_text(ir);(w/'math.c').write_text(MATH_C)
        c=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',str(w/'source.ll'),str(w/'math.c'),'-o',str(w/'helper.dylib')],capture_output=True,text=True,timeout=60)
        if c.returncode:raise RuntimeError(c.stderr[:5000])
        lib=ctypes.CDLL(str(w/'helper.dylib'));fn=lib.psr_outer_bw;fn.argtypes=[ctypes.c_void_p]*3
        for data in cases():
            native=np.zeros(3,dtype='f4');fn(data.ctypes.data,tex.ctypes.data,native.ctypes.data)
            outer=np.ctypeslib.as_array((ctypes.c_float*3).in_dll(lib,'psr_outer_tonal')).copy();bw=np.ctypeslib.as_array((ctypes.c_float*6).in_dll(lib,'psr_bw_trace')).copy();observed={'tonal468':outer,'stark12':bw[:3],'tonal67':bw[3:],'output492':native};ih.update(data.tobytes()+tex.tobytes());outputs.append(np.r_[outer,bw,native]);row={'input':data.tolist(),'observed':{k:v.tolist()for k,v in observed.items()}}
            for point in [True,False]:
                result=model(data,curve,point);values={'tonal468':None if result.outer is None else result.outer.tonal468,'stark12':None if result.bw is None else result.bw.stark12,'tonal67':None if result.bw is None else result.bw.tonal67,'output492':result.output492}
                row['point_reason'if point else'set_reason']=result.unknown_reason
                for name,actual in observed.items():
                    v=values[name];entry=row.setdefault(name,{})
                    if point:entry.update(point_unknown=v is None,half_bit_mismatches=None if v is None else int(np.count_nonzero(actual.astype('f2').view('u2')!=v.lo.astype('f2').view('u2'))),max_absolute_error=None if v is None else float(np.max(abs(actual-v.lo))))
                    else:entry.update(set_unknown=v is None,range_covered=None if v is None else bool(np.isfinite(actual).all()and np.all(actual>=v.lo)and np.all(actual<=v.hi)),max_box_width=None if v is None else float(np.max(v.hi-v.lo)))
            rows.append(row)
    metrics={}
    for name in ['tonal468','stark12','tonal67','output492']:
        a=[r[name]for r in rows];metrics[name]={'calls':len(a),'point_unknown':sum(x['point_unknown']for x in a),'set_unknown':sum(x['set_unknown']for x in a),'half_bit_mismatches_known':sum(x['half_bit_mismatches']or 0 for x in a),'max_absolute_error_known':max((x['max_absolute_error']for x in a if x['max_absolute_error']is not None),default=None),'range_violations_known':sum(x['range_covered']is False for x in a),'max_known_box_width':max((x['max_box_width']for x in a if x['max_box_width']is not None),default=None)}
    root=Path(__file__).parent;r={'model':'iPhone17,3','build':'24A446','metrics':metrics,'BW477_output_supplied_externally':False,'original_BW477_call_reconnected':True,'metadata':metadata,'observation_memory_summary_corrected':'BW memory(read)->memory(readwrite), all floating-point attributes preserved','source_sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest()for n in ['native_computed_bw_check.py','computed_bw_host.py','computed_bw_outer.py','bw_host.py','pixel_bw.py','outer_cast.py','outer_cast_host.py','leaf_host.py']},'host_ir_sha256':hashlib.sha256(ir.encode()).hexdigest(),'host_math_sha256':hashlib.sha256(MATH_C.encode()).hexdigest(),'input_sha256':ih.hexdigest(),'output_sha256':hashlib.sha256(np.array(outputs,dtype='f4').tobytes()).hexdigest(),'rows':rows,'old_batches_repeated':False,'GPU_executed':False,'full_pipeline_verified':False}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    if any(m['range_violations_known']for m in metrics.values()):raise AssertionError('Original full outer/BW observation outside set; receipt retained')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.output);print(json.dumps(r['metrics']))
