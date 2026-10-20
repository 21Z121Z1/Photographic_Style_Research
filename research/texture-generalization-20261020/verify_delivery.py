"""Offline integrity and native-data checks for preserved fixture results."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile

from validate_case import validate


def verify(root):
    delivery=json.loads((root/'DELIVERY.json').read_text())
    matrix=json.loads((root/'matrix.json').read_text())
    head=delivery['source_head'];run=delivery['run_id']
    assert matrix['source_head']==head and matrix['all_cases_passed']
    archives={a['path']:a for a in delivery['archives']}
    checked_files=0;checked_cases=0
    for name,entry in archives.items():
        path=root/name;raw=path.read_bytes()
        assert len(raw)==entry['bytes'] and hashlib.sha256(raw).hexdigest()==entry['sha256'],name
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None,name
            manifest=json.loads(archive.read('MANIFEST.json'))
            assert manifest['source_head']==head and manifest['run_id']==run
            listed={r['path'] for r in manifest['files']}
            assert len(listed)==len(manifest['files']) and set(archive.namelist())==listed|{'MANIFEST.json'}
            for row in manifest['files']:
                assert not Path(row['path']).is_absolute() and '..' not in Path(row['path']).parts
                raw=archive.read(row['path'])
                assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],name+':'+row['path']
                checked_files+=1
            if 'acceptance.json' in listed:
                case=name[:-4]
                receipt=json.loads(archive.read('acceptance.json'))
                assert receipt['source_head']==head and receipt['passed']
                row=next(r for r in matrix['rows'] if r['id']==case)
                assert row['passed'] and row['acceptance']==receipt
                with tempfile.TemporaryDirectory(prefix='texture-native-check-') as temp:
                    archive.extractall(temp)
                    assert validate(Path(temp),head)==receipt,case
                checked_cases+=1
    assert checked_cases==matrix['case_count']
    bundle=delivery['import_bundle'];path=root/bundle['path'];raw=path.read_bytes()
    assert len(raw)==bundle['bytes'] and hashlib.sha256(raw).hexdigest()==bundle['sha256']
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        files=json.loads(archive.read('FILES.json'))
        assert files['source_head']==head and files['run_id']==run
        assert files['all_matrix_cases_passed'] and files['matrix_case_count']==checked_cases
        assert len(files['cases'])==bundle['candidate_count']
        for name,entry in files['files'].items():
            raw=archive.read(name)
            assert len(raw)==entry['bytes'] and hashlib.sha256(raw).hexdigest()==entry['sha256'],name
        for line in archive.read('SHA256SUMS.txt').decode().splitlines():
            digest,name=line.split('  ',1)
            assert hashlib.sha256(archive.read(name)).hexdigest()==digest,name
        for case in files['cases']:
            raw=archive.read(case['candidate'])
            assert hashlib.sha256(raw).hexdigest()==case['sha256']
            native=next(r for r in matrix['rows'] if r['id']==case['id'])['acceptance']
            assert native['files']['texture-candidate.heic']['sha256']==case['sha256']
    return {'schema':'texture-fixture-offline-verification-v1','source_head':head,'run_id':run,
            'native_case_data_revalidated':checked_cases,'manifest_files_verified':checked_files,
            'import_candidates_verified':bundle['candidate_count'],'import_zip_sha256':bundle['sha256'],
            'scope':'integrity and recorded native-data consistency; this does not execute Apple frameworks or test Photos UI'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('results',type=Path);args=parser.parse_args()
    print(json.dumps(verify(args.results),indent=2))
