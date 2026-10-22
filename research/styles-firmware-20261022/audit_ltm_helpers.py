"""Targeted AIR7/AIR10 helper equality, excluding attribute group IDs only."""
import argparse,hashlib,json,re
from pathlib import Path


def audit(a,b):
    texts=[a.read_text(),b.read_text()];rows=[]
    for key in ['applySemanticSRL','linearFromCurved']:
        raw=[next(m[0]for m in re.finditer(r'^define[^\n]*@[^\n]*'+key+r'[^\n]*\{\n.*?^}',s,re.M|re.S))for s in texts]
        normalized=[re.sub(r' #\d+','',s)for s in raw]
        rows.append({'helper':key,'AIR7_text_sha256':hashlib.sha256(raw[0].encode()).hexdigest(),'AIR10_text_sha256':hashlib.sha256(raw[1].encode()).hexdigest(),'only_attribute_group_number_removed':True,'normalized_text_equal':normalized[0]==normalized[1]})
    return {'scope':__doc__,'rows':rows,'new_native_calls':0,'caller_sampler_or_GPU_equivalence_inferred':False,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('AIR7',type=Path);p.add_argument('AIR10',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    r=audit(a.AIR7,a.AIR10);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['rows']))
