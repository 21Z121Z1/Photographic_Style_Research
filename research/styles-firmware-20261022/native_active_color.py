"""Five raw one-control contexts through original AIR7/guided/AIR10/writer.

Compile once; execute each complete context independently. No supplied generated
maps or intermediate RGB. Observation/plain builds separately check the writer.
"""
import argparse,ctypes,hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from complete_fixture import decode
from complete_forward import forward
from native_complete_check import comparisons,bits
from air7_full_host import build as producer_build,C_SOURCE
from guided_host import build as guided_build
import main_full_host
from native_guided_check import texture,values,native as guided
from guided_conditioned import Inputs

EXTRA=[('color_half357',357,1),('color_gain364',364,1),('color_protect384',384,1)]
OBSERVATIONS=main_full_host.OBSERVATIONS+EXTRA
sha=lambda b:hashlib.sha256(b).hexdigest()


def build_main(source,observe):
    old=main_full_host.OBSERVATIONS;main_full_host.OBSERVATIONS=OBSERVATIONS
    try:return main_full_host.build(source,observe=observe)
    finally:main_full_host.OBSERVATIONS=old


def run_context(lib,plain,c,meta):
    native={};fn=lib.psr_produce;fn.argtypes=[ctypes.c_void_p]*9+[ctypes.c_uint8]*2+[ctypes.c_uint16]*2;fn.restype=None
    src=[texture(c.images[i])for i in [0,1]];gtc=texture(np.array(c.gtc.red_samples,dtype='f2')[None,:,None]);whites=texture(np.array(c.whites.red_samples,dtype='f2')[None,:,None]);matte=texture(c.images[3]);maps=[texture(np.zeros((*c.producer_shape,4)))for _ in range(2)];params=c.params.copy();traces=[];calls=0
    for y in range(c.producer_shape[0]):
        row=[]
        for x in range(c.producer_shape[1]):
            fn(*(a.ctypes.data for a in [*src,gtc,matte,*maps,c.management,params,c.srl]),0,0,x,y);row.append(np.ctypeslib.as_array((ctypes.c_float*21).in_dll(lib,'psr_producer_trace')).copy().reshape(7,3));calls+=1
        traces.append(row)
    traces=np.array(traces)
    for i,n in enumerate(['source24','postSRL34','linear37','reference96','working121','BG203','FG205']):native['producer_'+n]=traces[:,:,i,:]
    gs=[]
    for side,image in zip(['BG','FG'],[values(a,(*c.producer_shape,4))for a in maps]):
        native['raw_'+side]=image;g=guided(lib,Inputs(image,c.images[2],c.images[2].shape[:2],1,c.epsilon,'AIR7 RGBA16 gain domain'));calls+=3*np.prod(c.images[2].shape[:2]);gs.append(g)
        for n,a in g.items():native[side+'_'+n]=a
    arrays=[src[0],src[1],gtc,whites,None,*[texture(g['output'])for g in gs],*[texture(c.images[i])for i in [4,5,6,7,8,9]]];ptrs=(ctypes.c_void_p*13)(*[None if a is None else a.ctypes.data for a in arrays]);h,w=c.images[0].shape[:2];targets=[]
    for library,observe in [(lib,True),(plain,False)]:
        fn=library.psr_main_full;fn.argtypes=[ctypes.c_void_p]*7+[ctypes.c_int32]+[ctypes.c_uint16]*2+[ctypes.c_void_p];fn.restype=None;target=texture(c.output_initial);out=np.full((h,w,meta['observation_float_count']),np.nan,dtype='f4')
        for y in range(h):
            for x in range(w):
                params=c.params.copy();fn(ptrs,target.ctypes.data,c.management.ctypes.data,params.ctypes.data,c.stats.ctypes.data,c.roi.ctypes.data,c.srl.ctypes.data,c.version,x,y,out[y,x].ctypes.data);calls+=1
        targets.append(values(target,c.output_initial.shape))
        if observe:
            offset=0
            for n,ssa,count in OBSERVATIONS:native[n]=out[:,:,offset:offset+count];offset+=count
    native['writer']=targets[0]
    return native,int(calls),int(np.count_nonzero(targets[0].view('u2')!=targets[1].view('u2')))


