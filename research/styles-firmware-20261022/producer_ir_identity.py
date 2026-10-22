"""Audit availability of actual historical producer compiler inputs.

No reconstruction, shader build, compilation, execution or normalization.
Exact SHA plus retained-execution provenance is required before raw diff.
Even then a diff is unclassified until a separate, explicit rule is proved.
"""
import argparse,ast,difflib,hashlib,json,re,tempfile
from pathlib import Path

EXPECTED={'S21':'a787d7ada4c12ba8fbc36ad48161f47d5fb63be4fd5a01421731569127b8cf28','S22':'ba676ebda2421750a32823caa5d664970c78f4fa459650910e65a5269df695da'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())


def original_file(path,expected,*,retained_execution_provenance=False):
    if type(retained_execution_provenance)is not bool:raise TypeError('Explicit provenance decision required')
    result={'expected_sha256':expected,'actual_sha256':None,'sha_verified':False,'retained_execution_provenance':retained_execution_provenance,'admissible_historical_original':False}
    if path is None:return dict(result,status='missing_original_path')
    try:
        if not path.is_file():return dict(result,status='missing_original_file')
        actual=sha(path)
    except OSError as ex:return dict(result,status='unreadable',error_type=type(ex).__name__)
    result.update(actual_sha256=actual,sha_verified=actual==expected)
    if actual!=expected:return dict(result,status='recorded_SHA_mismatch')
    if not retained_execution_provenance:return dict(result,status='matching_bytes_but_execution_origin_unproved')
    return dict(result,status='verified_retained_execution_input',admissible_historical_original=True)


def compare_originals(left,right,expected_left,expected_right,*,retained_execution_provenance=False):
    a=original_file(left,expected_left,retained_execution_provenance=retained_execution_provenance);b=original_file(right,expected_right,retained_execution_provenance=retained_execution_provenance)
    result={'left':a,'right':b,'raw_comparison_executed':False,'normalization_rules':[],'normalized_pair_sha256':None,'semantic_equality':'not established','whole_pipeline_equality':False}
    if not(a['admissible_historical_original']and b['admissible_historical_original']):return dict(result,status='blocked_missing_or_unproved_actual_inputs')
    x=left.read_bytes();y=right.read_bytes();diff=''.join(difflib.unified_diff(x.decode('utf8').splitlines(True),y.decode('utf8').splitlines(True),fromfile='retained-S21-producer',tofile='retained-S22-producer'))
    return dict(result,status='raw_identical'if x==y else'verified_raw_difference_requires_classification',raw_comparison_executed=True,byte_identical=x==y,raw_diff_sha256=hashlib.sha256(diff.encode()).hexdigest(),classification='literal identity only'if x==y else'unclassified; no names/metadata/attributes discarded')


def harness_lifecycle(path,pre):
    digest=sha(path)
    if digest!=pre['source_sha256_before_execution'][path.name]:raise ValueError('Current harness bytes differ from executed prebinding')
    tree=ast.parse(path.read_text());contexts=[]
    for node in ast.walk(tree):
        if not isinstance(node,ast.With):continue
        for item in node.items:
            c=item.context_expr
            if not isinstance(c,ast.Call)or not isinstance(c.func,ast.Attribute)or c.func.attr!='TemporaryDirectory':continue
            keywords={v.arg:ast.literal_eval(v.value)for v in c.keywords};contexts.append({'source_line':node.lineno,'end_line':node.end_lineno,'prefix':keywords.get('prefix'),'explicit_delete_override':'delete'in keywords,'default_cleanup_on_context_exit':'delete'not in keywords,'recorded_artifact':'enumerate(units) writes temporary {i}.ll; producer index0 ->0.ll'})
    if len(contexts)!=1 or contexts[0]['explicit_delete_override']:raise ValueError('Unexpected historical temporary-file lifecycle')
    return {'harness':path.name,'executed_source_sha256':digest,'source_matches_original_prebinding':True,'temporary_context':contexts[0],'identity_limit':'source lifecycle evidence; not a global proof that no external copy exists'}


