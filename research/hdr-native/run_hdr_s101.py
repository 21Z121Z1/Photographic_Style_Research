"""Runner-only retained full-file delivery; frozen S42/S88/S89 pixel math.

Five old numerical cases are regenerated because earlier selected archives only
kept contacts/hashes. This is delivery, not a new independent validation cohort.
All new image outputs, including public-sample derivatives, are encrypted.
"""
from pathlib import Path
import ast,hashlib,json,os,shutil,subprocess,sys,tarfile
R=Path.cwd();D=R/'research/hdr-native';W=Path(os.environ['W']);O=W/'out';PRIVATE=W/'private';ENC=W/'encrypted'
sys.path[:0]=[str(R),str(D)]
from headroom_validation_s101 import validate as validate_actual_files
from export_hdr_target_s101 import export_target
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):
    with p.open('x')as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
cases=json.loads((D/'inputs-s89.json').read_text())['cases'];assert len(cases)==5
namespace={'D':D,'ast':ast,'hashlib':hashlib,'json':json}
tree=ast.parse((D/'run_hdr_s89.py').read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ['bindings','derive_case']];assert len(defs)==2
exec(compile(ast.Module(body=defs,type_ignores=[]),'S89-original-input-only-derivation-functions','exec'),namespace)
sources=['run_hdr_s101.py','rebuild_export_s101.py','headroom_validation_s101.py','export_hdr_target_s101.py','seal_partial_s101.py','s101_transfer_policy.json','run_hdr_s89.py','inputs-s89.json','run_hdr_s88.py','rebuild_master_s88.py','run_hdr_s42.py','source_s37.m','ltm_materialize_s42.m','run_hdr_s47.py','derive_display_s51.py','render_intent_s44.py','carrier_readback_s87.m','carrier_case_s87.py','iso_splice.py']
freeze={'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'source_SHA':{str((D/n).relative_to(R)):sha(D/n)for n in sources},'cases':cases,'purpose':'Close full-file retention gap: native common key1 R, separate global GTC hypothesis/local projection candidate, exact old relative master and independent-HDR HEIC carrier, full masks and fixed ACES previews. No new holdouts or physical scene proof.','pixel_math':'S42 original AST statements with one additional IO call; stripping it restores original AST. S88/S89 display and encoder math unchanged; same10-bit444/matrix6.','common_baseline':'Key1 reverse R precedes all supplied global/local hypotheses; these names do not imply isolated GTM/LTM on original S. Key1 whole style is not an isolated skin operator.','old_gates_changed':False,'new_semantic_correction_applied':False,'large_archive_route':'GitHub directly to Japan, no HK ZIP/large cipher body copy; complete GPG/member verification on Japan','engineering_accepted':False,'A_phase_complete':False,'acceptance_complete':False}
save(O/'suite-freeze.json',freeze);rows=[]
def seal(folder,name):
    save(folder/'manifest.json',{'run_id':os.environ['GITHUB_RUN_ID'],'commit':os.environ['GITHUB_SHA'],'os_build':'26A434','people_results_encrypted':True,'files':[{'path':str(p.relative_to(folder)),'size':p.stat().st_size,'sha256':sha(p)}for p in sorted(folder.rglob('*'))if p.is_file()]})
    tarpath=W/(name+'.tar.gz')
    with tarfile.open(tarpath,'w:gz')as t:t.add(folder,arcname='out')
    cipher=ENC/(name+'.tar.gz.gpg')
    with(O/(name+'-encrypt.log')).open('x')as log:subprocess.run(['gpg','--batch','--trust-model','always','--recipient','28E62F64A29764C2F2AEBF5D5B6B1C101E5F5ABA','--encrypt','--output',cipher,tarpath],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=1200)
    record={'file':cipher.name,'bytes':cipher.stat().st_size,'sha256':sha(cipher),'private_manifest_SHA256':sha(folder/'manifest.json'),'member_files':len(json.loads((folder/'manifest.json').read_text())['files'])}
    tarpath.unlink();return record
for case in cases:
    photo=case['photo'];cw=W/photo;cw.mkdir();co=cw/'out';cp=cw/'private';ce=cw/'encrypted'
    for p in [co,cp,ce,cw/'secure']:p.mkdir()
    public=O/photo;public.mkdir();export=PRIVATE/photo;row={'photo':photo,'previous_role':case['role'],'completed':False,'new_holdout':False};rows.append(row)
    driver,unused_old_helper,derivation=namespace['derive_case'](case)
    old="shutil.copyfile(path,full/'"+photo+"-independent-HDR.heic')"
    new=old+";shutil.copyfile(path,Path(os.environ['HDR_S101_EXPORT'])/'independent-HDR.heic')"
    assert driver.count(old)==1;driver=driver.replace(old,new)
    # The previously unused full-folder meaning file is small but essential to
    # retain the original render intent/offset/rotation interpretation.
    marker="assert before_pixels=={f:sha(folder/f)for f in before_pixels}"
    assert driver.count(marker)==1;driver=driver.replace(marker,"shutil.copyfile(full/'meaning.json',Path(os.environ['HDR_S101_EXPORT'])/'carrier-meaning.json')\n"+marker)
    ast.parse(driver);program=cw/'driver.py';program.write_text(driver)
    save(public/'derivation.json',{'S89_original_derivation':derivation,'S101_extra_driver_replacements':[{'old':old,'new':new},{'old':marker,'new':"shutil.copyfile(full/'meaning.json',Path(os.environ['HDR_S101_EXPORT'])/'carrier-meaning.json')\n"+marker}],'S101_final_driver_SHA256':sha(program),'rebuilder':'New rebuild_export_s101.py selects original S42 AST, adds only IO retention call. Original S89 substituted helper is not executed.','original_S88_pixel_math_changed':False})
    env=dict(os.environ,W=str(cw),HDR_S89_CASE_JSON=json.dumps(case),HDR_S89_REBUILD=str(D/'rebuild_export_s101.py'),HDR_S101_EXPORT=str(export))
    try:
        with(public/'driver.log').open('x')as log:p=subprocess.run([sys.executable,program],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=3300)
        assert p.returncode==0,'Native delivery child failed; inspect its logs before any retry'
        analysis=json.loads((co/'analysis.json').read_text());native=json.loads((co/'native.json').read_text());rebuild=json.loads((co/'rebuild-rebuild-result.json').read_text())
        target_record=export_target(cw,case,export)
        required=['native-key1-reverse.exr','global-only-GTC-hypothesis.exr','local-only-thumbnail-projection-candidate.exr','relative-scene-candidate.exr','independent-HDR-target.exr','target-EXR-readback.json','independent-HDR.heic','global-hypothesis-flags.u8','global-hypothesis-flags.json','inherited-S42-positive-pair-mask.npy','separated-meaning.json','carrier-meaning.json']
        assert all((export/n).is_file()for n in required)
        assert native['ImageIO_full_SDR']['decoded_sdr_max0_verified']and rebuild['EXR_matches_old_archive_member']and sha(export/'relative-scene-candidate.exr')==case['master_EXR_sha256']and sha(export/'independent-HDR.heic')==analysis['carrier_sha256']
        validate_actual_files(case,cw,co,export,row)
        meaning=json.loads((export/'separated-meaning.json').read_text());assert all(x['source_unchanged']for x in meaning['preview_checks'])
        save(export/'delivery-binding.json',{'photo':photo,'source_sha256':case['source_sha256'],'master_EXR_sha256':case['master_EXR_sha256'],'carrier_sha256':analysis['carrier_sha256'],'native_ImageIO_full_SDR_max0':True,'original_native_validation':native['ImageIO_full_SDR'],'full_original_source_retained_in_repo':case['source_path'],'new_physical_or_semantic_proof':False,'common_key1_and_hypothesis_boundaries':freeze['common_baseline']})
        row.update(completed=True,full_file_inventory=[{'file':n,'bytes':(export/n).stat().st_size,'sha256':sha(export/n)}for n in required],HDR_target_EXR=target_record,native_ImageIO_full_SDR_max0=True,master_exact_old_SHA=True,original_S88_metrics=analysis['metrics'],separated_storage_metrics=meaning['storage_only'],original_anchor=meaning['original_frozen_anchor'],original_map_variants=meaning['original_frozen_map_variants'],encrypted=seal(export,photo+'-full-delivery'))
        shutil.rmtree(export) # Only new per-run plaintext; complete files remain encrypted.
    except Exception as e:
        row.update(completed=False,failure_type=type(e).__name__,failure=str(e))
        if export.exists()and not(export/'manifest.json').exists():row['partial_encrypted']=seal(export,photo+'-partial-delivery')
    finally:
        for checkpoint in sorted(co.rglob('*')):
            if checkpoint.is_file():
                rel=checkpoint.relative_to(co);assert checkpoint.suffix in {'.json','.log','.txt'};target=public/rel
                target.parent.mkdir(parents=True,exist_ok=True)
                if not target.exists():shutil.copyfile(checkpoint,target)
        save(public/'delivery-analysis.json',row)
        assert cw.parent==W and cw.name==photo;shutil.rmtree(cw)
    if not row['completed']:break
save(O/'analysis.json',{'os_build':'26A434','rows':rows,'completed_photos':sum(r['completed']for r in rows),'all_five_completed':len(rows)==5 and all(r['completed']for r in rows),'output_files_actually_retained_in_ciphers':True,'same_five_old_numerical_cases':True,'new_semantic_or_physical_accuracy_claim':False,'engineering_accepted':False,'A_phase_complete':False,'acceptance_complete':False})
save(O/'encrypted-inventory.json',{'files':[{'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(ENC.glob('*.gpg'))],'plaintext_uploaded':False,'file_delivery_requires_Japan_GPG_all_members_verification':True})
print(json.dumps({'complete_photos':sum(r['completed']for r in rows),'new_scene_or_semantic_accuracy_claim':False}));sys.exit(0 if len(rows)==5 and all(r['completed']for r in rows)else 1)
