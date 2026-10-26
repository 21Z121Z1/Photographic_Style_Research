"""Read arithmetic metadata from the exact current native UnderEye AIR payload.

Bitcode and full shader text stay in a temporary directory on the runner. Only
the selected arithmetic SSA records and source identities leave that directory.
"""
from pathlib import Path
import hashlib
import re
import shutil
import subprocess
import tempfile

from air_alpha import canonicalize
from air_compare import payloads
from native_texture_reference import LIBRARY_SHA256

NAME = 'CMITextureStylesUnderEyeBrighten::FinalMix'


def collect_recipe() -> dict:
    path = Path('/System/Library/PrivateFrameworks/CMImaging.framework/Resources/default.metallib')
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != LIBRARY_SHA256:
        raise ValueError('Exact current metallib identity required')
    matches = [(i,offset,raw) for i,offset,raw in payloads(data) if NAME.encode() in raw]
    if len(matches) != 1:
        raise ValueError('Unique current UnderEye module required')
    compiler = next((str(p) for p in (shutil.which('llvm-dis'),
                     '/opt/homebrew/opt/llvm/bin/llvm-dis','/opt/homebrew/opt/llvm@20/bin/llvm-dis')
                     if p and Path(p).is_file()),None)
    if compiler is None:
        raise FileNotFoundError('No installed llvm-dis; no automatic package installation')
    index,offset,raw = matches[0]
    with tempfile.TemporaryDirectory(prefix='psr-under-eye-recipe-') as folder:
        bitcode=Path(folder)/'module.bc';bitcode.write_bytes(raw)
        text=subprocess.check_output([compiler,str(bitcode),'-o','-'],text=True,timeout=60)
    body=re.search(r'^define [^\n]*'+re.escape(NAME)+r'[^\n]*\n(.*?)^}',text,re.M|re.S)
    if not body:
        raise ValueError('Current named kernel body missing')
    records=[]
    for line in body[1].splitlines():
        line=line.split(';',1)[0].strip()
        match=re.match(r'(%[\w.]+) = (.+)',line)
        if not match:continue
        ssa,instruction=match.groups()
        if re.match(r'(?:fadd|fsub|fmul|fdiv|fptrunc|fpext|extractelement)\b',instruction):
            operation=instruction.split()[0]
        elif re.search(r'@(?:air|llvm)\.[\w.]*(?:mix|clamp|fma|saturate)[\w.]*\(',instruction):
            operation=re.search(r'@([\w.]+)\(',instruction)[1]
        else:continue
        records.append({'ssa':ssa,'operation':operation,'typed_operands':instruction})
    canonical,provenance=canonicalize(text)
    return {'source_metallib_sha256':LIBRARY_SHA256,'function':NAME,'module_index':index,
            'wrapper_offset':offset,'payload_sha256':hashlib.sha256(raw).hexdigest(),
            'canonical_module_sha256':hashlib.sha256(canonical.encode()).hexdigest(),
            'provenance':provenance,'llvm_dis_sha256':hashlib.sha256(Path(compiler).resolve().read_bytes()).hexdigest(),
            'llvm_dis_version':subprocess.check_output([compiler,'--version'],text=True).splitlines()[0],
            'arithmetic_records':records,'full_shader_or_binary_exported':False,'native_calls':0}
