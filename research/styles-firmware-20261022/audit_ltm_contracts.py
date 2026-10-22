"""Read-only static LTM binding/format/epsilon/coordinate evidence, no firmware run."""
import argparse,hashlib,json,re,struct
from pathlib import Path
from air_alpha import canonicalize


def audit(air7,air10,header,epsilon):
    root=Path(__file__).parent;a=air7.read_text();b=air10.read_text();h=header.read_text();ep=json.loads(epsilon.read_text());raw=bytes.fromhex(ep['raw_le_hex'])
    if hashlib.sha256(raw).hexdigest()!=ep['source']['sha256']or struct.unpack('<f',raw)[0]!=ep['f32_value']:raise ValueError('Epsilon proof inconsistent')
    formats={n:int(re.search(r'\bMTLPixelFormat'+n+r'\s*=\s*(\d+)',h)[1])for n in ['RGBA16Float','R16Float']}
    if formats!={'RGBA16Float':115,'R16Float':25}:raise ValueError('SDK enum mismatch')
    sources={n:(root/'evidence/ltm-format-s14'/n).read_bytes()for n in ['ltm-small-alloc.asm.txt','ltm-full-alloc.asm.txt','guided-encode.asm.txt','renderer-texture-alloc.asm.txt','manifest.json']}
    for name in ['ltm-small-alloc.asm.txt','ltm-full-alloc.asm.txt']:
        if not re.search(r'mov\s+w2, #0x73',sources[name].decode()):raise ValueError('Expected actual allocator argument missing')
    for tag,s,pattern in [('producer',a,r'%19 = .*?%21 = [^\n]+'),('consumer',b,r'%291 = .*?%308 = [^\n]+')]:
        if not re.search(pattern,s,re.S):raise ValueError('Coordinate evidence missing')
    return {'reference':{'hardware':'iPhone17,3','OS_build':'24A446','CMImaging_UUID':'0A9BC064-A4BC-330E-861A-C70A637B14B3'},'module_canonical_sha256':{str(i):hashlib.sha256(canonicalize(s)[0].encode()).hexdigest()for i,s in [(7,a),(10,b)]},'gain_map_storage':{'small_BG_FG':115,'final_BG_FG':115,'name':'RGBA16Float','small_grid':'renderer self+0x30 width/height','final_grid':'renderer original input self+0x20 width/height','alpha_written_by_producer':1},'epsilon':ep,'guided_radius':1,'guide_source':'self+0x20 original input, distinct from producer selected self+0x28 if nonnull else self+0x20','producer_bindings':{'AIR1/Metal0':'selected primary','AIR3/Metal1':'linear texture self+0x30','AIR4/Metal2':'GTC self+0x268','AIR5/Metal10':'matte self+0x248','AIR6/Metal8':'smallBG','AIR7/Metal9':'smallFG'},'coordinates':{'producer':'f32(uint16 gid+.5)/f32(destination6 width,height), normalized clamp-edge linear sampler .3','GTC':'f32(half(channel*half(width-1)))+.5, pixel linear sampler, y=.5','consumer':'ROI5/6.scale*f32(logical uint16 gid+.5)+ROI5/6.offset, byte48/64, normalized sampler .3','output_origin':'ROI12 affects uint16 destination27 only; not added to source UV29','guided':'coefficients+means at guide grid, apply at final destination grid'},'SDK_header_sha256':hashlib.sha256(header.read_bytes()).hexdigest(),'SDK_enum_values':formats,'static_method_evidence_sha256':{n:hashlib.sha256(v).hexdigest()for n,v in sources.items()},'source_formats_remaining_explicit':['selected primary','linear source','original guide','person matte','GTC'],'supported_synthetic_storage':['R16Float','RGBA16Float'],'hardware_sampler_precision_verified':False,'GPU_executed':False,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('AIR7',type=Path);p.add_argument('AIR10',type=Path);p.add_argument('SDK_header',type=Path);p.add_argument('epsilon_proof',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    r=audit(a.AIR7,a.AIR10,a.SDK_header,a.epsilon_proof);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'format':115,'epsilon_f32':r['epsilon']['f32_value'],'radius':1}))