def check(source_dir,context_file,contract_file,output):
    if output.exists():raise FileExistsError(output)
    contract=json.loads(contract_file.read_text());contexts=json.loads(context_file.read_text())
    if not contract['all_checks_pass']or sha(context_file.read_bytes())!=contract['context_file_sha256']or len(contexts['rows'])!=5:raise ValueError('Audited exact five-context family required')
    ir,pm=producer_build((source_dir/'0007.ll.txt').read_text(),observe=True);units=[ir];metadata=[pm]
    for i in range(3):ir,m=guided_build((source_dir/f'{90+i:04d}.ll.txt').read_text(),i);units.append(ir);metadata.append(m)
    source=(source_dir/'0010.ll.txt').read_text();ir,mm=build_main(source,True);units.append(ir);metadata.append(mm);plain,plain_meta=build_main(source,False);rows=[]
    with tempfile.TemporaryDirectory(prefix='psr-active-color-')as t:
        work=Path(t);paths=[]
        for i,ir in enumerate(units):p=work/f'{i}.ll';p.write_text(ir);paths.append(str(p))
        (work/'shim.c').write_text(C_SOURCE);(work/'plain.ll').write_text(plain)
        for files,name in [(paths,'chain'),([str(work/'plain.ll')],'plain')]:
            p=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',*files,str(work/'shim.c'),'-o',str(work/(name+'.dylib'))],capture_output=True,text=True,timeout=30)
            if p.returncode:raise RuntimeError(p.stderr[:4000])
        lib=ctypes.CDLL(str(work/'chain.dylib'));unobserved=ctypes.CDLL(str(work/'plain.dylib'))
        for row in contexts['rows']:
            native,calls,observer_diff=run_context(lib,unobserved,decode(row['context']),mm);rows.append({'control':row['control'],'original_kernel_calls':calls,'observer_plain_writer_half_bit_mismatches':observer_diff,'native_nonfinite_components':sum(int(np.count_nonzero(~np.isfinite(v)))for v in native.values()),'native_half_bits':{n:bits(v)for n,v in native.items()}})
    result={'scope':__doc__,'hardware':'iPhone17,3','build':'24A446','contexts_sha256':sha(context_file.read_bytes()),'contract_sha256':sha(contract_file.read_bytes()),'original':metadata,'plain_original':plain_meta,'host_IR_sha256':[sha(v.encode())for v in units],'plain_host_IR_sha256':sha(plain.encode()),'C_sha256':sha(C_SOURCE.encode()),'metrics':{'contexts':5,'original_kernel_calls':sum(v['original_kernel_calls']for v in rows),'per_context_producer_calls':6,'per_context_guided_calls':72,'per_context_observed_main_writer_calls':12,'per_context_plain_main_writer_calls':12,'observer_writer_half_bit_mismatches':sum(v['observer_plain_writer_half_bit_mismatches']for v in rows),'native_nonfinite_components':sum(v['native_nonfinite_components']for v in rows)},'rows':rows,'GPU_or_private_photo_executed':False,'intermediate_outputs_supplied':False,'point_is_set_acceptance':False}
    # Persist actual outputs, including failures, before any independent model.
    output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    for row,crow in zip(rows,contexts['rows']):
        native={n:np.array(v,dtype='u2').view('f2')for n,v in row['native_half_bits'].items()};point=forward(decode(crow['context']),point=True);row['point']=comparisons(native,point)
    output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({'metrics':result['metrics'],'point_mismatches':[sum(v['half_bit_mismatches']for v in r['point']['observations'].values())for r in rows]}))
    if result['metrics']['observer_writer_half_bit_mismatches']or result['metrics']['native_nonfinite_components']:raise AssertionError('Original host failure; receipt retained')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source_dir',type=Path);p.add_argument('contexts',type=Path);p.add_argument('contract',type=Path);p.add_argument('output',type=Path);a=p.parse_args();check(a.source_dir,a.contexts,a.contract,a.output)
