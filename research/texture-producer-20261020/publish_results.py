"""Preserve newly generated public research output on a separate Git branch.

This does not download an artifact or access a blocked storage endpoint.
The source branch is unchanged; the result branch is unique to this run.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


def command(*args):
    subprocess.run(args, check=True)


def main(evidence):
    root = Path.cwd(); repository = os.environ['GITHUB_REPOSITORY']; run = os.environ['GITHUB_RUN_ID']; head = os.environ['GITHUB_SHA']
    receipt = json.loads((evidence/'acceptance.json').read_text())
    manifest = json.loads((evidence/'manifest.json').read_text())
    assert receipt['source_head'] == manifest['head_sha'] == head
    assert receipt['cloud_production_and_final_file_replay_passed'] and not receipt['Photos_activation_proved']
    for row in manifest['files']:
        path = evidence/row['path']; raw = path.read_bytes()
        assert len(raw) == row['size'] and hashlib.sha256(raw).hexdigest() == row['sha256']
    branch = 'research/texture-output-' + run
    delivery = {'schema':'texture-import-delivery-v1','repository':repository,'source_head':head,'run_id':run,
                'workflow_url':f'https://github.com/{repository}/actions/runs/{run}','results_branch':branch,
                'Photos_activation_proved':False,'files':receipt['files']}
    guide = '''# 导入测试

请导入 `import/texture-candidate.heic`；`control.heic` 是同一编码主图的普通对照。
`final-file-mattify-preview.heic` 是效果烘焙预览，不是可编辑候选。

通过文件或 AirDrop 原件保存到照片。在支持相关功能的 iOS 27 设备上，检查候选是否出现摄影风格、纹理/颗粒、柔肤控制；比较对照，修改后保存并重新打开。

云端已验证三组真实 Apple SPI 统计、1 个人物实例、元数据回读，以及最终文件全部遮罩解码后的非零原生重放。Photos 激活尚未证明：运行器的平台支持标志、PhotographicStyleV2 capability 和编辑资格仍为 false。未将它们改为 true。

这是从公开 NASA 单人像新建的编辑上下文，不是原相机 RAW/拍摄信息恢复。鼻唇眉区域由本图人脸点派生，耳部和纹身的可选保护禁用；手部检测结果为零。通用多人物/无人像和更多方向、分辨率尚未认证。

文件 SHA、准确源码提交和工作流见 `DELIVERY.json` 与 `import/acceptance.json`；完整生成证据见 `evidence/`。
'''
    command('git','switch','--orphan',branch)
    (root/'.gitattributes').write_text('evidence/** -whitespace\n*.heic binary\n*.l8 binary\n*.bplist binary\n*.png binary\n')
    (root/'README.md').write_text(guide)
    (root/'DELIVERY.json').write_text(json.dumps(delivery,indent=2)+'\n')
    archive = root/'evidence'/('run'+run); archive.mkdir(parents=True)
    for row in manifest['files']:
        source = evidence/row['path']; destination = archive/row['path']; destination.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(source,destination)
    shutil.copyfile(evidence/'manifest.json',archive/'manifest.json')
    imports = root/'import'; imports.mkdir()
    for name in receipt['files']:
        shutil.copyfile(evidence/name,imports/name)
    for name in ['acceptance.json','final-working-input.png','final-working-mattify.png']:
        shutil.copyfile(evidence/name,imports/name)
    command('git','add','--sparse','.gitattributes','README.md','DELIVERY.json','import','evidence')
    command('git','-c','user.name=github-actions[bot]','-c','user.email=41898282+github-actions[bot]@users.noreply.github.com','commit','-m','Preserve native Texture production results for run '+run)
    command('git','-c','credential.helper=','-c','credential.helper=!gh auth git-credential','push','origin','HEAD:refs/heads/'+branch)
    print(json.dumps({'results_branch':branch,'source_head':head,'run_id':run}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('evidence',type=Path);main(parser.parse_args().evidence)
