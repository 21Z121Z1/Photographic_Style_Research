"""One saved S15 pixel's original selectiveColorFilter probes, not a new case."""
import argparse,ctypes,hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from complete_fixture import decode
from leaf_numeric import V
from cast_values import CastValues
from pixel_selective import SelectiveTexture,selective
from numeric_trace_host import build
from main_full_host import C_SOURCE,OBSERVATIONS
from native_guided_check import texture
from selective_neutral_joint import Inputs as JointInputs,enclose

MAP={20:'lms',24:'root',33:'lab',42:'angle',45:'radius',131:'basic',178:'changed',186:'inverse_v',190:'inverse_root',199:'converted',210:'gamma',213:'powered',230:'output'}


def check(source,context,saved,baseline,output):
    if output.exists():raise FileExistsError(output)
    if hashlib.sha256(context.read_bytes()).hexdigest()!=json.loads(saved.read_text())['context_sha256']:raise ValueError('Saved native outputs do not match this frozen context')
    c=decode(json.loads(context.read_text()));n={k:np.array(a,dtype='u2').view('f2')for k,a in json.loads(saved.read_text())['native_half_bits'].items()};grid=(0,0);value=lambda k:V.value(n[k][0,0,0]if n[k][0,0].size==1 else n[k][0,0]);lookup=SelectiveTexture(c.images[9],'fixed saved zero selective texture');zero=[V.value([0,0])for _ in range(3)];trace={};selective(value('warm409'),value('person96'),value('skin95'),V.value(c.images[8][0,0,0]),lookup,zero,V.value([0,0,0]),V.value(0),observations=trace,joint=False);models={'selective':('selectiveColorFilter',{ssa:trace[name]for ssa,name in MAP.items()})};ir,meta=build(source.read_text(),models)
    with tempfile.TemporaryDirectory(prefix='psr-selective-one-')as d:
        w=Path(d);(w/'p.ll').write_text(ir);(w/'shim.c').write_text(C_SOURCE);p=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',str(w/'p.ll'),str(w/'shim.c'),'-o',str(w/'p.dylib')],capture_output=True,text=True,timeout=60)
        if p.returncode:raise RuntimeError(p.stderr[:4000])
        lib=ctypes.CDLL(str(w/'p.dylib'));fn=lib.psr_main_full;fn.argtypes=[ctypes.c_void_p]*7+[ctypes.c_int32]+[ctypes.c_uint16]*2+[ctypes.c_void_p];fn.restype=None
        images=[c.images[0],c.images[1],np.array(c.gtc.red_samples,dtype='f2')[None,:,None],np.array(c.whites.red_samples,dtype='f2')[None,:,None],None,n['BG_output'],n['FG_output'],*[c.images[i]for i in [4,5,6,7,8,9]]];arrays=[None if a is None else texture(a)for a in images];ptrs=(ctypes.c_void_p*13)(*[None if a is None else a.ctypes.data for a in arrays]);target=texture(c.output_initial);out=np.zeros(meta['original']['observation_float_count'],dtype='f4');params=c.params.copy();fn(ptrs,target.ctypes.data,c.management.ctypes.data,params.ctypes.data,c.stats.ctypes.data,c.roi.ctypes.data,c.srl.ctypes.data,c.version,0,0,out.ctypes.data);m=meta['probes']['selective'];values=np.ctypeslib.as_array((ctypes.c_float*m['count']).in_dll(lib,'psr_trace_selective')).copy();rows=[]
        for ssa,ty,count,offset in m['layout']:
            a=values[offset:offset+count];dtype='f2'if ty=='half'else'f4';bits='u2'if ty=='half'else'u4';b=models['selective'][1][ssa].lo.reshape(-1);rows.append({'SSA':ssa,'name':MAP[ssa],'precision':ty,'native_bits':a.astype(dtype).view(bits).tolist(),'point_bit_mismatches':int(np.count_nonzero(a.astype(dtype).view(bits)!=b.astype(dtype).view(bits))),'point_max_error':float(np.max(abs(a-b)))})
        offset=0;observed={}
        for name,ssa,count in OBSERVATIONS:observed[name]=out[offset:offset+count];offset+=count
        stability={name:int(np.count_nonzero(observed[name].astype('f2').view('u2')!=n[name][0,0].reshape(-1).view('u2')))for name in ['selective413','output600']}
    # First pixel only, prior to the corrected twelve-pixel replay. Baseline
    # saved full-context warm/mask ranges remain whole sets, not point centers.
    baseline_data=json.loads(baseline.read_text());raw=baseline_data['pixel_traces'][0]['input_raw'];rgb=V(np.array(raw['lo']),np.array(raw['hi']),'h',False);H=lambda x:V.bounds(x,x);masks=[V(np.asarray(v['lo']),np.asarray(v['hi']),'h',False)for v in baseline_data['pixel_traces'][0]['input_masks']];joint=enclose(JointInputs(rgb,*masks,lookup,tuple(H([0,0])for _ in range(3)),H([0,0,0]),H(0)))
    coverage={}
    byname={row['name']:row for row in rows}
    for name,v in [('inverse_v',joint.inverse_v),('inverse_root',joint.inverse_root),('converted',joint.converted),('gamma',joint.gamma)]:
        row=byname[name];actual=np.array(row['native_bits'],dtype='u2'if row['precision']=='half'else'u4').view('f2'if row['precision']=='half'else'f4');coverage[name]={'covered':bool(np.all(actual>=v.lo)and np.all(actual<=v.hi)),'lo':v.lo.tolist(),'hi':v.hi.tolist(),'max_width':float(np.max(v.hi-v.lo))}
    r={'scope':__doc__,'grid':grid,'native_main_calls':1,'original':meta,'host_IR_sha256':hashlib.sha256(ir.encode()).hexdigest(),'context_sha256':hashlib.sha256(context.read_bytes()).hexdigest(),'rows':rows,'observer_stability':stability,'whole_first_pixel_joint_proof':joint.proof,'coverage':coverage,'first_joint_unknown':'converted.pow(gamma): negative base remains in the outer enclosure; no endpoint reachability claim','GPU_executed':False,'intermediate_inputs_for_diagnostics_only':'saved guided maps; not a new complete chain'};output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    if any(stability.values())or any(not x['covered']for x in coverage.values()):raise AssertionError('Selective saved probe stability/coverage failure; receipt retained')
    print(json.dumps({'stability':stability,'coverage':coverage}));return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('context',type=Path);p.add_argument('saved',type=Path);p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();check(a.source,a.context,a.saved,a.baseline,a.output)
