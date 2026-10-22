"""One saved failure witness: field19 wrapper must fail internal tonal equality.

No accepted batch reruns. Final conditional mix equality deliberately remains
insufficient: both variants must expose and compare the independent tonal468.
"""
import argparse,ctypes,hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from outer_cast_host import build,MATH_C


def check(source,witness,output):
    if output.exists():raise FileExistsError(output)
    w=json.loads(witness.read_text());data=np.array(w['input'],dtype='f4');ir,metadata=build(source.read_text());needle='getelementptr %struct.SSRParams,ptr %params,i64 0,i32 17'
    if ir.count(needle)!=1:raise AssertionError('Exactly one correct wrapper tuning location required')
    bad=ir.replace(needle,needle[:-2]+'19',1);outputs={}
    with tempfile.TemporaryDirectory(prefix='psr-tuning-regression-')as t:
        p=Path(t);(p/'math.c').write_text(MATH_C)
        for name,text in [('field17',ir),('field19',bad)]:
            (p/(name+'.ll')).write_text(text);libfile=p/(name+'.dylib')
            c=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',str(p/(name+'.ll')),str(p/'math.c'),'-o',str(libfile)],capture_output=True,text=True,timeout=60)
            if c.returncode:raise RuntimeError(c.stderr[:4000])
            lib=ctypes.CDLL(str(libfile));fn=lib.psr_outer;fn.argtypes=[ctypes.c_void_p]*2;out=np.zeros(3,dtype='f4');fn(data.ctypes.data,out.ctypes.data);tonal=np.ctypeslib.as_array((ctypes.c_float*3).in_dll(lib,'psr_outer_tonal')).copy();outputs[name]={'tonal468':tonal.tolist(),'final492':out.tolist(),'ir_sha256':hashlib.sha256(text.encode()).hexdigest()}
    correct=outputs['field17']['tonal468']==w['correct_tonal468'];failed=outputs['field19']['tonal468']==w['failed_tonal468'];distinct=outputs['field17']['tonal468']!=outputs['field19']['tonal468'];hidden=outputs['field17']['final492']==outputs['field19']['final492']
    r={'witness_sha256':hashlib.sha256(witness.read_bytes()).hexdigest(),'one_saved_witness_only':True,'old_batches_repeated':False,'correct_wrapper_matches_saved_tonal':correct,'bad_wrapper_matches_saved_failure':failed,'internal_observation_rejects_bad_wrapper':distinct,'final_mix_alone_hides_failure':hidden,'outputs':outputs,'source_sha256':{n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest()for n in ['regress_tuning_layout.py','outer_cast_host.py','leaf_host.py']},'GPU_executed':False}
    output.write_text(json.dumps(r,indent=2)+'\n')
    if not(correct and failed and distinct and hidden):raise AssertionError('Saved tuning failure regression changed; receipt retained')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('witness',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.witness,a.output);print(json.dumps({k:v for k,v in r.items()if k not in ['outputs','source_sha256']}))
