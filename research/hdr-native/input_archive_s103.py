"""Runner-only authenticated reuse of S101 outputs; no Japan image backhaul."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import re
import shutil
import subprocess
import tarfile
import urllib.error
import urllib.request
import zipfile

API = 'https://api.github.com/repos/21Z121Z1/Photographic_Style_Research/actions/artifacts/12310032763'
ZIP_BYTES = 2081013365
ZIP_SHA = 'b26a2c7c006fc931d93e312b71d64ba556d18ec00f58919fb6d5c14548379908'
SOURCE_COMMIT = '90d565c7686cd45f55e1d1e4e5fd9b0f6af31ef7'
SOURCE_RUN = 39518274902

def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, newurl):
        return None

def download(scratch):
    token = os.environ['GH_TOKEN']
    headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
    with urllib.request.urlopen(urllib.request.Request(API, headers=headers), timeout=60) as r:
        metadata = json.load(r)
    assert not metadata['expired'] and metadata['size_in_bytes'] == ZIP_BYTES
    assert metadata['digest'] == 'sha256:' + ZIP_SHA
    assert ZIP_BYTES < 3_000_000_000 and shutil.disk_usage(scratch).free > 6_000_000_000
    opener = urllib.request.build_opener(NoRedirect)
    try:
        response = opener.open(urllib.request.Request(API + '/zip', headers=headers), timeout=60)
    except urllib.error.HTTPError as response:
        assert response.code == 302
        location = response.headers['Location']
    else:
        response.close()
        raise RuntimeError('Expected signed artifact redirect; no unbounded download attempted')
    assert location.startswith('https://')
    # Never forward a repository credential to the signed blob URL.
    path = scratch / 's101-original-provider.zip'
    count = 0
    digest = hashlib.sha256()
    with urllib.request.urlopen(location, timeout=180) as response, path.open('xb') as out:
        length = response.headers.get('Content-Length')
        assert length is None or int(length) == ZIP_BYTES
        while block := response.read(1024 * 1024):
            count += len(block)
            assert count <= ZIP_BYTES
            digest.update(block)
            out.write(block)
    assert count == ZIP_BYTES and digest.hexdigest() == ZIP_SHA
    return path, {'source_run_id': SOURCE_RUN, 'artifact_id': 12310032763, 'bytes': count, 'sha256': digest.hexdigest(), 'route': 'GitHub artifact directly to macOS runner once; no JP/HK image backhaul', 'expires_at_observed': metadata['expires_at']}

def decrypt_photo(archive, destination, photo, session, encrypted_record):
    """Hash all private members, retain only four needed inputs as scratch."""
    assert re.fullmatch(r'[0-9]+(?:\.[0-9]+)?:[0-9A-Fa-f]+', session)
    cipher = destination / 'input.tar.gz.gpg'
    with zipfile.ZipFile(archive) as z:
        members = [q for q in z.infolist() if q.filename == encrypted_record['file']]
        assert len(members) == 1
        member = members[0]
        assert member.file_size == encrypted_record['bytes']
        with z.open(member) as src, cipher.open('xb') as out:
            shutil.copyfileobj(src, out, length=1024 * 1024)
    assert cipher.stat().st_size == encrypted_record['bytes'] and sha(cipher) == encrypted_record['sha256']
    needed = {'independent-HDR.heic', 'independent-HDR-target.exr', 'carrier-meaning.json', 'target-EXR-readback.json'}
    read_fd, write_fd = os.pipe()
    os.write(write_fd, (session + '\n').encode())
    os.close(write_fd)
    process = subprocess.Popen(['gpg', '--batch', '--no-tty', '--status-fd', '2', '--override-session-key-fd', str(read_fd), '--decrypt', str(cipher)], pass_fds=(read_fd,), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    os.close(read_fd)
    seen = {}
    manifest = None
    manifest_digest = None
    total_plaintext_bytes = 0
    try:
        with tarfile.open(fileobj=process.stdout, mode='r|gz') as tar:
            for item in tar:
                parts = PurePosixPath(item.name).parts
                assert parts and parts[0] == 'out' and '..' not in parts and not item.issym() and not item.islnk()
                if item.isdir():
                    continue
                assert item.isfile() and item.size < 600_000_000
                total_plaintext_bytes += item.size
                assert total_plaintext_bytes < 3_000_000_000
                rel = str(PurePosixPath(*parts[1:]))
                assert rel and rel not in seen
                src = tar.extractfile(item)
                digest = hashlib.sha256()
                size = 0
                out = (destination / rel).open('xb') if rel in needed else None
                collected = bytearray() if rel == 'manifest.json' else None
                try:
                    while block := src.read(1024 * 1024):
                        size += len(block)
                        digest.update(block)
                        if out is not None:
                            out.write(block)
                        if collected is not None:
                            assert len(collected) + len(block) < 100_000
                            collected.extend(block)
                finally:
                    if out is not None:
                        out.close()
                assert size == item.size
                seen[rel] = {'size': size, 'sha256': digest.hexdigest()}
                if collected is not None:
                    manifest = json.loads(collected)
                    manifest_digest = digest.hexdigest()
        # Consume the complete OpenPGP stream, including its authentication end.
        while process.stdout.read(1024 * 1024):
            pass
        process.stdout.close()
        status = process.stderr.read()
        process.stderr.close()
        rc = process.wait(timeout=180)
        events = re.findall(rb'^\[GNUPG:\] ([A-Z_]+)', status, flags=re.MULTILINE)
        assert rc == 0 and b'DECRYPTION_OKAY' in events and b'END_DECRYPTION' in events
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        cipher.unlink()
    assert manifest_digest == encrypted_record['private_manifest_SHA256']
    assert manifest['run_id'] == str(SOURCE_RUN) and manifest['commit'] == SOURCE_COMMIT and manifest['os_build'] == '26A434'
    expected = {q['path']: {'size': q['size'], 'sha256': q['sha256']} for q in manifest['files']}
    assert len(expected) == encrypted_record['member_files'] == 23
    assert {k: v for k, v in seen.items() if k != 'manifest.json'} == expected
    assert needed.issubset(expected)
    return {'photo': photo, 'cipher_sha256': encrypted_record['sha256'], 'authenticated_members': len(expected), 'manifest_sha256': manifest_digest, 'GPG_returncode': rc, 'GPG_event_names_only': sorted(set(x.decode() for x in events)), 'retained_scratch_members': sorted(needed), 'new_image_archive': False}
