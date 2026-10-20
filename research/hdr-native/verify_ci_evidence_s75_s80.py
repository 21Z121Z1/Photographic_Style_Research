"""Read-only integrity/record replay; no native or image computation on VM."""
from pathlib import Path
import argparse,hashlib,json,subprocess,zipfile

def digest(stream):
    h=hashlib.sha256()
    while b:=stream.read(1_048_576):h.update(b)
    return h.hexdigest()

def verify(archive_root):
    directory=Path(__file__).resolve().parent;repo=directory.parents[1]
    index=json.loads((directory/'evidence/s80/bundle-index.json').read_text());results=[]
    for row in index['archives']:
        path=Path(archive_root)/str(row['run_id'])/('artifact-'+str(row['artifact_id'])+'.zip')
        with path.open('rb')as f:assert digest(f)==row['ZIP_sha256'],path
        with zipfile.ZipFile(path)as z:
            names=z.namelist();assert len(names)==len(set(names))and all(not Path(n).is_absolute()and '..'not in Path(n).parts for n in names)
            raw=z.read('manifest.json');assert hashlib.sha256(raw).hexdigest()==row['manifest_sha256']
            manifest=json.loads(raw);assert manifest['commit']==row['source_commit']and manifest['run_id']==str(row['run_id'])and manifest['os_build']=='26A434'and manifest['no_photo_input']
            assert set(n for n in names if not n.endswith('/'))=={'manifest.json',*(r['path']for r in manifest['files'])}
            for member in manifest['files']:
                assert z.getinfo(member['path']).file_size==member['size']
                with z.open(member['path'])as f:assert digest(f)==member['sha256'],member['path']
            recipe=json.loads(z.read('recipe.json'))
            for source,expected in recipe['source_sha256'].items():
                raw=subprocess.check_output(['git','show',row['source_commit']+':'+source],cwd=repo)
                assert hashlib.sha256(raw).hexdigest()==expected,source
        results.append({'stage':row['stage'],'run_id':row['run_id'],'artifact_id':row['artifact_id'],'payload_SHA_verified':len(manifest['files']),'ZIP_sha256':row['ZIP_sha256']})
    analysis=json.loads((directory/'evidence/s80/run/analysis.json').read_text())
    assert analysis['finite_synthetic_CI_capture_gate']and analysis['cases_completed']==6
    assert analysis['all_AA_original_half_exact']and analysis['all_AA_float_original_gate']and analysis['geometry_readback_ABI_complete']
    assert analysis['A_phase_complete']is False and analysis['acceptance_complete']is False
    return {'archives':results,'total_payload_SHA_verified':sum(r['payload_SHA_verified']for r in results),'native_S80_finite_capture_only':True,'native_S80_cases':6,'A_phase_complete':False,'acceptance_complete':False,'no_new_numerical_or_native_experiment':True}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('archive_root',type=Path);args=parser.parse_args()
    print(json.dumps(verify(args.archive_root),indent=2))
