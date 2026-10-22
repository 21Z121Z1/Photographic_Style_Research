"""Replay saved guided checkpoints; three new calls only for missing witnesses."""
import argparse,ctypes,hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from diagnose_guided import candidate
from guided_precision import stages,coefficients
from guided_conditioned import legacy
from native_ltm_roi_chain import fixture,model_inputs,EPSILON
from full_ltm_chain import generate
from guided_host import build,C_SOURCE
from native_guided_check import texture,values


def check(source_dir,baseline,complete,output):
    if output.exists():raise FileExistsError(output)
    old=json.loads(baseline.read_text());saved=json.loads(complete.read_text());rows=[];units=[];meta=[]
    for i in [0,1]:ir,m=build((source_dir/f'{90+i:04d}.ll.txt').read_text(),i);units.append(ir);meta.append(m)
    with tempfile.TemporaryDirectory(prefix='psr-guided-refine-')as t:
        w=Path(t);paths=[]
        for i,ir in enumerate(units):p=w/f'{i}.ll';p.write_text(ir);paths.append(str(p))
        (w/'shim.c').write_text(C_SOURCE);p=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',*paths,str(w/'shim.c'),'-o',str(w/'witness.dylib')],capture_output=True,text=True,timeout=60)
        if p.returncode:raise RuntimeError(p.stderr[:2000])
        lib=ctypes.CDLL(str(w/'witness.dylib'))
        for frow in old['rows']:
            index=frow['fixture'];f=fixture(index);args,kw=model_inputs(f,(0,0),.2,True);gen=generate(*args,**{k:v for k,v in kw.items()if k not in['consumer_semantic7','roi','reference196','person96']});gain=gen.raw_fg.pixels.lo.astype('f2');new=stages(gain,f['guide'],EPSILON,legacy);a,b,ma,mb=coefficients(gain,f['guide'],EPSILON,legacy);x,y=frow['grid'];checks=[]
            for s in frow['stages']:
                actual=np.array(s['native_f32_bits'],dtype='u4');expected=new[s['name']][y,x].view('u4');checks.append({'stage':s['name'],'f32_bit_mismatches':int(np.count_nonzero(actual!=expected))})
            row={'fixture':index,'grid':[x,y],'f32_checkpoints':checks,'f32_components':52,'f32_bit_mismatches':sum(c['f32_bit_mismatches']for c in checks),'native_calls':0}
            if index==0:
                row['saved_a_bit_mismatches']=int(np.count_nonzero(a.view('u2')!=np.array(saved['native_half_bits']['FG_a'],dtype='u2')));row['saved_mean_a_bit_mismatches']=int(np.count_nonzero(ma.view('u2')!=np.array(saved['native_half_bits']['FG_mean_a'],dtype='u2')))
            else:
                fn=lib.psr_guided_0;fn.argtypes=[ctypes.c_void_p]*7+[ctypes.c_uint16]*2;fn.restype=None;aa=texture(np.zeros_like(a));bb=texture(np.zeros_like(b));gt,it=texture(gain),texture(f['guide']);radius=np.array([1],dtype='i2');eps=np.array([EPSILON],dtype='f4');single=np.array([0],dtype='u1');fn(*(v.ctypes.data for v in [gt,it,aa,bb,radius,eps,single]),x,y);unobserved=values(aa,a.shape)[y,x];row['observer_a_bits_match_unobserved']=bool(np.array_equal(unobserved.view('u2'),np.array(frow['native_half_a_bits'],dtype='u2')));row['unobserved_a_bit_mismatches']=int(np.count_nonzero(unobserved.view('u2')!=a[y,x].view('u2')));row['native_calls']+=1
                legacy_a,legacy_b,old_ma,old_mb=legacy.coefficients(gain,f['guide'],1,EPSILON);changed=np.argwhere(ma.view('u2')!=old_ma.view('u2'));row['mean_a_targets']=changed.tolist();row['mean_a_probes']=[]
                # Full arrays are conditional test inputs from the same model.
                # AIR90 equality follows the earlier S14B all-component receipt,
                # its one recovered mismatch, and the above original checkpoint.
                at,bt=texture(a),texture(b);mta,mtb=texture(np.zeros_like(ma)),texture(np.zeros_like(mb));avg=lib.psr_guided_1;avg.argtypes=[ctypes.c_void_p]*7+[ctypes.c_uint16]*2;avg.restype=None
                for yy,xx,lane in changed:
                    avg(*(v.ctypes.data for v in [at,bt,mta,mtb,radius,eps,single]),int(xx),int(yy));actual=values(mta,ma.shape)[yy,xx];row['mean_a_probes'].append({'grid':[int(xx),int(yy)],'lane':int(lane),'native_half_bits':actual.view('u2').tolist(),'new_half_bit_mismatches':int(np.count_nonzero(actual.view('u2')!=ma[yy,xx].view('u2'))),'old_half_bit_mismatches':int(np.count_nonzero(actual.view('u2')!=old_ma[yy,xx].view('u2')))});row['native_calls']+=1
                row['mean_a_probe_scope']='original AIR91 on explicit computed a/b arrays; not a new full guided/native-image run'
            rows.append(row)
    r={'scope':__doc__,'hardware':'iPhone17,3','build':'24A446','original':meta,'baseline_sha256':hashlib.sha256(baseline.read_bytes()).hexdigest(),'complete_sha256':hashlib.sha256(complete.read_bytes()).hexdigest(),'rows':rows,'native_calls':sum(r['native_calls']for r in rows),'old_batches_repeated':False,'epsilon_changed':False,'sampler_changed':False,'set_budgets_changed':False,'coefficient_order':'inv9 multiply; cov FMA; epsilon_plus_mii=FMA(sum_ii,inv9,epsilon); var=FMA(-mean_i,mean_i,epsilon_plus_mii); b FMA','iOS_GPU_order_proven':False};output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source_dir',type=Path);p.add_argument('baseline',type=Path);p.add_argument('complete',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source_dir,a.baseline,a.complete,a.output);print(json.dumps(r['rows']))
