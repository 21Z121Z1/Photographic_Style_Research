"""Bounded known-source color inversion returning equivalence candidates.

IEEE half-cell partition is exact within an explicit canonical nonnegative
f32 bit domain. Gain/protect compression uses the audited logical half/f32
interface, never writer monotonicity. Model matches are not GPU proofs.
"""
from dataclasses import dataclass
import hashlib
import numpy as np
from active_color import Color
from leaf_numeric import fc


def f32(bits):return np.array(bits,dtype='u4').view('f4')[()]
def u32(x):return int(np.float32(x).view('u4'))
def half(bits):return np.array(bits,dtype='u2').view('f2')[()]
def digest(array):return hashlib.sha256(np.asarray(array,dtype='f2').tobytes()).hexdigest()


@dataclass(frozen=True)
class Domain:
    first_bits: int=0
    last_bits: int=int(np.float32(.375).view('u4'))

    def __post_init__(self):
        if any(type(v)is not int for v in [self.first_bits,self.last_bits])or not 0<=self.first_bits<=self.last_bits<=u32(1):raise TypeError('Canonical +0/nonnegative finite f32 bit range within the prior[0,1] model contract required')

    @property
    def count(self):return self.last_bits-self.first_bits+1

    def record(self):return {'first_f32_bits':self.first_bits,'last_f32_bits':self.last_bits,'first_f32_hex':f'0x{self.first_bits:08x}','last_f32_hex':f'0x{self.last_bits:08x}','lower_real':float(f32(self.first_bits)),'upper_real':float(f32(self.last_bits)),'lower_closed':True,'upper_closed':True,'f32_population':self.count,'basis':'bounded research prefix [canonical+0,3/8] chosen before target matching within the existing [0,1] point-model contract; includes S21 platform and point3; not an Apple or UI range','negative_zero_searched':False}


def cell(bits,domain):
    if type(bits)is not int or not 0<=bits<=0x3c00:raise TypeError('Finite nonnegative half cell required')
    h=half(bits);even=bits%2==0;lo=0. if bits==0 else(float(half(bits-1))+float(h))/2;hi=(float(h)+float(half(bits+1)))/2;lc=True if bits==0 else even;hc=even
    first=u32(np.float32(lo))if lc else u32(np.nextafter(np.float32(lo),np.float32(np.inf)));last=u32(np.float32(hi))if hc else u32(np.nextafter(np.float32(hi),np.float32(-np.inf)))
    first=max(first,domain.first_bits);last=min(last,domain.last_bits)
    if first>last:return None
    if float(f32(domain.first_bits))>lo:lo=float(f32(domain.first_bits));lc=True
    if float(f32(domain.last_bits))<hi:hi=float(f32(domain.last_bits));hc=True
    center=u32(np.float32(h));representative=min(max(center,first),last)
    return {'half_bits':bits,'first_f32_bits':first,'last_f32_bits':last,'lower_real':lo,'upper_real':hi,'lower_closed':lc,'upper_closed':hc,'f32_population':last-first+1,'representative_f32_bits':representative}


def signature(raw):
    c=Color(raw);h=c.half;x=np.float32(h);positive=bool(h>0)
    if positive:protect=np.maximum(np.float32(x+np.float32(fc('BFE3333340000000'))),np.float32(fc('3FC99999A0000000')))
    else:protect=np.maximum(np.float32(np.float32(fc('3FB99999A0000000'))-np.float32(x*np.float32(fc('3FE3333340000000')))),np.float32(fc('3FC99999A0000000')))
    return (int(positive),int(c.gain.view('u2')),int(np.float16(protect).view('u2')))


def partition(domain):
    keys={};states=[];cells=[];last_half=int(np.float16(f32(domain.last_bits)).view('u2'))
    for bits in range(last_half+1):
        c=cell(bits,domain)
        if c is None:continue
        key=signature(f32(c['representative_f32_bits']))
        if key not in keys:
            index=len(states);keys[key]=index;states.append({'id':index,'branch':'RichSat'if key[0]else'smoothSat','key':list(key),'representative_f32_bits':c['representative_f32_bits'],'half_cells':0,'f32_population':0})
        index=keys[key];states[index]['half_cells']+=1;states[index]['f32_population']+=c['f32_population'];cells.append([bits,c['first_f32_bits'],c['last_f32_bits'],index])
    return cells,states


