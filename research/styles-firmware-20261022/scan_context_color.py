"""Target-free fresh model catalog for an explicitly frozen context."""
from dataclasses import asdict
from pathlib import Path
import argparse,json,time
import numpy as np
from context_color_api import identity,load
from baseline_archive import sha,encoded
from complete_fixture import decode
from complete_forward import forward
from active_color import Color,replace_color
from color_inverse import f32,signature,digest


def scan(context,precision,partition,start,count,output):
    if output.exists():raise FileExistsError(output)
    if not 0<=start<146 or not 1<=count<=16:raise ValueError('Bounded scan at most16 states')
    ident=identity(context,precision);contract=load(precision)
    if sha(partition)!=contract['partition_sha256']:raise ValueError('Reused exact partition required')
    p=load(partition);base=decode(load(context));begin=time.perf_counter();data={'scope':__doc__,'identity':asdict(ident),'partition_sha256':sha(partition),'start':start,'requested_count':count,'rows':[],'target_read':False,'native_calls':0}
    for s in p['states'][start:start+count]:
        t=time.perf_counter();c=Color(f32(s['representative_f32_bits']));result=forward(replace_color(base,c),point=True);row={'state_id':s['id'],'key':list(signature(c.raw)),'representative_f32_bits':s['representative_f32_bits'],'writer_known':result.writer is not None,'pixel_unknowns':result.pixel_unknowns,'internal_unknowns':result.internal_unknowns,'model_elapsed_seconds':time.perf_counter()-t}
        if result.writer is not None:
            a=result.writer.output.pixels.lo.astype('f2');row.update(writer_half_bits=a.view('u2').tolist(),writer_sha256=digest(a))
        data['rows'].append(row);data['elapsed_seconds']=time.perf_counter()-begin;output.write_bytes(encoded(data))
    print(json.dumps({'start':start,'evaluated':len(data['rows']),'unknown':sum(not r['writer_known']for r in data['rows']),'elapsed_seconds':data['elapsed_seconds']}));return data


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('context',type=Path);p.add_argument('precision',type=Path);p.add_argument('partition',type=Path);p.add_argument('start',type=int);p.add_argument('count',type=int);p.add_argument('output',type=Path);a=p.parse_args();scan(a.context,a.precision,a.partition,a.start,a.count,a.output)
