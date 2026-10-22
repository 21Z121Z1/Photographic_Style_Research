"""First saved target-B output mismatch, traced code3 transfer checkpoints."""
from pathlib import Path
import argparse,ctypes,json
import numpy as np
from baseline_archive import Archive,sha,encoded,compiler_identity,compile_saved
from traceable_color_baseline import validate_private_location,COMPILER
from numeric_trace_host import build
from baseline_field3 import functions
from complete_fixture import decode
from complete_forward import forward
from active_color import Color,replace_color
from color_inverse import f32
from pixel_skin import encode
from pixel_leaves import H
from leaf_numeric import hc
from native_guided_check import texture
from main_full_host import C_SOURCE,OBSERVATIONS

ROOT=Path(__file__).parent;REPO=ROOT.parents[1]


def check(air,context_file,saved_file,private,output):
    if output.exists():raise FileExistsError(output)
    saved=json.loads(saved_file.read_text());row=saved['rows'][0];c=replace_color(decode(json.loads(context_file.read_text())),Color(f32(row['control']['raw_f32_bits'])));native={n:np.array(a,dtype='u2').view('f2')for n,a in {**saved['prefix_native_half_bits'],**row['native_half_bits']}.items()};model=forward(c,point=True);difference=native['output600'].view('u2')!=model.observations['output600'].lo.astype('f2').view('u2');y,x,lane=np.argwhere(difference)[0];x,y,lane=map(int,[x,y,lane]);linear=model.observations['linear597'][y,x];q={};expected=encode(linear,observations=q);probes={11:q['abs'],12:q['abs']*H(hc('4a76'),linear),13:q['power'],14:q['scaled'],15:q['offset'],17:q['chosen'],18:q['output']};name=next(n for n in functions(air.read_text())if 'curvedFromLinear'in n);ir,meta=build(air.read_text(),{'transfer':(name,probes)});validate_private_location(private);a=Archive(private,create=True,repo=REPO)
    for f in ROOT.glob('*.py'):a.input('generators/'+f.name,f.read_bytes(),'exact diagnostic source')
    for n,p in [('source.ll.txt',air),('context.json',context_file),('saved.json',saved_file)]:a.input('binding/'+n,p.read_bytes(),'diagnostic input')
    a.input('inputs/trace.ll',ir.encode(),'actual traced host compiler input');a.input('inputs/shim.c',C_SOURCE.encode(),'actual shim');compiler=compiler_identity(a,COMPILER);manifest=a.seal({'scope':__doc__,'compiler':compiler,'grid':[x,y],'metadata':meta});command=compile_saved(a,COMPILER,['inputs/trace.ll','inputs/shim.c'],'artifacts/trace.dylib','trace');products={'artifacts/trace.dylib':command['product']};proofs=[a.proof('before-load',products)];lib=ctypes.CDLL(str(a.path('artifacts/trace.dylib')));fn=lib.psr_main_full;fn.argtypes=[ctypes.c_void_p]*7+[ctypes.c_int32]+[ctypes.c_uint16]*2+[ctypes.c_void_p];fn.restype=None
    images=[c.images[0],c.images[1],np.array(c.gtc.red_samples,dtype='f2')[None,:,None],np.array(c.whites.red_samples,dtype='f2')[None,:,None],None,native['BG_output'],native['FG_output'],*[c.images[i]for i in [4,5,6,7,8,9]]];arrays=[None if v is None else texture(v)for v in images];ptrs=(ctypes.c_void_p*13)(*[None if v is None else v.ctypes.data for v in arrays]);target=texture(c.output_initial);out=np.zeros(meta['original']['observation_float_count'],dtype='f4');params=c.params.copy();fn(ptrs,target.ctypes.data,c.management.ctypes.data,params.ctypes.data,c.stats.ctypes.data,c.roi.ctypes.data,c.srl.ctypes.data,c.version,x,y,out.ctypes.data);actual=np.ctypeslib.as_array((ctypes.c_float*meta['probes']['transfer']['count']).in_dll(lib,'psr_trace_transfer')).copy();stages=[]
    for ssa,ty,count,offset in meta['probes']['transfer']['layout']:
        na=actual[offset:offset+count].astype('f2');mo=probes[ssa].lo.reshape(-1).astype('f2');stages.append({'SSA':ssa,'native_bits':na.view('u2').tolist(),'model_bits':mo.view('u2').tolist(),'bit_mismatches':int(np.count_nonzero(na.view('u2')!=mo.view('u2')))})
    obs={};offset=0
    for n,ssa,count in OBSERVATIONS:obs[n]=out[offset:offset+count];offset+=count
    stability={n:int(np.count_nonzero(obs[n].astype('f2').view('u2')!=native[n][y,x].reshape(-1).view('u2')))for n in ['channel567','linear597','output600']};result={'scope':__doc__,'context_sha256':sha(context_file),'saved_sha256':sha(saved_file),'grid':[x,y],'lane':lane,'model_linear597_values':linear.lo.tolist(),'model_linear597_half_bits':linear.lo.astype('f2').view('u2').tolist(),'saved_native_linear597_half_bits':native['linear597'][y,x].view('u2').tolist(),'stages':stages,'first_divergence':next((s for s in stages if s['bit_mismatches']),None),'observer_stability_half_bit_mismatches':stability,'encode_fma_candidate_half_bits':encode(linear,host_fma=True).lo.astype('f2').view('u2').tolist(),'native_calls':1,'new_full_point_calls':1,'private_manifest_sha256':sha(manifest),'private_storage_relative_to_task':str(a.root.relative_to(REPO.parent)),'command':command,'products':products,'proofs':proofs,'diagnostic_uses_saved_guided_maps_not_full_chain':True};proofs.append(a.proof('after-run',products));a.write('run-result.private.json',encoded(result),mode=0o400);output.write_bytes(encoded(result));print(json.dumps({'grid':[x,y],'first':result['first_divergence'],'stability':stability,'fma_candidate':result['encode_fma_candidate_half_bits']}));return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('air',type=Path);p.add_argument('context',type=Path);p.add_argument('saved',type=Path);p.add_argument('private',type=Path);p.add_argument('output',type=Path);a=p.parse_args();check(a.air,a.context,a.saved,a.private,a.output)
