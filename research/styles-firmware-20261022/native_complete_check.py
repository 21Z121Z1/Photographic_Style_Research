"""One saved 3x4 conditional context, actual AIR7/guided/full AIR10/writer."""
import argparse,ctypes,hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from complete_fixture import context,encode,decode
from complete_forward import forward
from air7_full_host import build as producer_build,C_SOURCE
from guided_host import build as guided_build
from main_full_host import build as main_build,OBSERVATIONS
from native_guided_check import texture,values,native as guided
from guided_conditioned import Inputs


def dump(path,data):path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
def digest(a):return hashlib.sha256(a).hexdigest()
def bits(a):return np.asarray(a,dtype='f2').view('u2').tolist()


def comparisons(native,result):
    rows={}
    for name,v in result.observations.items():
        if name not in native:continue
        a=np.asarray(native[name],dtype='f8');a=a[...,0]if a.shape==v.lo.shape+(1,)else a
        if result.point:rows[name]={'components':int(a.size),'half_bit_mismatches':int(np.count_nonzero(a.astype('f2').view('u2')!=v.lo.astype('f2').view('u2'))),'max_absolute_error':float(np.max(abs(a-v.lo)))}
        else:rows[name]={'components':int(a.size),'range_covered':bool(np.isfinite(a).all()and np.all(a>=v.lo)and np.all(a<=v.hi)),'max_width':float(np.max(v.hi-v.lo))}
    return {'observations':rows,'pixel_unknowns':result.pixel_unknowns,'internal_unknowns':result.internal_unknowns,'writer_known':result.writer is not None,'first_unknown':next(iter(result.pixel_unknowns.items()),None)}


def replay(context_file,native_file,output):
    c=decode(json.loads(context_file.read_text()));saved=json.loads(native_file.read_text());native={k:np.array(a,dtype='u2').view('f2')for k,a in saved['native_half_bits'].items()};r={'context_sha256':digest(context_file.read_bytes()),'saved_native_sha256':digest(native_file.read_bytes()),'native_calls':0,'point':comparisons(native,forward(c,point=True)),'set':comparisons(native,forward(c,point=False))};root=Path(__file__).parent;r['source_sha256']={p:digest((root/p).read_bytes())for p in ['complete_fixture.py','complete_forward.py','native_complete_check.py','main_pre393.py','full_ltm_chain.py','guided_conditioned.py','guided_precision.py','leaf_correlations.py','pixel_leaves.py']};dump(output,r);return r


