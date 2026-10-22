"""Twelve adjacent-f32 boundary probes only; accepted 409-case batch not rerun."""
import argparse,ctypes,hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from air_alpha import canonicalize
from native_positive_tone_check import SHIMS
from native_positive_blocks_check import buffers
from positive_tone import PositiveToneStats,PositiveToneContext
from tone_interface import RendererControls,ResolvedSceneType,SuppliedToneStats,ToneFrameContext,evaluate
from negative_tone import ToneStats,h


def check(private_air: Path,output: Path):
    if output.exists():raise FileExistsError(output)
    if hashlib.sha256(canonicalize(private_air.read_text())[0].encode()).hexdigest()!='5ca4d2dce19c7e8825f0608b04d3637ddf05f3eb507f33430670617624c02c53':raise ValueError('Exact source required')
    tones=[]
    for label,t in [('FG_pow',.5**(4/3)),('BG_pow',h('3FDBDB8CE0000000')**(1/h('3FF3333340000000'))),('FG_t04',h('3FD99999A0000000')),('FG_t05',.5)]:
        t=np.float32(t)
        tones.extend((label,float(x))for x in [np.nextafter(t,np.float32(0)),t,np.nextafter(t,np.float32(1))])
    tun=tuple([0.]*66);frame=ToneFrameContext(SuppliedToneStats(ToneStats(.4,.5,.08,.06,.003,.05,.02,.008,.5),.4,.05),tun)
    context=PositiveToneContext(PositiveToneStats(.4,.003,.05),tun);rows=[]
    with tempfile.TemporaryDirectory(prefix='psr-boundaries-')as t:
        w=Path(t);(w/'shim.c').write_text(SHIMS);libpath=w/'boundary.dylib'
        subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib','-x','ir',str(private_air),'-x','c',str(w/'shim.c'),'-fno-fast-math','-o',str(libpath)],check=True,capture_output=True,timeout=60)
        lib=ctypes.CDLL(str(libpath));fn=lib.RenderingParamsFromStats;fn.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_uint16,ctypes.c_uint16]
        powfn=getattr(lib,'air.fast_pow.f32');powfn.argtypes=[ctypes.c_float,ctypes.c_float];powfn.restype=ctypes.c_float
        for label,tone in tones:
            p,s=buffers(tone,context);model=evaluate(RendererControls(.5,tone,0),ResolvedSceneType(0),frame)
            for group in (0,1):fn(p.ctypes.data,s.ctypes.data,group,0)
            post_r=powfn(tone,.75);post_q=powfn(tone,h('3FF3333340000000'));actual=p[488//4:648//4]
            indexes=[9,19,21,23,24,32];covered=bool(np.all(actual[indexes]>=model.output_lower[indexes])and np.all(actual[indexes]<=model.output_upper[indexes]))
            rows.append({'label':label,'tone_f32':tone,'post_pow_r_f32':post_r,'post_pow_q_f32':post_q,
                         'actual_r_olt_half':post_r<.5,'actual_q_ugt_threshold':post_q>h('3FDBDB8CE0000000'),
                         'actual_FG_mids':float(actual[19]),'center_FG_mids':float(model.values[19]),
                         'FG_mids_interval':[float(model.output_lower[19]),float(model.output_upper[19])],
                         'branch_determined':model.branch_determined,'range_covered':covered,
                         'decisions':[b.__dict__ for b in model.branch_decisions]})
    r={'scope':__doc__,'hardware_reference':'iPhone17,3','build':'24A446','records':len(rows),'kernel_calls':len(rows)*2,
       'range_violations':sum(not x['range_covered']for x in rows),'set_coverage_is_not_numerical_agreement':True,
       'source_comparisons':{'FG_pow':'SSA342 fcmp fast olt float %341, .5; equality selects upper/right branch',
                             'BG_pow':'SSA219 fcmp fast ugt float %195, f32 threshold; finite equality selects lower/left branch'},
       'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'iOS_GPU_execution':False,'accepted_409_batch_repeated':False,'rows':rows}
    output.write_text(json.dumps(r,indent=2)+'\n')
    if r['range_violations']:raise AssertionError('Boundary range coverage failure; receipt retained')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('private_air',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.private_air,a.output);print(json.dumps({k:r[k]for k in ['records','range_violations']}))
