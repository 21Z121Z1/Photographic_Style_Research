"""Runner-only full-file retention from the unchanged frozen S42 calculation.

One new AST call copies local v tiles before the original loop deletes its
temporary textures. Stripping this call must reproduce the original AST.
Global LUT inversion is the existing hypothesis, with its original invalid mask.
The common native key1 reverse is explicitly retained as a separate baseline.
"""
from pathlib import Path
import ast,copy,hashlib,json,os,shutil,subprocess
import numpy as np
from rebuild_master_s88 import selections

def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):
    with p.open('x')as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
def hook_module(module):
    original=copy.deepcopy(module);work=copy.deepcopy(module);count=0
    class Insert(ast.NodeTransformer):
        def visit_Assign(self,node):
            nonlocal count
            self.generic_visit(node)
            if len(node.targets)==1 and isinstance(node.targets[0],ast.Name)and node.targets[0].id=='v'and ast.unparse(node.value)=='at * qt / (E if weight == 0 else 1)':
                count+=1;extra=ast.parse('retain_local_tile(tag, weight, top, stop, v)').body[0];return [node,ast.copy_location(extra,node)]
            return node
    work=ast.fix_missing_locations(Insert().visit(work));assert count==1
    class Strip(ast.NodeTransformer):
        def visit_Expr(self,node):
            if isinstance(node.value,ast.Call)and isinstance(node.value.func,ast.Name)and node.value.func.id=='retain_local_tile':return None
            return self.generic_visit(node)
    stripped=Strip().visit(copy.deepcopy(work));assert ast.dump(stripped,include_attributes=False)==ast.dump(original,include_attributes=False)
    return work,{'inserted_IO_calls':count,'removing_IO_calls_restores_original_AST':True,'original_AST_SHA256':hashlib.sha256(ast.dump(original,include_attributes=False).encode()).hexdigest(),'new_AST_SHA256':hashlib.sha256(ast.dump(work,include_attributes=False).encode()).hexdigest(),'pixel_expressions_modified':False}
def metric(a,b):
    d=np.asarray(a,'f8')-np.asarray(b,'f8');good=np.isfinite(d);return float(abs(d[good]).max())if good.any()else 0.
