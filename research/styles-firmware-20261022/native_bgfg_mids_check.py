"""Only neutral/mids paths through original BG and FG helpers on host CPU.

Other leaf functions are replaced by aborting stubs; exercising one fails the
owned checker process. This never validates their arithmetic or full helpers.
"""
import argparse,ctypes,hashlib,json,re,subprocess,tempfile
from pathlib import Path
import numpy as np
from native_semantic_tone_check import fragment,SHIM_IR,SAMPLER_C
from bgfg_tone import mids_half,run,PixelContext,GATE
from semantic_tone import I
from tone_interface import ConsumerFields,ScaledControls,ResolvedSceneType

EXTRA=r'''
declare float @llvm.fabs.f32(float)
declare float @psr_pow_scalar(float,float)
declare void @abort() noreturn
define float @air.fast_fabs.f32(float %x){
 %r=call float @llvm.fabs.f32(float %x)
 ret float %r
}
define <3 x half> @air.fmax.v3f16(<3 x half> %a,<3 x half> %b){
 %c=fcmp ogt <3 x half> %a,%b
 %r=select <3 x i1> %c,<3 x half> %a,<3 x half> %b
 ret <3 x half> %r
}
define <3 x half> @air.saturate.v3f16(<3 x half> %x){
 %a=call <3 x half> @air.fmax.v3f16(<3 x half> %x,<3 x half> zeroinitializer)
 %b=call <3 x half> @air.fmin.v3f16(<3 x half> %a,<3 x half> splat(half 0xH3C00))
 ret <3 x half> %b
}
define half @air.fmax3.f16(half %a,half %b,half %c){
 %p=fcmp ogt half %a,%b
 %x=select i1 %p,half %a,half %b
 %q=fcmp ogt half %x,%c
 %r=select i1 %q,half %x,half %c
 ret half %r
}
define half @air.pow.f16(half %a,half %b){
 %af=fpext half %a to float
 %bf=fpext half %b to float
 %f=call float @psr_pow_scalar(float %af,float %bf)
 %r=fptrunc float %f to half
 ret half %r
}
'''


def make_fragment(source):
    fragment(source)  # Source/module identity check only, no accepted batch.
    functions={}
    for m in re.finditer(r'^define[^\n]*?@([^ (]+)\([^\n]+\{\n',source,re.M):functions[m[1]]=source[m.start():source.index('\n}',m.end())+2]
    names=[next(n for n in functions if key in n)for key in ['renderBGAdjustments','renderFGAdjustments']];bodies=[functions[n]for n in names]
    stubs=[]
    for name in sorted({x for body in bodies for x in re.findall(r'@(_Z[^ (]+)\(',body)}-set(names)):
        header=functions[name].splitlines()[0];header=re.sub(r' #\d+', '',header)
        stubs.append(header+'\ncall void @abort()\nunreachable\n}')
    implemented=set(re.findall(r'^define[^\n]*?@([^ (]+)\(',SHIM_IR+'\n'+EXTRA,re.M))
    for name in sorted({x for body in bodies for x in re.findall(r'@(air\.[^ (]+)\(',body)}-implemented):
        declaration=re.search(r'^declare[^\n]*?@'+re.escape(name)+r'\([^\n]+$',source,re.M)[0]
        header=declaration.replace('declare','define',1).split(' local_unnamed_addr',1)[0]
        stubs.append(header+' {\ncall void @abort()\nunreachable\n}')
    metadata=dict(re.findall(r'^!(\d+) = (.*)$',source,re.M));ids=set(re.findall(r'!(\d+)', '\n'.join(bodies)));pending=list(ids)
    while pending:
        for n in re.findall(r'!(\d+)',metadata[pending.pop()]):
            if n not in ids:ids.add(n);pending.append(n)
    attrs=set(re.findall(r'#(\d+)', '\n'.join(bodies)))
    wrapper=['define void @psr_mids(i32 %which,ptr %input,ptr %params,ptr %output){']
    for n in range(9):wrapper += [f'%p{n}=getelementptr float,ptr %input,i64 {n}',f'%f{n}=load float,ptr %p{n}',f'%h{n}=fptrunc float %f{n} to half']
    for label,base in [('x',0),('y',3)]:wrapper += [f'%{label}0=insertelement <3 x half> poison,half %h{base},i32 0',f'%{label}1=insertelement <3 x half> %{label}0,half %h{base+1},i32 1',f'%{label}=insertelement <3 x half> %{label}1,half %h{base+2},i32 2']
    wrapper += ['%pp=addrspacecast ptr %params to ptr addrspace(1)','%isbg=icmp eq i32 %which,0','br i1 %isbg,label %bg,label %fg','bg:',
                f'%b=call fastcc <3 x half> @{names[0]}(<3 x half> %x,half %h6,half undef,half %h7,ptr addrspace(1) %pp,ptr addrspace(1) null)','br label %done','fg:',
                f'%f=call fastcc <3 x half> @{names[1]}(<3 x half> %x,<3 x half> %y,half %h7,half undef,half %h8,half %h6,ptr addrspace(1) %pp,ptr addrspace(1) null)','br label %done','done:','%r=phi <3 x half> [%b,%bg],[%f,%fg]']
    for n in range(3):wrapper += [f'%o{n}=extractelement <3 x half> %r,i32 {n}',f'%v{n}=fpext half %o{n} to float',f'%q{n}=getelementptr float,ptr %output,i64 {n}',f'store float %v{n},ptr %q{n}']
    wrapper += ['ret void','}']
    types=[re.search(r'^%struct\.'+name+r' = .*$',source,re.M)[0]for name in ['SSRBGAdjustment','SSRFGAdjustment']]
    ir='\n'.join([*types,*bodies,*stubs,SHIM_IR,EXTRA,'\n'.join(wrapper),*[re.search(r'^attributes #'+n+r' = .*$',source,re.M)[0]for n in attrs],*[f'!{n} = {metadata[n]}'for n in sorted(ids,key=int)]])+'\n'
    return ir,{n:hashlib.sha256(functions[n].encode()).hexdigest()for n in names},len(stubs)


