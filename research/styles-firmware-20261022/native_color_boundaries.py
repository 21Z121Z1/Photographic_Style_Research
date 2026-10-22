"""Minimal new raw boundary controls after exhaustive finite model search.

Producer/guided execute ONCE from the frozen raw inputs. The audited raw color
field is absent from that prefix; each new full main/writer uses this generated
prefix, not a saved/native intermediate oracle. Both observer/plain roots run.
"""
import argparse,ctypes,hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from active_color import Color,replace_color
from color_inverse import f32,signature,digest
from complete_fixture import decode
from complete_forward import forward
from native_complete_check import bits,comparisons
from native_active_color import build_main,OBSERVATIONS
from air7_full_host import build as producer_build,C_SOURCE
from guided_host import build as guided_build
from native_guided_check import texture,values,native as guided
from guided_conditioned import Inputs
from select_active_color import CONTEXT_SHA

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
dump=lambda p,d:p.write_text(json.dumps(d,separators=(',',':'),allow_nan=False)+'\n')


def upstream(lib,c):
    fn=lib.psr_produce;fn.argtypes=[ctypes.c_void_p]*9+[ctypes.c_uint8]*2+[ctypes.c_uint16]*2;fn.restype=None;src=[texture(c.images[i])for i in [0,1]];gtc=texture(np.array(c.gtc.red_samples,dtype='f2')[None,:,None]);whites=texture(np.array(c.whites.red_samples,dtype='f2')[None,:,None]);matte=texture(c.images[3]);maps=[texture(np.zeros((*c.producer_shape,4)))for _ in range(2)];params=c.params.copy();traces=[];native={};calls=0
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
    arrays=[src[0],src[1],gtc,whites,None,*[texture(g['output'])for g in gs],*[texture(c.images[i])for i in [4,5,6,7,8,9]]];ptrs=(ctypes.c_void_p*13)(*[None if a is None else a.ctypes.data for a in arrays])
    return {'arrays_keepalive':arrays,'ptrs':ptrs,'native':native,'calls':int(calls)}


def render(lib,plain,c,prepared,meta):
    h,w=c.images[0].shape[:2];targets=[];native=dict(prepared['native']);calls=0
    for library,observe in [(lib,True),(plain,False)]:
        fn=library.psr_main_full;fn.argtypes=[ctypes.c_void_p]*7+[ctypes.c_int32]+[ctypes.c_uint16]*2+[ctypes.c_void_p];fn.restype=None;target=texture(c.output_initial);out=np.full((h,w,meta['observation_float_count']),np.nan,dtype='f4')
        for y in range(h):
            for x in range(w):
                params=c.params.copy();fn(prepared['ptrs'],target.ctypes.data,c.management.ctypes.data,params.ctypes.data,c.stats.ctypes.data,c.roi.ctypes.data,c.srl.ctypes.data,c.version,x,y,out[y,x].ctypes.data);calls+=1
        targets.append(values(target,c.output_initial.shape))
        if observe:
            offset=0
            for n,ssa,count in OBSERVATIONS:native[n]=out[:,:,offset:offset+count];offset+=count
    native['writer']=targets[0];return native,calls,int(np.count_nonzero(targets[0].view('u2')!=targets[1].view('u2')))


