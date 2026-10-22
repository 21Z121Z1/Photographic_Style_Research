"""Static link shared model constants to the already acquired exact AIR10."""
import argparse,hashlib,json,re
from pathlib import Path
from native_semantic_tone_check import fragment
from leaf_host import short
from air_alpha import canonicalize
from color_matrices import *


def check(source,output):
    if output.exists():raise FileExistsError(output)
    text=source.read_text();fragment(text);body=next(m[0]for m in re.finditer(r'^define[^\n]*@([^ (]+)\([^\n]+\{\n.*?^}',text,re.M|re.S)if short(m[1])=='selectiveColorFilter');expected={14:TO_LMS_COLUMNS[0],16:TO_LMS_COLUMNS[1],19:TO_LMS_COLUMNS[2],23:(POWER_HEX,),26:TO_LAB_COLUMNS[0],28:TO_LAB_COLUMNS[1],31:TO_LAB_COLUMNS[2],182:FROM_LAB_A,185:FROM_LAB_B,189:(INVERSE_POWER_HEX,),192:FROM_ROOT_COLUMNS[0],194:FROM_ROOT_COLUMNS[1],197:FROM_ROOT_COLUMNS[2]};rows=[]
    for ssa,values in expected.items():
        line=next(line for line in body.splitlines()if line.startswith(f'  %{ssa} ='));actual=tuple(re.findall(r'0x([0-9A-F]{16})',line));rows.append({'SSA':ssa,'constant_count':len(actual),'matches_shared_constants':actual==values,'original_instruction_sha256':hashlib.sha256(line.encode()).hexdigest()})
    r={'scope':__doc__,'hardware':'iPhone17,3','build':'24A446','canonical_module_sha256':hashlib.sha256(canonicalize(text)[0].encode()).hexdigest(),'function_sha256':hashlib.sha256(body.encode()).hexdigest(),'source_line':text.count('\n',0,text.index(body))+1,'model_constants_sha256':hashlib.sha256((Path(__file__).parent/'color_matrices.py').read_bytes()).hexdigest(),'rows':rows,'all_match':all(x['matches_shared_constants']for x in rows),'native_calls':0,'original_GPU_verified':False};output.write_text(json.dumps(r,indent=2)+'\n')
    if not r['all_match']:raise AssertionError('Shared constants differ from exact reference AIR; receipt retained')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.output);print(r['all_match'])
