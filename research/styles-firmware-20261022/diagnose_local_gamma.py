"""Bounded replay of the saved local+gamma witness, with SSA checkpoints.

Only that witness is executed. Instrumentation adds stores, not arithmetic;
instrumented output is checked against an uninstrumented original block.
"""
import argparse,ctypes,hashlib,json,re,subprocess,tempfile
from pathlib import Path
import numpy as np
from leaf_host import build,MATH_C
from leaf_numeric import V,hc,fc,mix,exterior
from pixel_leaves import H,F,dot,root_components
from pixel_remaining import local_contrast,gamma_contrast


LOCAL={89:'half',94:'half',98:'half',99:'<3 x half>',100:'half',101:'half',102:'half',128:'<3 x half>',134:'<3 x half>',135:'<3 x half>',136:'<3 x half>',137:'<3 x half>',140:'<3 x half>',142:'<3 x half>'}
GAMMA={153:'<3 x half>',154:'half',155:'float',156:'float',157:'float',158:'half',159:'float',160:'float',161:'float',162:'half',163:'half',164:'half',165:'half',166:'half',167:'half',170:'<3 x half>',171:'<3 x half>',174:'<3 x half>'}


def model_trace(rgb,guide,amount,local):
    if local:
        c=rgb.clamp();s=dot(c,[hc('3555')]*3).sqrt();shape=((1-s.f())*s.f()).h();root=c.sqrt();groot=guide.sqrt();a=shape*amount;amp=a*H(2,rgb)
        r,g,b=root_components(root,amp);color=(((g+root)+r)+b)+(a*H(-2,rgb))*groot
        neutral=mix(root,groot,a*H(-2,rgb));mixed=mix(neutral,color,H(hc('3a66'),rgb));positive=mixed.maximum(0);squared=positive.square();work=exterior(rgb)+squared;out=mix(work,work.maximum(rgb),H(0,rgb))
        d={89:amount,94:s,98:shape,99:root,100:groot,101:a,102:amp,128:color,134:neutral,135:mixed,136:positive,137:squared,140:work,142:out}
        np.testing.assert_array_equal(out.lo,local_contrast(rgb,guide,amount).lo)
    else:
        c=rgb.clamp();mean=dot(c,[hc('3555')]*3);g=guide.f();prod=g*F(fc('400B333340000000'),rgb);q=prod+F(fc('BFF3340000000000'),rgb);qh=q.h();qf=qh.f();added=qf+F(fc('3FF0FDBF40000000'),rgb);scaled=added*F(fc('3FDA374BC0000000'),rgb);mapped=scaled.h();delta=mapped-mean;amp=amount*H(2,rgb);product=amp*delta;shifted=product+1;exponent=shifted.maximum(0);power=c.pow(exponent);positive=power.maximum(0);out=exterior(rgb)+positive
        d={153:c,154:mean,155:g,156:prod,157:q,158:qh,159:qf,160:added,161:scaled,162:mapped,163:delta,164:amp,165:product,166:shifted,167:exponent,170:power,171:positive,174:out}
        np.testing.assert_array_equal(out.lo,gamma_contrast(rgb,guide,amount).lo)
    return d


def instrument(ir,checkpoints):
    # Instrument complete original BG function, preserving all gate behavior.
    start=ir.index('define internal fastcc <3 x half> @_Z19renderBGAdjustments');end=ir.index('\n}',start)+2;body=ir[start:end];offset=0;locations={}
    for ssa,ty in checkpoints.items():
        m=re.search(r'^  %'+str(ssa)+r' = [^\n]+',body,re.M)
        if not m:raise ValueError(ssa)
        n=3 if ty.startswith('<')else 1;lines=[];locations[ssa]=(offset,n)
        for lane in range(n):
            value=f'%{ssa}'
            if n>1:lines.append(f'%trace_{ssa}_{lane}_h=extractelement {ty} %{ssa},i32 {lane}');value=f'%trace_{ssa}_{lane}_h'
            if 'half'in ty:lines.append(f'%trace_{ssa}_{lane}_f=fpext half {value} to float');value=f'%trace_{ssa}_{lane}_f'
            lines += [f'%trace_{ssa}_{lane}_p=getelementptr [128 x float],ptr @psr_trace,i32 0,i32 {offset}',f'store float {value},ptr %trace_{ssa}_{lane}_p'];offset+=1
        body=body[:m.end()]+'\n'+'\n'.join(lines)+body[m.end():]
    observed='@psr_trace = global [128 x float] zeroinitializer\n'+ir[:start]+body+ir[end:]
    group=re.search(r'unnamed_addr #(\d+) \{',body)[1];attributes=re.search(r'^attributes #'+group+r' = .*$',observed,re.M)[0]
    if'memory(read)'not in attributes:raise ValueError('Expected original BG read-only memory summary')
    observed=observed.replace(attributes,attributes.replace('memory(read)','memory(readwrite)'))
    return observed,locations


