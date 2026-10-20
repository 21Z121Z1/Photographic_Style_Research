"""Preserve fresh native results; does not retrieve remote artifacts."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile


def make_import_bundle(evidence,output,matrix,run):
    if matrix.get('phase')!='generate' or not matrix.get('all_cases_passed'):
        return None
    files={};cases=[]
    guide='''# XDRemux 真实样张 Texture 导入测试

将 originals/ 中的 HEIC 原件导入此前成功激活的同一台设备。controls/ 是同一编码主图的普通对照，previews/ 仅为逐人原生效果烘焙图。derived/ 是明确标识的双人拼接及尺寸压力用例。

建议先测 Samsung JPEG 人像、vivo 店内多人场景、OPPO portrait-02、OPPO hr-01 无人像，以及 derived/derived-two-fixture-faces.heic。随后批量测试 originals/。

每张输出均为新建的 SDR 编辑副本，默认长边 1024；derived/ 的尺寸变体另标 512/2048。原照片 HDR 和动态视频没有带入该副本。不要把 previews/ 当作可编辑候选。

记录是否激活、纹理/颗粒与柔肤控件是否产生变化，以及修改保存后重新打开是否保留。小脸或无人物区域可能没有某项人物效果，逐图真实原生输出见 receipts/ 和 FILES.json。

本包是新的 fixture 输出，尚无设备激活反馈。此前用户已确认的 NASA 候选 SHA 为 a7ac5d0dc8721e0cac4db6bfec153864f96fc83f406adeedc2036bc6f0543a7b；它的结果不自动适用于这些新文件。
'''
    files['README.zh-CN.md']=guide.encode()
    for row in matrix['rows']:
        if not row.get('passed') or row.get('kind') not in {'original_fixture','derived_two_input_stress','resolution_variant'}:
            continue
        directory=evidence/row['id'];receipt=json.loads((directory/'acceptance.json').read_text())
        assert receipt['source_head']==matrix['source_head'] and receipt['passed']
        folder='originals' if row['kind']=='original_fixture' else 'derived'
        for original,target in [('texture-candidate.heic',folder+'/'+row['id']+'.heic'),('control.heic','controls/'+row['id']+'.heic')]:
            raw=(directory/original).read_bytes();expected=receipt['files'][original]
            assert len(raw)==expected['bytes'] and hashlib.sha256(raw).hexdigest()==expected['sha256']
            files[target]=raw
        files['receipts/'+row['id']+'.json']=(directory/'acceptance.json').read_bytes()
        for index in range(receipt['stored_person_count']):
            preview=directory/('person-'+str(index))/'final-file-mattify-preview.heic'
            files['previews/'+row['id']+'__person-'+str(index)+'.heic']=preview.read_bytes()
        cases.append({'id':row['id'],'kind':row['kind'],'fixture':row.get('fixture'),
                      'candidate':folder+'/'+row['id']+'.heic','sha256':receipt['files']['texture-candidate.heic']['sha256'],
                      'dimensions':receipt['dimensions'],'stored_people':receipt['stored_person_count'],
                      'native_effect_outcomes':receipt['native_effect_outcomes']})
    manifest={'schema':'texture-fixture-import-package-v1','source_head':matrix['source_head'],'run_id':run,
              'fixture_head':matrix['fixture_head'],'all_matrix_cases_passed':True,'matrix_case_count':matrix['case_count'],
              'device_activation_for_new_candidates':'not tested','cases':cases,
              'files':{name:{'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()} for name,raw in files.items()}}
    files['FILES.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    files['SHA256SUMS.txt']=''.join(hashlib.sha256(raw).hexdigest()+'  '+name+'\n' for name,raw in sorted(files.items())).encode()
    target=output/('texture-fixture-imports-'+run+'.zip')
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
        for name,raw in files.items():archive.writestr(name,raw)
    return {'path':target.name,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'candidate_count':len(cases)}


def main(evidence):
    head = os.environ['GITHUB_SHA']; run = os.environ['GITHUB_RUN_ID']
    repository = os.environ['GITHUB_REPOSITORY']
    output = Path(os.environ['RUNNER_TEMP']) / 'texture-matrix-publish'
    output.mkdir()
    matrix = evidence / 'matrix.json'
    data={}
    if matrix.exists():
        data = json.loads(matrix.read_text()); assert data['source_head'] == head
        shutil.copyfile(matrix, output / 'matrix.json')
    bundle=make_import_bundle(evidence,output,data,run)
    archives = []
    for directory in sorted(evidence.iterdir()):
        if not directory.is_dir():
            continue
        entries = []
        target = output / (directory.name + '.zip')
        with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(directory.rglob('*')):
                if not path.is_file() or path.suffix not in {'.json','.txt','.log','.heic','.png','.l8','.bplist','.tiff','.rgba32f'}:
                    continue
                raw = path.read_bytes(); name = str(path.relative_to(directory))
                entries.append({'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
                archive.writestr(name,raw)
            archive.writestr('MANIFEST.json',json.dumps({'source_head':head,'run_id':run,'files':entries},indent=2)+'\n')
        assert target.stat().st_size < 95 * 1024 * 1024, 'split oversized evidence before preserving it'
        archives.append({'path':target.name,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    branch = 'research/texture-matrix-output-' + run
    (output / 'DELIVERY.json').write_text(json.dumps({'schema':'texture-matrix-delivery-v1','source_head':head,'run_id':run,'repository':repository,'branch':branch,'archives':archives,'import_bundle':bundle,'device_results':'Only the earlier NASA candidate has a user-confirmed activation; these new outputs require device tests.'},indent=2)+'\n')
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