def verify_partition(domain,cells,states):
    if [s['id']for s in states]!=list(range(len(states)))or len({tuple(s['key'])for s in states})!=len(states):raise ValueError('State IDs or interface keys duplicate/unordered')
    if not cells or cells[0][1]!=domain.first_bits or cells[-1][2]!=domain.last_bits:raise ValueError('Domain endpoints omitted')
    if any(a[2]+1!=b[1]for a,b in zip(cells,cells[1:])):raise ValueError('Raw f32 gap or overlap')
    if sum(c[2]-c[1]+1 for c in cells)!=domain.count or len({c[0]for c in cells})!=len(cells):raise ValueError('Population/cell duplication')
    first=np.array([c[1]for c in cells],dtype='u4').view('f4');last=np.array([c[2]for c in cells],dtype='u4').view('f4');h=np.array([c[0]for c in cells],dtype='u2')
    if not(np.array_equal(first.astype('f2').view('u2'),h)and np.array_equal(last.astype('f2').view('u2'),h)):raise ValueError('Independent endpoint conversion fails')
    for i,c in enumerate(cells):
        if i and np.float16(f32(c[1]-1)).view('u2')==c[0]:raise ValueError('Cell lower preimage omits an f32')
        if i+1<len(cells)and np.float16(f32(c[2]+1)).view('u2')==c[0]:raise ValueError('Cell upper preimage omits an f32')
        key=list(signature(f32(cell(c[0],domain)['representative_f32_bits'])))
        if states[c[3]]['key']!=key:raise ValueError('Compressed state key mismatches a half cell')
    for state in states:
        members=[c for c in cells if c[3]==state['id']]
        if not members or len(members)!=state['half_cells']or sum(c[2]-c[1]+1 for c in members)!=state['f32_population']:raise ValueError('Compressed membership population differs')
    return {'half_cells':len(cells),'interface_states':len(states),'f32_population':domain.count,'raw_integer_cover_no_gaps_or_overlap':True,'endpoint_casts_and_adjacent_omission_checks':2*len(cells)+2*(len(cells)-1),'all_endpoint_checks_pass':True,'interior_argument':'IEEE RN-even f32->half is monotone; exact binary midpoint intervals plus exhaustive contiguous raw-bit partition cover every interior f32, without enumerating a billion values','writer_monotonicity_assumed':False,'equivalence_scope':'same branch/gain364/protect384 under the audited point half/f32 interface; not an original GPU proof'}


def interval(domain,first_cell,last_cell,ids):
    a=cell(first_cell[0],domain);b=cell(last_cell[0],domain);lo=first_cell[1];hi=last_cell[2]
    return {'lower_real':a['lower_real'],'upper_real':b['upper_real'],'lower_closed':a['lower_closed'],'upper_closed':b['upper_closed'],'first_f32_bits':lo,'last_f32_bits':hi,'first_f32_hex':f'0x{lo:08x}','last_f32_hex':f'0x{hi:08x}','f32_population':hi-lo+1,'signature_ids':sorted(ids),'membership':'all uint32 bit patterns first<=bits<=last interpreted as canonical nonnegative f32; inclusive integer endpoints'}


def runs(domain,cells,allowed):
    out=[];first=last=None;ids=set()
    for c in cells:
        if c[3]in allowed:
            if first is None:first=c
            elif last[2]+1!=c[1]:out.append(interval(domain,first,last,ids));first=c;ids=set()
            last=c;ids.add(c[3])
        elif first is not None:out.append(interval(domain,first,last,ids));first=last=None;ids=set()
    if first is not None:out.append(interval(domain,first,last,ids))
    return out


def solve_target(domain,cells,states,evaluations,target_half_bits):
    """Return ALL exact model matches in the finite catalog, including holes.

    This accepts arbitrary explicit target writer bits for the known context;
    it does not select a nearest parameter or read the old five S21 points.
    """
    if not isinstance(target_half_bits,np.ndarray)or target_half_bits.dtype!=np.dtype('u2')or target_half_bits.ndim!=3 or target_half_bits.shape[-1]!=4:raise TypeError('Explicit uint16 HxWxRGBA writer bit pattern required')
    if not np.isfinite(target_half_bits.view('f2')).all():raise ValueError('Finite half target required')
    proof=verify_partition(domain,cells,states);rows={};matching=set();unknown=[]
    for row in evaluations:
        i=row['state_id']
        if type(i)is not int or not 0<=i<len(states)or i in rows:raise ValueError('Duplicate or invalid interface state')
        if row['key']!=states[i]['key']or row['representative_f32_bits']!=states[i]['representative_f32_bits']:raise ValueError('Unbound representative or signature')
        rows[i]=row
        if not row['writer_known']:unknown.append(i);continue
        bits=np.array(row['writer_half_bits'],dtype='u2')
        if bits.shape!=target_half_bits.shape:raise ValueError('Target shape differs from frozen writer contract')
        if digest(bits.view('f2'))!=row['writer_sha256']:raise ValueError('Catalog writer digest mismatch')
        if np.array_equal(bits,target_half_bits):matching.add(i)
    missing=sorted(set(range(len(states)))-rows.keys())
    return {'scope':'bounded known-source model inverse; exact matches only, no nearest/unique estimate','domain':domain.record(),'coverage':dict(proof,evaluated_states=len(rows),missing_state_ids=missing,unknown_state_ids=sorted(unknown),complete_model_coverage=not missing and not unknown),'target_writer_sha256':digest(target_half_bits.view('f2')),'model_matching_state_ids':sorted(matching),'candidate_union':runs(domain,cells,matching),'candidate_interface_classes':[{'state_id':i,'key':states[i]['key'],'intervals':runs(domain,cells,{i}),'proved_equivalence':'same logical half/f32 branch/gain/protect interface within each class; exact IEEE raw half preimages','target_relation':'exact independent point-model writer match; original host/GPU requires separate evidence'}for i in sorted(matching)],'found_f32_population':sum(s['f32_population']for s in states if s['id']in matching),'not_searched':'outside the explicit domain,including negative zero; missing/unknown states are not excluded candidates','unique_parameter':False,'original_host_exhaustive':False,'original_GPU_or_unknown_source_inverse_verified':False}
