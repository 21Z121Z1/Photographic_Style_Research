"""Seven new writer tiles, including clipping, zero extent and ushort wrapping."""
import argparse,ctypes,hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from leaf_numeric import V
from texture_numeric import Texture,PixelFormat
from output_writer import Controls,forward
from output_writer_host import build,C_SOURCE
from native_guided_check import texture,values


def fixtures():
    colors=np.array([[[-.25,.5,2],[.2,.4,.8],[1.5,-.1,.3]],[[.7,.3,.2],[.05,1.1,.4],[.8,.6,.4]]],dtype='f2')
    cases=[('direct',Controls((1,1),(2,1),(8,6),False)),('imageblock',Controls((1,1),(2,1),(8,6),True)),('edge-clipped',Controls((1,1),(2,1),(5,3),True)),('zero-extent',Controls((1,1),(2,1),(3,2),True)),('unsigned-edge-underflow',Controls((1,1),(2,1),(2,1),True)),('direct-destination-wrap',Controls((65535,65535),(2,2),(8,6),False)),('imageblock-destination-wrap',Controls((65535,65535),(2,2),(8,6),True))]
    for name,c in cases:yield name,c,colors,np.full((6,8,4),-.75,dtype='f2')


def execute(lib,controls,colors,frame,*,leader_first=False):
    fn=lib.psr_write;fn.argtypes=[ctypes.c_void_p]*4+[ctypes.c_uint8];fn.restype=None;begin=lib.psr_writer_begin;begin.argtypes=[ctypes.c_uint32];begin.restype=None
    target=texture(frame);roi=np.zeros(88,dtype='u2');roi[4:6]=controls.render_edge2;roi[80:82]=controls.output_offset12;h,w=colors.shape[:2];begin(h*w if controls.imageblock else 0);nonleaders=[(x,y)for y in range(h)for x in range(w)if x or y];order=[(0,0),*nonleaders]if leader_first else[*nonleaders,(0,0)];inputhash=hashlib.sha256()
    for x,y in order:
        rgb=colors[y,x].astype('f4');grid=tuple((v+d)&65535 for v,d in zip(controls.logical_origin,(x,y)));coords=np.array([*grid,x,y,w,h],dtype='u2');fn(rgb.ctypes.data,target.ctypes.data,roi.ctypes.data,coords.ctypes.data,int(controls.imageblock));inputhash.update(rgb.tobytes()+coords.tobytes())
    inputhash.update(roi.tobytes()+frame.tobytes())
    return values(target,frame.shape),{n:ctypes.c_uint32.in_dll(lib,'psr_writer_'+n).value for n in ['errors','pixels','copies']},inputhash.hexdigest(),h*w


def check(source,output):
    if output.exists():raise FileExistsError(output)
    ir,meta=build(source.read_text());rows=[];inputhash=hashlib.sha256();outputhash=hashlib.sha256();calls=0
    with tempfile.TemporaryDirectory(prefix='psr-writer-')as t:
        w=Path(t);(w/'source.ll').write_text(ir);(w/'shim.c').write_text(C_SOURCE);c=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',str(w/'source.ll'),str(w/'shim.c'),'-o',str(w/'writer.dylib')],capture_output=True,text=True,timeout=60)
        if c.returncode:raise RuntimeError(c.stderr[:4000])
        lib=ctypes.CDLL(str(w/'writer.dylib'));fn=lib.psr_write;fn.argtypes=[ctypes.c_void_p]*4+[ctypes.c_uint8];fn.restype=None;begin=lib.psr_writer_begin;begin.argtypes=[ctypes.c_uint32];begin.restype=None
        for name,controls,colors,frame in fixtures():
            target=texture(frame);roi=np.zeros(88,dtype='u2');roi[4:6]=controls.render_edge2;roi[80:82]=controls.output_offset12;h,w=colors.shape[:2];begin(h*w if controls.imageblock else 0);order=[(x,y)for y in range(h)for x in range(w)if x or y]+[(0,0)]
            for x,y in order:
                rgb=colors[y,x].astype('f4');grid=tuple((v+d)&65535 for v,d in zip(controls.logical_origin,(x,y)));coords=np.array([*grid,x,y,w,h],dtype='u2');fn(rgb.ctypes.data,target.ctypes.data,roi.ctypes.data,coords.ctypes.data,int(controls.imageblock));inputhash.update(rgb.tobytes()+coords.tobytes());calls+=1
            errors=ctypes.c_uint32.in_dll(lib,'psr_writer_errors').value
            if errors:raise AssertionError('Invalid CPU writer/barrier/OOB schedule')
            native=values(target,frame.shape);outputhash.update(native.tobytes());inputhash.update(roi.tobytes()+frame.tobytes());point=forward(Texture(V.value(frame),PixelFormat.RGBA16Float,'output storage'),V.value(colors),controls);bounds=forward(Texture(V.bounds(frame,frame),PixelFormat.RGBA16Float,'output storage'),V.bounds(colors,colors),controls);pixel_count=ctypes.c_uint32.in_dll(lib,'psr_writer_pixels').value;copies=ctypes.c_uint32.in_dll(lib,'psr_writer_copies').value
            row={'case':name,'logical_origin':controls.logical_origin,'output_offset12':controls.output_offset12,'render_edge2':controls.render_edge2,'imageblock':controls.imageblock,'tile_shape':colors.shape,'native_output_half_bits':native.view('u2').tolist(),'half_bit_mismatches':int(np.count_nonzero(native.view('u2')!=point.output.pixels.lo.astype('f2').view('u2'))),'range_covered':bool(np.all(native>=bounds.output.pixels.lo)and np.all(native<=bounds.output.pixels.hi)),'native_written_pixels':pixel_count,'expected_written_pixels':int(point.written_pixels.sum()),'native_copy_calls':copies,'phased_scheduler_errors':errors,'destination27':point.leader_destination27,'copy_extent614':point.copy_extent614}
            if pixel_count!=point.written_pixels.sum():raise AssertionError('Write address/extent mask mismatch')
            rows.append(row)
    root=Path(__file__).parent;r={'scope':__doc__,'hardware':'iPhone17,3','build':'24A446','original':meta,'metrics':{'tiles':len(rows),'original_writer_calls':calls,'half_components':sum(len(x['native_output_half_bits'])*len(x['native_output_half_bits'][0])*4 for x in rows),'half_bit_mismatches':sum(x['half_bit_mismatches']for x in rows),'known_set_violations':sum(not x['range_covered']for x in rows),'phased_scheduler_errors':sum(x['phased_scheduler_errors']for x in rows)},'input_tile_colors':next(fixtures())[2].tolist(),'target_initial_value':-.75,'source_sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest()for n in ['output_writer.py','output_writer_host.py','native_output_writer_check.py']},'host_IR_sha256':hashlib.sha256(ir.encode()).hexdigest(),'C_sha256':hashlib.sha256(C_SOURCE.encode()).hexdigest(),'input_sha256':inputhash.hexdigest(),'output_sha256':outputhash.hexdigest(),'rows':rows,'GPU_or_multithreaded_imageblock_executed':False,'old_accepted_batches_repeated':False,'input_RGB600_supplied':True}
    output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    if r['metrics']['half_bit_mismatches']or r['metrics']['known_set_violations']:raise AssertionError('Writer comparison failure; receipt retained')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.output);print(json.dumps(r['metrics']))
