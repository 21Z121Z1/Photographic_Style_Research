"""New AIR7 gain core host comparison, explicit upstream96/98 and CCM."""
import argparse,ctypes,hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from leaf_numeric import V,vec,DomainUnknown,hc
from ltm_gain import Parameters,forward
from semantic_tone import Curve1D
from air7_gain_host import build,MATH_C


def cases():
    for linear in [[.2,.4,.8],[.7,.45,.3],[0,0,0]]:
        for scale,params in [(.8,[.6,.8,.7,1.2,.6,.3,.4]),(1.1,[.6,.8,1.2,.8,.4,.3,.4])]:
            yield np.r_[np.array([.25,.5,1,*linear],dtype='f2').astype('f4'),np.array([[1,.02,0],[.01,1,.03],[0,-.01,1]],dtype='f4').flat,scale,params].astype('f4')
    eps=np.float16(hc('1c04'))
    for ref in [np.nextafter(eps,np.float16(0)),eps,np.nextafter(eps,np.float16(1)),np.float16(0)]:
        yield np.r_[np.array([ref,ref,ref,.2,.4,.8],dtype='f2').astype('f4'),np.eye(3,dtype='f4').flat,1,[.6,.8,.7,1.2,.6,.3,.4]].astype('f4')


def model(data,curve,point):
    h=lambda x:V.value(x)if point else V.bounds(x,x)
    f=lambda x:V.value(x,'f')if point else V.bounds(x,x,'f')
    r=forward(h(data[:3]),h(data[3:6]),Parameters(f(data[6:15].reshape(3,3)),f(data[15]),f(data[16:23])),curve)
    return vec([r.bg203[i]for i in range(3)]+[r.fg205[i]for i in range(3)]+[r.transformed_linear121[i]for i in range(3)])


def check(source,output):
    if output.exists():raise FileExistsError(output)
    ir,original=build(source.read_text());rows=[];inputs=hashlib.sha256();outs=[];curve=Curve1D(tuple(np.linspace(0,1,17)**.8),'AIR7 supplied GTC pixel-index domain');tex=np.r_[np.array([17],dtype='u4').view('f4'),np.array(curve.red_samples,dtype='f4')]
    with tempfile.TemporaryDirectory(prefix='psr-ltm-core-')as t:
        w=Path(t);(w/'source.ll').write_text(ir);(w/'math.c').write_text(MATH_C)
        c=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',str(w/'source.ll'),str(w/'math.c'),'-o',str(w/'helper.dylib')],capture_output=True,text=True,timeout=60)
        if c.returncode:raise RuntimeError(c.stderr[:4000])
        lib=ctypes.CDLL(str(w/'helper.dylib'));fn=lib.psr_gain;fn.argtypes=[ctypes.c_void_p]*3
        for data in cases():
            native=np.zeros(9,dtype='f4');fn(data.ctypes.data,tex.ctypes.data,native.ctypes.data);inputs.update(data.tobytes()+tex.tobytes());outs.append(native.copy());row={'input':data.tolist(),'native_half_bits':native.astype('f2').view('u2').tolist(),'native_nonfinite':int(np.count_nonzero(~np.isfinite(native)))}
            for point in [True,False]:
                try:
                    v=model(data,curve,point)
                    if point:row.update(point_unknown=None,half_bit_mismatches=int(np.count_nonzero(native.astype('f2').view('u2')!=v.lo.astype('f2').view('u2'))),max_absolute_error=float(np.max(abs(native-v.lo))))
                    else:row.update(set_unknown=None,range_covered=bool(np.isfinite(native).all()and np.all(native>=v.lo)and np.all(native<=v.hi)),max_set_width=float(np.max(v.hi-v.lo)))
                except DomainUnknown as e:row['point_unknown'if point else'set_unknown']=str(e)
            rows.append(row)
    metrics={'calls':len(rows),'point_unknown':sum(x['point_unknown']is not None for x in rows),'set_unknown':sum(x['set_unknown']is not None for x in rows),'half_bit_mismatches_known':sum(x.get('half_bit_mismatches',0)for x in rows),'max_absolute_error_known':max((x.get('max_absolute_error',0)for x in rows),default=0),'range_violations_known':sum(x.get('range_covered')is False for x in rows),'max_set_width_known':max((x.get('max_set_width',0)for x in rows),default=0)}
    r={'hardware':'iPhone17,3','OS_build':'24A446','scope':__doc__,'original':original,'metrics':metrics,'source_sha256':{n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest()for n in ['ltm_gain.py','air7_gain_host.py','native_ltm_gain_check.py','leaf_numeric.py','pixel_leaves.py','semantic_tone.py']},'IR_sha256':hashlib.sha256(ir.encode()).hexdigest(),'shim_C_sha256':hashlib.sha256(MATH_C.encode()).hexdigest(),'input_sha256':inputs.hexdigest(),'output_sha256':hashlib.sha256(np.array(outs,dtype='f4').tobytes()).hexdigest(),'curve_half_samples':list(curve.red_samples),'rows':rows,'GPU_executed':False,'guided_filter_applied':False,'sampler':'ideal pixel-linear clamp host shim; not GPU interpolation proof','set_error_budget':'existing 2u half/4u f32 assumption','upstream_reference96_linear98_CCM_scale_semantic_are_supplied':True,'old_accepted_batches_repeated':False}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    if metrics['range_violations_known']:raise AssertionError('Known set violation, receipt retained')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.output);print(json.dumps(r['metrics']))