def check(source_dir,output,context_file):
    if output.exists()or context_file.exists():raise FileExistsError('Do not overwrite evidence')
    c=context();dump(context_file,encode(c)) # fixed before compilation/evaluation
    ir,pm=producer_build((source_dir/'0007.ll.txt').read_text(),observe=True);units=[ir];metadata=[pm]
    for i in range(3):ir,m=guided_build((source_dir/f'{90+i:04d}.ll.txt').read_text(),i);units.append(ir);metadata.append(m)
    ir,mm=main_build((source_dir/'0010.ll.txt').read_text());units.append(ir);metadata.append(mm);plain,plainmeta=main_build((source_dir/'0010.ll.txt').read_text(),observe=False)
    native={};calls=0
    with tempfile.TemporaryDirectory(prefix='psr-complete-')as t:
        w=Path(t);paths=[]
        for i,ir in enumerate(units):p=w/f'{i}.ll';p.write_text(ir);paths.append(str(p))
        (w/'shim.c').write_text(C_SOURCE);(w/'plain.ll').write_text(plain)
        for files,name in [(paths,'chain'),([str(w/'plain.ll')],'plain')]:
            proc=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',*files,str(w/'shim.c'),'-o',str(w/(name+'.dylib'))],capture_output=True,text=True,timeout=60)
            if proc.returncode:raise RuntimeError(proc.stderr[:4000])
        lib=ctypes.CDLL(str(w/'chain.dylib'));fn=lib.psr_produce;fn.argtypes=[ctypes.c_void_p]*9+[ctypes.c_uint8]*2+[ctypes.c_uint16]*2;fn.restype=None
        src=[texture(c.images[i])for i in [0,1]];gtc=texture(np.array(c.gtc.red_samples,dtype='f2')[None,:,None]);whites=texture(np.array(c.whites.red_samples,dtype='f2')[None,:,None]);matte=texture(c.images[3]);maps=[texture(np.zeros((*c.producer_shape,4)))for _ in range(2)];params=c.params.copy();traces=[]
        for y in range(c.producer_shape[0]):
            row=[]
            for x in range(c.producer_shape[1]):
                fn(*(a.ctypes.data for a in [*src,gtc,matte,*maps,c.management,params,c.srl]),0,0,x,y);row.append(np.ctypeslib.as_array((ctypes.c_float*21).in_dll(lib,'psr_producer_trace')).copy().reshape(7,3));calls+=1
            traces.append(row)
        traces=np.array(traces)
        for i,n in enumerate(['source24','postSRL34','linear37','reference96','working121','BG203','FG205']):native['producer_'+n]=traces[:,:,i,:]
        raw=[values(a,(*c.producer_shape,4))for a in maps];gs=[]
        for side,image in zip(['BG','FG'],raw):
            native['raw_'+side]=image;g=guided(lib,Inputs(image,c.images[2],c.images[2].shape[:2],1,c.epsilon,'AIR7 RGBA16 gain domain'));calls+=3*np.prod(c.images[2].shape[:2]);gs.append(g)
            for n,a in g.items():native[side+'_'+n]=a
        arrays=[src[0],src[1],gtc,whites,None,*[texture(g['output'])for g in gs],*[texture(c.images[i])for i in [4,5,6,7,8,9]]];ptrs=(ctypes.c_void_p*13)(*[None if a is None else a.ctypes.data for a in arrays]);height,width=c.images[0].shape[:2]
        targets=[]
        for library,observe in [(lib,True),(ctypes.CDLL(str(w/'plain.dylib')),False)]:
            main=library.psr_main_full;main.argtypes=[ctypes.c_void_p]*7+[ctypes.c_int32]+[ctypes.c_uint16]*2+[ctypes.c_void_p];main.restype=None;target=texture(c.output_initial);out=np.full((height,width,mm['observation_float_count']),np.nan,dtype='f4')
            for y in range(height):
                for x in range(width):
                    params=c.params.copy();main(ptrs,target.ctypes.data,c.management.ctypes.data,params.ctypes.data,c.stats.ctypes.data,c.roi.ctypes.data,c.srl.ctypes.data,c.version,x,y,out[y,x].ctypes.data);calls+=1
            targets.append(values(target,c.output_initial.shape))
            if observe:
                offset=0
                for n,ssa,count in OBSERVATIONS:native[n]=out[:,:,offset:offset+count];offset+=count
        native['writer']=targets[0];observer_bits=int(np.count_nonzero(targets[0].view('u2')!=targets[1].view('u2')))
    # Native outputs are saved before model evaluation, including discrepancies.
    r={'scope':__doc__,'context_sha256':digest(context_file.read_bytes()),'context_file':context_file.name,'original':metadata,'plain_original':plainmeta,'host_IR_sha256':[digest(ir.encode())for ir in units],'C_sha256':digest(C_SOURCE.encode()),'native_half_bits':{k:bits(a)for k,a in native.items()},'metrics':{'contexts':1,'producer_calls':6,'guided_calls':72,'main_with_writer_calls':12,'unobserved_main_calls':12,'total_original_kernel_calls':int(calls),'observer_final_half_bit_mismatches':observer_bits,'native_nonfinite_components':sum(int(np.count_nonzero(~np.isfinite(a)))for a in native.values())},'GPU_or_photo_executed':False,'intermediate_outputs_supplied':False,'remaining_external_inputs':encode(c)['remaining_external_inputs'],'old_accepted_batches_repeated':False}
    dump(output,r)
    r['point']=comparisons(native,forward(c,point=True));r['set']=comparisons(native,forward(c,point=False));root=Path(__file__).parent;r['source_sha256']={p:digest((root/p).read_bytes())for p in ['complete_fixture.py','complete_forward.py','native_complete_check.py','main_full_host.py','main_pre393.py','full_ltm_chain.py','guided_conditioned.py']};dump(output,r)
    if observer_bits:raise AssertionError('Observers perturbed final output; receipt retained')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source_dir',type=Path);p.add_argument('output',type=Path);p.add_argument('context',type=Path);a=p.parse_args();r=check(a.source_dir,a.output,a.context);print(json.dumps({'metrics':r['metrics'],'point_first_unknown':r['point']['first_unknown'],'set_first_unknown':r['set']['first_unknown']}))
