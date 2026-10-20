"""Verify an existing encrypted artifact beside its archive; never export its body.

The only HK-bound ciphertext is a bounded OpenPGP header. An archive-specific
session key returns on SSH stdin and reaches GPG through an anonymous pipe.
Neither that key nor decrypted tar members are written to disk or logged.
Historical remote_artifact_store.py is deliberately left unchanged.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import resource
import subprocess
import sys
import tarfile
import tempfile
import threading
import zipfile

ROOT = Path.home() / 'work/styles-gtm-ltm'
HEADER_LIMIT = 32768


def require(condition):
    if not condition:
        raise ValueError('verification contract failed')


def archive_path(relative):
    p = (ROOT / relative).resolve()
    require(ROOT.resolve() in p.parents and p.is_file())
    return p


def member_name(name):
    require(Path(name).name == name and name.endswith('.gpg'))
    return name


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def header(relative, name):
    with zipfile.ZipFile(archive_path(relative)) as z:
        require(z.namelist().count(member_name(name)) == 1)
        with z.open(name) as f:
            raw = f.read(HEADER_LIMIT)
        require(len(raw) > 0)
        sys.stdout.buffer.write(raw)


def verify_private(plan):
    # Limits apply to this helper and its GPG child, not to other JP services.
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_AS, (400 * 1024**2, 400 * 1024**2))
    p = archive_path(plan['relative_path'])
    require(p.stat().st_size == plan['ZIP_bytes'])
    require(sha(p) == plan['ZIP_sha256'])
    name = member_name(plan['cipher_member'])
    key = plan.pop('session_key')
    require(re.fullmatch(r'[0-9]+(?:\.[0-9]+)?:[0-9A-Fa-f]{32,128}', key) is not None)
    require(re.fullmatch(r'[0-9a-f]{40}', plan['source_commit']) is not None)
    actual = {}
    pm = None
    events = []
    failures = []
    cipher_hash = hashlib.sha256()
    cipher_size = [0]
    total = 0
    with zipfile.ZipFile(p) as z, tempfile.TemporaryDirectory(prefix='semantic-gpg-') as home:
        os.chmod(home, 0o700)
        require(z.namelist().count(name) == 1)
        require(z.getinfo(name).file_size == plan['cipher_bytes'])
        rd, wr = os.pipe()
        try:
            os.write(wr, (key + '\n').encode('ascii'))
        finally:
            os.close(wr)
        del key
        try:
            gpg = subprocess.Popen(
                ['gpg', '--no-options', '--homedir', home, '--batch', '--no-tty',
                 '--no-autostart', '--status-fd', '2',
                 '--override-session-key-fd', str(rd), '--decrypt'],
                pass_fds=(rd,), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        finally:
            os.close(rd)

        def write_cipher():
            try:
                with z.open(name) as f:
                    while block := f.read(65536):
                        cipher_hash.update(block)
                        cipher_size[0] += len(block)
                        gpg.stdin.write(block)
                gpg.stdin.close()
            except BaseException as exc:
                failures.append(type(exc).__name__)

        def statuses():
            # Never retain raw GPG text: only fixed event names, no filenames/keys.
            for line in iter(gpg.stderr.readline, b''):
                if line.startswith(b'[GNUPG:] '):
                    event = line.split()[1].decode('ascii', 'replace')
                    if len(events) < 1000:
                        events.append(event)

        writer = threading.Thread(target=write_cipher, daemon=True)
        reader = threading.Thread(target=statuses, daemon=True)
        writer.start()
        reader.start()
        try:
            with tarfile.open(fileobj=gpg.stdout, mode='r|gz') as tar:
                for entry in tar:
                    if entry.isdir():
                        continue
                    require(entry.isfile() and entry.size < 600_000_000)
                    total += entry.size
                    require(total < 3_000_000_000 and len(actual) < 50_000)
                    n = Path(entry.name)
                    require(not n.is_absolute() and '..' not in n.parts and n.parts[0] == 'out')
                    relative = str(n.relative_to('out'))
                    require(relative not in actual)
                    digest = hashlib.sha256()
                    metadata = bytearray() if relative == 'manifest.json' else None
                    with tar.extractfile(entry) as f:
                        while block := f.read(65536):
                            digest.update(block)
                            if metadata is not None:
                                metadata.extend(block)
                                require(len(metadata) < 2_000_000)
                    actual[relative] = {'size': entry.size, 'sha256': digest.hexdigest()}
                    if metadata is not None:
                        pm = json.loads(metadata)
            # Consume gzip/tar tail before joining the cipher writer.
            while gpg.stdout.read(65536):
                pass
            writer.join(timeout=120)
            rc = gpg.wait(timeout=120)
            reader.join(timeout=120)
            require(rc == 0 and not failures and not writer.is_alive() and not reader.is_alive())
            require('DECRYPTION_OKAY' in events)
            require(not any(x in events for x in ('BADMDC', 'DECRYPTION_FAILED', 'ERROR', 'FAILURE')))
            require(cipher_size[0] == plan['cipher_bytes'])
            require(cipher_hash.hexdigest() == plan['cipher_sha256'])
            require(pm is not None and pm['run_id'] == str(plan['run_id']))
            require(pm['commit'] == plan['source_commit'] and pm['os_build'] == plan['os_build'])
            require(set(actual) == {'manifest.json', *(x['path'] for x in pm['files'])})
            require(len(pm['files']) == len({x['path'] for x in pm['files']}))
            for row in pm['files']:
                require(actual[row['path']] == {'size': row['size'], 'sha256': row['sha256']})
        finally:
            if gpg.poll() is None:
                gpg.kill()
            gpg.wait(timeout=30)
            writer.join(timeout=30)
            reader.join(timeout=30)
            for f in (gpg.stdin, gpg.stdout, gpg.stderr):
                try:
                    f.close()
                except BrokenPipeError:
                    pass

    return {
        'protocol': 'JP-local-GPG-v2', 'run_id': plan['run_id'],
        'source_commit': plan['source_commit'], 'os_build': pm['os_build'],
        'ZIP_bytes': p.stat().st_size, 'ZIP_sha256': plan['ZIP_sha256'],
        'cipher_member': name, 'cipher_bytes': cipher_size[0],
        'cipher_sha256': cipher_hash.hexdigest(), 'GPG_returncode': rc,
        'event_names_only': events, 'all_manifest_members_verified': len(pm['files']),
        'private_manifest_SHA256': actual['manifest.json']['sha256'],
        'member_hashes_only': actual,
        'images_decoded_or_written': False, 'private_key_received': False,
        'session_key_received_via_SSH_stdin_and_anonymous_fd': True,
        'session_key_saved_or_logged': False, 'plaintext_members_saved': False,
        'temporary_GNUPGHOME_removed': True, 'whole_cipher_or_ZIP_exported': False,
        'remote_max_RSS_KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'child_max_RSS_KiB': resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
    }


def main():
    if sys.argv[1] == 'header':
        require(len(sys.argv) == 4)
        header(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'verify-private':
        require(len(sys.argv) == 2)
        result = verify_private(json.load(sys.stdin))
        print(json.dumps(result, separators=(',', ':')))
    else:
        raise ValueError('unknown mode')


if __name__ == '__main__':
    try:
        main()
    except BaseException as exc:
        # Untrusted diagnostics must never echo an input plan or session key.
        print('remote-verification-failed: ' + type(exc).__name__, file=sys.stderr)
        sys.exit(1)
