"""Small read-only archive/scalar checks. No photograph processing."""
from pathlib import Path
import argparse,hashlib,json,sys,zipfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
from global_headroom_s66 import evaluate_helper,restore_recorded_headroom
p=argparse.ArgumentParser();p.add_argument('--archive-root',type=Path,required=True);a=p.parse_args();D=Path(__file__).resolve().parent
records=json.loads((D/'evidence/s66/archive-provenance.json').read_text())['runs'];checks={}
for rid,r in records.items():
    archive=a.archive_root/'runs'/rid/f"artifact-{r['artifact_id']}.zip"
    with archive.open('rb')as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['ZIP_sha256']
    with zipfile.ZipFile(archive)as z:
        raw=z.read('manifest.json');assert hashlib.sha256(raw).hexdigest()==r['manifest_sha256'];m=json.loads(raw);assert m['commit']==r['commit']and m['os_build']=='26A434'
        for x in m['files']:assert len(z.read(x['path']))==x['size']and hashlib.sha256(z.read(x['path'])).hexdigest()==x['sha256']
        if rid=='39329429383':
            b=json.loads(z.read('bucket-decomposition-s65.json'));analysis=json.loads(z.read('analysis-s65.json'));assert analysis['reference_tail_different_components']==0
            assert len(b['rows'])==5 and all(x['native_code_unique_elements']==1024 for x in b['rows'])
            assert [x['different_histogram_bucket_elements']for x in b['rows'][:3]]==[914,977,883]
            assert all(x['both_order_additive_identity_max_abs']==0 for x in b['rows'][:3]);checks['local_normalizer_only_explanation']=False
        else:
            n=json.loads(z.read('native-headroom-s66.json'));errors=[];roundtrip=[]
            for x in n['rows']:
                cast=bool(x['cast_is_LongGray_pointer']);h=x['input'];f=evaluate_helper(h,cast_is_long_gray=cast);b=evaluate_helper(h,cast_is_long_gray=cast,inverse=True)
                errors.extend([abs(f-x['forward']),abs(b-x['inverse_direct'])]);r=restore_recorded_headroom(f,cast_is_long_gray=cast,applied_branch=True)
                if h>0:roundtrip.append(abs(r-h)/h)
            assert len(n['rows'])==60 and max(errors)<=1e-5 and max(roundtrip)<=1e-3
            try:restore_recorded_headroom(2,cast_is_long_gray=True,applied_branch=None)
            except ValueError:pass
            else:raise AssertionError('Unknown photograph context must not be restored')
            checks.update({'native_scalar_comparisons':120,'VM_scalar_model_max_abs':max(errors),'VM_scalar_roundtrip_max_relative':max(roundtrip),'unknown_applied_context_rejected':True})
checks.update({'all_archive_members_verified':True,'no_pixel_GTMLTM_or_HDR_carrier_gate_pass_inferred':True,'A_phase_complete':False,'acceptance_complete':False});print(json.dumps(checks))
