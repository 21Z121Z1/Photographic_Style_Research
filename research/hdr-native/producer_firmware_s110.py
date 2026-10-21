"""Static iOS producer extraction on macOS only; text outputs only.

Uses only the OS DMG entry from the reviewed Apple manifest. No iOS binary is
executed, no full IPSW is downloaded and no Apple binary/image is uploaded.
"""
from pathlib import Path
import hashlib
import json
import os
import plistlib
import re
import shutil
import struct
import subprocess
import sys
import time
import traceback
import urllib.request
import zlib

W=Path(os.environ['RUNNER_TEMP'])/'producer-firmware-s110'
O=Path(os.environ['RUNNER_TEMP'])/'producer-s110-text'
W.mkdir();O.mkdir(exist_ok=True)
D=Path(__file__).resolve().parent
metadata=json.loads((D/'evidence/s110/firmware-filesystems.json').read_text())
URL=metadata['firmware_URL'];total=metadata['IPSW_total_bytes_NOT_downloaded']
roles=metadata['all_filesystem_roles'][0]['components'];target=roles['OS']
entry=next(q for q in metadata['all_dmg_entries']if q['name']==target)
assert entry['method']==0 and entry['compressed_bytes']==7784628224
state={'stage':'S110 iOS actual producer static source','build':'24A446','reference_device':'iPhone12,1, not IMG2810 matching hardware','source_commit':os.environ['GITHUB_SHA'],'runner_build':subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip(),'image_version':os.environ.get('ImageVersion'),'selected_OS_entry':entry,'source_URL':URL,'whole_IPSW_downloaded':False,'received_range_body_bytes':0,'large_download_region':'Apple CDN to GitHub macOS runner only','Japan_HK_large_backhaul_bytes':0,'executed_iOS_binary':False,'Apple_binary_uploaded':False,'photo_inputs':0,'completed':False,'functions_or_pixels_not_inferred_from_names':True}
device=None
def save():
    (O/'status.json').write_text(json.dumps(state,indent=2)+'\n')
def run(args,name,timeout=300,check=True):
    path=O/name
    with path.open('w')as out:
        p=subprocess.run(args,stdout=out,stderr=subprocess.STDOUT,text=True,timeout=timeout)
    if path.stat().st_size>64*1024*1024:raise RuntimeError('Text output exceeded64MiB; no binary fallback')
    if check and p.returncode:raise RuntimeError(f'{args[0]} failed rc={p.returncode}; see {name}')
    return p.returncode
def response(start,n):
    req=urllib.request.Request(URL,headers={'Range':f'bytes={start}-{start+n-1}'})
    r=urllib.request.urlopen(req,timeout=60)
    if r.status!=206 or r.headers.get('Content-Range')!=f'bytes {start}-{start+n-1}/{total}':
        r.close();raise RuntimeError('Exact206 required; no full IPSW response accepted')
    return r
