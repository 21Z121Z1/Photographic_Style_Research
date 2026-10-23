"""Artificial observation tolerance over existing writer tables, NOT codec/GPU.

Only written RGB gets one finite-half rank step. Alpha and unwritten storage
are bit-exact. Existing model arithmetic/exact acceptance is never modified.
"""
from pathlib import Path
from dataclasses import asdict
import hashlib,json
import numpy as np
from baseline_archive import sha,encoded
from context_color_api import Target,strict_bits,load
from joint_color_api import Observation,_binding,compatible,SharedField3,V3
from raw_f32_sets import Interval,normalize,intersect_all,difference,population,records,same_members
from color_inverse import Domain,runs


def ranks(bits):
    b=np.asarray(bits)
    if b.dtype!=np.dtype('u2')or not np.isfinite(b.view('f2')).all():raise TypeError('Finite raw binary16 encodings required')
    u=b.astype('i4');return np.where((u&0x8000)!=0,0xffff-u,0x8000+u)


def from_ranks(keys):
    k=np.asarray(keys)
    if k.dtype.kind not in 'iu'or np.any(k<0x400)or np.any(k>0xfbff):raise ValueError('Finite binary16 ranks required; no clipping')
    b=np.where(k>=0x8000,k-0x8000,0xffff-k).astype('u2')
    if not np.isfinite(b.view('f2')).all():raise ValueError('Nonfinite rank result')
    return b


def digest_bits(bits):return hashlib.sha256(np.asarray(bits,dtype='u2').tobytes()).hexdigest()
def bitmap(ids):
    a=np.zeros(146,dtype='u1');a[list(ids)]=1;return np.packbits(a,bitorder='little').tobytes().hex()


def geometry(context_file):
    d=load(context_file);source=np.array(d['images_half_bits'][0],dtype='u2');initial=np.array(d['output_initial_half_bits'],dtype='u2');roi=np.array(d['raw_f32_bits']['roi'],dtype='u4').view('u2');x,y=map(int,roi[80:82]);h,w=source.shape[:2]
    if initial.shape!=(5,6,4)or (h,w)!=(3,4)or (x,y)!=(1,1):raise ValueError('Existing non-imageblock3x4-to5x6/offset1,1 contract only')
    written=np.zeros(initial.shape[:2],dtype=bool);written[y:y+h,x:x+w]=True;rgb=np.zeros(initial.shape,dtype=bool);rgb[...,:3]=written[...,None];return {'context_sha256':sha(context_file),'output_shape':list(initial.shape),'active_source_shape':[h,w],'logical_origin':[0,0],'output_offset':[x,y],'imageblock':False,'written_pixels':written.tolist(),'tolerated_RGB_components':rgb.tolist(),'RGB_component_count':int(rgb.sum()),'exact_component_count':int((~rgb).sum()),'mask_basis':'original non-imageblock writer: source-grid dimensions and raw ROI ushort offsets80/81; no new writer forward'}


class Catalog:
    def __init__(self,handle,error_contract_file):
        self.handle=handle;self.error_contract_file=Path(error_contract_file);self.error=load(error_contract_file);self.error_sha256=sha(error_contract_file)
        if self.error['schema']!='psr-artificial-written-RGB-half-step1-v1'or self.error['RGB_half_rank_budget']!=1 or not self.error['alpha_bit_exact']or not self.error['unwritten_bit_exact']:raise ValueError('Frozen artificial one-step measurement contract required')
        ident,_,_,_=handle.checked();dummy=Target(ident,handle.expected_catalog_sha256,np.array(load(handle.context_file)['output_initial_half_bits'],dtype='u2'));self.identity,self.contract,self.provenance=_binding(Observation('catalog',handle,dummy));ident,m,self.plan,self.rows=handle.checked()
        if ident.precision_contract_sha256!=V3 or self.error['precision_contract_sha256']!=V3:raise ValueError('Accepted v3 precision only')
        own=geometry(handle.context_file)
        if self.error['contexts'][ident.complete_context_sha256]!=own:raise ValueError('Frozen context/mask does not match raw writer geometry')
        self.mask=np.array(own['tolerated_RGB_components'],dtype=bool);self.written=np.array(own['written_pixels'],dtype=bool);self.shape=tuple(own['output_shape']);self.ids=sorted(i for i,r in self.rows.items()if r['writer_known']);self.unknown=sorted(set(range(146))-set(self.ids));self.arrays=np.array([strict_bits(self.rows[i]['writer_half_bits'])for i in self.ids],dtype='u2').reshape((len(self.ids),*self.shape));self.prediction_ranks=ranks(self.arrays);self.initial=np.array(load(handle.context_file)['output_initial_half_bits'],dtype='u2')
        if self.ids:
            if np.any(self.arrays[:,self.mask].view('f2')<=0):raise ValueError('Predeclared positive finite written-RGB dataset restriction failed; do not shrink mask')
            if np.any(self.arrays[:,~self.written,:]!=self.initial[~self.written,:]):raise ValueError('Catalog unwritten storage contract differs')
            if np.any(self.arrays[:,self.written,3]!=np.float16(1).view('u2')):raise ValueError('Catalog written alpha contract differs')
        for a in [self.mask,self.written,self.arrays,self.prediction_ranks,self.initial]:a.setflags(write=False)

    def candidate_set(self,ids):return tuple(Interval.read(d)for d in runs(Domain(),self.plan['cells'],set(ids)))

    def scan(self,target:Target,*,diagnostics=False):
        if not isinstance(target,Target)or target.identity!=self.identity or target.catalog_sha256!=self.handle.expected_catalog_sha256:raise ValueError('Observation belongs to another context/precision/catalog')
        observed=target.writer_half_bits
        if observed.shape!=self.shape:raise ValueError('All writer observation components required')
        distance=np.abs(self.prediction_ranks-ranks(observed)[None,...]);exact=np.all(self.arrays==observed,axis=(1,2,3));outside_counts=np.count_nonzero(self.arrays[:,~self.mask]!=observed[~self.mask],axis=1);rgb_max=distance[:,self.mask].max(axis=1)if self.ids else np.array([],dtype='i4');allowed=(outside_counts==0)&(rgb_max<=1)
        exact_ids=[i for i,ok in zip(self.ids,exact)if ok];tolerance_ids=[i for i,ok in zip(self.ids,allowed)if ok];u=self.candidate_set(self.unknown);a=self.candidate_set(exact_ids);b=self.candidate_set(tolerance_ids)
        result={'identity':asdict(self.identity),'catalog_sha256':self.handle.expected_catalog_sha256,'catalog_provenance':self.provenance,'observation_error_contract_sha256':self.error_sha256,'observed_writer_sha256':digest_bits(observed),'domain':Domain().record(),'exact':{'known_state_ids':exact_ids,'known_candidates':records(a),'known_population':population(a),'possible_candidates':records(normalize((*a,*u))),'possible_population':population(normalize((*a,*u)))},'tolerance':{'known_state_ids':tolerance_ids,'known_candidates':records(b),'known_population':population(b),'possible_candidates':records(normalize((*b,*u))),'possible_population':population(normalize((*b,*u)))},'unknown_state_ids':self.unknown,'unknown_possible_candidates':records(u),'all_states_considered':146,'known_states_checked':len(self.ids),'components_checked_per_known_state':int(np.prod(self.shape)),'RGB_tolerated_components':int(self.mask.sum()),'exact_components':int((~self.mask).sum()),'exact_match_bitmap':bitmap(exact_ids),'tolerance_match_bitmap':bitmap(tolerance_ids),'unknown_bitmap':bitmap(self.unknown),'evidence_grade':'model_only; artificial observation tolerance, not JPEG/HEIC/GPU error','nearest_fallback':False,'new_forward_or_kernel_calls':0}
        if diagnostics:result['per_known_state']=[{'state_id':i,'exact_match':bool(e),'tolerance_match':bool(t),'max_written_RGB_half_steps':int(d),'exact_zone_differing_components':int(n)}for i,e,t,d,n in zip(self.ids,exact,allowed,rgb_max,outside_counts)]
        return result


