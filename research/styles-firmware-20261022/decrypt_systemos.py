"""Decrypt only a completed, manifest-matched owned SystemOS component.

Public FCS material is passed via a private local JSON, never printed/copied to
evidence. This does not mount, install, execute or automatically redownload it.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess

from download_component import select_component
from extract_downloaded import sha_file


def decrypt(scratch: Path, metadata: Path, key_database: Path, output: Path) -> dict:
    download=json.loads((scratch/'download.json').read_text());manifest=json.loads(metadata.read_text())
    entry=select_component(manifest,'Cryptex1,SystemOS','Customer Erase Install (IPSW)')
    if (not download['completed'] or not download['zip_crc_verified'] or download['entry']!=entry
            or download['source_url']!=manifest['source_url']
            or download['build_manifest_sha256']!=manifest['build_manifest_sha256']):
        raise ValueError('Completed exact manifest component identity required')
    source=scratch/entry['name']
    if source.stat().st_size!=entry['compressed_bytes'] or sha_file(source)!=download['sha256']:
        raise ValueError('Source component changed')
    if output.exists():raise FileExistsError(output)
    required=3*source.stat().st_size+4*1024**3
    free=shutil.disk_usage(scratch).free
    if free<required:raise ValueError('Insufficient bounded decryption reserve')
    output.mkdir()
    state={'hardware':manifest['supported_product_types'],'build':manifest['build'],'source_url':manifest['source_url'],
           'build_manifest_sha256':manifest['build_manifest_sha256'],'source_component':entry,
           'encrypted_sha256':download['sha256'],'free_before':free,'required_free':required,
           'completed':False,'mount_or_install_performed':False,'binary_or_FCS_uploaded':False}
    receipt=output/'decryption.json'
    try:
        with (output/'decrypt.private.log').open('xb') as f:
            process=subprocess.run(['ipsw','fw','aea',str(source),'--pem-db',str(key_database),'--output',str(output)],stdout=f,stderr=subprocess.STDOUT,timeout=900)
        if process.returncode:raise RuntimeError(f'Public AEA decrypt failed rc={process.returncode}; private log retained')
        images=list(output.glob('*.dmg'))
        if len(images)!=1:raise ValueError('Expected one decrypted DMG')
        image=images[0]
        if image.stat().st_size>3*source.stat().st_size:raise ValueError('Output exceeds recorded size allowance')
        state.update(decrypted_image=image.name,decrypted_bytes=image.stat().st_size,decrypted_sha256=sha_file(image),completed=True)
    except Exception as e:
        state['error']=str(e);raise
    finally:receipt.write_text(json.dumps(state,indent=2)+'\n')
    return state


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('scratch',type=Path);p.add_argument('metadata',type=Path);p.add_argument('key_database',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();r=decrypt(a.scratch,a.metadata,a.key_database,a.output)
    print(json.dumps({k:r[k] for k in ['completed','decrypted_bytes','decrypted_sha256']}))