def main():
    root=Path.cwd();d=root/'research/hdr-native';wdir=Path(os.environ['W']);out=wdir/'out';export=Path(os.environ['HDR_S101_EXPORT']);export.mkdir(parents=True,exist_ok=False)
    case_info=json.loads(os.environ['HDR_S89_CASE_JSON']);photo=case_info['photo'];parts,exr_call,spans=selections((d/'run_hdr_s42.py').read_text());native,binding=hook_module(parts['native_master'])
    g={'__name__':'s101_frozen_S42_with_IO_copy'};exec(compile(parts['preamble'],'S42-original-preamble','exec'),g)
    row=next(t for t in g['PHOTOS']if t[0]==photo);g.update(photo=row[0],role=row[1],source=row[2]);local=None;local_max=0.;local_nf=0;copied_rows={}
    def retain(tag,weight,top,stop,v):
        nonlocal local,local_max,local_nf
        copied_rows[tag]=copied_rows.get(tag,0)+stop-top
        if weight!=1:return
        if local is None:
            p=wdir/'local-delivery.f16'
            with p.open('xb')as f:f.truncate(g['h']*g['w']*3*2)
            local=np.memmap(p,mode='r+',dtype='<f2',shape=(g['h'],g['w'],3))
        stored=v.astype('<f2');local[top:stop]=stored;local_max=max(local_max,metric(stored,v));local_nf+=int((~np.isfinite(stored)&np.isfinite(v)).sum())
    g['retain_local_tile']=retain;exec(compile(native,'S42-original-native-statements-plus-IO-copy','exec'),g)
    assert local is not None and all(n==g['h']for n in copied_rows.values())and len(copied_rows)==2
    local.flush();g['scene'].flush();exec(compile(parts['old_transport_mask'],'S42-original-transport-mask-statements','exec'),g);g['mask'].flush()
    master=eval(compile(exr_call,'S42-original-master-EXR-call','eval'),g);assert master['sha256']==case_info['master_EXR_sha256'],'Frozen master differs from previous exact file; no delivery pass inferred'
    full=g['full'];shutil.copyfile(full/master['path'],export/'relative-scene-candidate.exr')
    np.save(full/'positive_pair_mask.npy',np.asarray(g['mask'],dtype=bool))
    shutil.copyfile(full/'positive_pair_mask.npy',export/'inherited-S42-positive-pair-mask.npy')
    a=g['a'];table=g['table'].reshape(-1);E=g['E'];h=g['h'];width=g['w'];global_path=wdir/'global-delivery.f16';flags_path=export/'global-hypothesis-flags.u8'
    for path,nbytes in [(global_path,h*width*3*2),(flags_path,h*width*3)]:
        with path.open('xb')as f:f.truncate(nbytes)
    global_image=np.memmap(global_path,mode='r+',dtype='<f2',shape=(h,width,3));flags=np.memmap(flags_path,mode='r+',dtype='u1',shape=(h,width,3));global_max=0.;global_nf=0;counts={}
    for top in range(0,h,g['ROWS']):
        stop=min(top+g['ROWS'],h);tile=np.asarray(a[top:stop,:,:3],dtype='f2');answer,c=g['global_inverse_hypothesis'](tile,table,E);stored=answer.astype('<f2');global_image[top:stop]=stored;global_max=max(global_max,metric(stored,answer));global_nf+=int((~np.isfinite(stored)&np.isfinite(answer)).sum())
        for k,v in c.items():counts[k]=counts.get(k,0)+v
        v=tile.astype('f8');lo=(np.nextafter(tile,np.float16(-np.inf)).astype('f8')+v)*.5;hi=(np.nextafter(tile,np.float16(np.inf)).astype('f8')+v)*.5;low=lo<=table[0];high=hi>=table[-1];flat=np.zeros(tile.shape,bool)
        for z in np.unique(table[:-1][np.diff(table)==0]):flat|=(lo<=z)&(hi>=z)
        f=low.astype('u1')*1+high.astype('u1')*2+flat.astype('u1')*4+(~np.isfinite(v)).astype('u1')*8
        assert np.array_equal(~np.isfinite(answer),f!=0),'Flags must reproduce frozen global hypothesis exclusions exactly'
        flags[top:stop]=f
    flags.flush();global_image.flush();assert counts==g['global_masks']and global_nf==local_nf==0
    common={'photo':photo,'common_baseline':'Native Neutrino key1 reverse R is shared BEFORE both global/local hypotheses; R itself reverses a whole style and does not isolate semantic processing','os_build':'26A434','formula_freeze_sha256':g['frozen_sha'],'RAW_scene_accuracy_unverified':True,'Apple_Log_unchanged':True,'no_new_camera_inverse_or_99percent_scene_claim':True}
    files=[{'path':'relative-scene-candidate.exr','sha256':sha(export/'relative-scene-candidate.exr'),'bytes':(export/'relative-scene-candidate.exr').stat().st_size,'original_frozen_EXR_exact':True}]
    definitions=[('native-key1-reverse.exr',a[...,:3],'Native full-style inverse R, not isolated global/local/skin'),('global-only-GTC-hypothesis.exr',global_image,'Existing supplied GTC monotone inverse /E on strict valid domain. Producer order/global color/baseGain relationship unproven; flags and NaNs retained'),('local-only-thumbnail-projection-candidate.exr',local,'Existing native RGB guided projection with GTC retained, relative to shared R. Not certified camera c/d LTM inverse')]
    for name,array,status in definitions:
        record=g['exr_write'](export/name,array,dict(common,status=status));files.append(record)
    previews=[('original SDR',g['previews']['SDR']),('native key1 reverse',g['previews']['inverse-key1']),('global GTC hypothesis',global_image[g['ys'][:,None],g['xs'][None,:]]),('local projection candidate',local[g['ys'][:,None],g['xs'][None,:]]),('both scene candidate',g['scene'][g['ys'][:,None],g['xs'][None,:]])];checks=[]
    for index,(name,array)in enumerate(previews):
        c,_=g['preview'](array,export/f'preview-{index}.png',g['row']['orientation']);c['label']=name;checks.append(c)
    save(export/'global-hypothesis-flags.json',{'file':flags_path.name,'shape':[h,width,3],'dtype':'u1','sha256':sha(flags_path),'bits':{'1':'lower GTC endpoint half cell','2':'upper GTC endpoint half cell','4':'flat knot crossed by half cell','8':'nonfinite R component'},'zero':'Original supplied GTC hypothesis strict valid component; not full consumer/camera inverse mask','invalid_output':'NaN preserved in EXR, black only in preview; no missing component guessed','counts':counts,'interval_boundary':'No certified original consumer/camera interval inferred from this hypothetical curve domain'})
    meaning=dict(common,shape=[h,width,3],relative_exposure_E=E,files=files,global_mask=counts,storage_only={'local_half_max_abs_vs_frozen_v':local_max,'global_half_max_abs_vs_frozen_hypothesis':global_max,'new_half_overflow_components':global_nf+local_nf,'all_EXR_storage_readback_differences':0},original_frozen_map_variants=g['row']['map_variants'],original_frozen_anchor=g['row']['native_RGB_anchor'],preview_checks=checks,display=g['display'],ast_binding=binding,separate_file_export_is_not_physical_recovery_proof=True)
    save(export/'separated-meaning.json',meaning)
    result={'original_template_sha256':sha(d/'run_hdr_s42.py'),'selection':spans,'selection_photo':photo,'scope':'Original frozen S42 master plus IO-only retained global/local/common-key1 files. No old large archive read.','OS_build':'26A434','math_or_parameters_changed':False,'old_full_archive_reused':False,'master_EXR':master,'old_master_EXR_sha256':case_info['master_EXR_sha256'],'master_pixel_sha256':sha(g['case']/'scene_candidate.f16'),'source_sha256':sha(g['source']),'formula_freeze_sha256':g['frozen_sha'],'mask':{'file':str((full/'positive_pair_mask.npy').relative_to(wdir)),'sha256':sha(full/'positive_pair_mask.npy'),'scope':'Original S42 zero-offset inherited positive transport mask; not scene inverse/new HDR gain mask'},'old_S42_native_map_variants':g['row']['map_variants'],'anchor_diagnostic':g['row']['native_RGB_anchor'],'EXR_matches_old_archive_member':True,'full_separated_export':meaning}
    save(out/'rebuild-result.json',result);print(json.dumps({'completed':True,'photo':photo,'frozen_master_exact':True,'separate_full_files_written':len(files),'new_scene_or_semantic_proof':False}))
if __name__=='__main__':main()