def check(source: Path,output: Path):
    if output.exists():raise FileExistsError(output)
    ir,functions,stubcount=make_fragment(source.read_text());rng=np.random.default_rng(0x5589);rows=[];outputs=[]
    with tempfile.TemporaryDirectory(prefix='psr-bgfg-mids-')as t:
        w=Path(t);(w/'fragment.ll').write_text(ir);(w/'shim.c').write_text(SAMPLER_C+'\nfloat psr_pow_scalar(float a,float b){return powf(a,b);}\n');libpath=w/'mids.dylib'
        c=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',str(w/'fragment.ll'),str(w/'shim.c'),'-o',str(libpath)],capture_output=True,text=True,timeout=60)
        if c.returncode:raise RuntimeError(c.stderr[:5000])
        lib=ctypes.CDLL(str(libpath));fn=lib.psr_mids;fn.argtypes=[ctypes.c_uint32,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p];fn.restype=None
        for block in ['bg','fg']:
            for person in [0.,.35,1.]:
                for amount in [-.5,-GATE,float(np.nextafter(np.float32(GATE),np.float32(0))),0.,GATE,.2,.5,.9]:
                    data=np.r_[rng.uniform(0,1,6),.4,person,.2].astype('f2').astype('f4');v=np.zeros(40);v[8]=v[11]=v[22]=1;v[17]=.25;v[7 if block=='bg'else 19]=amount
                    fields=ConsumerFields(ScaledControls(np.float32(.5),np.float32(.3),np.float32(0),ResolvedSceneType(4)),'synthetic_control',v,np.zeros(40))
                    params=v[:17].astype('f4')if block=='bg'else v[17:33].astype('f4');out=np.zeros(3,dtype='f4');fn(block=='fg',data.ctypes.data,params.ctypes.data,out.ctypes.data)
                    bounds=run(block,I.point(data[:3]),fields,PixelContext(*map(float,data[[6,7,8]])),semantic_rgb=I.point(data[3:6]))
                    if bounds.status!='computed_set':raise AssertionError('Unexpected missing operator in controlled mids fixture')
                    h=lambda a:np.asarray(a,dtype='f2')
                    mix=lambda a,b,w:h(h(a)+h(h(h(b)-h(a))*h(w)))
                    initial=h(data[:3])if block=='bg'else mix(data[:3],data[3:6],np.float16(np.float32(.75)*np.float32(data[7])))
                    changed=mids_half(initial,np.float16(amount))if abs(float(np.float32(amount)))>=GATE else initial
                    model=changed if block=='bg'else mix(initial,changed,data[7]);outputs.append(out.copy())
                    rows.append({'block':block,'person_weight':float(data[7]),'amount_f32':float(np.float32(amount)),
                                 'half_bit_mismatches':int(np.count_nonzero(out.astype('f2').view('u2')!=model.view('u2'))),'max_absolute_error':float(np.max(abs(out.astype('f8')-model))),
                                 'range_covered':bool(np.all(out>=bounds.output.lo)and np.all(out<=bounds.output.hi))})
    r={'scope':__doc__,'source_function_sha256':functions,'host_fragment_sha256':hashlib.sha256(ir.encode()).hexdigest(),'unmodeled_aborting_stubs':stubcount,
       'records':len(rows),'RGB_values':len(rows)*3,'half_bit_mismatches':sum(x['half_bit_mismatches']for x in rows),'max_absolute_error':max(x['max_absolute_error']for x in rows),'range_violations':sum(not x['range_covered']for x in rows),
       'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'model_sha256':hashlib.sha256((Path(__file__).parent/'bgfg_tone.py').read_bytes()).hexdigest(),'native_output_sha256':hashlib.sha256(np.asarray(outputs,dtype='f4').tobytes()).hexdigest(),
       'complete_BG_FG_operators_verified':False,'GPU_executed':False,'accepted_batches_repeated':False,'rows':rows}
    output.write_text(json.dumps(r,indent=2)+'\n')
    if r['range_violations']:raise AssertionError('Controlled mids path outside set allowance; receipt retained')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.output);print(json.dumps({k:r[k]for k in ['records','RGB_values','half_bit_mismatches','max_absolute_error','range_violations']}))
