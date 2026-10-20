"""Readonly native-archive replay. VM: scripts/local-python-scope.sh -I -B ..."""
from pathlib import Path
import hashlib,json,runpy,sys,zipfile

def validate(path):
    with zipfile.ZipFile(path)as z:
        manifest=json.loads(z.read('manifest.json'))
        assert manifest['os_build']=='26A434' and manifest['no_photo_input']
        for f in manifest['files']:
            b=z.read(f['path']);assert len(b)==f['size']and hashlib.sha256(b).hexdigest()==f['sha256']
        freeze=json.loads(z.read('freeze.json'));native=json.loads(z.read('native.json'));analysis=json.loads(z.read('analysis.json'))
    assert native['completed']and native['PhotoImaging']['UUID']=='5F17E1DB-A15E-38C7-9BEC-E081688B62E5'
    assert native['ROI_IMP_unslid']=='0x1cbef066c'and native['extent_getter']['selector']=='CGRectValue'
    assert len(native['rows'])==len(freeze['expected'])==54
    assert all(x['indirect_pointer_decoded']and x['target_symbol']['exact_address']==1 and x['target_symbol']['image_UUID']=='5E0B3F6B-554E-3373-A411-4A4D1CF0A057'for x in native['C_callsite_bindings'])
    model=runpy.run_path(str(Path(__file__).with_name('consumer_roi_s73.py')))['requested_roi']
    cases={c['id']:c for c in freeze['cases']};rows=[]
    for a,b in zip(native['rows'],freeze['expected'],strict=True):
        assert all(a[k]==b[k]for k in ['case','input_index','useLightMap'])
        c=cases[a['case']];expected=model(a['input_index'],c['extents'],c['output'])
        frozen_error=max(abs(x-y)for x,y in zip(a['native_ROI'],b['reference_ROI'],strict=True))
        implementation_error=max(abs(x-y)for x,y in zip(a['native_ROI'],expected,strict=True))
        rows.append({'case':a['case'],'input_index':a['input_index'],'useLightMap':a['useLightMap'],'frozen_max_abs':frozen_error,'implementation_max_abs':implementation_error})
    maximum=max(r['frozen_max_abs']for r in rows);current=max(r['implementation_max_abs']for r in rows)
    assert maximum==analysis['max_abs']and maximum<=freeze['CPU_ROI_max_abs_gate']and current<=freeze['CPU_ROI_max_abs_gate']
    return {'run_id':manifest['run_id'],'source_commit':manifest['commit'],'os_build':manifest['os_build'],'image_version':manifest.get('image_version'),'ZIP_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'all_original_members_SHA_verified':True,'cases':54,'double_components':216,'native_vs_pre_frozen_max_abs':maximum,'post_native_implementation_max_abs':current,'CPU_geometry_gate':freeze['CPU_ROI_max_abs_gate'],'implementation_post_native_not_new_holdout':True,'rows':rows,'actual_CI_allocated_regions_or_sampling_certified':False,'full_33_point_C01_C05_certified':False,'A_phase_complete':False,'acceptance_complete':False}
if __name__=='__main__':print(json.dumps(validate(Path(sys.argv[1])),indent=2,allow_nan=False))
