"""Reconstruct a paired Smart Style v16 Live Photo using this Mac's native resources.

Usage: python3 run.py PHOTO.HEIC PHOTO.MOV NEW_WORK_DIRECTORY NEW_PACKAGE.pvt
Requires macOS/Apple Silicon, Xcode command-line tools, numpy/scipy, ffprobe,
and exiftool. Personal media stays on this machine.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent

def sha(path: Path) -> str:
    with path.open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for k in ['photo', 'movie', 'work', 'package']: p.add_argument(k, type=Path)
    args = p.parse_args()
    photo, movie = args.photo.resolve(strict=True), args.movie.resolve(strict=True)
    out, package = args.work.resolve(), args.package.resolve()
    if out.exists() or package.exists(): p.error('Both work directory and PVT destination must be new paths.')
    identifiers = json.loads(subprocess.check_output(['exiftool','-j','-ContentIdentifier',str(photo),str(movie)]))
    if not identifiers[0].get('ContentIdentifier') or identifiers[0]['ContentIdentifier'] != identifiers[1].get('ContentIdentifier'):
        p.error('The HEIC and MOV content identifiers must match.')
    original_hashes = {str(f):sha(f) for f in [photo,movie]}
    out.mkdir(); stages=[]
    def run(name, command):
        command = [str(v) for v in command]
        print(f'{name} ...', flush=True)
        with (out / f'{name}.log').open('w') as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
        stages.append(dict(stage=name, command=command, status=result.returncode))
        (out/'stages.json').write_text(json.dumps(stages,indent=2)+'\n')
        if result.returncode: raise RuntimeError(f'{name} failed; inspect {out/name}.log')
    native = out/'native'
    framework_names = ['Foundation','AVFoundation','CoreMedia','CoreVideo','CoreImage','ImageIO','Metal','Vision','VideoToolbox']
    command=['xcrun','clang','-O2','-fobjc-arc','-fblocks','-fmodules',
             '-fmodules-cache-path=/private/tmp/independent-style-modules','-Wno-deprecated-declarations']
    for framework in framework_names: command += ['-framework',framework]
    run('build',command+[SRC/'native.m','-o',native])
    collection, model = out/'collection', out/'model'
    video = out/'dynamic-hlg.mov'
    run('collect',[native,'collect',photo,movie,collection,384])
    run('fit',[sys.executable,SRC/'fit.py',collection,model,native])
    run('render',[native,'render',collection,model,movie,video])
    run('package',[sys.executable,SRC/'package.py',photo,movie,video,package,out/'package.json'])
    final_movie=package/f'{photo.stem}_dynamic.mov'
    run('audit',[native,'audit',final_movie,out/'audit',384])
    run('validate',[sys.executable,SRC/'validate.py',collection,model,video,out/'audit',out/'package.json',out/'validation.json'])
    assert {str(f):sha(f) for f in [photo,movie]} == original_hashes
    manifest=dict(sources=original_hashes, package=str(package), work=str(out),
                  code={f.name:sha(f) for f in SRC.glob('*') if f.suffix in ['.py','.m']},
                  artifacts={f.name:sha(f) for f in package.iterdir()}, stages=stages)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Passed native, HDR look, HLG decode, timing and container checks: {package}',flush=True)

if __name__ == '__main__': main()
