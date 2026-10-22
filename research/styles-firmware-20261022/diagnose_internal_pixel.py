"""One saved pixel: independent bright, tonal and haze internal checkpoints."""
import argparse,ctypes,hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from leaf_numeric import V
from complete_fixture import decode
from numeric_trace_host import build
from main_full_host import C_SOURCE,OBSERVATIONS
from native_guided_check import texture
from pixel_bright import forward as bright,BrightStats
from outer_cast import tonal
from pixel_haze import forward as haze,Parameters as Haze


def model_probes(c,native,grid):
    x,y=grid;H=lambda a:V.value(a);F=lambda a:V.value(a,'f');value=lambda n:H(native[n][y,x].reshape(-1)[0]if native[n][y,x].size==1 else native[n][y,x]);stat=lambda g,k:F(c.stats[2560+g*9+k]);models={};expected={}
    b={};expected['bright']=bright(value('skin393'),value('working286'),value('person96'),value('skin95'),F(c.params[7]).h(),BrightStats(stat(2,4),stat(3,4),stat(5,0),stat(6,6),stat(6,4)),observations=b);models['bright']=('renderBrightAndContrast',b)
    t={};expected['tonal']=tonal(value('selective413'),value('person96'),F(c.params[2]),F(c.params[108]),2,observations=t);models['tonal']=('psrMainFull',t)
    h={};expected['haze']=haze(value('mixed492'),value('guide211'),value('person96'),Haze(F(c.params[114:122]),False),observations=h);models['haze']=('renderVideoHazeCorrection',h)
    return models,expected


def check(source,context_file,saved_file,output,grid=(0,0),probe_layout=None,probe_names=None):
    if output.exists():raise FileExistsError(output)
    if hashlib.sha256(context_file.read_bytes()).hexdigest()!=json.loads(saved_file.read_text())['context_sha256']:raise ValueError('Saved native outputs do not match this frozen context')
    c=decode(json.loads(context_file.read_text()));saved=json.loads(saved_file.read_text());native={n:np.array(a,dtype='u2').view('f2')for n,a in saved['native_half_bits'].items()};x,y=grid;H=lambda a:V.value(a);F=lambda a:V.value(a,'f');value=lambda n:H(native[n][y,x].reshape(-1)[0]if native[n][y,x].size==1 else native[n][y,x]);stat=lambda g,k:F(c.stats[2560+g*9+k]);models={};expected={}
    models,expected=model_probes(c,native,grid)
    if probe_names is not None:models={name:models[name]for name in probe_names}
    if probe_layout is not None:
        for name,row in probe_layout.items():models[name]=(models[name][0],{int(ssa):models[name][1][int(ssa)]for ssa,ty,count,offset in row['layout']})
    ir,meta=build(source.read_text(),models)
    with tempfile.TemporaryDirectory(prefix='psr-internal-pixel-')as d:
        w=Path(d);(w/'trace.ll').write_text(ir);(w/'shim.c').write_text(C_SOURCE);p=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',str(w/'trace.ll'),str(w/'shim.c'),'-o',str(w/'trace.dylib')],capture_output=True,text=True,timeout=60)
        if p.returncode:raise RuntimeError(p.stderr[:3000])
        lib=ctypes.CDLL(str(w/'trace.dylib'));fn=lib.psr_main_full;fn.argtypes=[ctypes.c_void_p]*7+[ctypes.c_int32]+[ctypes.c_uint16]*2+[ctypes.c_void_p];fn.restype=None
        images=[c.images[0],c.images[1],np.array(c.gtc.red_samples,dtype='f2')[None,:,None],np.array(c.whites.red_samples,dtype='f2')[None,:,None],None,native['BG_output'],native['FG_output'],*[c.images[i]for i in [4,5,6,7,8,9]]];arrays=[None if a is None else texture(a)for a in images];ptrs=(ctypes.c_void_p*13)(*[None if a is None else a.ctypes.data for a in arrays]);target=texture(c.output_initial);out=np.zeros(meta['original']['observation_float_count'],dtype='f4');params=c.params.copy();fn(ptrs,target.ctypes.data,c.management.ctypes.data,params.ctypes.data,c.stats.ctypes.data,c.roi.ctypes.data,c.srl.ctypes.data,c.version,x,y,out.ctypes.data);observed={};offset=0
        for n,ssa,count in OBSERVATIONS:observed[n]=out[offset:offset+count];offset+=count
        stability={n:int(np.count_nonzero(observed[n].astype('f2').view('u2')!=native[n][y,x].reshape(-1).view('u2')))for n in ['bright400','tonal468','haze493','output600']};rows={}
        for name,(label,values)in models.items():
            m=meta['probes'][name];actual=np.ctypeslib.as_array((ctypes.c_float*m['count']).in_dll(lib,'psr_trace_'+name)).copy();stages=[]
            for ssa,ty,count,offset in m['layout']:
                a=actual[offset:offset+count];b=values[ssa].lo.reshape(-1);dtype='f2'if ty=='half'else'f4';integer='u2'if ty=='half'else'u4';stages.append({'SSA':ssa,'precision':ty,'native_bits':a.astype(dtype).view(integer).tolist(),'model_bits':b.astype(dtype).view(integer).tolist(),'bit_mismatches':int(np.count_nonzero(a.astype(dtype).view(integer)!=b.astype(dtype).view(integer))),'max_absolute_error':float(np.max(abs(a-b)))})
            stages.sort(key=lambda r:r['SSA']);rows[name]={'stages':stages,'first_divergence':next((s for s in stages if s['bit_mismatches']),None)}
    r={'scope':__doc__,'grid':[x,y],'context_sha256':hashlib.sha256(context_file.read_bytes()).hexdigest(),'saved_native_sha256':hashlib.sha256(saved_file.read_bytes()).hexdigest(),'original':meta,'native_main_calls':1,'host_IR_sha256':hashlib.sha256(ir.encode()).hexdigest(),'observer_stability_half_bit_mismatches':stability,'rows':rows,'intermediate_inputs_for_diagnostic_only':'saved original guided outputs; not counted as another complete forward chain','GPU_executed':False,'old_batches_repeated':False};output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');print(json.dumps({n:r['first_divergence']for n,r in rows.items()}));print('observer stability',stability);return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('context',type=Path);p.add_argument('saved',type=Path);p.add_argument('output',type=Path);p.add_argument('--grid',nargs=2,type=int,default=[0,0]);a=p.parse_args();check(a.source,a.context,a.saved,a.output,tuple(a.grid))
