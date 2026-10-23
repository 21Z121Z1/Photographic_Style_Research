"""S30 independent point composition, raw frozen source/context only.

Selected four sites require the exact S29 whitelist. A rejected site remains
unknown even when cast0's independent writer branch can finish. No native
intermediate-array argument exists; the reference is a guard, never pixel data.
"""
from dataclasses import dataclass,field
from pathlib import Path
import ast,hashlib
import numpy as np
import complete_forward
from active_color import Color,replace_color
from baseline_archive import encoded,sha
from bright137_witness import require_inverse_scope
from bright_point_profile import Profile
from bright_saved_replay import fingerprint,bits
from color_inverse import f32
from complete_fixture import decode
from context_color_api import load
from leaf_numeric import DomainUnknown

R=Path(__file__).parent
E=R/'evidence'
NAME='source-connected-bright-s30-four-approved-sites-point-v1'


def deltas(actual,expected):
    rows=[]
    for i,(a,b)in enumerate(zip(actual,expected)):
        if a!=b:
            rows.append({'argument_index':i,'actual':a,'expected':b,
                         'differing_bit_indices':[j for j,(x,y)in enumerate(zip(a['bits'],b['bits']))if x!=y]})
    return rows


@dataclass
class Dispatch:
    profile:Profile
    targets:dict
    visits:list=field(default_factory=list)
    failures:list=field(default_factory=list)

    def __call__(self,*args,grid):
        grid=tuple(grid)
        if grid not in self.targets:
            self.visits.append({'grid':list(grid),'mode':'unchanged_v3_non_target'})
            return complete_forward.bright(*args)
        expected_key=self.targets[grid]
        profile=self.profile.checked()
        actual=fingerprint(args)
        key=hashlib.sha256(encoded(actual)).hexdigest()
        expected=profile['points'][expected_key]['complete_inputs']
        entry={'grid':list(grid),'mode':'S29_profile_target','expected_input_key':expected_key,
               'model_input_key':key,'model_inputs':actual,'exact_full_input_match':actual==expected,
               'input_differences':deltas(actual,expected),'guard_admitted':False}
        self.visits.append(entry)
        if actual!=expected:
            entry['failure']='Model upstream did not reach exact approved full input tuple; no replacement or fallback'
            self.failures.append(entry)
            raise DomainUnknown(entry['failure'])
        stages={}
        try:
            result=self.profile.forward(*args,observations=stages)
        except (ValueError,TypeError)as ex:
            entry['failure']=str(ex);self.failures.append(entry)
            raise DomainUnknown('Independent profile rejected model input: '+str(ex))from ex
        entry.update(guard_admitted=True,
                     bright_stage_bits={str(k):{'precision':v.precision,'bits':bits(v)}for k,v in stages.items()},
                     bright_output_bits=bits(result))
        return result


def clone(dispatch):
    precision=load(E/'model-precision-v3-s25c6.json')
    path=R/'complete_forward.py'
    if sha(path)!=precision['model_source_sha256'][path.name]:raise ValueError('Pinned v3 connected source required')
    tree=ast.parse(path.read_text())
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='forward')
    class Connect(ast.NodeTransformer):
        count=0
        def visit_Call(self,node):
            self.generic_visit(node)
            if isinstance(node.func,ast.Name)and node.func.id=='bright':
                self.count+=1;node.func=ast.Name(id='psr_bright_at',ctx=ast.Load())
                node.keywords.append(ast.keyword(arg='grid',value=ast.Tuple(elts=[ast.Name(id='x',ctx=ast.Load()),ast.Name(id='y',ctx=ast.Load())],ctx=ast.Load())))
            return node
    transform=Connect();fn=transform.visit(fn)
    if transform.count!=1:raise ValueError('Exactly one original bright callsite required')
    namespace=dict(vars(complete_forward));namespace['psr_bright_at']=dispatch
    module=ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[]))
    exec(compile(module,'<PSR-S30-source-connected-bright>','exec'),namespace)
    return namespace['forward']


def source_run(context_file:Path,control:dict,profile:Profile,plan:dict):
    if sha(context_file)!=plan['context_sha256']:raise ValueError('Only the frozen synthetic source context is supported')
    if control not in plan['controls']:raise ValueError('Only the three predeclared controls/sites are supported')
    if sha(profile.file)!=plan['profile_sha256']:raise ValueError('Separate accepted S29 profile required')
    base=decode(load(context_file))
    require_inverse_scope(int(base.params.view('u4')[0]),frozenset({3}))
    raw=control['raw_f32_bits']
    if type(raw)is not int or not 0<=raw<=0x3ec00000:raise ValueError('Existing canonical+0..3/8 raw domain only')
    context=replace_color(base,Color(f32(raw)))
    dispatch=Dispatch(profile,{tuple(s['grid']):s['input_key']for s in control['targets']})
    result=clone(dispatch)(context,point=True)
    targets=[r for r in dispatch.visits if r['mode']=='S29_profile_target']
    complete=len(targets)==len(control['targets'])and all(r['guard_admitted']for r in targets)
    return result,{'experiment':NAME,'context_sha256':sha(context_file),'control':control,
                   'visits':dispatch.visits,'target_input_connection_complete':complete,
                   'target_failures':dispatch.failures,'pixel_unknowns':result.pixel_unknowns,
                   'internal_unknowns':result.internal_unknowns,
                   'writer_generated':result.writer is not None,
                   'status':'model_source_to_bright_connected'if complete and not result.pixel_unknowns and not result.internal_unknowns else'failed_or_unknown_no_oracle_fallback',
                   'native_intermediate_arrays_used_as_inputs':False,
                   'cast0_selected404_is_skin393':True,
                   'bright_selected_to_writer_certified':False}
