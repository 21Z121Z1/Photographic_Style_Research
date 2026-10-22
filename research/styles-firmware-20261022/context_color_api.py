"""Version/context/precision/catalog-bound finite color inverse API.

Only canonical +0..3/8 is supported. Targets contain no true control. Missing
or unknown states remain possible candidates, never implicit exclusions.
"""
from dataclasses import dataclass,asdict
from pathlib import Path
import json
import numpy as np
from baseline_archive import sha,encoded
from complete_fixture import decode
from color_inverse import Domain,digest,runs

ROOT=Path(__file__).parent
EXPECTED_VERSION=('iPhone17,3','24A446','SmartStyleV1','CMISmartStyleProcessorV1',0)
load=lambda p:json.loads(Path(p).read_text())


def create_precision(output:Path,*,host_code3=False):
    if output.exists():raise FileExistsError(output)
    prior=load(ROOT/'evidence/prepared-baseline-s24a.json');v=load(ROOT/'evidence/verification-s24.json')
    if sha(ROOT/'evidence/prepared-baseline-s24a.json')!=v['evidence_sha256']['prepared-baseline-s24a.json']:raise ValueError('Saved S24 contract identity required')
    sources=dict(prior['catalog_reuse']['source_hashes'])
    profile={'name':'original pre-S25 point contract','source_patches':[]}
    if host_code3:
        from output_code3 import runtime_contract
        sources['pixel_output.py']=sha(ROOT/'pixel_output.py');sources['output_code3.py']=sha(ROOT/'output_code3.py');profile={'name':'S25 final code3 host f32 powf then separate half mul/add profile','source_patches':['pixel_output.py','output_code3.py'],'runtime':runtime_contract(),'prior_precision_sha256':sha(ROOT/'evidence/model-precision-s25b.json'),'rejected_fused_profile_sha256':sha(ROOT/'evidence/model-precision-v2-s25c4.json'),'diagnostic_sha256':sha(ROOT/'evidence/output-diagnostic-s25c3.json'),'old_precision_not_relabelled':True}
    if any(sha(ROOT/n)!=h for n,h in sources.items()):raise ValueError('Forward sources changed')
    plan=ROOT/'evidence/color-partition-s22a.json'
    expected=load(ROOT/'evidence/verification-s22.json')['evidence_sha256'][plan.name]
    if sha(plan)!=expected:raise ValueError('Original exact partition evidence changed')
    d={'schema':'psr-known-context-color-v1','version':list(EXPECTED_VERSION),'free_parameter':'post-scene SSRParams.color field3 byte12 raw f32','domain':Domain().record(),'point_precision':'existing explicit half/f32 instruction order, host FMA and shim assumptions; not set or GPU acceptance','profile':profile,'model_source_sha256':sources,'inverse_API_sha256':sha(Path(__file__)),'source_AIR_sha256':prior['AIR_sha256'],'field3_contract':prior['new_field3_contract'],'partition_sha256':expected,'partition_proof_reused_without_reenumeration':True,'GPU_UI_unknown_source_inverse':False}
    output.write_bytes(encoded(d));return d


@dataclass(frozen=True)
class Identity:
    hardware:str
    build:str
    bundle:str
    processor_class:str
    main_version_argument:int
    complete_context_sha256:str
    precision_contract_sha256:str


def identity(context_file:Path,precision_file:Path)->Identity:
    c=load(context_file);p=load(precision_file);i=c['identity'];version=(i['hardware'],i['build'],i['bundle'],i['class'],c['version'])
    if version!=EXPECTED_VERSION or tuple(p['version'])!=EXPECTED_VERSION:raise ValueError('Matched build/internal class/version required')
    decode(c)
    if c['raw_f32_bits']['params'][3]!=0:raise ValueError('Frozen family context must contain canonical +0 in the free field3 slot')
    if p['schema']!='psr-known-context-color-v1' or p['domain']['first_f32_bits']!=0 or p['domain']['last_f32_bits']!=0x3ec00000:raise ValueError('Fixed canonical +0..3/8 precision/domain required')
    if p['inverse_API_sha256']!=sha(Path(__file__))or any(sha(ROOT/n)!=h for n,h in p['model_source_sha256'].items()):raise ValueError('Model/API precision source identity changed')
    if p.get('profile',{}).get('runtime'):
        from output_code3 import runtime_contract
        if p['profile']['runtime']!=runtime_contract():raise ValueError('Host math profile differs from bound precision contract')
    return Identity(*version,sha(context_file),sha(precision_file))


def strict_bits(values)->np.ndarray:
    raw=np.asarray(values)
    if raw.dtype.kind not in 'ui'or raw.ndim!=3 or raw.shape[-1]!=4 or np.any(raw<0)or np.any(raw>65535):raise TypeError('Raw uint16 HxWxRGBA integers required')
    a=raw.astype('u2')
    if not np.isfinite(a.view('f2')).all():raise ValueError('Finite half writer required')
    return a


@dataclass(frozen=True)
class Target:
    identity:Identity
    catalog_sha256:str
    writer_half_bits:np.ndarray

    def __post_init__(self):
        if not isinstance(self.identity,Identity)or type(self.catalog_sha256)is not str or len(self.catalog_sha256)!=64:raise TypeError('Explicit bound target identity/catalog digest required')
        if not isinstance(self.writer_half_bits,np.ndarray)or self.writer_half_bits.dtype!=np.dtype('u2'):raise TypeError('Typed uint16 target required')
        a=strict_bits(self.writer_half_bits).copy();a.setflags(write=False);object.__setattr__(self,'writer_half_bits',a)

    def record(self):return {'identity':asdict(self.identity),'catalog_sha256':self.catalog_sha256,'writer_half_bits':self.writer_half_bits.tolist(),'true_control_provided_to_solver':False}


