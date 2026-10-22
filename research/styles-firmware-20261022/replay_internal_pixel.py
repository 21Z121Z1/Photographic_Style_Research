"""Pure model replay of saved S16B first-divergence probes, no new native calls."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
from complete_fixture import decode
from diagnose_internal_pixel import model_probes


def check(context,saved,traces,output):
    if output.exists():raise FileExistsError(output)
    c=decode(json.loads(context.read_text()));native={n:np.array(a,dtype='u2').view('f2')for n,a in json.loads(saved.read_text())['native_half_bits'].items()};rows=[]
    for path in traces:
        receipt=json.loads(path.read_text());models,expected=model_probes(c,native,tuple(receipt['grid']));stages={}
        for name,row in receipt['rows'].items():
            data=[]
            for before in row['stages']:
                v=models[name][1][before['SSA']];dtype='f2'if v.precision=='h'else'f4';integer='u2'if v.precision=='h'else'u4';actual=np.array(before['native_bits'],dtype=integer);bits=v.lo.reshape(-1).astype(dtype).view(integer);data.append({'SSA':before['SSA'],'bit_mismatches_before':before['bit_mismatches'],'bit_mismatches_after':int(np.count_nonzero(actual!=bits)),'max_absolute_error_after':float(np.max(abs(actual.view(dtype).astype('f8')-v.lo.reshape(-1))))})
            stages[name]={'checks':data,'first_remaining_divergence':next((x for x in data if x['bit_mismatches_after']),None)}
        rows.append({'trace_file':path.name,'trace_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'grid':receipt['grid'],'probes':stages})
    r={'scope':__doc__,'native_calls':0,'rows':rows,'output_transfer_does_not_inherit_bright_encode_fma':True,'remaining_errors_are_not_accepted_as_bit_exact':True};output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');print(json.dumps([{k:v for k,v in row.items()if k!='probes'}|{'first_remaining':{n:p['first_remaining_divergence']for n,p in row['probes'].items()}}for row in rows]));return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('context',type=Path);p.add_argument('saved',type=Path);p.add_argument('output',type=Path);p.add_argument('traces',nargs='+',type=Path);a=p.parse_args();check(a.context,a.saved,a.traces,a.output)
