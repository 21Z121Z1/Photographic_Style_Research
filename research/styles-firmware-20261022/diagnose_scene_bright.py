"""Bounded first failing saved S25 bright pixel; persistent instrumented input."""
from pathlib import Path
import argparse,ctypes,json,re
import numpy as np
from baseline_archive import Archive,sha,encoded,compiler_identity,compile_saved
from complete_fixture import decode
from active_color import Color,replace_color
from color_inverse import f32
from leaf_numeric import V,hc
from pixel_bright import forward,BrightStats
from numeric_trace_host import build
from main_full_host import C_SOURCE,OBSERVATIONS
from native_guided_check import texture,values
from traceable_color_baseline import validate_private_location,COMPILER

ROOT=Path(__file__).parent;REPO=ROOT.parents[1]


def check(air,context_file,saved_file,private,output,detail=False):
    if output.exists():raise FileExistsError(output)
    saved=json.loads(saved_file.read_text());row=saved['rows'][0]
    if saved['identity']['complete_context_sha256']!=sha(context_file):raise ValueError('Context mismatch')
    c=replace_color(decode(json.loads(context_file.read_text())),Color(f32(row['control']['raw_f32_bits'])));native={n:np.array(a,dtype='u2').view('f2')for n,a in {**saved['prefix_native_half_bits'],**row['native_half_bits']}.items()};selected=None
    stat=lambda g,k:V.value(c.stats[2560+g*9+k],'f')
    for y in range(3):
        for x in range(4):
            val=lambda n:V.value(native[n][y,x].reshape(-1)[0]if native[n][y,x].size==1 else native[n][y,x]);probes={};expected=forward(val('skin393'),val('working286'),val('person96'),val('skin95'),V.value(c.params[7]).h(),BrightStats(stat(2,4),stat(3,4),stat(5,0),stat(6,6),stat(6,4)),observations=probes)
            if not np.array_equal(expected.lo.astype('f2').view('u2'),native['bright400'][y,x].view('u2')):selected=(x,y,probes);break
        if selected:break
    if selected is None:raise ValueError('Saved first witness did not reproduce')
    x,y,probes=selected;fused={}
    if detail:
        s=probes[132];probes[133]=s.sqrt();probes[134]=s*V.value(hc('4c00'));probes[135]=probes[134]+V.value(hc('ca00'));probes[136]=probes[135]*s;probes[137]=probes[136]+V.value(4);probes[138]=probes[137]*s
        fused={'SSA135_one_round_half_bits':s.fma_half(V.value(hc('4c00')),V.value(hc('ca00'))).lo.astype('f2').view('u2').tolist(),'SSA137_one_round_half_bits':probes[135].fma_half(s,V.value(4)).lo.astype('f2').view('u2').tolist()}
    ir,meta=build(air.read_text(),{'bright':('renderBrightAndContrast',probes)});validate_private_location(private);a=Archive(private,create=True,repo=REPO)
    for f in ROOT.glob('*.py'):a.input('generators/'+f.name,f.read_bytes(),'exact diagnostic source')
    for name,p in [('source.ll.txt',air),('context.json',context_file),('saved.json',saved_file)]:a.input('binding/'+name,p.read_bytes(),'diagnostic input')
    a.input('inputs/trace.ll',ir.encode(),'actual new instrumented host compiler input');a.input('inputs/shim.c',C_SOURCE.encode(),'actual shim');compiler=compiler_identity(a,COMPILER);m=a.seal({'scope':__doc__,'compiler':compiler,'grid':[x,y],'metadata':meta});proofs=[a.proof('before-compile')];command=compile_saved(a,COMPILER,['inputs/trace.ll','inputs/shim.c'],'artifacts/trace.dylib','trace');products={'artifacts/trace.dylib':command['product']};proofs.append(a.proof('before-load',products));lib=ctypes.CDLL(str(a.path('artifacts/trace.dylib')));fn=lib.psr_main_full;fn.argtypes=[ctypes.c_void_p]*7+[ctypes.c_int32]+[ctypes.c_uint16]*2+[ctypes.c_void_p];fn.restype=None
    images=[c.images[0],c.images[1],np.array(c.gtc.red_samples,dtype='f2')[None,:,None],np.array(c.whites.red_samples,dtype='f2')[None,:,None],None,native['BG_output'],native['FG_output'],*[c.images[i]for i in [4,5,6,7,8,9]]];arrays=[None if v is None else texture(v)for v in images];ptrs=(ctypes.c_void_p*13)(*[None if v is None else v.ctypes.data for v in arrays]);target=texture(c.output_initial);out=np.zeros(meta['original']['observation_float_count'],dtype='f4');params=c.params.copy();fn(ptrs,target.ctypes.data,c.management.ctypes.data,params.ctypes.data,c.stats.ctypes.data,c.roi.ctypes.data,c.srl.ctypes.data,c.version,x,y,out.ctypes.data);actual=np.ctypeslib.as_array((ctypes.c_float*meta['probes']['bright']['count']).in_dll(lib,'psr_trace_bright')).copy();stages=[]
    for ssa,ty,count,offset in meta['probes']['bright']['layout']:
        dt='f2'if ty=='half'else'f4';ut='u2'if ty=='half'else'u4';na=actual[offset:offset+count].astype(dt);mo=probes[ssa].lo.reshape(-1).astype(dt);stages.append({'SSA':ssa,'precision':ty,'native_bits':na.view(ut).tolist(),'model_bits':mo.view(ut).tolist(),'bit_mismatches':int(np.count_nonzero(na.view(ut)!=mo.view(ut)))})
    stages.sort(key=lambda s:s['SSA']);obs={};offset=0
    for n,ssa,count in OBSERVATIONS:obs[n]=out[offset:offset+count];offset+=count
    stability={n:int(np.count_nonzero(obs[n].astype('f2').view('u2')!=native[n][y,x].reshape(-1).view('u2')))for n in ['bright400','skin393','selected404','output600']if n in obs}
    # Hash the actual saved root's consumers rather than publish proprietary IR.
    maintext=(REPO.parent/saved['private_storage_relative_to_task']/'inputs/4-main-observed.ll').read_text();lines=maintext.splitlines();use400=[l for l in lines if re.search(r'%400(?![A-Za-z0-9_])',l)];selection=[l for l in lines if re.match(r'\s*%(399|400|401|402|403|404) =',l)]
    result={'scope':__doc__,'saved_receipt_sha256':sha(saved_file),'context_sha256':sha(context_file),'grid':[x,y],'control':row['control'],'stages':stages,'one_round_candidates':fused,'first_observed_checkpoint_divergence':next(s for s in stages if s['bit_mismatches']),'observer_stability_half_bit_mismatches':stability,'saved_root_SSA399_404_instruction_sha256':[__import__('hashlib').sha256(l.encode()).hexdigest()for l in selection],'saved_root_SSA400_use_line_sha256':[__import__('hashlib').sha256(l.encode()).hexdigest()for l in use400],'native_main_calls':1,'full_chain_calls':0,'saved_guided_maps_for_diagnostic_only':True,'private_manifest_sha256':sha(m),'private_storage_relative_to_task':str(a.root.relative_to(REPO.parent)),'actual_compiler_inputs':{n:a.manifest()['files'][n]for n in ['inputs/trace.ll','inputs/shim.c']},'command':command,'products':products,'proofs':proofs,'original_FP_attributes_changed':False,'GPU_verified':False};proofs.append(a.proof('after-run',products));a.write('run-result.private.json',encoded(result),mode=0o400);output.write_bytes(encoded(result));print(json.dumps({'grid':[x,y],'first_checkpoint':result['first_observed_checkpoint_divergence'],'observer_stability':stability,'native_main_calls':1}));return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('air',type=Path);p.add_argument('context',type=Path);p.add_argument('saved',type=Path);p.add_argument('private',type=Path);p.add_argument('output',type=Path);p.add_argument('--detail',action='store_true');a=p.parse_args();check(a.air,a.context,a.saved,a.private,a.output,a.detail)