def perturb(bits,mask,pattern):
    original=strict_bits(bits);result=original.copy();k=ranks(result);coordinates=np.argwhere(mask);y,x,c=map(int,coordinates[0]);changed=[]
    if pattern=='identity':pass
    elif pattern in('first_rgb_plus1','first_rgb_minus1','first_rgb_plus2'):
        delta={'first_rgb_plus1':1,'first_rgb_minus1':-1,'first_rgb_plus2':2}[pattern];k[y,x,c]+=delta;changed=[([y,x,c],delta)]
    elif pattern=='checker_rgb_pm1':
        for a,b,c in coordinates:
            delta=1 if (int(a)+int(b)+int(c))%2==0 else-1;k[a,b,c]+=delta;changed.append(([int(a),int(b),int(c)],delta))
    elif pattern=='first_alpha_plus1':k[y,x,3]+=1;changed=[([y,x,3],1)]
    elif pattern=='first_unwritten_rgb_plus1':
        written=np.any(mask,axis=2);a,b=map(int,np.argwhere(~written)[0]);k[a,b,0]+=1;changed=[([a,b,0],1)]
    else:raise ValueError('Only frozen coordinate-based perturbation patterns')
    result=from_ranks(k);changed_count=int(np.count_nonzero(result!=original));distance=np.abs(ranks(result)-ranks(original));admissible=bool(np.array_equal(result[~mask],original[~mask])and np.all(distance[mask]<=1));return result,{'pattern':pattern,'changed_components':changed_count,'max_half_rank_steps':int(distance.max()),'changes':changed,'within_artificial_contract':admissible}


def joint(scans,mode,*,shared_parameter:SharedField3):
    if not isinstance(shared_parameter,SharedField3)or mode not in('exact','tolerance')or len(scans)<2:raise ValueError('Explicit shared field3 declaration and exact/tolerance scans required')
    if len({s['identity']['complete_context_sha256']for s in scans})<2:raise ValueError('Two supported known contexts required')
    if len({s['identity']['precision_contract_sha256']for s in scans})!=1 or len({s['observation_error_contract_sha256']for s in scans})!=1:raise ValueError('Mixed precision or observation contracts')
    known=[tuple(Interval.read(d)for d in s[mode]['known_candidates'])for s in scans];possible=[tuple(Interval.read(d)for d in s[mode]['possible_candidates'])for s in scans];a=intersect_all(known);b=intersect_all(possible);u=difference(b,a);ids=set(scans[0][mode]['known_state_ids'])
    for s in scans[1:]:ids.intersection_update(s[mode]['known_state_ids'])
    return {'mode':mode,'shared_parameter_declaration':asdict(shared_parameter),'known_state_ids':sorted(ids),'known_candidates':records(a),'known_population':population(a),'possible_candidates':records(b),'possible_population':population(b),'unresolved_possible_candidates':records(u),'unresolved_population':population(u),'equal_to_single_indices':[i for i,p in enumerate(possible)if same_members(b,p)],'additional_elimination_beyond_smallest_single':min(population(p)for p in possible)-population(b),'missing_unknown_not_excluded':True,'single_target_invalidity_claim':False,'evidence_grade':'model_only; caller-declared shared raw, artificial observation tolerance','new_forward_or_kernel_calls':0}
