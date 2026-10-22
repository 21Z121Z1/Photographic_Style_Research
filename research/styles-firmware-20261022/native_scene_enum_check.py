"""Complete original 36B scene enum leaf, including unchanged ADRP/table loads."""
import argparse,hashlib,json,re,struct,subprocess,tempfile
from pathlib import Path
import numpy as np
from renderer_enums import resolve_scene_type


def check(output: Path):
    if output.exists():raise FileExistsError(output)
    root=Path(__file__).resolve().parent;e=root/'evidence/enum-24A446';m=json.loads((e/'manifest.json').read_text());method=next(x for x in m['methods']if x['file']=='scene-enum.asm.txt')
    words=[int(w,16)for w in re.findall(r'^[0-9a-f]+: ([0-9a-f]{8})\s',(e/method['file']).read_text(),re.M)];raw=b''.join(struct.pack('<I',w)for w in words)
    if len(raw)!=36 or hashlib.sha256(raw).hexdigest()!=method['instructions_sha256']:raise ValueError('Complete original enum leaf required')
    mapping=json.loads((root/'evidence/enum-mapping.json').read_text());table=[mapping['scene']['mapping'][str(i)]for i in (1,2,3)]
    asm='.text\n.p2align 12\n_psr_page:\n.space 0xce4\n.globl _psr_scene_enum\n_psr_scene_enum:\n'+''.join(f'.long 0x{w:08x}\n'for w in words)+'.space 0x1f0ce0-(.-_psr_page)\n'+''.join(f'.long {x}\n'for x in table)
    c='#include <stdint.h>\n#include <stdio.h>\nextern uint32_t psr_scene_enum(uint32_t);\nint main(void){uint32_t in,out;while(fread(&in,4,1,stdin)==1){out=psr_scene_enum(in);if(fwrite(&out,4,1,stdout)!=1)return 2;}return feof(stdin)?0:3;}\n'
    rng=np.random.default_rng(0x3ce4);values=np.r_[np.arange(24,dtype='u4'),np.array([0x7fffffff,0x80000000,0xfffffffe,0xffffffff],dtype='u4'),rng.integers(0,2**32,size=16,dtype='u4')].astype('<u4')
    expected=np.array([resolve_scene_type(int(x)).code for x in values],dtype='<u4')
    with tempfile.TemporaryDirectory(prefix='psr-scene-enum-')as t:
        w=Path(t);(w/'leaf.S').write_text(asm);(w/'main.c').write_text(c)
        subprocess.run(['xcrun','clang','-arch','arm64',str(w/'main.c'),str(w/'leaf.S'),'-o',str(w/'check')],check=True,capture_output=True,timeout=60)
        out=subprocess.run([str(w/'check')],input=values.tobytes(),capture_output=True,check=True,timeout=30).stdout;actual=np.frombuffer(out,dtype='<u4');bad=int(np.count_nonzero(actual!=expected))
    r={'scope':__doc__,'original_sha256':method['instructions_sha256'],'instruction_words_patched':0,'original_ADRP_relative_layout_preserved':True,'table_sha256':mapping['scene']['table_sha256'],'cases':len(values),'mismatches':bad,
       'input_sha256':hashlib.sha256(values.tobytes()).hexdigest(),'output_sha256':hashlib.sha256(out).hexdigest(),'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'iOS_library_loaded':False,'tuning_ObjC_or_error_path_executed':False}
    output.write_text(json.dumps(r,indent=2)+'\n')
    if bad:raise AssertionError('Scene enum mismatch; receipt retained')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);r=check(p.parse_args().output);print(json.dumps({'cases':r['cases'],'mismatches':r['mismatches']}))
