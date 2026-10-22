"""Two saved S14B coefficient witnesses, bounded f32 trace and model replay."""
import argparse,ctypes,hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from guided_conditioned import legacy
from guided_trace_host import build,CHECKPOINTS
from air7_full_host import C_SOURCE
from native_ltm_roi_chain import fixture,model_inputs,EPSILON
from full_ltm_chain import generate
from native_guided_check import texture,values


def candidate(p,guide,epsilon,*,original_order):
    h,w=guide.shape[:2];c=p.shape[-1];x=np.arange(w,dtype='f4')[None,:];y=np.arange(h,dtype='f4')[:,None];shape=(h,w,c);sp=np.zeros(shape,'f4');si=sp.copy();sip=sp.copy();sii=sp.copy()
    for dx in range(-1,2):
        for dy in range(-1,2):
            ux=(x+np.float32(.5+dx))/np.float32(w);uy=(y+np.float32(.5+dy))/np.float32(h);pv=legacy.normalized_sample(p,ux,uy);iv=legacy.normalized_sample(guide,ux,uy);sp+=pv;si+=iv;sip=legacy.fma(iv,pv,sip);sii=legacy.fma(iv,iv,sii)
    div=lambda a:a*np.float32(1/9)
    mp,mi,mip,mii=map(div,[sp,si,sip,sii]);cov=legacy.fma(-mi,mp,mip);ep=np.float32(epsilon)+mii
    var=legacy.fma(-mi,mi,ep)if original_order else legacy.fma(-mi,mi,mii)+np.float32(epsilon);a=(cov/var).astype('f4');b=legacy.fma(-a,mi,mp)
    return dict(zip([n for n,_ in CHECKPOINTS],[sp,si,sip,sii,mp,mi,mip,mii,cov,ep,var,a,b]))


def check(source,output,saved_complete):
    if output.exists():raise FileExistsError(output)
    saved=json.loads(saved_complete.read_text());ir,meta=build(source.read_text());rows=[]
    with tempfile.TemporaryDirectory(prefix='psr-guided-diag-')as t:
        w=Path(t);(w/'source.ll').write_text(ir);(w/'shim.c').write_text(C_SOURCE);p=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',str(w/'source.ll'),str(w/'shim.c'),'-o',str(w/'trace.dylib')],capture_output=True,text=True,timeout=60)
        if p.returncode:raise RuntimeError(p.stderr[:2000])
        lib=ctypes.CDLL(str(w/'trace.dylib'));fn=lib.psr_guided_0;fn.argtypes=[ctypes.c_void_p]*7+[ctypes.c_uint16]*2;fn.restype=None
        for index in range(2):
            f=fixture(index);args,kw=model_inputs(f,(0,0),.2,True);gen=generate(*args,**{k:v for k,v in kw.items()if k not in['consumer_semantic7','roi','reference196','person96']});gain=gen.raw_fg.pixels.lo.astype('f2');old=candidate(gain,f['guide'],EPSILON,original_order=False);new=candidate(gain,f['guide'],EPSILON,original_order=True);diff=old['a_f32'].astype('f2').view('u2')!=new['a_f32'].astype('f2').view('u2');locations=np.argwhere(diff)
            aa=texture(np.zeros(f['guide'].shape));bb=texture(np.zeros(f['guide'].shape));gt=texture(gain);it=texture(f['guide']);radius=np.array([1],dtype='i2');eps=np.array([EPSILON],dtype='f4');single=np.array([0],dtype='u1')
            if index==0:
                old_bits=old['a_f32'].astype('f2').view('u2');prior=np.array(saved['native_half_bits']['FG_a'],dtype='u2');locations=np.argwhere(old_bits!=prior);y,x,lane=map(int,locations[0]);grids=[(x,y)]
            else:
                # The earlier S14B receipt stored only aggregate mismatch counts,
                # not its array. Recover only this 20-pixel coefficient pass,
                # never the producer, averaging, apply or ROI batches.
                grids=[(x,y)for y in range(f['guide'].shape[0])for x in range(f['guide'].shape[1])]
            traces={}
            for x,y in grids:
                fn(*(a.ctypes.data for a in [gt,it,aa,bb,radius,eps,single]),x,y);traces[x,y]=np.ctypeslib.as_array((ctypes.c_float*52).in_dll(lib,'psr_guided_trace')).copy().reshape(13,4)
            if index==1:
                native_a=values(aa,f['guide'].shape);locations=np.argwhere(old['a_f32'].astype('f2').view('u2')!=native_a.view('u2'))
                if len(locations)!=1:raise AssertionError('Saved S14B fixture1 coefficient mismatch count changed')
                y,x,lane=map(int,locations[0])
            trace=traces[x,y];stages=[]
            for i,(name,ssa)in enumerate(CHECKPOINTS):
                native=trace[i];a=old[name][y,x];b=new[name][y,x];stages.append({'name':name,'SSA':ssa,'native_f32_bits':native.view('u4').tolist(),'legacy_f32_bits':a.view('u4').tolist(),'original_order_f32_bits':b.view('u4').tolist(),'legacy_bit_mismatches':int(np.count_nonzero(native.view('u4')!=a.view('u4'))),'original_order_bit_mismatches':int(np.count_nonzero(native.view('u4')!=b.view('u4')))})
            actual_a=values(aa,f['guide'].shape)[y,x];actual_b=values(bb,f['guide'].shape)[y,x];r={'fixture':index,'grid':[x,y],'first_differing_lane':lane,'old_half_a_bits':old['a_f32'][y,x].astype('f2').view('u2').tolist(),'new_half_a_bits':new['a_f32'][y,x].astype('f2').view('u2').tolist(),'native_half_a_bits':actual_a.view('u2').tolist(),'native_half_b_bits':actual_b.view('u2').tolist(),'stages':stages,'first_f32_divergence':next((s['name']for s in stages if s['legacy_bit_mismatches']),None),'candidate_all_f32_checkpoints_equal':all(not s['original_order_bit_mismatches']for s in stages)}
            if index==0:
                prior=np.array(saved['native_half_bits']['FG_a'],dtype='u2')[y,x];r['observer_half_a_bits_match_saved_unobserved']=bool(np.array_equal(prior,actual_a.view('u2')))
            else:r['observer_half_a_bits_match_saved_unobserved']=None # S14B receipt had aggregate metrics only
            rows.append(r)
    result={'scope':__doc__,'hardware':'iPhone17,3','build':'24A446','original':meta,'native_calls':21,'old_batches_repeated':False,'rows':rows,'host_IR_sha256':hashlib.sha256(ir.encode()).hexdigest(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'saved_complete_sha256':hashlib.sha256(saved_complete.read_bytes()).hexdigest(),'input_gain_source':'previously proven bit-identical point producer model; source identities unchanged; no native producer rerun','provisional_order_only':True,'GPU_executed':False};output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);p.add_argument('saved_complete',type=Path);a=p.parse_args();r=check(a.source,a.output,a.saved_complete);print(json.dumps([{k:v for k,v in row.items()if k not in['stages']}for row in r['rows']]))
