"""S16 sorted/half-lattice proofs admitted into the default S19 contrast path.

Only the seven saved families, exact half parameter, and the exact saved
parent box are admitted. Parent composition recomputes all64 input boxes;
saved output values are never used. No global numeric-method patching here.
"""
from dataclasses import dataclass
from functools import lru_cache
import hashlib,itertools,json
from pathlib import Path
import numpy as np
from leaf_numeric import V,DomainUnknown
from contrast_span_joint import CELL0_AMOUNT,GATE
from contrast_order_domains import ordered_box,lattice_span_lower

ROOT_LO=(0.,-.014420070058153133,0.)
ROOT_HI=(.9401097123345006,1.000976622104645,.679305245082874)
SOURCE_SHA='31b167989bddf8a93d67a42ed66f7b8daf655810bcc156ee24bb8e263705a59c'


@lru_cache(maxsize=1)
def saved_cells():
    p=Path(__file__).parent/'evidence/bg-dependency-s15c.json';raw=p.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:raise DomainUnknown('Exact saved contrast input cover required')
    d=json.loads(raw)
    if d['amount_half']!=CELL0_AMOUNT or tuple(d['contrast_input_lo'])!=ROOT_LO or tuple(d['contrast_input_hi'])!=ROOT_HI:raise DomainUnknown('Saved cover admission mismatch')
    rows=sorted(d['partition']['known_subsets']+d['partition']['unknown_subsets'],key=lambda r:r['cell'])
    if [r['cell']for r in rows]!=list(range(64)):raise DomainUnknown('Saved64 complete input cover required')
    axes=[sorted({r[k][a]for r in rows for k in ['input_lo','input_hi']})for a in range(3)]
    if any(len(v)!=5 or v[0]!=ROOT_LO[a]or v[-1]!=ROOT_HI[a]for a,v in enumerate(axes)):raise DomainUnknown('Saved input grid endpoints do not cover parent')
    expected={(tuple(axes[a][i[a]]for a in range(3)),tuple(axes[a][i[a]+1]for a in range(3)))for i in itertools.product(range(4),repeat=3)}
    if {(tuple(r['input_lo']),tuple(r['input_hi']))for r in rows}!=expected:raise DomainUnknown('Saved64 input cover has a gap or overlap mismatch')
    # Only input coordinates, cell identities and original failure families.
    return tuple((r['cell'],tuple(r['input_lo']),tuple(r['input_hi']))for r in rows),frozenset(r['cell']for r in d['partition']['unknown_subsets']if r['cell']!=0)


def typed(rgb,amount):
    return isinstance(rgb,V)and not rgb.point and rgb.precision=='h'and np.shape(rgb.lo)==(3,)and isinstance(amount,V)and not amount.point and amount.precision=='h'and np.shape(amount.lo)==()and float(amount.lo)==CELL0_AMOUNT and float(amount.hi)==CELL0_AMOUNT


def family_id(rgb,amount):
    if not typed(rgb,amount):return None
    rows,ids=saved_cells()
    return next((i for i,lo,hi in rows if i in ids and np.all(rgb.lo>=lo)and np.all(rgb.hi<=hi)),None)


def whole_supported(rgb,amount):return typed(rgb,amount)and np.array_equal(rgb.lo,ROOT_LO)and np.array_equal(rgb.hi,ROOT_HI)


def union(values):
    if not values:raise DomainUnknown('Empty contrast cover cannot produce a bound')
    return V(np.min([v.lo for v in values],axis=0),np.max([v.hi for v in values],axis=0),'h',False)


@dataclass(frozen=True)
class Result:
    output: V
    family: int
    branches: tuple


def enclose_family(rgb,amount):
    family=family_id(rgb,amount)
    if family is None:raise DomainUnknown('Seven-family sorted contrast admission not met')
    from pixel_leaves import _contrast_body
    rows=[];values=[];floor=np.float16(GATE)
    if float(floor)>GATE:floor=np.nextafter(floor,np.float16(-np.inf))
    for order in itertools.permutations(range(3)):
        box=ordered_box(rgb,order)
        if box is None:rows.append({'order':order,'branch':'empty order'});continue
        span=box[order[-1]]-box[order[0]];lower=lattice_span_lower(box)
        for active,lo,hi in [(True,max(float(span.lo),lower),float(span.hi)),(False,max(0.,float(span.lo)),min(float(span.hi),float(floor)))]:
            if lo>hi:rows.append({'order':order,'branch':'positive'if active else'else','status':'empty'});continue
            admitted=V(np.asarray(lo),np.asarray(hi),'h',False)
            v=_contrast_body(box,amount,input_minimum=box[order[0]],input_span=admitted,positive_branch=active);values.append(v);rows.append({'order':order,'branch':'positive'if active else'else','status':'known','half_span_lower':lo,'half_span_upper':hi,'max_width':float(np.max(v.hi-v.lo))})
    return Result(union(values),family,tuple(rows))


def enclose_cover(rgb,amount):
    if not whole_supported(rgb,amount):raise DomainUnknown('Exact saved parent contrast box required')
    from pixel_leaves import contrast
    values=[]
    for i,lo,hi in saved_cells()[0]:values.append(contrast(V(np.array(lo),np.array(hi),'h',False),amount))
    return union(values)
