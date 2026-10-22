"""One clamp-domain counterexample: original AIR prefix ends before pow SSA213.

Eight model-only corners select one witness. One original prefix host call
tests its actual pre-pow half base and gamma. Never evaluate pow on a negative
base, infer integer-exponent semantics, clamp its base, or claim original GPU.
"""
import argparse,ctypes,hashlib,itertools,json,re,subprocess,tempfile
from pathlib import Path
import numpy as np
from leaf_numeric import V,DomainUnknown
from pixel_selective import selective,SelectiveTexture
from leaf_host import build,MATH_C


def model_corner(rgb):
    H=V.value;trace={};tex=SelectiveTexture(np.zeros((4,360,4),dtype='f2'),'explicit zero lookup')
    try:selective(H(rgb),H(.4),H(.25),H(.2),tex,[H([0,0])for _ in range(3)],H([0,0,0]),H(0),observations=trace)
    except DomainUnknown:pass
    return {'rgb_half':list(rgb),'converted_half_bits':trace['converted'].lo.astype('f2').view('u2').tolist(),'gamma_half_bits':trace['gamma'].lo.astype('f2').view('u2').tolist(),'converted_half':trace['converted'].lo.tolist()}


def check(source,output):
    if output.exists():raise FileExistsError(output)
    candidates=[model_corner(v)for v in itertools.product([0.,1.],repeat=3)];witness=min(candidates,key=lambda r:min(r['converted_half']))
    text=source.read_text();ir,meta=build(text,['selectiveColorFilter'],emit_wrappers=False)
    body=next(m[0]for m in re.finditer(r'^define[^\n]*@([^ (]+)\([^\n]+\{\n.*?^}',text,re.M|re.S)if'selectiveColorFilter'in m[1]);symbol=re.search(r'@([^ (]+)',body)[1]
    # Keep the exact original arithmetic/call prefix through gamma210.
    stop=re.search(r'^  %210 = [^\n]+',body,re.M).end();prefix=body[:stop]
    result_type='{<3 x half>,half}';prefix=prefix.replace('fastcc <3 x half>','fastcc '+result_type,1)+'\n  %psr0 = insertvalue '+result_type+' poison, <3 x half> %199, 0\n  %psr1 = insertvalue '+result_type+' %psr0, half %210, 1\n  ret '+result_type+' %psr1\n}'
    ir=ir.replace(body,prefix)
    wrapper=['define void @psr_domain(ptr %input,ptr %texture,ptr %output){']
    for i in range(3):wrapper += [f'%p{i}=getelementptr half,ptr %input,i64 {i}',f'%h{i}=load half,ptr %p{i}']
    wrapper += ['%v0=insertelement <3 x half> poison,half %h0,i32 0','%v1=insertelement <3 x half> %v0,half %h1,i32 1','%v=insertelement <3 x half> %v1,half %h2,i32 2','%tex=addrspacecast ptr %texture to ptr addrspace(1)',f'%r=call fastcc {result_type} @{symbol}(<3 x half> %v,half 0xH3666,half 0xH3400,half 0xH3266,ptr addrspace(1) %tex,<2 x half> zeroinitializer,<2 x half> zeroinitializer,<2 x half> zeroinitializer,<3 x half> zeroinitializer,half 0xH0000)',f'%rgb=extractvalue {result_type} %r,0',f'%gamma=extractvalue {result_type} %r,1']
    for i in range(3):wrapper += [f'%c{i}=extractelement <3 x half> %rgb,i32 {i}',f'%o{i}=getelementptr half,ptr %output,i64 {i}',f'store half %c{i},ptr %o{i}']
    wrapper += ['%og=getelementptr half,ptr %output,i64 3','store half %gamma,ptr %og','ret void','}'];ir+='\n'+'\n'.join(wrapper)
    if re.search(r'^  %213 =',ir,re.M):raise AssertionError('Post-prefix pow must be absent')
    with tempfile.TemporaryDirectory(prefix='psr-selective-domain-')as t:
        w=Path(t);(w/'p.ll').write_text(ir);(w/'shim.c').write_text(MATH_C);p=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',str(w/'p.ll'),str(w/'shim.c'),'-o',str(w/'p.dylib')],capture_output=True,text=True,timeout=60)
        if p.returncode:raise RuntimeError(p.stderr[:4000])
        # Existing leaf sampler ABI: uint32 width then float red values.
        # Its other channels are zero. This is exact only for the supplied
        # all-zero RGBA texture: all rows/coordinates give the same zero.
        lookup=np.r_[np.array([360],dtype='u4').view('f4'),np.zeros(360,dtype='f4')]
        lib=ctypes.CDLL(str(w/'p.dylib'));fn=lib.psr_domain;fn.argtypes=[ctypes.c_void_p]*3;fn.restype=None;rgb=np.array(witness['rgb_half'],dtype='f2');out=np.zeros(4,dtype='f2');fn(rgb.ctypes.data,lookup.ctypes.data,out.ctypes.data)
    r={'scope':__doc__,'reference':'iPhone17,3 /24A446 AIR10','source_canonical_gate':'leaf_host.build exact canonical module admission','original_function_text_sha256':hashlib.sha256(body.encode()).hexdigest(),'original_selected_prefix_sha256':hashlib.sha256(body[:stop].encode()).hexdigest(),'original_inclusive_last_SSA':210,'post_pow_SSA213_executed':False,'host_IR_sha256':hashlib.sha256(ir.encode()).hexdigest(),'host_build':meta,'model_only_corner_candidates':candidates,'original_host_prefix_calls':1,'witness_rgb_half':witness['rgb_half'],'native_converted_half':out[:3].astype('f8').tolist(),'native_gamma_half':float(out[3]),'native_half_bits':out.view('u2').tolist(),'negative_components':np.flatnonzero(out[:3]<0).tolist(),'model_vs_host_converted_bit_mismatches':int(np.count_nonzero(out[:3].view('u2')!=np.array(witness['converted_half_bits'],dtype='u2'))),'input_inside_original_clamp_domain':True,'actual_host_rounding_graph_negative_reachable':bool(np.any(out[:3]<0)),'all_clamp_domain_nonnegative_claim_refuted_for_this_host_contract':bool(np.any(out[:3]<0)),'original_GPU_negative_reachability':'unverified; host math and contraction are explicit assumptions','AIR_pow_negative_base_semantics':'not inferred from host powf or gamma1; conservative model restriction retained','full_domain_proof':'one counterexample refutes universal positivity under this host contract; no characterization of all negative regions or arbitrary lookup','S17_outer_negative_endpoints_reachable':'not established by this small negative witness','clamp_domain_or_pow_budgets_changed':False,'original_GPU_executed':False};output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');print(json.dumps({k:r[k]for k in ['witness_rgb_half','native_converted_half','native_gamma_half','negative_components','original_host_prefix_calls']}));return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();check(a.source,a.output)
