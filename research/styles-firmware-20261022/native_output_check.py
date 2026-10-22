"""New original568..600 composition checks with independent linear/gain output."""
import argparse,ctypes,hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from leaf_numeric import V,vec,DomainUnknown
from pixel_output import Parameters,forward
from output_host import build,MATH_C


def cases():
    columns=np.array([[1,.02,0],[.01,1,.03],[0,-.01,1]],dtype='f4')
    for rgb in [[.2,.4,.8],[.7,.45,.3],[0,0,0]]:
        for inc,outc,gain in [(3,3,1),(6,6,.7),(6,7,1.2)]:yield np.r_[np.array([*rgb,gain],dtype='f2').astype('f4'),np.float32(.4),inc,columns.flat,outc].astype('f4')
    yield np.r_[np.array([.2,.4,.8,0],dtype='f2').astype('f4'),np.float32(.4),6,columns.flat,3].astype('f4')


def model(data,point):
    h=lambda x:V.value(x)if point else V.bounds(x,x)
    f=lambda x:V.value(x,'f')if point else V.bounds(x,x,'f')
    p=Parameters(h(data[3]),f(data[4]),f(data[6:15].reshape(3,3)),int(data[5]),int(data[15]));r=forward(h(data[:3]),p)
    return vec([r.output600[i]for i in range(3)]+[r.linear597[i]for i in range(3)]+[r.gain577])


def check(source,output):
    if output.exists():raise FileExistsError(output)
    ir,original=build(source.read_text());rows=[];inputhash=hashlib.sha256();outputhash=hashlib.sha256()
    with tempfile.TemporaryDirectory(prefix='psr-output-')as t:
        w=Path(t);(w/'source.ll').write_text(ir);(w/'math.c').write_text(MATH_C);c=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',str(w/'source.ll'),str(w/'math.c'),'-o',str(w/'helper.dylib')],capture_output=True,text=True,timeout=60)
        if c.returncode:raise RuntimeError(c.stderr[:4000])
        lib=ctypes.CDLL(str(w/'helper.dylib'));fn=lib.psr_output;fn.argtypes=[ctypes.c_void_p]*2;fn.restype=None
        for data in cases():
            native=np.zeros(7,dtype='f4');fn(data.ctypes.data,native.ctypes.data);inputhash.update(data.tobytes());outputhash.update(native.tobytes());row={'input':data.tolist(),'native_half_bits':native.astype('f2').view('u2').tolist(),'native_nonfinite':int(np.count_nonzero(~np.isfinite(native)))}
            for point in [True,False]:
                try:
                    v=model(data,point)
                    if point:row.update(point_unknown=None,half_bit_mismatches=int(np.count_nonzero(native.astype('f2').view('u2')!=v.lo.astype('f2').view('u2'))),max_absolute_error=float(np.max(abs(native-v.lo))))
                    else:row.update(set_unknown=None,range_covered=bool(np.isfinite(native).all()and np.all(native>=v.lo)and np.all(native<=v.hi)),max_set_width=float(np.max(v.hi-v.lo)))
                except DomainUnknown as error:row['point_unknown'if point else'set_unknown']=str(error)
            rows.append(row)
    metrics={'calls':len(rows),'point_unknown':sum(r['point_unknown']is not None for r in rows),'set_unknown':sum(r['set_unknown']is not None for r in rows),'half_bit_mismatches_known':sum(r.get('half_bit_mismatches',0)for r in rows),'max_absolute_error_known':max((r.get('max_absolute_error',0)for r in rows),default=0),'range_violations_known':sum(r.get('range_covered')is False for r in rows),'max_set_width_known':max((r.get('max_set_width',0)for r in rows),default=0)}
    r={'scope':__doc__,'hardware':'iPhone17,3','build':'24A446','original':original,'metrics':metrics,'source_sha256':{n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest()for n in ['pixel_output.py','output_host.py','native_output_check.py','pixel_transfer.py','leaf_host.py','leaf_numeric.py']},'host_IR_sha256':hashlib.sha256(ir.encode()).hexdigest(),'host_C_sha256':hashlib.sha256(MATH_C.encode()).hexdigest(),'input_sha256':inputhash.hexdigest(),'output_sha256':outputhash.hexdigest(),'rows':rows,'GPU_or_image_writer_executed':False,'old_accepted_batches_repeated':False,'input_dependencies':['RGB567','reference gain176 half','parameter2 f32','input enum136','output CCM columns f32','output enum599'],'set_2u_4u_is_assumption':True}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    if metrics['range_violations_known']:raise AssertionError('Known set violation, receipt retained')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.output);print(json.dumps(r['metrics']))