def read_rows(chunks,expected_identity,plan_sha):
    seen={}
    for path in chunks:
        data=load(path)
        if data['identity']!=asdict(expected_identity)or data['partition_sha256']!=plan_sha:raise ValueError('Wrong context/build/precision chunk')
        for row in data['rows']:
            i=row['state_id']
            if type(i)is not int or not 0<=i<146 or i in seen:raise ValueError('Duplicate or invalid state')
            seen[i]=row
    return seen


def seal_catalog(context_file,precision_file,partition_file,chunks,output):
    if output.exists():raise FileExistsError(output)
    ident=identity(context_file,precision_file);precision=load(precision_file)
    if sha(partition_file)!=precision['partition_sha256']:raise ValueError('Exact reused half partition required')
    rows=read_rows(chunks,ident,sha(partition_file));p=load(partition_file)
    for i,row in rows.items():validate_row(row,p['states'][i])
    missing=sorted(set(range(146))-rows.keys());unknown=sorted(i for i,r in rows.items()if not r['writer_known'])
    data={'schema':'psr-context-catalog-v1','identity':asdict(ident),'partition_sha256':sha(partition_file),'chunks':[{'name':f.name,'sha256':sha(f)}for f in chunks],'evaluated_states':len(rows),'missing_state_ids':missing,'unknown_state_ids':unknown,'complete_model_coverage':not missing and not unknown,'new_forward_evaluations':len(rows),'target_used_for_forward_scan':False,'original_host_exhaustive':False,'scope':'complete model catalog for this exact known context only; original host is finite witness layer'}
    output.write_bytes(encoded(data));return data


def validate_row(row,state):
    if row['key']!=state['key']or row['representative_f32_bits']!=state['representative_f32_bits']:raise ValueError('Interface representative/key changed')
    if type(row['writer_known'])is not bool:raise TypeError('Explicit known/unknown writer required')
    if row['writer_known']:
        a=strict_bits(row['writer_half_bits'])
        if digest(a.view('f2'))!=row['writer_sha256']:raise ValueError('Writer digest differs')


@dataclass(frozen=True)
class BoundCatalog:
    context_file:Path
    precision_file:Path
    partition_file:Path
    catalog_file:Path
    expected_catalog_sha256:str

    def checked(self):
        ident=identity(self.context_file,self.precision_file)
        if sha(self.catalog_file)!=self.expected_catalog_sha256:raise ValueError('Catalog digest mismatch')
        m=load(self.catalog_file)
        if m['schema']!='psr-context-catalog-v1'or m['identity']!=asdict(ident):raise ValueError('Catalog belongs to another context/build/precision contract')
        expected=load(self.precision_file)['partition_sha256']
        if sha(self.partition_file)!=expected or m['partition_sha256']!=expected:raise ValueError('Partition identity mismatch')
        paths=[]
        for part in m['chunks']:
            if Path(part['name']).name!=part['name']:raise ValueError('Catalog-relative chunk name required')
            f=self.catalog_file.parent/part['name']
            if sha(f)!=part['sha256']:raise ValueError('Chunk digest mismatch')
            paths.append(f)
        rows=read_rows(paths,ident,expected);p=load(self.partition_file)
        for i,row in rows.items():validate_row(row,p['states'][i])
        return ident,m,p,rows

    def query(self,target:Target):
        if not isinstance(target,Target):raise TypeError('Typed bound target required')
        ident,m,p,rows=self.checked()
        if target.identity!=ident or target.catalog_sha256!=self.expected_catalog_sha256:raise ValueError('Target context/build/precision/catalog mismatch')
        d=Domain();matching=set();unknown=set(range(146))-rows.keys()
        for i,row in rows.items():
            if not row['writer_known']:unknown.add(i);continue
            a=strict_bits(row['writer_half_bits'])
            if a.shape!=target.writer_half_bits.shape:raise ValueError('Target shape differs from bound writer')
            if np.array_equal(a,target.writer_half_bits):matching.add(i)
        return {'scope':'exact bounded known-context candidate set; no nearest value or uniqueness claim','identity':asdict(ident),'catalog_sha256':self.expected_catalog_sha256,'domain':d.record(),'partition_proof_reused':True,'model_matching_state_ids':sorted(matching),'candidate_union':runs(d,p['cells'],matching),'candidate_interface_classes':[{'state_id':i,'key':p['states'][i]['key'],'intervals':runs(d,p['cells'],{i})}for i in sorted(matching)],'found_f32_population':sum(p['states'][i]['f32_population']for i in matching),'coverage':{'evaluated_states':len(rows),'missing_state_ids':sorted(set(range(146))-rows.keys()),'unknown_state_ids':sorted(i for i,row in rows.items()if not row['writer_known']),'complete_model_coverage':not unknown},'unresolved_possible_union':runs(d,p['cells'],unknown),'unresolved_are_not_excluded':True,'true_control_input_to_solver':False,'new_model_or_native_calls':0,'original_host_exhaustive':False,'GPU_UI_unknown_source_inverse':False}
