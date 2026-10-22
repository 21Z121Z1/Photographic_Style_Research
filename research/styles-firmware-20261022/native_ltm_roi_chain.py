"""New full original AIR7/guided/block290 composition with intermediate probes."""
import argparse,ctypes,hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from leaf_numeric import V
from texture_numeric import Texture,PixelFormat,ROI,rgba
from ltm_preprocess import Parameters as Pre
from ltm_gain import Parameters as Gain
from semantic_tone import Curve1D
from full_ltm_chain import forward
from air7_full_host import build as producer_build,C_SOURCE
from guided_host import build as guided_build
from block290_host import build as consumer_build
from native_guided_check import native as native_guided,texture,values
from guided_conditioned import Inputs

EPSILON=np.array([0x3a83126f],dtype='u4').view('f4')[0]


def fixture(index):
    h,w=(3,4)if index==0 else(4,5);y,x=np.mgrid[:h,:w];rgb=np.stack([.5+.025*x,.45+.02*y,.4+.015*x+.01*y],axis=2).astype('f2');primary=rgba(V.value(rgb)).lo.astype('f2');guide=primary.copy()
    if index==1:primary=(primary.astype('f4')*np.array([.95,1.02,1.05,1],dtype='f4')).astype('f2')
    yy,xx=np.mgrid[:2,:3];linear=rgba(V.value(np.stack([.2+.01*xx,.25+.02*yy,.3+.01*xx],axis=2))).lo.astype('f2');matte=(.2+.1*xx+.05*yy)[...,None].astype('f2')
    semantic=np.array([.6,.8,.9,1.1,.6,.3,.4],dtype='f4');columns=np.array([[1,.01,0],[.01,1,.02],[0,-.01,1]],dtype='f4')
    return {'primary':primary,'guide':guide,'linear':linear,'matte':matte,'semantic':semantic,'columns':columns,'SRL':np.float32(.4),'use_srl':bool(index),'imageblock':bool(index),'transfer':3,'producer_shape':(2,3),'ROI5':np.array([1/w,1/h,-.07,.04],dtype='f4'),'ROI6':np.array([1/w,1/h,.08,-.05],dtype='f4')}


def model_inputs(f,grid,person,point):
    h=lambda x:V.value(x)if point else V.bounds(x,x)
    fp=lambda x:V.value(x,'f')if point else V.bounds(x,x,'f')
    source=lambda name:Texture(h(f[name]),PixelFormat.RGBA16Float,'synthetic '+name+' explicit working domain')
    return (source('primary'),source('linear'),Texture(h(f['matte']),PixelFormat.R16Float,'synthetic person matte'),source('guide')),dict(producer_shape=f['producer_shape'],pre_parameters=Pre(fp(f['SRL']),fp(f['columns']),f['transfer'],f['use_srl'],False),gain_parameters=Gain(fp(f['columns']),fp(.9),fp(f['semantic'])),consumer_semantic7=fp(f['semantic']),curve=Curve1D(tuple(np.linspace(0,1,17)**.8),'supplied AIR7 GTC'),epsilon=fp(EPSILON),roi=ROI(grid,fp(f['ROI5']),fp(f['ROI6'])),reference196=h([.25,.4,.6]),person96=h(person),input_branch_decisions=('synthetic fixed cast0, explicit producer and post-caller semantic arrays',))


def metric(native,v):
    return {'half_bit_mismatches':int(np.count_nonzero(native.astype('f2').view('u2')!=v.lo.astype('f2').view('u2'))),'max_absolute_error':float(np.max(abs(native.astype('f8')-v.lo))),'components':int(native.size)}


