"""Same frozen S15A context: compare saved old widths and shared-window sets."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
from complete_fixture import decode
from complete_forward import forward
from native_complete_check import comparisons
from guided_affine import forward_set
from leaf_numeric import V


def check(context_file,saved_file,baseline_file,trace_file,output):
    if output.exists():raise FileExistsError(output)
    c=decode(json.loads(context_file.read_text()));saved=json.loads(saved_file.read_text());baseline=json.loads(baseline_file.read_text());native={n:np.array(a,dtype='u2').view('f2')for n,a in saved['native_half_bits'].items()};point=comparisons(native,forward(c,point=True));m=forward(c,point=False);current=comparisons(native,m);details={}
    for name,gain in [('BG',m.generated.raw_bg),('FG',m.generated.raw_fg)]:
        d={};forward_set(gain.pixels,V.bounds(c.images[2],c.images[2]),V.bounds(c.epsilon,c.epsilon,'f'),c.images[2].shape[:2],diagnostics=d);details[name]=d
    witness=json.loads(trace_file.read_text())['rows'][0];x,y=witness['grid'];fg=details['FG']['stage_bounds'];cover=[]
    for stage in witness['stages']:
        n=stage['name'];a=np.array(stage['native_f32_bits'],dtype='u4').view('f4');lo=np.array(fg[n]['lo'])[y,x];hi=np.array(fg[n]['hi'])[y,x];cover.append({'stage':n,'components':4,'range_covered':bool(np.all(a>=lo)and np.all(a<=hi)),'max_width':float(np.max(hi-lo))})
    widths={n:{'before':b['max_width'],'after':current['observations'][n]['max_width']}for n,b in baseline['set']['observations'].items()if n in current['observations']};r={'scope':__doc__,'native_calls':0,'context_sha256':hashlib.sha256(context_file.read_bytes()).hexdigest(),'saved_native_sha256':hashlib.sha256(saved_file.read_bytes()).hexdigest(),'baseline_sha256':hashlib.sha256(baseline_file.read_bytes()).hexdigest(),'point':point,'set':current,'widths':widths,'window_diagnostics':details,'saved_52_f32_window_coverage':cover,'unchanged_context':{'cast0':int(c.params.view('u4')[0]),'tuning17':int(c.params.view('u4')[163]),'BG_FG':'neutral','lookup_all_zero':bool(np.all(c.images[9]==0)),'102_original_calls_were_one_context':True},'budgets_or_domain_relaxed':False,'backend_pow_changed':False,'full_pipeline_verified':False};root=Path(__file__).parent;r['source_sha256']={n:hashlib.sha256((root/n).read_bytes()).hexdigest()for n in ['guided_affine.py','guided_conditioned.py','leaf_numeric.py','pixel_bright.py','pixel_skin.py','pixel_haze.py','outer_cast.py','complete_forward.py','replay_shared_sets.py']};output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');print(json.dumps({'FG_a':widths['FG_a'],'FG_output':widths['FG_output'],'warm409':widths['warm409'],'unknown_pixels':len(current['pixel_unknowns']),'first_unknown':current['first_unknown'],'52_f32_coverage_violations':sum(not s['range_covered']for s in cover),'point_differences':{n:v for n,v in point['observations'].items()if v['half_bit_mismatches']}}));return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('context',type=Path);p.add_argument('saved',type=Path);p.add_argument('baseline',type=Path);p.add_argument('trace',type=Path);p.add_argument('output',type=Path);a=p.parse_args();check(a.context,a.saved,a.baseline,a.trace,a.output)
