"""Verify legacy skin AIR correspondence with typed constant normalization."""
import argparse,hashlib,json,re,struct
from pathlib import Path
import numpy as np
from native_semantic_tone_check import fragment


def skin_body(source):return re.search(r'^define[^\n]*@_Z21renderSkinAdjustments[^\n]+\{\n.*?^}',source,re.M|re.S)[0]


def normalize(body):
    lines=[]
    for line in body.splitlines():
        line=re.sub(r'!\d+','!M',re.sub(r'#\d+','#A',line))
        precision='f4'if'float'in line else'f2'
        def number(m):
            token=m[0]
            if token.startswith('0xH'):return 'FP'+token[3:].lower()
            if token.startswith('f0x'):return 'FP'+token[3:].lower()
            value=struct.unpack('>d',bytes.fromhex(token[2:]))[0]if token.startswith('0x')else float(token)
            value=np.asarray(value,dtype=precision)
            return 'FP'+format(int(value.view('u4'if precision=='f4'else'u2')),'08x'if precision=='f4'else'04x')
        line=re.sub(r'0xH[0-9A-Fa-f]{4}|f0x[0-9A-Fa-f]{8}|0x[0-9A-Fa-f]{16}|[-+]?\d+\.\d+[eE][-+]?\d+',number,line)
        lines.append(line)
    return '\n'.join(lines)


def contract(legacy,current):
    a=legacy.read_text();b=current.read_text();assert hashlib.sha256(legacy.read_bytes()).hexdigest()=='9ce57aea2bcc11021cf04ce4b44f57ac83270b0722283c7860436c3ec4d523c1';fragment(b)
    x=skin_body(a);y=skin_body(b);nx=normalize(x);ny=normalize(y)
    bg=re.search(r'^define[^\n]*@_Z19renderBGAdjustments[^\n]+\{\n.*?^}',b,re.M|re.S)[0]
    local=re.search(r'^  %90 = .*?^  %142 = [^\n]+',bg,re.M|re.S)[0];skin=re.search(r'^  %20 = .*?^  %72 = [^\n]+',y,re.M|re.S)[0]
    def rename(text,is_bg):
        aliases={'83':'rgb','89':'amount','1':'guide'}if is_bg else{'0':'rgb','19':'amount','3':'guide'}
        text=re.sub(r'%(\d+)',lambda m:'%'+aliases.get(m[1],'v'+str(int(m[1])-(70 if is_bg else 0))),text)
        lines=text.splitlines();lines[-1]=re.sub(r', <3 x half> (?:zeroinitializer|splat \(half 0xH3C00\))\)',', <3 x half> FINAL_PROTECTION_WEIGHT)',lines[-1]);return '\n'.join(lines)
    return {'legacy_AIR_sha256':hashlib.sha256(legacy.read_bytes()).hexdigest(),'legacy_function_sha256':hashlib.sha256(x.encode()).hexdigest(),'current_function_sha256':hashlib.sha256(y.encode()).hexdigest(),'typed_constant_and_attribute_number_normalization_equal':nx==ny,'normalized_sha256':hashlib.sha256(nx.encode()).hexdigest(),'brightness_BG_local_equal_except_final_protection_mix':rename(local,True)==rename(skin,False),'BG_final_mix':0,'skin_final_mix':1,'legacy_continuous_model_sha256':hashlib.sha256((Path(__file__).parent.parent/'semantic-styles/semantic_skin_model.py').read_bytes()).hexdigest(),'continuous_model_replaced':False,'native_half_or_GPU_equivalence_claimed':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('legacy',type=Path);p.add_argument('current',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    r=contract(a.legacy,a.current);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
