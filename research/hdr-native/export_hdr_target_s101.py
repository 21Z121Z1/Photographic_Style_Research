"""Runner-only FLOAT EXR copy of the unchanged S44/S47 HDR target."""
from pathlib import Path
import hashlib,json
import numpy as np
import OpenEXR,Imath
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def export_target(cw,case,export):
    h,w=case['shape'][:2];source=cw/'case/HDR.f32';assert source.stat().st_size==h*w*3*4;before=sha(source);a=np.memmap(source,mode='r',dtype='<f4',shape=(h,w,3));path=export/'independent-HDR-target.exr';assert not path.exists()
    meaning=json.loads((export/'carrier-meaning.json').read_text());meta={'photo':case['photo'],'representation':'Relative display-linear P3 RGB, independent S44/S47 intent; not scene-linear truth or a nit calibration','HDR_intent':meaning['display_intent'],'source_f32_SHA256':before,'stored_canvas':[h,w,3],'orientation':'Raw stored canvas, same as all master/operator EXRs; original HEIC irot applies only when displaying the carrier','no_new_pixel_calculation':True}
    ptype=Imath.PixelType(Imath.PixelType.FLOAT);header=OpenEXR.Header(w,h);header['channels']={c:Imath.Channel(ptype)for c in 'RGB'};header['chromaticities']=Imath.Chromaticities(Imath.V2f(.68,.32),Imath.V2f(.265,.69),Imath.V2f(.15,.06),Imath.V2f(.3127,.3290));header['comments']=json.dumps(meta,sort_keys=True).encode();out=OpenEXR.OutputFile(str(path),header);nf=0
    for top in range(0,h,32):
        b=a[top:top+32];nf+=int((~np.isfinite(b)).sum());out.writePixels({c:np.ascontiguousarray(b[...,i],dtype='<f4').tobytes()for i,c in enumerate('RGB')},len(b))
    out.close();read=OpenEXR.InputFile(str(path));different=0
    for i,c in enumerate('RGB'):
        for top in range(0,h,32):
            stop=min(top+32,h);decoded=np.frombuffer(read.channel(c,ptype,top,stop-1),dtype='<f4').reshape(stop-top,w);different+=int(np.count_nonzero(decoded.view('u4')!=np.ascontiguousarray(a[top:stop,:,i],dtype='<f4').view('u4')))
    read.close();assert different==0 and nf==0 and sha(source)==before
    record={'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path),'shape':[h,w,3],'dtype':'<f4','RGB_storage_readback_different_components':different,'nonfinite_components':nf,'source_f32_SHA256':before,'source_f32_unchanged':True,'metadata':meta}
    with(export/'target-EXR-readback.json').open('x')as f:json.dump(record,f,indent=2);f.write('\n')
    return record
