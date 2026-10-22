"""New three-pass original guided kernel CPU comparison, never a GPU oracle."""
import argparse,ctypes,hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from leaf_numeric import DomainUnknown
from guided_host import build,C_SOURCE
from guided_conditioned import Inputs,forward,LEGACY


def fixtures():
    y,x=np.mgrid[:4,:5];guide=(.1+.07*x+.1*y)[...,None];p=(.2+.13*np.arange(6).reshape(2,3))[...,None]
    yield Inputs(p,guide,(6,7),1,np.float32(.05),'synthetic supplied gain/guide'), 'scalar-resize'
    yield Inputs(np.concatenate([p,p*.7,p*1.2],axis=2),np.concatenate([guide,guide*.7,guide*1.1],axis=2),(6,7),1,np.float32(.03),'synthetic supplied RGB gain/guide'),'RGB-resize'
    yield Inputs(np.concatenate([p,p*.7,p*1.2],axis=2),guide,(6,7),1,np.float32(.05),'synthetic supplied RGB gain/scalar guide'),'RGB-scalar-guide'
    yield Inputs(np.full((2,3,1),.5),np.full((4,5,1),.4),(4,5),1,np.float32(.05),'synthetic constant'),'constant'
    yield Inputs(np.full((2,3,1),.5),np.zeros((4,5,1)),(4,5),1,np.float32(0),'synthetic zero divisor'),'epsilon-zero-negative'


def texture(a):
    a=np.asarray(a,dtype='f2').astype('f4');h,w,c=a.shape
    return np.r_[np.array([w,h,c,0],dtype='u4').view('f4'),a.ravel()].astype('f4')


def values(buffer,shape):return buffer[4:].reshape(shape).astype('f2')


def native(lib,inputs):
    p=texture(inputs.input_gain);guide=texture(inputs.guide);h,w=inputs.guide.shape[:2];c=inputs.input_gain.shape[2];shape=(h,w,c);outshape=(*inputs.output_shape,c)
    a=texture(np.zeros(shape));b=texture(np.zeros(shape));ma=texture(np.zeros(shape));mb=texture(np.zeros(shape));out=texture(np.zeros(outshape));radius=ctypes.c_int16(inputs.radius);epsilon=ctypes.c_float(float(inputs.epsilon_f32));single=ctypes.c_uint8(inputs.guide.shape[2]==1)
    for index,textures,grid in [(0,[p,guide,a,b],(h,w)),(1,[a,b,ma,mb],(h,w)),(2,[guide,ma,mb,out],inputs.output_shape)]:
        fn=getattr(lib,f'psr_guided_{index}');fn.argtypes=[ctypes.c_void_p]*7+[ctypes.c_uint16]*2;fn.restype=None
        for y in range(grid[0]):
            for x in range(grid[1]):fn(*(z.ctypes.data for z in textures),ctypes.byref(radius),ctypes.byref(epsilon),ctypes.byref(single),x,y)
    return {n:values(t,s)for n,t,s in [('a',a,shape),('b',b,shape),('mean_a',ma,shape),('mean_b',mb,shape),('output',out,outshape)]}


def check(source_dir,output):
    if output.exists():raise FileExistsError(output)
    rows=[];original=[];irhash=[];inputhash=hashlib.sha256();outputhash=hashlib.sha256()
    with tempfile.TemporaryDirectory(prefix='psr-guided3-')as t:
        w=Path(t);sources=[]
        for i in range(3):
            ir,meta=build((source_dir/f'{90+i:04d}.ll.txt').read_text(),i);original.append(meta);irhash.append(hashlib.sha256(ir.encode()).hexdigest());p=w/f'{i}.ll';p.write_text(ir);sources.append(str(p))
        (w/'shims.c').write_text(C_SOURCE)
        result=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',*sources,str(w/'shims.c'),'-o',str(w/'guided.dylib')],capture_output=True,text=True,timeout=60)
        if result.returncode:raise RuntimeError(result.stderr[:4000])
        lib=ctypes.CDLL(str(w/'guided.dylib'))
        for inputs,name in fixtures():
            observed=native(lib,inputs);row={'case':name,'input_gain':inputs.input_gain.tolist(),'guide':inputs.guide.tolist(),'output_shape':inputs.output_shape,'epsilon_f32':float(inputs.epsilon_f32),'native_half_bits':{k:v.view('u2').tolist()for k,v in observed.items()},'set_unknown':'Correlated set model not implemented; no center-point bound','observations':{}}
            inputhash.update(inputs.input_gain.tobytes()+inputs.guide.tobytes()+inputs.epsilon_f32.tobytes())
            for key,v in observed.items():outputhash.update(key.encode()+v.tobytes())
            try:
                modeled=forward(inputs);row['point_unknown']=None
                for k,v in modeled.items():row['observations'][k]={'half_bit_mismatches':int(np.count_nonzero(v.view('u2')!=observed[k].view('u2'))),'max_absolute_error':float(np.max(abs(v.astype('f4')-observed[k].astype('f4')))),'nonfinite_native':int(np.count_nonzero(~np.isfinite(observed[k])))}
            except DomainUnknown as error:row['point_unknown']=str(error);row['nonfinite_native']={k:int(np.count_nonzero(~np.isfinite(v)))for k,v in observed.items()}
            rows.append(row)
    metrics={k:{'half_bit_mismatches_known':sum(r['observations'].get(k,{}).get('half_bit_mismatches',0)for r in rows),'max_absolute_error_known':max((r['observations'].get(k,{}).get('max_absolute_error',0)for r in rows),default=0)}for k in ['a','b','mean_a','mean_b','output']}
    root=Path(__file__).parent;r={'scope':__doc__,'hardware':'iPhone17,3','build':'24A446','original':original,'host_IR_sha256':irhash,'shim_C_sha256':hashlib.sha256(C_SOURCE.encode()).hexdigest(),'reused_legacy_model':{'path':str(LEGACY.relative_to(root.parents[1])),'sha256':hashlib.sha256(LEGACY.read_bytes()).hexdigest()},'source_sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest()for n in ['guided_host.py','guided_conditioned.py','native_guided_check.py']},'input_sha256':inputhash.hexdigest(),'output_sha256':outputhash.hexdigest(),'fixtures':len(rows),'point_unknown':sum(r['point_unknown']is not None for r in rows),'set_unknown':len(rows),'metrics':metrics,'GPU_executed':False,'original_imageblock_execution':False,'one_thread_group_CPU_shim':True,'scalar_guide_R16_lane_behavior_retained':True,'old_accepted_batches_repeated':False,'rows':rows}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source_dir',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source_dir,a.output);print(json.dumps({k:r[k]for k in ['fixtures','point_unknown','set_unknown','metrics']}))
