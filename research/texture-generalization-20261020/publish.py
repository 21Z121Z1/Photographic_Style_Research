"""Preserve fresh native results; does not retrieve remote artifacts."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile


def main(evidence):
    head = os.environ['GITHUB_SHA']; run = os.environ['GITHUB_RUN_ID']
    repository = os.environ['GITHUB_REPOSITORY']
    output = Path(os.environ['RUNNER_TEMP']) / 'texture-matrix-publish'
    output.mkdir()
    matrix = evidence / 'matrix.json'
    if matrix.exists():
        data = json.loads(matrix.read_text()); assert data['source_head'] == head
        shutil.copyfile(matrix, output / 'matrix.json')
    archives = []
    for directory in sorted(evidence.iterdir()):
        if not directory.is_dir():
            continue
        entries = []
        target = output / (directory.name + '.zip')
        with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(directory.rglob('*')):
                if not path.is_file() or path.suffix not in {'.json','.txt','.log','.heic','.png','.l8','.bplist'}:
                    continue
                raw = path.read_bytes(); name = str(path.relative_to(directory))
                entries.append({'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
                archive.writestr(name,raw)
            archive.writestr('MANIFEST.json',json.dumps({'source_head':head,'run_id':run,'files':entries},indent=2)+'\n')
        assert target.stat().st_size < 95 * 1024 * 1024, 'split oversized evidence before preserving it'
        archives.append({'path':target.name,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    branch = 'research/texture-matrix-output-' + run
    (output / 'DELIVERY.json').write_text(json.dumps({'schema':'texture-matrix-delivery-v1','source_head':head,'run_id':run,'repository':repository,'branch':branch,'archives':archives,'device_results':'Only the earlier NASA candidate has a user-confirmed activation; these new outputs require device tests.'},indent=2)+'\n')
    (output / '.gitattributes').write_text('*.zip binary\n')
    subprocess.run(['git','switch','--orphan',branch],check=True)
    for path in output.iterdir():
        shutil.copyfile(path,Path.cwd()/path.name)
    subprocess.run(['git','add','--sparse','.gitattributes','DELIVERY.json',*[p.name for p in output.iterdir() if p.suffix in {'.zip'} or p.name=='matrix.json']],check=True)
    subprocess.run(['git','-c','user.name=github-actions[bot]','-c','user.email=41898282+github-actions[bot]@users.noreply.github.com','commit','-m','Preserve native fixture matrix '+run],check=True)
    subprocess.run(['git','-c','credential.helper=','-c','credential.helper=!gh auth git-credential','push','origin','HEAD:refs/heads/'+branch],check=True)
    print(json.dumps({'results_branch':branch,'source_head':head,'archives':len(archives)}))


if __name__ == '__main__':
    main(Path(sys.argv[1]))
