"""Read-only replay of the S74 original native ZIP. Use local-python-scope.sh."""
from pathlib import Path
import hashlib,json,runpy,sys,zipfile

def validate(path):
    assert path.stat().st_size<1000000
    with zipfile.ZipFile(path)as z:
        manifest=json.loads(z.read('manifest.json'))
        assert manifest['os_build']=='26A434'and manifest['no_photo_input']
        assert set(z.namelist())=={'manifest.json',*(f['path']for f in manifest['files'])}
        for row in manifest['files']:
            assert Path(row['path']).name==row['path']and row['size']<240000
            raw=z.read(row['path'])
            assert len(raw)==row['size']and hashlib.sha256(raw).hexdigest()==row['sha256']
        recipe=json.loads(z.read('recipe.json'));freeze=json.loads(z.read('freeze.json'))
        meta=json.loads(z.read('metadata.json'));native=json.loads(z.read('native.json'));analysis=json.loads(z.read('analysis.json'))
        assert hashlib.sha256(z.read('recipe.json')).hexdigest()==freeze['recipe_sha256']
        assert hashlib.sha256(z.read('metadata.json')).hexdigest()==freeze['metadata_sha256']
    assert meta['primitive_calls']==0 and meta['completed']and native['completed']
    assert meta['metadata']==native['metadata']
    metadata=native['metadata']
    assert metadata['PhotoImaging']['UUID']=='5F17E1DB-A15E-38C7-9BEC-E081688B62E5'
    assert metadata['NeutrinoCore']['UUID']=='5E0B3F6B-554E-3373-A411-4A4D1CF0A057'
    assert metadata['PixelRect_size']==32 and metadata['PixelRect_alignment']==8 and metadata['policy']==0
    assert all(b['indirect_pointer_decoded']and b['target_symbol']['exact_address']==1 for name in['original_PI_C_imports','original_NC_CGRect_imports']for b in metadata[name])
    model_path=Path(__file__).with_name('consumer_pixelrect_s74.py');model=runpy.run_path(str(model_path))
    ca,cb=model['literal_values'](metadata)
    cases=freeze['cases'];assert len(cases)==len(native['rows'])==len(freeze['expected'])==54
    rows=[]
    for case,actual,frozen in zip(cases,native['rows'],freeze['expected'],strict=True):
        expected=model['reference_case'](case,ca,cb)
        assert case['id']==actual['case']==frozen['case']
        assert actual['integer_inputs_unchanged']
        assert expected==frozen
        integers=all(actual[k]==expected[k]for k in['from_pixel_rect','scaled_pixel_rect'])
        maximum=max(abs(a-b)for key in['from_CGRect','scaled_CGRect','flipped_CGRect']for a,b in zip(actual[key],expected[key],strict=True))
        rows.append({'case':actual['case'],'integer_exact':integers,'max_CGRect_abs':maximum})
    maximum=max(r['max_CGRect_abs']for r in rows)
    exact=all(r['integer_exact']for r in rows)
    assert maximum==analysis['max_CGRect_abs']and exact==analysis['integer_exact']
    assert exact and maximum<=recipe['finite_CGRect_gate']and analysis['gate_passed']and analysis['cases_SHA_unchanged']
    return{'run_id':manifest['run_id'],'source_commit':manifest['commit'],'os_build':manifest['os_build'],
           'image_version':manifest.get('image_version'),'ZIP_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
           'all_original_members_SHA_verified':True,'implementation_sha256':hashlib.sha256(model_path.read_bytes()).hexdigest(),
           'controls':54,'integer_fields_compared':432,'CGRect_fields_compared':648,'integer_exact':exact,
           'max_CGRect_abs':maximum,'finite_CGRect_gate':recipe['finite_CGRect_gate'],
           'original_literals':metadata['rounding_literals'],'original_getter':metadata['original_input_CGRect_getter']['selector'],
           'standalone_replay_not_new_holdout':True,'rows':rows,
           'actual_CI_allocated_regions_or_sampling_certified':False,'full_33_point_C01_C05_certified':False,
           'A_phase_complete':False,'acceptance_complete':False}
if __name__=='__main__':print(json.dumps(validate(Path(sys.argv[1])),indent=2,allow_nan=False))
