"""Summarize unique producer/guided contexts without counting ROI repeats."""
import argparse,hashlib,json
from pathlib import Path


def summarize(path):
    r=json.loads(path.read_text());unique={row['fixture']:row for row in r['rows']};groups={}
    for label,predicate in [('producer',lambda k:k in ['source24','postSRL34','linear37','reference96','working121','BG203','FG205']),('raw_RGBA_writes',lambda k:k.startswith('raw_')),('guided',lambda k:k.startswith(('BG_','FG_')))]:
        values=[v for row in unique.values()for k,v in row['point'].items()if predicate(k)]
        groups[label]={'unique_fixtures':len(unique),'components':sum(v['components']for v in values),'half_bit_mismatches':sum(v['half_bit_mismatches']for v in values),'max_absolute_error':max(v['max_absolute_error']for v in values)}
    groups['consumer']={'calls':len(r['rows']),'half_bit_mismatches':sum(row['point']['consumer335']['half_bit_mismatches']for row in r['rows']),'components':sum(row['point']['consumer335']['components']for row in r['rows'])}
    return {'native_receipt_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'unique_context_metrics':groups,'known_set_violations':r['metrics']['known_set_violations'],'largest_conditional_box_width':max(v['max_width']for row in r['rows']for k,v in row['set'].items()if k!='unknowns'),'new_native_calls':0,'set_coverage_does_not_imply_numerical_agreement':True,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('receipt',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    r=summarize(a.receipt);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
