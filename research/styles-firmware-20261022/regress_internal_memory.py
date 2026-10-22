"""Three saved probe layouts only: review diagnostic callsite memory summaries."""
import argparse,hashlib,json,tempfile
from pathlib import Path
from diagnose_internal_pixel import check


def regress(source,context,saved,receipts,output):
    if output.exists():raise FileExistsError(output)
    rows=[]
    with tempfile.TemporaryDirectory(prefix='psr-memory-replay-')as d:
        for i,path in enumerate(receipts):
            old=json.loads(path.read_text());new=check(source,context,saved,Path(d)/f'{i}.json',tuple(old['grid']),old['original']['probes']);mismatches=[]
            for name,row in old['rows'].items():
                actual={r['SSA']:r for r in new['rows'][name]['stages']}
                for s in row['stages']:
                    if actual[s['SSA']]['native_bits']!=s['native_bits']:mismatches.append([name,s['SSA']])
            rows.append({'original_receipt':path.name,'original_receipt_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'replayed_original':new['original'],'replayed_host_IR_sha256':new['host_IR_sha256'],'grid':old['grid'],'probe_bit_differences_after_memory_review':mismatches,'saved_final_observer_stability':new['observer_stability_half_bit_mismatches'],'original_calls':new['native_main_calls']})
    r={'scope':__doc__,'native_main_calls':sum(r['original_calls']for r in rows),'new_contexts':0,'old_complete_chain_or_leaf_batches_repeated':False,'rows':rows,'FP_arithmetic_predicates_or_inputs_changed':False};output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    if any(row['probe_bit_differences_after_memory_review']or any(row['saved_final_observer_stability'].values())for row in rows):raise AssertionError('Memory review replay changed original observations; receipt retained')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('context',type=Path);p.add_argument('saved',type=Path);p.add_argument('output',type=Path);p.add_argument('receipts',nargs='+',type=Path);a=p.parse_args();regress(a.source,a.context,a.saved,a.receipts,a.output)
