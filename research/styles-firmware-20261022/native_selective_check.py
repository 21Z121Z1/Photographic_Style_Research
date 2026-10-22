"""New complete selective root cases with deterministic nonconstant RGBA rows."""
import argparse,ctypes,hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from selective_host import build
from leaf_numeric import V,DomainUnknown
from cast_values import CastValues
from pixel_selective import SelectiveTexture,forward


def texture():
    x=np.arange(360,dtype='f8')*np.pi/180;rows=[]
    for row in range(4):rows.append(np.stack([.02*np.sin(x+row),.05*np.cos(x+row),.03*np.cos(2*x+row),.04*np.sin(2*x+row)],axis=-1))
    return SelectiveTexture(np.array(rows,dtype='f2'),'explicit synthetic selective hue/saturation/luminance/gamma coefficients')


def cases():
    for rgb in [[.2,.4,.8],[.8,.3,.15],[.4,.4,.4],[0,0,0]]:
        for weights in [[.2,.3,.4,.8],[.8,.7,.1,.2]]:
            for enabled in [False,True]:
                raw=np.zeros(34,dtype='f4');raw[18:27]=[.8,.4,.2,.2,.7,.4,.3,.4,.8]
                if enabled:raw[15:18]=[.2,.1,.15]
                yield np.r_[np.array([*rgb,*weights],dtype='f2').astype('f4'),raw].astype('f4')


def model(data,tex,point):
    h=lambda x:V.value(x)if point else V.bounds(x,x)
    f=lambda x:V.value(x,'f')if point else V.bounds(x,x,'f')
    return forward(h(data[:3]),CastValues(f(data[7:41])),tex,*[h(x)for x in data[3:7]])


def check(source,output):
    if output.exists():raise FileExistsError(output)
    ir,functions,math=build(source.read_text());tex=texture();packed=np.r_[np.array([360,4],dtype='u4').view('f4'),tex.values.astype('f4').ravel()];rows=[];ih=hashlib.sha256();outputs=[]
    with tempfile.TemporaryDirectory(prefix='psr-selective-')as t:
        w=Path(t);(w/'source.ll').write_text(ir);(w/'math.c').write_text(math)
        c=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',str(w/'source.ll'),str(w/'math.c'),'-o',str(w/'helper.dylib')],capture_output=True,text=True,timeout=60)
        if c.returncode:raise RuntimeError(c.stderr[:4000])
        lib=ctypes.CDLL(str(w/'helper.dylib'));fn=lib.psr_leaf_0;fn.argtypes=[ctypes.c_void_p]*3
        for data in cases():
            native=np.zeros(3,dtype='f4');fn(data.ctypes.data,packed.ctypes.data,native.ctypes.data);outputs.append(native.copy());ih.update(data.tobytes());row={'input':data.tolist(),'native_half_output':native.tolist(),'native_nonfinite':int(np.count_nonzero(~np.isfinite(native)))}
            for point in [True,False]:
                try:
                    value=model(data,tex,point)
                    if point:row.update(point_unknown=None,half_bit_mismatches=int(np.count_nonzero(native.astype('f2').view('u2')!=value.lo.astype('f2').view('u2'))),max_absolute_error=float(np.max(abs(native-value.lo))))
                    else:row.update(set_unknown=None,range_covered=bool(np.isfinite(native).all()and np.all(native>=value.lo)and np.all(native<=value.hi)),max_box_width=float(np.max(value.hi-value.lo)))
                except DomainUnknown as error:
                    if point:row.update(point_unknown=str(error),half_bit_mismatches=None,max_absolute_error=None)
                    else:row.update(set_unknown=str(error),range_covered=None,max_box_width=None)
            rows.append(row)
    metrics={'calls':len(rows),'point_unknown':sum(r['point_unknown']is not None for r in rows),'set_unknown':sum(r['set_unknown']is not None for r in rows),'half_bit_mismatches_known':sum(r['half_bit_mismatches']or 0 for r in rows),'max_absolute_error_known':max((r['max_absolute_error']for r in rows if r['max_absolute_error']is not None),default=None),'range_violations_known':sum(r['range_covered']is False for r in rows),'max_known_box_width':max((r['max_box_width']for r in rows if r['max_box_width']is not None),default=None)}
    root=Path(__file__).parent;r={'model':'iPhone17,3','build':'24A446','metrics':metrics,'original_complete_functions_sha256':functions,'original_bodies_modified':False,'texture_shape':[4,360,4],'texture_half_sha256':hashlib.sha256(tex.values.tobytes()).hexdigest(),'texture_generation_is_synthetic':True,'sampler_contract':'Normalized bilinear/clamp, f32 interpolation then half, explicit host assumption','source_sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest()for n in ['native_selective_check.py','selective_host.py','pixel_selective.py','precomputed_semantic.py','pixel_color.py','pixel_skin.py','leaf_numeric.py','cast_values.py','leaf_host.py']},'host_ir_sha256':hashlib.sha256(ir.encode()).hexdigest(),'host_math_sha256':hashlib.sha256(math.encode()).hexdigest(),'input_sha256':ih.hexdigest(),'output_sha256':hashlib.sha256(np.array(outputs,dtype='f4').tobytes()).hexdigest(),'rows':rows,'GPU_executed':False,'old_batches_repeated':False,'lookup_producer_recovered':False,'full_pipeline_verified':False}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    if metrics['range_violations_known']:raise AssertionError('Original helper output outside declared box; receipt retained')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.output);print(json.dumps(r['metrics']))
