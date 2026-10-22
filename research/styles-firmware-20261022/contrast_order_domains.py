"""Only the eight saved S15C failures: channel identity and half-lattice facts.

Ordered polytopes are conservatively enclosed by tightened boxes. No new
uniform split, shifted gate or changed quotient/product evaluation is used.
A gray else branch remains separate; any failed positive branch stays unknown.
"""
import argparse,itertools,json,hashlib,math
from contextlib import contextmanager
from pathlib import Path
import numpy as np
from leaf_numeric import V,DomainUnknown,fc
from leaf_correlations import channel_span
from leaf_domains import strictly_positive_branch
import pixel_leaves

THRESHOLD=fc('3EE4F8B580000000')


def ordered_box(box,order):
    lo=box.lo.copy();hi=box.hi.copy()
    for _ in range(3):
        for a,b in zip(order,order[1:]):lo[b]=max(lo[b],lo[a]);hi[a]=min(hi[a],hi[b])
    if np.any(lo>hi):return None
    return V(lo,hi,'h',False)


def lattice_span_lower(b):
    """All original RGB components are half after shadows, not arbitrary reals.

    Any difference of two finite half values with abs>=m is an integer multiple
    of the smallest half step in that region. A rounded positive half span
    has an exact nominal difference >=that step. Apply the unchanged2u+tiny
    subtraction allowance before intersecting the original strict gate.
    """
    # First fact: a region excluding zero has one minimum half quantum.
    if np.any((b.lo<=0)&(b.hi>=0)):step=2**-24
    else:
        magnitudes=np.minimum(abs(b.lo),abs(b.hi));m=float(np.min(magnitudes));mhalf=np.float16(m)
        if float(mhalf)>m:mhalf=np.nextafter(mhalf,np.float16(-np.inf))
        step=2**-24 if mhalf<=0 else float(mhalf)-float(np.nextafter(mhalf,np.float16(-np.inf)))
    # D=0 cannot satisfy the original positive branch: its2u+tiny result
    # is <=tiny, strictly below the unchanged threshold.
    # Second fact couples span to the known max lower bound M. For binary
    # boundary P<M: either D=max-min >=M-P, or min>P and every channel lies
    # on the half quantum above P. Thus nonzero D >=min(M-P,quantum(P)).
    # This is a logical cover, not a shifted shader gate or a uniform split.
    maximum_lower=float(np.max(b.lo))
    if maximum_lower>0:
        boundary=2.**math.floor(math.log2(maximum_lower))
        if boundary==maximum_lower:boundary*=.5
        if boundary<2**-24:quantum=2**-24
        else:
            value=np.float16(boundary);quantum=float(np.nextafter(value,np.float16(np.inf)))-float(value)
        step=max(step,min(maximum_lower-boundary,quantum))
    step=step*(1-2**-10)-2**-24
    rounded=np.float16(step)
    if float(rounded)>step:rounded=np.nextafter(rounded,np.float16(-np.inf))
    return max(float(rounded),float(strictly_positive_branch(V(np.array(0.),np.array(1.),'h',False),THRESHOLD).lo))


def positive(box,amount,order,*,active=True):
    lower=lattice_span_lower(box);oldspan=pixel_leaves.channel_span;oldmin=V.min_channels;olddiv=V.__truediv__;failure={}
    def minimum(v):return v[order[0]]if v is box else oldmin(v)
    def span(v):
        if v is not box:return channel_span(v)
        out=box[order[-1]]-box[order[0]]
        if active:out=V(np.maximum(out.lo,lower),out.hi,'h',False)
        else:
            threshold=np.float16(THRESHOLD)
            if float(threshold)>THRESHOLD:threshold=np.nextafter(threshold,np.float16(-np.inf))
            out=V(np.maximum(out.lo,0),np.minimum(out.hi,float(threshold)),'h',False)
        return out
    def divide(a,b):
        try:return olddiv(a,b)
        except DomainUnknown as e:
            if not failure and 'budget'in str(e):
                b=a.box(b);failure.update(expression='newspan / original-half-span',numerator_lo=np.asarray(a.lo).tolist(),numerator_hi=np.asarray(a.hi).tolist(),denominator_lo=np.asarray(b.lo).tolist(),denominator_hi=np.asarray(b.hi).tolist(),joint_endpoint_reachability='not established; independent cover only')
            raise
    pixel_leaves.channel_span=span;V.min_channels=minimum;V.__truediv__=divide
    try:
        v=pixel_leaves.contrast(box,amount);return {'status':'known','max_width':float(np.max(v.hi-v.lo)),'active_span_lower':lower}
    except DomainUnknown as e:return {'status':'unknown','reason':str(e),'active_span_lower':lower,'failure':failure}
    finally:pixel_leaves.channel_span=oldspan;V.min_channels=oldmin;V.__truediv__=olddiv


def check(saved,output):
    if output.exists():raise FileExistsError(output)
    data=json.loads(saved.read_text());rows=[]
    for cell in data['partition']['unknown_subsets']:
        b=V(np.array(cell['input_lo']),np.array(cell['input_hi']),'h',False);orders=[]
        for order in itertools.permutations(range(3)):
            v=ordered_box(b,order)
            if v is None:orders.append({'order':order,'status':'empty_order'});continue
            row={'order':order,'input_lo':v.lo.tolist(),'input_hi':v.hi.tolist(),**positive(v,V.value(data['amount_half'],point=False),order)}
            row['else_branch']=positive(v,V.value(data['amount_half'],point=False),order,active=False);orders.append(row)
        rows.append({'original_cell':cell['cell'],'orders':orders,'unknown':any(x['status']=='unknown'or x.get('else_branch',{}).get('status')=='unknown'for x in orders)})
    r={'scope':__doc__,'saved_sha256':hashlib.sha256(saved.read_bytes()).hexdigest(),'native_calls':0,'original_cells':8,'ordered_positive_domains':sum(x['status']!='empty_order'for row in rows for x in row['orders']),'known_positive_domains':sum(x['status']=='known'for row in rows for x in row['orders']),'unknown_positive_domains':sum(x['status']=='unknown'for row in rows for x in row['orders']),'remaining_unknown_original_cells':sum(row['unknown']for row in rows),'rows':rows,'quotient_order_changed':False,'threshold_changed':False,'rounding_budgets_changed':False,'mask_changed':False,'gray_else_retained':True,'remaining_failure':'Max-lower-bound/span coupling excludes false tiny spans even when an ordered box includes zero. Only the remaining low-magnitude cell still permits positive spans close to the strict threshold; Without the joint relation between changed span and original span, independent changed-span bounds can still exceed the quotient finite budget. Ordered boxes are outer covers of polytopes, not proof that every independent corner is reachable.'};output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');print(json.dumps({k:v for k,v in r.items()if k!='rows'}));return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('saved',type=Path);p.add_argument('output',type=Path);a=p.parse_args();check(a.saved,a.output)