def diagnose(source,receipt,output):
    if output.exists():raise FileExistsError(output)
    r=json.loads(receipt.read_text());witness=next(x for x in r['rows']if x['point_half_bit_mismatches']);assert witness['profile']=='local+gamma'
    data=np.array(witness['input'],dtype='f4');fields=np.array(witness['field_values'],dtype='f4');raw=np.r_[data,fields].astype('f4');tex=np.array([0],dtype='f4');original,functions=build(source.read_text(),['renderBGAdjustments']);traced,locations=instrument(original,{**LOCAL,**GAMMA});native={};results={};variant_trace={}
    with tempfile.TemporaryDirectory(prefix='psr-local-gamma-')as t:
        root=Path(t);(root/'math.c').write_text(MATH_C)
        variants=[('original',original),('instrumented',traced)]
        for name,ssas in [('separate_f32_156_157',[156,157]),('separate_half_165_166',[165,166])]:
            variant=traced
            for ssa in ssas:variant=re.sub(r'(^  %'+str(ssa)+r' = f(?:mul|add)) fast ',r'\1 ',variant,flags=re.M)
            variants.append((name,variant))
        for label,ir in variants:
            (root/(label+'.ll')).write_text(ir);libfile=root/(label+'.dylib')
            p=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',str(root/(label+'.ll')),str(root/'math.c'),'-o',str(libfile)],capture_output=True,text=True,timeout=60)
            if p.returncode:raise RuntimeError(p.stderr[:4000])
            lib=ctypes.CDLL(str(libfile));fn=lib.psr_leaf_0;fn.argtypes=[ctypes.c_void_p]*3;out=np.zeros(3,dtype='f4');fn(raw.ctypes.data,tex.ctypes.data,out.ctypes.data);results[label]=out.tolist()
            if label!='original':
                trace=np.ctypeslib.as_array((ctypes.c_float*128).in_dll(lib,'psr_trace')).copy()
                values={ssa:trace[pos:pos+n].astype('f8')for ssa,(pos,n)in locations.items()}
                variant_trace[label]={str(k):values[k].tolist()for k in [157,158,165,166,170]}
                if label=='instrumented':native=values
    stable=results['original']==results['instrumented']==witness['native_output_half']
    local=model_trace(V.value(data[:3]),V.value(data[3]),V.value(fields[5]),True)
    # Trace both gamma paths: model-local input, and supplied native-local input.
    gamma=model_trace(local[142],V.value(data[3]),V.value(fields[4]),False)
    gamma_same_input=model_trace(V.value(native[142]),V.value(data[3]),V.value(fields[4]),False)
    rows=[]
    for ssa,v in {**local,**gamma}.items():
        a=np.atleast_1d(v.lo);b=native[ssa];row={'SSA':ssa,'precision':v.precision,'native':b.tolist(),'model':a.tolist(),'equal':bool(np.array_equal(a,b))}
        if ssa in gamma_same_input:row['equal_with_native_local_input']=bool(np.array_equal(np.atleast_1d(gamma_same_input[ssa].lo),b))
        rows.append(row)
    fused157=float(np.float32(float(data[3])*fc('400B333340000000')+fc('BFF3340000000000')))
    fused166=float(np.float16(float(gamma[164].lo)*float(gamma[163].lo)+1))
    result={'witness_receipt_sha256':hashlib.sha256(receipt.read_bytes()).hexdigest(),'one_saved_witness_only':True,'old_batches_rerun':False,'original_BG_function_sha256':functions['renderBGAdjustments'],'original_host_ir_sha256':hashlib.sha256(original.encode()).hexdigest(),'instrumented_ir_sha256':hashlib.sha256(traced.encode()).hexdigest(),'instrumentation_output_matches_original_and_saved':stable,'observation_memory_summary':'memory(readwrite), preserving all original floating-point attributes','outputs':results,'variant_checkpoints':variant_trace,'diagnostic_variants':'Only fast flags of indicated two original instructions removed; variants are not original GPU execution','one_round_fma_candidates':{'SSA157':fused157,'SSA166':fused166,'match_observed_host':bool(fused157==native[157][0]and fused166==native[166][0])},'first_selected_different_SSA':next((x['SSA']for x in rows if not x['equal']),None),'rows':rows,'source_sha256':{n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest()for n in ['diagnose_local_gamma.py','leaf_numeric.py','pixel_remaining.py','leaf_host.py']},'GPU_executed':False}
    output.write_text(json.dumps(result,indent=2)+'\n')
    if not stable:raise AssertionError('Instrumentation perturbed output; trace not accepted')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('receipt',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=diagnose(a.source,a.receipt,a.output);print(json.dumps({k:v for k,v in r.items()if k!='rows'and k!='source_sha256'}))