def check(source_dir,basefile,inverse_file,plan_file,prior_native,output):
    if output.exists():raise FileExistsError(output)
    plan=load(plan_file);inverse=load(inverse_file);prior=load(prior_native)
    if sha(basefile)!=CONTEXT_SHA or plan['inverse_sha256']!=sha(inverse_file)or not plan['complete_model_coverage_before_native']or not inverse['coverage']['complete_model_coverage']:raise ValueError('Complete finite model search must precede new original calls')
    if not 1<=len(plan['controls'])<=16:raise ValueError('At most16 necessary new boundary controls')
    if any(v['raw_f32_bits']in plan['existing_raw_controls_reused']for v in plan['controls']):raise ValueError('Old original five raw values must not be rerun')
    base=decode(load(basefile));goals={n:np.array(prior['rows'][i]['native_half_bits']['writer'],dtype='u2')for n,i in [('platform',1),('point3',3)]};units=[];metadata=[]
    ir,m=producer_build((source_dir/'0007.ll.txt').read_text(),observe=True);units.append(ir);metadata.append(m)
    for i in range(3):ir,m=guided_build((source_dir/f'{90+i:04d}.ll.txt').read_text(),i);units.append(ir);metadata.append(m)
    ir,main_meta=build_main((source_dir/'0010.ll.txt').read_text(),True);units.append(ir);metadata.append(main_meta);plain,plain_meta=build_main((source_dir/'0010.ll.txt').read_text(),False);result={'scope':__doc__,'base_context_sha256':CONTEXT_SHA,'inverse_sha256':sha(inverse_file),'boundary_plan_sha256':sha(plan_file),'prior_native_sha256':sha(prior_native),'original':metadata,'plain_original':plain_meta,'host_IR_sha256':[hashlib.sha256(v.encode()).hexdigest()for v in units],'plain_IR_sha256':hashlib.sha256(plain.encode()).hexdigest(),'C_sha256':hashlib.sha256(C_SOURCE.encode()).hexdigest(),'rows':[],'prefix_original_calls':0,'new_main_original_calls':0,'total_original_kernel_calls':0,'new_model_forward_calls':0,'GPU_or_private_media_executed':False,'intermediate_outputs_supplied':False};dump(output,result)
    with tempfile.TemporaryDirectory(prefix='psr-inverse-boundaries-')as t:
        work=Path(t);paths=[]
        for i,ir in enumerate(units):p=work/f'{i}.ll';p.write_text(ir);paths.append(str(p))
        (work/'shim.c').write_text(C_SOURCE);(work/'plain.ll').write_text(plain)
        for files,name in [(paths,'chain'),([str(work/'plain.ll')],'plain')]:
            proc=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',*files,str(work/'shim.c'),'-o',str(work/(name+'.dylib'))],capture_output=True,text=True,timeout=30)
            if proc.returncode:raise RuntimeError(proc.stderr[:4000])
        lib=ctypes.CDLL(str(work/'chain.dylib'));unobserved=ctypes.CDLL(str(work/'plain.dylib'));prepared=upstream(lib,base);result['prefix_original_calls']=prepared['calls'];result['prefix_native_half_bits']={n:bits(a)for n,a in prepared['native'].items()};result['prefix_reuse_basis']='S21 exact AIR7 raw pointer audit has no field3 read; guided has no SSRParams; all other immutable raw inputs equal';result['prefix_half_bit_mismatches_vs_S21']=sum(int(np.count_nonzero(a.astype('f2').view('u2')!=np.array(prior['rows'][0]['native_half_bits'][n],dtype='u2')))for n,a in prepared['native'].items());dump(output,result)
        for c in plan['controls']:
            context=replace_color(base,Color(f32(c['raw_f32_bits'])));native,calls,observer=render(lib,unobserved,context,prepared,main_meta);result['new_main_original_calls']+=calls;result['total_original_kernel_calls']=result['prefix_original_calls']+result['new_main_original_calls'];row={'control':c,'main_original_calls':calls,'observer_plain_writer_half_bit_mismatches':observer,'native_nonfinite_components':sum(int(np.count_nonzero(~np.isfinite(a)))for a in native.values()),'native_half_bits':{n:bits(a)for n,a in native.items()if n not in prepared['native']}};result['rows'].append(row);dump(output,result)
            row['target_matches']={n:bool(np.array_equal(native['writer'].view('u2'),g))for n,g in goals.items()};row['target_match_expectations_agree']=row['target_matches']==c['expected_matches'];row['model_writer_sha256_match']=digest(native['writer'])==c['expected_writer_sha256'];row['logical_interface_matches']={'half357':bool(np.all(native['color_half357']==np.float16(f32(c['raw_f32_bits'])))),'gain364':bool(np.all(native['color_gain364'].astype('f2').view('u2')==c['key'][1])),'protect384':bool(np.all(native['color_protect384'].astype('f2').view('u2')==c['key'][2]))};row['point']=comparisons(native,forward(context,point=True));result['new_model_forward_calls']+=1;dump(output,result)
            if observer or row['native_nonfinite_components']or not row['target_match_expectations_agree']or not row['model_writer_sha256_match']or not all(row['logical_interface_matches'].values())or any(v['half_bit_mismatches']for v in row['point']['observations'].values()):raise AssertionError('Boundary counterexample retained; remaining original calls not run')
    print(json.dumps({'controls':len(result['rows']),'prefix_calls':result['prefix_original_calls'],'main_calls':result['new_main_original_calls'],'original_kernel_calls':result['total_original_kernel_calls'],'original_writer_boundary_mismatches':sum(not r['target_match_expectations_agree']for r in result['rows']),'point_half_bit_mismatches':sum(v['half_bit_mismatches']for r in result['rows']for v in r['point']['observations'].values())}));return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source_dir',type=Path);p.add_argument('base',type=Path);p.add_argument('inverse',type=Path);p.add_argument('plan',type=Path);p.add_argument('prior_native',type=Path);p.add_argument('output',type=Path);a=p.parse_args();check(a.source_dir,a.base,a.inverse,a.plan,a.prior_native,a.output)