def check(source_dir,output):
    if output.exists():raise FileExistsError(output)
    producer_ir,pm=producer_build((source_dir/'0007.ll.txt').read_text(),observe=True);consumer_ir,cm=consumer_build((source_dir/'0010.ll.txt').read_text());units=[producer_ir];metadata=[pm]
    for i in range(3):ir,m=guided_build((source_dir/f'{90+i:04d}.ll.txt').read_text(),i);units.append(ir);metadata.append(m)
    units.append(consumer_ir);metadata.append(cm);rows=[];inputhash=hashlib.sha256();outputhash=hashlib.sha256();kernel_calls=0
    with tempfile.TemporaryDirectory(prefix='psr-ltm-roi-')as t:
        w=Path(t);paths=[]
        for i,ir in enumerate(units):p=w/f'{i}.ll';p.write_text(ir);paths.append(str(p))
        (w/'shims.c').write_text(C_SOURCE);c=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',*paths,str(w/'shims.c'),'-o',str(w/'chain.dylib')],capture_output=True,text=True,timeout=60)
        if c.returncode:raise RuntimeError(c.stderr[:4000])
        lib=ctypes.CDLL(str(w/'chain.dylib'));produce=lib.psr_produce;produce.argtypes=[ctypes.c_void_p]*9+[ctypes.c_uint8]*2+[ctypes.c_uint16]*2;produce.restype=None;consume=lib.psr_precomputed;consume.argtypes=[ctypes.c_void_p]*6;consume.restype=None
        for index in range(2):
            f=fixture(index);src=[texture(f[n])for n in ['primary','linear']];curve=Curve1D(tuple(np.linspace(0,1,17)**.8),'supplied');ct=texture(np.array(curve.red_samples,dtype='f2')[None,:,None]);matte=texture(f['matte']);bg=texture(np.zeros((2,3,4)));fg=texture(np.zeros((2,3,4)));management=np.zeros(80,dtype='f4');management.view('u4')[0]=3
            for slot in [0,1]:
                for col in range(3):management[20*slot+4+4*col:20*slot+7+4*col]=f['columns'][col]
            params=np.zeros(168,dtype='f4');params[6]=.9;params[155:162]=f['semantic'];srl=np.array([f['SRL']],dtype='f4');traces=[]
            for data in [*src,ct,matte,management,params,srl,f['guide'],f['ROI5'],f['ROI6']]:inputhash.update(data.tobytes())
            for y in range(2):
                line=[]
                for x in range(3):
                    produce(*(v.ctypes.data for v in [*src,ct,matte,bg,fg,management,params,srl]),int(f['use_srl']),int(f['imageblock']),x,y);line.append(np.ctypeslib.as_array((ctypes.c_float*21).in_dll(lib,'psr_producer_trace')).copy().reshape(7,3));kernel_calls+=1
                traces.append(line)
            traces=np.array(traces);native_maps=[values(v,(2,3,4))for v in [bg,fg]];guided=[]
            for image in native_maps:
                guided.append(native_guided(lib,Inputs(image,f['guide'],f['guide'].shape[:2],1,EPSILON,'actual RGBA16 gain working domain')));h,w=f['guide'].shape[:2];kernel_calls+=3*h*w
            textures=[texture(g['output'])for g in guided];roi=np.zeros(44,dtype='f4');roi[12:16]=f['ROI5'];roi[16:20]=f['ROI6'];raw=[]
            for grid,person in [((0,0),.2),((2,1),.6),((7,5),.8)]:
                data=np.r_[np.array(grid,dtype='f4')+.5,np.array([.25,.4,.6,person],dtype='f2').astype('f4')].astype('f4');out=np.zeros(3,dtype='f4');consume(*(v.ctypes.data for v in [data,params,roi,*textures,out]));kernel_calls+=1;probe=np.ctypeslib.as_array((ctypes.c_float*12).in_dll(lib,'psr_consumer_trace')).copy().reshape(4,3);inputhash.update(data.tobytes());outputhash.update(out.tobytes()+probe.tobytes());row={'fixture':index,'grid':grid,'person_half':float(np.float16(person)),'original_producer_imageblock_flag':f['imageblock'],'point':{},'set':{},'native_consumer_output_bits':out.astype('f2').view('u2').tolist(),'native_consumer_probe_bits':probe.astype('f2').view('u2').tolist()}
                for point in [True,False]:
                    args,kw=model_inputs(f,grid,person,point);m=forward(*args,**kw);result=row['point'if point else'set'];result['unknowns']=m.unknowns
                    observations={**m.producer_observations,'raw_BG':None if m.raw_bg is None else m.raw_bg.pixels,'raw_FG':None if m.raw_fg is None else m.raw_fg.pixels}
                    natives={name:traces[:,:,i,:]for i,name in enumerate(['source24','postSRL34','linear37','reference96','working121','BG203','FG205'])};natives.update(raw_BG=native_maps[0],raw_FG=native_maps[1])
                    for side,ng,mg in [('BG',guided[0],m.guided_bg),('FG',guided[1],m.guided_fg)]:
                        if mg is not None:
                            for name,v in mg.items():observations[side+'_'+name]=v;natives[side+'_'+name]=ng[name]
                    if m.consumer is not None:
                        for name,i in [('sample305',0),('sample308',1)]:observations[name]=m.consumer[name];natives[name]=probe[i]
                        observations['consumer335']=m.consumer['output335'];natives['consumer335']=out
                    for name,v in observations.items():
                        if v is None:continue
                        if point:result[name]=metric(natives[name],v)
                        else:result[name]={'range_covered':bool(np.isfinite(natives[name]).all()and np.all(natives[name]>=v.lo)and np.all(natives[name]<=v.hi)),'max_width':float(np.max(v.hi-v.lo))}
                raw.append(row)
            outputhash.update(traces.tobytes()+b''.join(v.tobytes()for g in guided for v in g.values()));rows+=raw
    metrics={'new_fixtures':2,'consumer_calls':6,'original_host_kernel_invocations':kernel_calls,'point_unknown_rows':sum(bool(x['point']['unknowns'])for x in rows),'set_unknown_rows':sum(bool(x['set']['unknowns'])for x in rows),'known_set_violations':sum(v.get('range_covered')is False for r in rows for k,v in r['set'].items()if k!='unknowns')}
    root=Path(__file__).parent;r={'scope':__doc__,'hardware':'iPhone17,3','build':'24A446','epsilon_source':'verified cached constant 0x1d44e3d78 bytes6f12833a','epsilon_f32':float(EPSILON),'gain_pixel_format':115,'guide_source':'explicit original source texture, distinct from selected primary override in fixture1','caller_cast0':0,'semantic_mutation_scope':'producer and post-caller arrays explicitly supplied; cast2 excluded from this combination','original':metadata,'host_IR_sha256':[hashlib.sha256(x.encode()).hexdigest()for x in units],'C_sha256':hashlib.sha256(C_SOURCE.encode()).hexdigest(),'source_sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest()for n in ['native_ltm_roi_chain.py','full_ltm_chain.py','texture_numeric.py','air7_full_host.py','block290_host.py','guided_host.py','guided_conditioned.py']},'input_sha256':inputhash.hexdigest(),'output_sha256':outputhash.hexdigest(),'metrics':metrics,'rows':rows,'GPU_or_photo_executed':False,'old_accepted_batches_repeated':False,'sampler_precision_is_host_assumption':True,'old_155_125_envelope_still_retained':True}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    if metrics['known_set_violations']:raise AssertionError('Known chain set violation; receipt retained')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source_dir',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source_dir,a.output);print(json.dumps(r['metrics']))
