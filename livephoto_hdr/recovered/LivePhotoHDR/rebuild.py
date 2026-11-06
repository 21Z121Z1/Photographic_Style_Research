#!/usr/bin/env python3
"""把配对实况照片文件夹重建为 HDR HLG PVT。成功验证后默认备份并替换原目录。"""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import uuid

ROOT=Path(__file__).resolve().parent
SRC=ROOT/'src'

def digest(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def write_json(path,data):
    tmp=path.with_name(path.name+'.tmp')
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    tmp.replace(path)

def discover(path):
    if path.is_symlink() or not path.is_dir():raise ValueError(f'需要实际文件夹路径: {path}')
    photos=sorted(p for p in path.iterdir()if p.is_file()and p.suffix.lower()in ['.heic','.heif'])
    movies=sorted(p for p in path.iterdir()if p.is_file()and p.suffix.lower()=='.mov')
    if len(photos)!=1 or len(movies)!=1:raise ValueError(f'{path}: 需要恰好一个 HEIC 和一个 MOV，发现 {len(photos)} / {len(movies)}')
    if any(p.is_symlink()for p in photos+movies):raise ValueError('媒体文件不能是符号链接')
    ids=json.loads(subprocess.check_output(['exiftool','-j','-ContentIdentifier',str(photos[0]),str(movies[0])],stderr=subprocess.DEVNULL))
    if not ids[0].get('ContentIdentifier')or ids[0]['ContentIdentifier']!=ids[1].get('ContentIdentifier'):
        raise ValueError(f'{path}: 照片和视频的配对 UUID 不一致')
    return photos[0],movies[0]

def ensure_native():
    binary=ROOT/'native'
    stamp=ROOT/'native-build.json'
    sha=digest(SRC/'native.m')
    if binary.exists()and stamp.exists():
        built=json.loads(stamp.read_text())
        if built.get('sourceSHA256')==sha and built.get('binarySHA256')==digest(binary):return binary
    command=['xcrun','clang','-O2','-fobjc-arc','-fblocks','-fmodules',
             '-fmodules-cache-path=/private/tmp/livephoto-hdr-modules','-Wno-deprecated-declarations']
    for framework in ['Foundation','AVFoundation','CoreMedia','CoreVideo','CoreImage','ImageIO','Metal','Vision','VideoToolbox']:
        command+=['-framework',framework]
    candidate=ROOT/('native-'+uuid.uuid4().hex)
    subprocess.run(command+[str(SRC/'native.m'),'-o',str(candidate)],check=True)
    candidate.replace(binary)
    write_json(stamp,dict(sourceSHA256=sha,binarySHA256=digest(binary)))
    return binary

def convert(folder,native,keep_originals=False):
    photo,movie=discover(folder)
    final=folder.with_name(folder.name+'.pvt')
    if final.exists():raise FileExistsError(f'已有目标，拒绝覆盖: {final}')
    if shutil.disk_usage(folder.parent).free<3*2**30:raise RuntimeError('至少需要 3 GiB 可用临时空间')
    run_id=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]
    work_root=folder.parent/'.LivePhotoHDR-work';work_root.mkdir(exist_ok=True)
    work=work_root/(folder.name+'-'+run_id);work.mkdir()
    sources={str(p):digest(p)for p in [photo,movie]}
    staged=folder.parent/('.'+folder.name+'.'+run_id+'.pvt')
    stages=[]
    def run(name,cmd):
        print(f'[{folder.name}] {name}',flush=True)
        command=list(map(str,cmd))
        with (work/(name+'.log')).open('w')as log:
            completed=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
        stages.append(dict(stage=name,command=command,status=completed.returncode))
        write_json(work/'stages.json',stages)
        if completed.returncode:
            tail='\n'.join((work/(name+'.log')).read_text(errors='replace').splitlines()[-16:])
            raise RuntimeError(f'{name} 失败。原件未替换。日志 {work/(name+".log")}\n{tail}')
    try:
        run('extract',[sys.executable,SRC/'extract.py',photo,work/'resources'])
        run('collect',[native,'collect',photo,movie,work/'collection',384])
        c=json.loads((work/'collection/collection.json').read_text())
        print(f'[{folder.name}] 路径 {c["reverseMode"]}，主视频 {len(c["frames"])} 帧，场景参考 {len(c["thumbnails"])} 帧',flush=True)
        run('fit',[sys.executable,SRC/'fit.py',work/'collection',work/'model',native])
        video=work/'hdr-hlg.mov'
        run('render',[native,'render',work/'collection',work/'model',movie,video])
        run('package',[sys.executable,SRC/'package.py',photo,movie,video,staged,work/'package.json'])
        run('audit',[native,'audit',staged/(photo.stem+'_dynamic.mov'),work/'audit',384])
        run('validate',[sys.executable,SRC/'validate.py',work/'collection',work/'model',video,work/'audit',work/'package.json',work/'validation.json'])
        validation=json.loads((work/'validation.json').read_text())
        if not validation['overallPass']:raise RuntimeError('最终验证未通过，原件未替换')
        if {str(p):digest(p)for p in [photo,movie]}!=sources:raise RuntimeError('输入在处理中发生变化，原件未替换')
        receipt=dict(schema='LivePhotoHDR-receipt-v1',inputDirectory=str(folder),output=str(final),
                     work=str(work),sources=sources,reverseMode=c['reverseMode'],
                     checks=validation['checks'],encodedAnchor=validation['encodedAnchor'],
                     sourceCodeHashes={p.name:digest(p)for p in [Path(__file__),*SRC.glob('*.py'),*SRC.glob('*.m')]},
                     backup=None,installed=False)
        write_json(work/'receipt.json',receipt)
        # Destination and input are rechecked immediately before the two local renames.
        # The original folder moves intact to a unique backup on the same volume.
        backup=None
        if final.exists():raise FileExistsError(f'处理期间目标出现，拒绝覆盖: {final}')
        if not keep_originals:
            backup_root=folder.parent/'.LivePhotoHDR-originals';backup_root.mkdir(exist_ok=True)
            backup=backup_root/(folder.name+'-'+run_id)
            if backup.exists():raise FileExistsError(str(backup))
            folder.rename(backup)
            if {str(folder/p.name):digest(backup/p.name)for p in [photo,movie]}!=sources:
                backup.rename(folder);raise RuntimeError('备份验证失败，已恢复原路径')
        try:
            if final.exists():raise FileExistsError(str(final))
            staged.rename(final)
        except BaseException:
            if backup is not None and not folder.exists():backup.rename(folder)
            raise
        receipt.update(backup=str(backup)if backup else None,installed=True,
                       outputSHA256={p.name:digest(p)for p in final.iterdir()if p.is_file()})
        write_json(work/'receipt.json',receipt)
        write_json(final.with_name(final.name+'.receipt.json'),receipt)
        print(f'完成: {final}\n原件备份: {backup or folder}\n报告: {work/"validation.json"}',flush=True)
        return receipt
    except BaseException as e:
        write_json(work/'failure.json',dict(input=str(folder),error=str(e),originalHashes=sources,stagedPackage=str(staged)))
        raise

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('folders',nargs='*',type=Path,help='一个或多个包含 HEIC 和 MOV 的文件夹')
    p.add_argument('--keep-originals',action='store_true',help='生成同名 .pvt，保留输入文件夹原路径')
    p.add_argument('--check',action='store_true',help='只检查配对和依赖，不转换或替换')
    args=p.parse_args()
    if not args.folders:
        args.folders=[Path(x)for x in shlex.split(input('输入或拖入实况文件夹路径，可输入多个，然后按回车:\n'))]
    if not args.folders:p.error('没有输入文件夹')
    for tool in ['exiftool','ffprobe','xcrun']:
        if not shutil.which(tool):p.error(f'缺少依赖: {tool}')
    for module in ['numpy','scipy']:
        try:__import__(module)
        except ImportError:p.error(f'缺少 Python 依赖: {module}。运行 {sys.executable} -m pip install numpy scipy')
    folders=[]
    for value in args.folders:
        folder=Path(os.path.abspath(value.expanduser()))
        if not folder.exists()and folder.with_name(folder.name+'.pvt').exists()and folder.with_name(folder.name+'.pvt.receipt.json').exists():
            final=folder.with_name(folder.name+'.pvt')
            receipt=json.loads(folder.with_name(folder.name+'.pvt.receipt.json').read_text())
            hashes=receipt.get('outputSHA256',{})
            if not receipt.get('installed')or not hashes or not all((final/n).is_file()and digest(final/n)==h for n,h in hashes.items()):
                p.error(f'已有 PVT 与验证收据不一致，拒绝跳过或覆盖: {final}')
            print(f'已完成且哈希一致，跳过: {final}');continue
        discover(folder);folders.append(folder)
    if args.check:
        for folder in folders:print(f'配对检查通过: {folder}')
        return
    if not folders:return
    with (ROOT/'.run.lock').open('a')as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:p.error('另一个 LivePhotoHDR 正在运行')
        native=ensure_native();failures=[]
        for folder in dict.fromkeys(folders):
            try:convert(folder,native,args.keep_originals)
            except Exception as e:
                failures.append((str(folder),str(e)));print(f'失败: {folder}\n{e}',file=sys.stderr,flush=True)
        if failures:raise SystemExit(1)

if __name__=='__main__':main()