def check(output):
    if output.exists():raise FileExistsError(output)
    root=Path(__file__).parent;e=root/'evidence';a=load(e/'native-active-s21c.json');b=load(e/'native-boundaries-s22d.json');v21=load(e/'verification-s21.json');v22=load(e/'verification-s22.json')
    if sha(e/'native-active-s21c.json')!=v21['evidence_sha256']['native-active-s21c.json']or sha(e/'native-boundaries-s22d.json')!=v22['evidence_sha256']['native-boundaries-s22d.json']:raise ValueError('Historical receipt identity changed')
    if a['host_IR_sha256'][0]!=EXPECTED['S21']or b['host_IR_sha256'][0]!=EXPECTED['S22']:raise ValueError('Recorded producer target SHA changed')
    lifecycle={stage:harness_lifecycle(root/name,load(e/pre))for stage,name,pre in [('S21','native_active_color.py','native-binding-s21c.pre.json'),('S22','native_color_boundaries.py','native-binding-s22d.pre.json')]}
    scopes=[];candidates=[];roots=[]
    for label,path in [('user_tmp',Path(tempfile.gettempdir())),('system_tmp',Path('/tmp'))]:
        resolved=path.resolve()
        if resolved in roots:continue
        roots.append(resolved)
        for stage,life in lifecycle.items():
            prefix=life['temporary_context']['prefix'];row={'root_label':label,'resolved_root_path_sha256':hashlib.sha256(str(resolved).encode()).hexdigest(),'stage':stage,'top_level_pattern':prefix+'*','candidate_relative_file':'0.ll','recursive_search':False}
            try:
                paths=list(resolved.glob(prefix+'*'));row['matching_directory_entries']=len(paths);row['status']='read'
                for p in paths:
                    q=p/'0.ll';candidates.append({'scope':label,'entry_name':p.name,'candidate_file':'0.ll',**original_file(q,EXPECTED[stage])})
            except OSError as ex:row.update(status='unreadable',error_type=type(ex).__name__)
            scopes.append(row)
    # These six files were discovered only in this research directory. Hash
    # them as candidates; never relabel source AIR as executed host IR.
    for folder in ['plugin-24A435','plugin-iphone17-3-24A446/SmartStyleV1.bundle']:
        for i in range(3):
            rel=f'{folder}/air-{i}.ll.txt';p=e/rel;row={'scope':'existing_research_IR_files','relative_path':rel,'exists':p.is_file()}
            if p.is_file():row.update(bytes=p.stat().st_size,actual_sha256=sha(p),matching_recorded_execution_stages=[s for s,h in EXPECTED.items()if sha(p)==h])
            candidates.append(row)
    logs={}
    for stage,path,post in [('S21',Path('../s21-final-local-logs/native-binding-s21c.log'),'native-binding-s21c.json'),('S22',Path('../s22-final-local-logs/native-binding-s22d.log'),'native-binding-s22d.json')]:
        row={'relative_path':str(path),'exists':path.is_file()};expected=load(e/post)['log_sha256']
        if path.is_file():
            if sha(path)!=expected:raise ValueError('Original run log SHA differs')
            prefix=lifecycle[stage]['temporary_context']['prefix'];row.update(sha256=expected,log_matches_original_post=True,exact_producer_temp_path_recorded=bool(re.search(re.escape(prefix)+r'[^/\s]+/0\.ll',path.read_text())))
        logs[stage]=row
    result={'scope':__doc__,'recorded_actual_producer_IR_sha256':EXPECTED,'historical_receipt_sha256':{'native-active-s21c.json':sha(e/'native-active-s21c.json'),'native-boundaries-s22d.json':sha(e/'native-boundaries-s22d.json')},'executed_harness_lifecycle':lifecycle,'bounded_temp_scopes':scopes,'existing_IR_candidates':candidates,'successful_original_logs':logs,'actual_pair':compare_originals(None,None,EXPECTED['S21'],EXPECTED['S22']),'blocked_action':'SHA verification and literal/semantic diff of the two actual historical producer compiler inputs','block_reason':'historical harnesses used cleaned TemporaryDirectory units and kept SHA only; no actual raw pair available in bounded known locations; no exact temporary paths in successful logs','block_status':'missing artifacts, not a permission denial','global_filesystem_absence_proved':False,'difference_classification':{k:'not performed; actual pair unavailable'for k in ['names_order_metadata','arithmetic_constants_FP_attributes','memory_summaries_ABI_writes_dependencies']},'normalization_rules':[],'normalized_pair_sha256':None,'corroborating_only':{'original_function_metadata_equal':a['original']==b['original'],'plain_metadata_equal':a['plain_original']==b['plain_original'],'prefix_half_bit_mismatches':b['prefix_half_bit_mismatches_vs_S21'],'does_not_prove_module_equality':True},'unchanged_evidence_scope':{'model_interface_states_exhaustively_searched':146,'original_host_signature_states_with_finite_witnesses':[0,1,2,92,93,94],'historical_module_equality':'unproved'},'reconstructed_IR_generated':False,'new_model_forward_calls':0,'new_original_kernel_calls':0,'new_leaf_cases':0,'downloads_mounts_private_media_or_process_inventory':False,'next_step':'only a retained original pair with established execution provenance and recorded SHA can reopen historical diff; a future persisted/new run is new evidence and cannot replace S21/S22'}
    output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({'historical_pair':result['actual_pair']['status'],'temp_entries':sum(s.get('matching_directory_entries',0)for s in scopes),'known_local_IR_candidates':6,'matching_recorded_IR_files':sum(bool(c.get('matching_recorded_execution_stages'))for c in candidates),'normalized_hash':None,'new_original_calls':0}));return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);a=p.parse_args();check(a.output)
