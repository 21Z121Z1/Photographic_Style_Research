"""New complete pre393 main composition, using original recursive helpers."""
import argparse,ctypes,hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from leaf_numeric import V
from texture_numeric import Texture,PixelFormat,rgba
from semantic_tone import Curve1D
from cast_values import CastValues
from ltm_preprocess import Parameters as Pre
from typed_bgfg import Fields
from main_pre393 import Controls,forward
from main_pre393_host import build,C_SOURCE,OBSERVATIONS
from native_guided_check import texture


def fixtures():
    y,x=np.mgrid[:3,:4];primary=rgba(V.value(np.stack([.5+.02*x,.45+.02*y,.4+.01*x],axis=2))).lo.astype('f2');linear=(primary.astype('f4')*np.array([.4,.55,.7,1],dtype='f4')).astype('f2');g8=(.2+.04*x+.03*y)[...,None].astype('f2');g9=(.35+.02*x+.01*y)[...,None].astype('f2');person=(.4+.03*x)[...,None].astype('f2');skin=(.25+.02*y+np.zeros_like(x))[...,None].astype('f2');sky=np.full((3,4,1),.2,dtype='f2');bg=rgba(V.value(np.full((3,4,3),.9))).lo.astype('f2');fg=rgba(V.value(np.full((3,4,3),1.1))).lo.astype('f2');columns=np.array([[1,.01,0],[.01,1,.02],[0,-.01,1]],dtype='f4');sem=np.array([.6,.8,.9,1.1,.6,.3,.4],dtype='f4');bp=np.zeros(17,dtype='f4');bp[[0,1,3,7,8,11]]=[.04,.03,.04,.025,.95,1];fp=np.zeros(16,dtype='f4');fp[[0,2,4,5,7,11]]=[.3,.02,.02,1,.02,.05]
    for i,(version,srl,color,tone,cast,hint)in enumerate([(0,.4,-.3,-.2,2,-1),(1,.4,.3,.2,0,.6),(2,2.4,.15,0,2,-1),(2,.4,0,.2,0,.6),(0,.4,.3,.2,0,-1)]):
        images=[primary.copy(),linear.copy(),None,None,None,bg,fg,g8,g9,person,skin,sky,None]
        if i<2:images[5]=None;images[6]=None
        if i==4:images[0][...,:3]=0;images[1][...,:3]=0;images[5]=None;images[6]=None
        transforms={k:np.array([.25,1/3,0,0],dtype='f4')for k in range(3,12)};transforms[5][2:]=[-.05,.04];transforms[6][2:]=[.07,-.03]
        yield {'index':i,'images':images,'columns':columns,'semantic':sem,'bg':bp,'fg':fp,'version':version,'SRL':np.float32(srl),'color':np.float32(color),'tone':np.float32(tone),'cast':cast,'hint':np.float32(hint),'transforms':transforms,'grid':(i%3,i%2),'intensity':np.float32(.7),'scale':np.float32(.9),'baseline':np.float32(.8),'boost':np.float32(4),'threshold':np.float32(.8)}


def model(f,point):
    h=lambda x:V.value(x)if point else V.bounds(x,x)
    fp=lambda x:V.value(x,'f')if point else V.bounds(x,x,'f')
    def tex(i):
        if f['images'][i]is None:return None
        return Texture(h(f['images'][i]),PixelFormat.R16Float if f['images'][i].shape[2]==1 else PixelFormat.RGBA16Float,'synthetic gain map working domain'if i in(5,6)else'synthetic role'+str(i))
    raw=np.zeros(34,dtype='f4');raw[33]=f['threshold'];gtc=Curve1D(tuple(np.linspace(0,1,17)**.8),'GTC');whites=Curve1D(tuple(np.linspace(0,1,17)**1.1),'whites')
    return forward(tex(0),tex(1),tex(7),tex(8),tex(9),tex(10),tex(11),(tex(5),tex(6)),grid=f['grid'],transforms={k:fp(v)for k,v in f['transforms'].items()},pre_parameters=Pre(fp(f['SRL']),fp(f['columns']),3,False,False),linear_CCM_columns=fp(f['columns']),controls=Controls(f['cast'],f['version'],fp(f['intensity']),fp(f['tone']),fp(f['color']),fp(f['scale']),fp(f['baseline']),fp(f['hint']),fp(f['boost'])),cast=CastValues(fp(raw)),semantic7=fp(f['semantic']),helper_fields=Fields(fp(f['bg']),fp(f['fg'])),gtc=gtc,whites=whites,input_branch_decisions=('explicit synthetic caller controls; no coefficient centers',))


