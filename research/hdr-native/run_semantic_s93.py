"""S93: coarse cold starts for practical robustness; no half-lattice search."""
from pathlib import Path
import hashlib,json,os

D=Path(__file__).resolve().parent;source=D/'run_semantic_s91.py'
original=source.read_text();expected='58d3f1f6480a5ec44e37d0837c5e944b5c771f6f6b516cb8e2dbf07e6b9670f1'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
changes=[('inputs_s91.json','inputs_s93.json'),('SEMANTIC_S91_INPUT_SESSION','SEMANTIC_S93_INPUT_SESSION')]
for field in['width','height','pixelFormat']:changes.append((f'[call[@"textures"][@"0"] {field}]',f'((id<MTLTexture>)call[@"textures"][@"0"]).{field}'))
injection=r'''
# Derive a new include. The old S5/V7 include, bounds, eligible mask, LM
# equations, 24 iterations and finite differences remain unchanged.
old_inc=(GEN/'semantic_inverse_s5.inc').read_text()
coarse_block=r"""
 NSMutableArray*coldRows=[NSMutableArray new];const float coldScales[]={2,1,.5f,.25f,.125f,.0625f,.03125f,.015625f};
 if(!saved)for(NSUInteger ci=0;ci<8;ci++){@autoreleasepool{
  for(NSUInteger i=0;i<n;i++)for(int c=0;c<3;c++)x[i*3+c]=fminf(high,fmaxf(low,(float)target[i*4+c]*coldScales[ci]));
  NSData*y=evaluate(x);remember(x,y.bytes);NSUInteger failed=0;float maximum=0;
  for(NSUInteger i=0;i<n;i++)if(eligible[i]){failed+=best[i]>1e-3;maximum=fmaxf(maximum,best[i]);}
  [coldRows addObject:@{@"output_scale":@(coldScales[ci]),@"best_failed_eligible":@(failed),@"best_max_relative":@(maximum)}];
 }}
 NSMutableData*coarseStorage=[NSMutableData dataWithBytes:bestX length:n*12];const float*coarseSeed=coarseStorage.bytes;
 [[NSJSONSerialization dataWithJSONObject:@{@"method":@"Eight predeclared output-derived powers-of-two seeds, choose native forward residual per pixel, then unchanged24LM. No original input/original neutral oracle is a seed.",@"steps":coldRows,@"lower":@(low),@"upper":@(high),@"legacy_mask_and_1e3_threshold_unchanged":@YES,@"half_lattice_search":@NO}options:NSJSONWritingPrettyPrinted error:NULL]writeToFile:[dir stringByAppendingPathComponent:@"native-inverse-cold-start.json"]atomically:YES];
"""
anchor=' for(int seed=0;seed<(saved?0:1);seed++){'
init='saved?saved[i*3+c]:target[i*4+c]*factors[seed]'
assert old_inc.count(anchor)==1 and old_inc.count(init)==1
new_inc=old_inc.replace(anchor,coarse_block+anchor).replace(init,'saved?saved[i*3+c]:coarseSeed[i*3+c]')
label='S5: one output-derived seed, 24 bounded log-RGB LM iterations, native Apple oracle; no lattice search; all failures retained'
assert new_inc.count(label)==1
new_inc=new_inc.replace(label,'S93: eight coarse output-derived powers-of-two starts then unchanged24LM, native Apple oracle; no lattice search; all failures retained')
(GEN/'semantic_inverse_s93.inc').write_text(new_inc)
(O/'S93-inverse-include.txt').write_text(new_inc)
save(O/'S93-seed-binding.json',{'old_generated_include_SHA256':hashlib.sha256(old_inc.encode()).hexdigest(),'new_generated_include_SHA256':hashlib.sha256(new_inc.encode()).hexdigest(),'scales':[2,1,.5,.25,.125,.0625,.03125,.015625],'original_include_unchanged':True,'new_include':'semantic_inverse_s93.inc','original_input_used_as_seed':False,'neutral_oracle_used_for_seed_selection':False,'LM_equations_iterations_bounds_mask_unchanged':True,'half_lattice_search':False})
'''
anchor="assert command([sys.executable,S/'generate_semantic_s5.py',GEN],O/'generate.log') == 0"
changes.append((anchor,anchor+'\n'+injection))
anchor="(GEN/'semantic_consumer_s91.m').write_text(native)"
changes.append((anchor,"native=native.replace('#include \"semantic_inverse_s5.inc\"','#include \"semantic_inverse_s93.inc\"')\n"+anchor))
anchor="row['inverse_available']=True;row['inverse']=json.loads((p/'native-inverse.json').read_text());rt="
extra="row['cold_start']=json.loads((p/'native-inverse-cold-start.json').read_text());rt="
changes.append((anchor,anchor[:-3]+extra))
# Extra observations use held-aside original inputs only after the solve.
anchor="eligible=np.fromfile(p/'native-inverse-eligible.u8','u1').reshape(shape).astype(bool)"
observation=r'''
    true_input=image(p/'texture-0.bin')
    outside=np.any((true_input<2**-20)|(true_input>1.25),axis=-1)
    row['held_out_original_input_domain']={'min':float(true_input.min()),'max':float(true_input.max()),'eligible_outside_old_search_domain':int((eligible&outside).sum()),'total_outside_old_search_domain':int(outside.sum()),'not_used_as_solver_seed':True}
    mt=json.loads((p/'texture-11.bin.json').read_text());assert mt['shape'][:2]==list(shape)
    matte=np.fromfile(p/'texture-11.bin','<f2').reshape(mt['shape'])[...,0].astype('f8')
    pad=np.pad(matte,1,mode='edge');mx=np.maximum.reduce([pad[y:y+shape[0],x:x+shape[1]]for y in range(3)for x in range(3)]);mn=np.minimum.reduce([pad[y:y+shape[0],x:x+shape[1]]for y in range(3)for x in range(3)])
    support=mx>0;boundary=(mx-mn)>1/255
    row['matte_3x3_diagnostic']={'support_pixels':int(support.sum()),'outside_pixels':int((~support).sum()),'boundary_pixels':int(boundary.sum()),'not_a_new_legacy_mask':True,'not_used_to_gate_output':True,'scope':'Conservative3x3 support on native texture11 with the S92/S93 identity normalized affine; diagnostic, not full-domain certification'}
'''
changes.append((anchor,anchor+'\n'+observation))
anchor="row['operator_metrics'].append(r)"
extra=r'''
            r['outside_matte_3x3_max_change']=float(np.max(abs(a-base)[~support]))if (~support).any()else None
            r['outside_matte_3x3_native_oracle_max_change']=float(np.max(abs(oracle-base)[~support]))if (~support).any()else None
            r['matte_boundary_eligible_EV']=stats(abs(np.log2(ya[good&boundary]/yb[good&boundary])))
            r['PSNR_peak1_dB']='inf'if not np.any(a!=b)else float(-10*np.log10(np.mean((a.astype('f8')-b)**2)))
'''
changes.append((anchor,extra+'\n            '+anchor))
derived=original;records=[]
for old,new in changes:
    count=derived.count(old);assert count==1,(old,count)
    derived=derived.replace(old,new);records.append({'old':old,'new':new,'count':count})
compile(derived,'S93-derived-preflight','exec')
out=Path(os.environ['W'])/'out';(out/'S93-derived-driver.txt').write_text(derived)
(out/'S93-binding.json').write_text(json.dumps({'original_source':'research/hdr-native/run_semantic_s91.py','original_source_SHA256':expected,'derived_source_SHA256':hashlib.sha256(derived.encode()).hexdigest(),'wrapper_source_SHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'exact_replacements':records,'change_scope':'Explicit Metal type/transport bindings, new coarse-seed include and extra held-aside domain/matte diagnostics. Original S5/V7/structured model and S82 effect interpolation remain unchanged.','precision_research':False},indent=2)+'\n')
exec(compile(derived,'S93-derived-S91-driver','exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
