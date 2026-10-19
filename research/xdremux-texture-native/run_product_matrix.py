#!/usr/bin/env python3
"""Exercise actual XDRemux product routes using only generated CC0 media."""
import hashlib
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys

repo, images, evidence, inspector = map(Path,sys.argv[1:])
sys.path.insert(0,str(repo))
from scripts.inspect_oppo_heif import inspect as inspect_file, boxes, payload_for_item

evidence.mkdir(parents=True,exist_ok=True)
cli = repo/'target/debug/xdremux'
fixture = repo/'target/debug/examples/texture_synthetic_uhdr'
rows=[]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def call(args,label,timeout=180):
    try:
        p=subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=timeout)
        code,stdout,stderr=p.returncode,p.stdout,p.stderr
    except subprocess.TimeoutExpired:
        code,stdout,stderr=124,'','process timed out'
    (evidence/(label+'.log')).write_text(stdout+stderr)
    print('PRODUCT_CALL',label,'exit_code='+str(code),flush=True)
    if stdout:print(stdout,flush=True)
    if stderr:print(stderr,flush=True)
    return code

for name in ['landscape-gradient','portrait-checker','landscape-hdr-edge','portrait-hdr-impulse']:
    source=images/(name+'-synthetic-uhdr.heic')
    out=images/(name+'-converted.heic')
    row={'case':name,'source_provenance':'generated CC0 image with synthetic ProXDR metadata, no camera context','texture_activation':'unverified'}
    code=call([fixture,images/(name+'-sdr.heic'),images/(name+'-sdr.jpg'),source],name+'-source')
    row['source_generation_exit']=code
    if code==0:
        row['source_sha256']=sha(source)
        code=call([cli,'convert','--input',source,'--output',out,'--apple-styles'],name+'-convert')
        row['convert_exit']=code
        if code==0:
            data=out.read_bytes();report=inspect_file(out)
            row['output_sha256']=sha(out)
            items=[r for r in report['items'] if r.get('type')=='uri ' and r.get('name')=='styleMetadata']
            assert len(items)==1,'expected one v15 Photographic Styles metadata item'
            meta=next(b for b in boxes(data,0,len(data)) if b['type']=='meta')
            idat=next(b for b in boxes(data,meta['payload_start']+4,meta['end']) if b['type']=='idat')
            properties=plistlib.loads(payload_for_item(data,items[0]['location'],idat))
            assert properties['0']==15 and 'l' not in properties
            assert b'tag:apple.com,2026:photo:metadata:texture_styles\0' not in data
            assert b'tag:apple.com,2026:photo:aux:' not in data
            row['photographic_styles_version']=properties['0']
            row['texture_metadata_generated']=False
            row['native_readback_exit']=call([inspector,'--inspect',out,evidence/(name+'-native-facts.json')],name+'-native-readback')
            row['validation_exit']=call([cli,'validate',out],name+'-validate')
            batch=images/(name+'-batch');batch.mkdir()
            row['batch_exit']=call([cli,'batch','--input',source,'--output-dir',batch,'--apple-styles','--jobs','1','--json'],name+'-batch')
            if row['batch_exit']==0:
                files=list(batch.glob('*.heic'))
                assert len(files)==1, 'expected an actual batch output'
                batch_data=files[0].read_bytes()
                assert b'tag:apple.com,2026:photo:metadata:texture_styles\0' not in batch_data
                row['batch_output_sha256']=sha(files[0])
                row['batch_native_readback_exit']=call([inspector,'--inspect',files[0],evidence/(name+'-batch-native-facts.json')],name+'-batch-native-readback')
    rows.append(row)
    (evidence/'product-matrix.json').write_text(json.dumps({'xdremux_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),'scope':'ordinary Styles functional regression only; never Texture activation','photos_used':False,'rows':rows},indent=2)+'\n')
print('TEXTURE_JSON_BEGIN product-matrix.json',flush=True)
print((evidence/'product-matrix.json').read_text(),end='',flush=True)
print('TEXTURE_JSON_END product-matrix.json',flush=True)
if any(r.get('convert_exit',1) or r.get('batch_exit',1) or r.get('native_readback_exit',1) or r.get('validation_exit',1) for r in rows):
    sys.exit('PRODUCT_NATIVE_CONTEXT_UNSUPPORTED_OR_FAILED: inspect per-operation evidence')