def check(source,output):
    if output.exists():raise FileExistsError(output)
    ir,meta=build(source.read_text());rows=[];inputhash=hashlib.sha256();outputhash=hashlib.sha256()
    with tempfile.TemporaryDirectory(prefix='psr-main-pre393-')as t:
        w=Path(t);(w/'main.ll').write_text(ir);(w/'shim.c').write_text(C_SOURCE);c=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',str(w/'main.ll'),str(w/'shim.c'),'-o',str(w/'main.dylib')],capture_output=True,text=True,timeout=60)
        if c.returncode:raise RuntimeError(c.stderr[:4000])
        lib=ctypes.CDLL(str(w/'main.dylib'));fn=lib.psr_main_pre;fn.argtypes=[ctypes.c_void_p]*6+[ctypes.c_int32]+[ctypes.c_uint16]*2+[ctypes.c_void_p];fn.restype=None
        for f in fixtures():
            arrays=[None if a is None else texture(a)for a in f['images']];arrays[2]=texture(np.array(Curve1D(tuple(np.linspace(0,1,17)**.8),'GTC').red_samples,dtype='f2')[None,:,None]);arrays[3]=texture(np.array(Curve1D(tuple(np.linspace(0,1,17)**1.1),'whites').red_samples,dtype='f2')[None,:,None]);ptrs=(ctypes.c_void_p*13)(*[None if a is None else a.ctypes.data for a in arrays]);management=np.zeros(80,dtype='f4');management.view('u4')[0]=3
            for slot in [0,1]:
                for col in range(3):management[20*slot+4+4*col:20*slot+7+4*col]=f['columns'][col]
            params=np.zeros(168,dtype='f4');params.view('u4')[0]=f['cast'];params[1:4]=[f['intensity'],f['tone'],f['color']];params[6:8]=[f['scale'],f['baseline']];params[167]=f['hint'];params[42]=f['threshold'];params[111]=f['boost'];params[122:139]=f['bg'];params[139:155]=f['fg'];params[155:162]=f['semantic'];roi=np.zeros(44,dtype='f4')
            for k,v in f['transforms'].items():roi[4*(k-3)+4:4*(k-3)+8]=v
            # First3 ushort2 fields consume12B, then float4 alignment at16B.
            stats=np.zeros(2660,dtype='f4');srl=np.array([f['SRL']],dtype='f4');out=np.zeros(meta['observation_float_count'],dtype='f4');inputhash.update(b''.join(a.tobytes()for a in arrays if a is not None)+management.tobytes()+params.tobytes()+roi.tobytes()+srl.tobytes());fn(ptrs,management.ctypes.data,params.ctypes.data,stats.ctypes.data,roi.ctypes.data,srl.ctypes.data,f['version'],*f['grid'],out.ctypes.data);outputhash.update(out.tobytes()+params[155:162].tobytes());row={'case':f['index'],'cast':f['cast'],'version':f['version'],'SRL':float(f['SRL']),'color_f32':float(f['color']),'tone_f32':float(f['tone']),'maps_present':arrays[5]is not None,'native_output_half_bits':out.astype('f2').view('u2').tolist(),'native_nonfinite':int(np.count_nonzero(~np.isfinite(out))),'native_post_semantic_f32':params[155:162].tolist(),'point':{},'set':{}}
            for point in [True,False]:
                m=model(f,point);r=row['point'if point else'set'];r['unknown_operator']=m.unknown_operator;r['unknown_reason']=m.unknown_reason;offset=0
                for name,ssa,n in OBSERVATIONS:
                    actual=out[offset:offset+n]if n==3 else out[offset];offset+=n
                    if name not in m.observations:continue
                    v=m.observations[name]
                    if point:r[name]={'half_bit_mismatches':int(np.count_nonzero(np.asarray(actual,dtype='f2').view('u2')!=v.lo.astype('f2').view('u2'))),'max_absolute_error':float(np.max(abs(actual-v.lo)))}
                    else:r[name]={'range_covered':bool(np.isfinite(actual).all()and np.all(actual>=v.lo)and np.all(actual<=v.hi)),'max_width':float(np.max(v.hi-v.lo))}
                if m.post_semantic7 is not None:
                    if point:r['post_semantic7']={'f32_bit_mismatches':int(np.count_nonzero(params[155:162].view('u4')!=m.post_semantic7.lo.astype('f4').view('u4'))),'max_absolute_error':float(np.max(abs(params[155:162]-m.post_semantic7.lo)))}
                    else:r['post_semantic7']={'range_covered':bool(np.all(params[155:162]>=m.post_semantic7.lo)and np.all(params[155:162]<=m.post_semantic7.hi)),'max_width':float(np.max(m.post_semantic7.hi-m.post_semantic7.lo))}
            rows.append(row)
    metrics={'calls':len(rows),'known_point_rows':sum(r['point']['unknown_operator']is None for r in rows),'set_unknown_rows':sum(r['set']['unknown_operator']is not None for r in rows),'known_set_violations':sum(v.get('range_covered')is False for r in rows for k,v in r['set'].items()if isinstance(v,dict))}
    root=Path(__file__).parent;r={'scope':__doc__,'hardware':'iPhone17,3','build':'24A446','original':meta,'metrics':metrics,'host_IR_sha256':hashlib.sha256(ir.encode()).hexdigest(),'C_sha256':hashlib.sha256(C_SOURCE.encode()).hexdigest(),'source_sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest()for n in ['main_pre393.py','main_pre393_host.py','native_main_pre393_check.py','typed_bgfg.py','pre_skin_color.py','ltm_gain.py','ltm_preprocess.py']},'input_sha256':inputhash.hexdigest(),'output_sha256':outputhash.hexdigest(),'rows':rows,'GPU_executed':False,'old_accepted_batches_repeated':False,'parameter_buffer_reset_per_single_context':True,'actual_input_dependencies':'synthetic raw textures,ROI,CCM,cast34,BG17/FG16/semantic7,caller controls; none recovered from a photograph'}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    if metrics['known_set_violations']:raise AssertionError('Known set violation; receipt retained')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.output);print(json.dumps(r['metrics']))