try:
    assert state['runner_build']=='26A434'
    state['disk_free_before_bytes']=shutil.disk_usage(W).free
    state['disk_required_bytes']=2*entry['compressed_bytes']+2*1024**3
    save()
    if state['disk_free_before_bytes']<state['disk_required_bytes']:
        state['stop_reason']='Insufficient runner disk for encrypted+decrypted OS and2GiB reserve; no DMG download'
        save();raise SystemExit(20)
    # Confirm the known decrypt/disassembly prerequisite before the large read.
    if not shutil.which('ipsw'):
        run(['brew','tap','blacktop/tap'],'brew-tap.log',180)
        run(['brew','trust','--formula','blacktop/tap/ipsw-frida'],'brew-trust.log',120,False)
        run(['brew','install','--formula','blacktop/tap/ipsw'],'brew-install.log',900)
    run(['ipsw','version'],'ipsw-version.txt')
    with response(entry['local_header_offset'],30)as r:header=r.read(31)
    assert len(header)==30 and header[:4]==b'PK\x03\x04'
    n,e=struct.unpack_from('<HH',header,26);offset=entry['local_header_offset']+30+n+e
    state['received_range_body_bytes']+=len(header)
    target_path=W/target;sha=hashlib.sha256();crc=0;retries=0;chunk=16*1024*1024
    with target_path.open('xb')as output:
        for start in range(0,entry['compressed_bytes'],chunk):
            count=min(chunk,entry['compressed_bytes']-start)
            for attempt in range(4):
                try:
                    data=bytearray()
                    with response(offset+start,count)as r:
                        while len(data)<count:
                            block=r.read(min(1024*1024,count-len(data)));assert block
                            data.extend(block);state['received_range_body_bytes']+=len(block)
                            if state['received_range_body_bytes']>entry['compressed_bytes']+256*1024*1024:raise RuntimeError('Network retry budget exceeded')
                        assert not r.read(1)
                    output.write(data);sha.update(data);crc=zlib.crc32(data,crc);break
                except Exception:
                    retries+=1
                    if attempt==3:raise
                    time.sleep(min(2**attempt,8))
            if start%(256*1024*1024)==0:state['downloaded_entry_bytes']=start+count;state['retry_count']=retries;save()
    assert f'{crc&0xffffffff:08x}'==entry['CRC32']
    state.update({'downloaded_entry_bytes':entry['compressed_bytes'],'encrypted_OS_SHA256':sha.hexdigest(),'ZIP_entry_CRC32_verified':True,'retry_count':retries});save()
    decrypt=W/'decrypted';decrypt.mkdir()
    # No brute force or key bypass. AEA key/decrypt failure stops this phase.
    run(['ipsw','fw','aea',str(target_path),'--output',str(decrypt)],'aea-decrypt.log',900)
    images=list(decrypt.glob('*.dmg'));assert len(images)==1,'Expected one decrypted OS DMG'
    state['decrypted_OS_bytes']=images[0].stat().st_size;save()
    mount=W/'mount';mount.mkdir()
    process=subprocess.run(['hdiutil','attach','-readonly','-nobrowse','-plist','-mountpoint',str(mount),str(images[0])],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=180)
    (O/'mount-stderr.txt').write_bytes(process.stderr)
    if process.returncode:raise RuntimeError('Read-only OS mount failed')
    attachment=plistlib.loads(process.stdout);(W/'mount.plist').write_bytes(process.stdout)
    devices=[q.get('dev-entry')for q in attachment.get('system-entities',[])if re.fullmatch(r'/dev/disk\d+',q.get('dev-entry',''))]
    assert len(devices)==1;device=devices[0]
    roots=[Path(q['mount-point'])for q in attachment['system-entities']if'mount-point'in q]
    assert mount in roots
    expected=mount/'System/Library/VideoProcessors/SmartStyleV1.bundle'
    state['actual_producer_bundle_exists']=expected.is_dir();state['VideoProcessors_children']=sorted(p.name for p in expected.parent.iterdir())if expected.parent.exists()else[];save()
    if not expected.is_dir():raise RuntimeError('Actual reference producer bundle absent from selected OS; no substitute module claimed')
    infos=[p for p in [expected/'Info.plist',expected/'Contents/Info.plist']if p.is_file()];assert len(infos)==1
    info=plistlib.loads(infos[0].read_bytes());name=info['CFBundleExecutable'];candidates=[expected/name,expected/'Contents/MacOS'/name];binary=next(p for p in candidates if p.is_file())
    with binary.open('rb')as f:binary_sha=hashlib.file_digest(f,'sha256').hexdigest()
    state['producer_executable']={'bundle':str(expected.relative_to(mount)),'name':name,'bytes':binary.stat().st_size,'SHA256':binary_sha,'CFBundleIdentifier':info.get('CFBundleIdentifier'),'CFBundleVersion':info.get('CFBundleVersion')};save()
    run(['xcrun','dwarfdump','--uuid',str(binary)],'producer-uuid.txt')
    run(['ipsw','macho','info','--loads','--objc','--objc-refs','--symbols','--strings',str(binary)],'producer-metadata.txt',300)
    run(['ipsw','macho','disass','--section','__TEXT.__text','--cache',str(W/'producer-symbols.a2s'),str(binary)],'producer-code.asm.txt',600)
    state['metallibs']=[]
    libraries=list(expected.rglob('*.metallib'))
    if libraries:
        deps=W/'pydeps'
        run([sys.executable,'-m','pip','install','--quiet','--only-binary=:all:','--no-deps','--target',str(deps),'llvmlite'],'llvm-wheel-install.log',180)
        sys.path.insert(0,str(deps));state['llvmlite_version']=__import__('llvmlite').__version__
    for libindex,lib in enumerate(libraries):
        data=lib.read_bytes();rec={'path':str(lib.relative_to(expected)),'bytes':len(data),'SHA256':hashlib.sha256(data).hexdigest(),'modules':[]};state['metallibs'].append(rec)
        for i,m in enumerate(re.finditer(b'\xde\xc0\x17\x0b',data)):
            start=m.start()
            if start+20>len(data):continue
            _,_,off,size,_=struct.unpack_from('<5I',data,start);raw=data[start+off:start+off+size]
            if raw[:4]!=b'BC\xc0\xde'or len(raw)!=size:continue
            module={'index':i,'payload_SHA256':hashlib.sha256(raw).hexdigest(),'payload_bytes':size};rec['modules'].append(module)
            try:
                bc=W/f'producer-{libindex}-{i:04d}.bc';bc.write_bytes(raw);out=O/f'producer-air-{libindex}-{i:04d}.ll'
                process=subprocess.run([sys.executable,str(D/'producer_air_text_s110.py'),str(deps),str(bc),str(out)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=45)
                bc.unlink();module['parse_returncode']=process.returncode
                if process.returncode:module['error']=process.stdout.decode(errors='replace')[:2000]
                if out.exists():module['text']=out.name;module['text_SHA256']=hashlib.sha256(out.read_bytes()).hexdigest()
            except Exception as error:module['error']=str(error)[:2000]
        save()
    for path in expected.rglob('*.plist'):
        try:
            obj=plistlib.loads(path.read_bytes());out=O/('plist-'+str(path.relative_to(expected)).replace('/','_')+'.txt');out.write_text(repr(obj)+'\n')
        except Exception:pass
    state['completed']=True;state['scope']='Static source only; no native consumer/photo validation or camera same-frame/scene claim';save()
except SystemExit:raise
except Exception as error:
    state['error']=str(error);(O/'failure.txt').write_text(traceback.format_exc());save();raise
finally:
    if device:
        process=subprocess.run(['hdiutil','detach',device],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
        (O/'detach.txt').write_bytes(process.stdout);state['owned_mount_detached']=process.returncode==0;save()
    # Every retained artifact is text; scratch DMGs/binaries remain outside O
    # and are removed by the workflow's always step, including failure.
    files=[]
    for path in sorted(O.iterdir()):
        if path.is_file():
            assert path.suffix in ['.txt','.json','.log','.ll']
            with path.open('rb')as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
            files.append({'file':path.name,'bytes':path.stat().st_size,'SHA256':digest})
    (O/'text-manifest.json').write_text(json.dumps(files,indent=2)+'\n')
