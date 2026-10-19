"""Reuse remaining four encrypted masters, sequentially, for frozen HDR intent."""
from pathlib import Path
import os,sys,json,hashlib,subprocess,shutil,tarfile,math
from derive_display_s51 import derive
R=Path.cwd();D=R/'research/hdr-native';W=Path(os.environ['W']);O=W/'out';PRIVATE=W/'private';ENC=W/'encrypted';plan=json.loads((D/'inputs-s51.json').read_text());repo='21Z121Z1/Photographic_Style_Research'
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
assert sys.platform=='darwin' and subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
assert sum(c['ZIP_bytes'] for c in plan['cases'])==plan['total_master_download_bytes']<1_000_000_000
assert len(plan['cases'])==4 and sum(c['role']=='display-formula-holdout' for c in plan['cases'])==2
for name,digest in plan['frozen_source_sha256'].items():assert sha(D/name)==digest
template=(D/'run_hdr_s47.py').read_text();derived={};derivations={}
for c in plan['cases']:
    derived[c['photo']],derivations[c['photo']]=derive(template,c)
freeze={'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'cases':plan['cases'],'total_master_download_bytes':plan['total_master_download_bytes'],'frozen_source_sha256':plan['frozen_source_sha256'],'derivations':derivations,'source_sha256':{p.name:sha(p) for p in [D/'run_hdr_s51.py',D/'derive_display_s51.py',D/'inputs-s51.json']},'holdout_scope':plan['holdout_scope'],'recipe':'S44/S47 exposure_intent + hdr_intent + supplied_pair_log, no formula/parameter fit; keep original master/key1/Apple Log/guided untouched','preview':'Same fixed ACES configuration; contact-only encrypted output, no plaintext photo upload','new_pixel_work':'Native SDR decode and supplied-pair native headroom only, no full source/key1/guided rerun','original_thresholds':{'max_abs':1e-5,'PSNR_peak1_min_db':60,'relative_max':1e-3,'SDR_max_abs':0},'all_inverse_masks_changed':False,'full_new_arrays_archived':False,'scope':'Four new independent display outputs plus prior S47 development output form five-photo formula suite; cannot certify camera scene inverse or encoded carrier'}
save(O/'suite-freeze.json',freeze);freeze_sha=sha(O/'suite-freeze.json');results=[];failure=None
try:
    for c in plan['cases']:
        assert sha(O/'suite-freeze.json')==freeze_sha and shutil.disk_usage(W).free>3_000_000_000
        name=c['photo'];case=W/name;case.mkdir();(case/'out').mkdir();(case/'private').mkdir();(case/'secure').mkdir();(case/'encrypted').mkdir();derived_path=case/'case_runner.py';derived_path.write_text(derived[name]);assert sha(derived_path)==derivations[name]['derived_script_sha256']
        metadata=json.loads(subprocess.check_output(['gh','api',f"repos/{repo}/actions/artifacts/{c['artifact_id']}"]));assert not metadata['expired'] and metadata['size_in_bytes']==c['ZIP_bytes'] and metadata['digest']=='sha256:'+c['ZIP_sha256']
        with (case/'S42.zip').open('xb') as out:subprocess.run(['gh','api',f"repos/{repo}/actions/artifacts/{c['artifact_id']}/zip"],stdout=out,check=True,timeout=600)
        assert (case/'S42.zip').stat().st_size==c['ZIP_bytes'] and sha(case/'S42.zip')==c['ZIP_sha256']
        env=os.environ.copy();env['W']=str(case);env['PYTHONPATH']=str(D);env['S47_S42_SESSION']=os.environ.pop(c['session_env']);assert len(env['S47_S42_SESSION'])<200
        # Do not pass other cases' transient sessions into the child.
        for sibling in plan['cases']:env.pop(sibling['session_env'],None)
        env.pop('GH_TOKEN',None)
        with (case/'out/case-driver.log').open('w') as log:child=subprocess.run([sys.executable,str(derived_path)],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=1200)
        del env
        target=O/name;shutil.copytree(case/'out',target);(target/'derived-source.txt').write_text(derived[name]);assert child.returncode==0,f'{name} driver failed; inspect aggregate case log before another run'
        a=json.loads((target/'analysis-s47.json').read_text());assert a['completed'] and a['source_input_before']==a['source_input_after'] and a['source_input_before']['master_EXR']==c['master_EXR_sha256'];assert a['display']['config_sha256']==plan['fixed_ACES_config_sha256'];assert all(p['input_before_SHA256']==p['input_after_SHA256'] for p in a['preview_input_checks']);assert len(a['variants'])==2 and all(len(v['native']['headrooms'])==5 for v in a['variants'])
        a['role']=c['role'];results.append(a);dest=PRIVATE/name;dest.mkdir();shutil.copyfile(case/'private/contact.private.png',dest/'contact.private.png');shutil.copyfile(case/'private/meaning.json',dest/'meaning.json')
        save(O/'analysis-s51.json',{'os_build':'26A434','image_version':os.environ.get('ImageVersion'),'suite_freeze_sha256':freeze_sha,'rows':results,'completed_photos':len(results),'required_new_photos':4,'total_master_download_bytes':plan['total_master_download_bytes'],'full_master_recomputed':False,'original_thresholds_or_masks_changed':False,'completed':False,'acceptance_complete':False,'A_phase_complete':False})
        # These are this job's new plaintext copies, never historical files.
        shutil.rmtree(case)
except BaseException as exc:
    failure=exc;save(O/'failure.json',{'class':type(exc).__name__,'message':str(exc),'completed_new_photos':len(results),'no_secret_values_logged':True})
finally:
    files=[{'path':str(p.relative_to(PRIVATE)),'size':p.stat().st_size,'sha256':sha(p)} for p in sorted(PRIVATE.rglob('*')) if p.is_file()]
    if files:
        save(PRIVATE/'manifest.json',{'run_id':os.environ['GITHUB_RUN_ID'],'commit':os.environ['GITHUB_SHA'],'os_build':'26A434','people_results_encrypted':True,'files':files})
        with tarfile.open(W/'previews.tar.gz','w:gz') as tar:tar.add(PRIVATE,arcname='out')
        with (O/'preview-encrypt.log').open('w') as log:subprocess.run(['gpg','--batch','--trust-model','always','--recipient','28E62F64A29764C2F2AEBF5D5B6B1C101E5F5ABA','--encrypt','--output',ENC/'previews.tar.gz.gpg',W/'previews.tar.gz'],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        cipher=ENC/'previews.tar.gz.gpg';save(O/'encrypted-inventory.json',{'files':[{'file':cipher.name,'size':cipher.stat().st_size,'sha256':sha(cipher)}],'plaintext_uploaded':False,'contact_only':True,'full_arrays_reuploaded':False})
if failure:raise failure
assert len(results)==4 and sha(O/'suite-freeze.json')==freeze_sha
a=json.loads((O/'analysis-s51.json').read_text());a['completed']=True;a['encrypted_previews_sealed']=True;save(O/'analysis-s51.json',a);print(json.dumps({'completed_new_photos':4,'master_inputs_unchanged':True,'no_formula_fit':True,'acceptance_complete':False}))
