"""Bounded HK coordinator for JP-local authenticated archive verification.

No image decode, whole artifact download, private-key export or key log.
Run through scripts/local-python-scope.sh on the HK VM.
"""
from pathlib import Path
import datetime
import hashlib
import json
import re
import resource
import shlex
import subprocess
import sys

R = Path('/home/Z121Z121/work/styles-gtm-ltm')
O = R / 'hdr-native-20261019'
W = Path(__file__).resolve().parent
CONFIG = json.loads((O / 'storage-jp-20261021.json').read_text())
REMOTE = '/home/Z121Z121/work/styles-gtm-ltm/tools/remote_artifact_store_v2.py'
SSH = ['ssh', *[v for x in CONFIG['ssh_options'] for v in ('-o', x)], CONFIG['ssh_destination']]


def remote(args, payload=None):
    return subprocess.run(
        SSH + [shlex.join(args)], input=payload, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, timeout=900, check=True).stdout


def install_helper():
    raw = (W / 'remote_artifact_store_v2.py').read_bytes()
    expected = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
    probe_code = (
        "from pathlib import Path;import hashlib,json;"
        f"p=Path({REMOTE!r});"
        "print(json.dumps(None if not p.exists() else "
        "{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}))"
    )
    existing = remote(['python3', '-c', probe_code])
    installed = json.loads(existing)
    if installed is not None:
        assert installed == expected
        return installed, 0, len(existing)
    code = (
        "from pathlib import Path;import hashlib,json,os,sys;"
        f"p=Path({REMOTE!r});b=sys.stdin.buffer.read();"
        "assert len(b)<100000;"
        "os.umask(0o077);"
        "assert not p.exists() or p.read_bytes()==b;"
        "f=None if p.exists() else p.open('xb');"
        "None if f is None else (f.write(b),f.flush(),os.fsync(f.fileno()),f.close());"
        "print(json.dumps({'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}))"
    )
    reply = remote(['python3', '-c', code], raw)
    receipt = json.loads(reply)
    assert receipt == expected
    return receipt, len(raw), len(existing) + len(reply)


def bounded_gpg_prefix(prefix):
    """Reframe only a truncated encrypted packet's length for key extraction.

    GPG otherwise buffers a complete OpenPGP partial-length chunk before emitting
    SESSION_KEY. Preserve all complete PKESK bytes and encrypted body bytes. The
    shortened message cannot authenticate and is NEVER used as an integrity test.
    """
    def new_length(pos):
        octet = prefix[pos]
        pos += 1
        if octet < 192:
            return octet, pos, False
        if octet < 224:
            return ((octet - 192) << 8) + prefix[pos] + 192, pos + 1, False
        if octet == 255:
            assert pos + 4 <= len(prefix)
            return int.from_bytes(prefix[pos:pos+4], 'big'), pos + 4, False
        return 1 << (octet & 31), pos, True

    pos = 0
    while pos < len(prefix):
        start = pos
        first = prefix[pos]
        pos += 1
        assert first & 0x80
        if first & 0x40:
            tag = first & 63
            length, pos, partial = new_length(pos)
        else:
            tag = (first >> 2) & 15
            kind = first & 3
            assert kind != 3
            n = 1 << kind
            length = int.from_bytes(prefix[pos:pos+n], 'big')
            pos += n
            partial = False
        assert tag in (1, 3, 10, 18, 20)
        if tag in (18, 20):
            # Partial body length octets are packet framing, not ciphertext.
            chunks = []
            while True:
                end = min(pos + length, len(prefix))
                chunks.append(prefix[pos:end])
                if end == len(prefix) or end - pos < length or not partial:
                    break
                pos = end
                length, pos, partial = new_length(pos)
            body = b''.join(chunks)
            assert len(body) > 64
            new_header = bytes([0xC0 | tag, 255]) + len(body).to_bytes(4, 'big')
            return prefix[:start] + new_header + body
        assert not partial and pos + length <= len(prefix)
        pos += length
    raise ValueError('no truncated encrypted packet in bounded prefix')


def verify_private(plan):
    """plan has expected hashes/run/build/relative path; return hashes + counters."""
    assert 'session_key' not in plan
    # A test-only encrypted cache prevents repeatedly fetching the same header
    # while diagnosing the prefix protocol. It contains no session key.
    cache = W / 's93-encrypted-prefix.tmp'
    use_cache = plan['run_id'] == 39480275514 and cache.exists()
    prefix = cache.read_bytes() if use_cache else remote(
        ['python3', REMOTE, 'header', plan['relative_path'], plan['cipher_member']])
    assert 0 < len(prefix) <= 32768
    framed = bounded_gpg_prefix(prefix)
    result = subprocess.run(
        ['gpg', '--homedir', str(R / 'semantic-20261018/private/gnupg'),
         '--batch', '--no-tty', '--show-session-key', '--status-fd', '2', '--decrypt'],
        input=framed, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=60)
    # Truncated ciphertext is deliberate; it is not an authenticated decryption.
    keys = re.findall(rb'^\[GNUPG:\] SESSION_KEY ([0-9]+(?:\.[0-9]+)?:[0-9A-Fa-f]+)\s*$',
                      result.stderr, flags=re.MULTILINE)
    assert len(set(keys)) == 1, 'bounded prefix did not yield a unique session key'
    prefix_rc = result.returncode
    small_plan = dict(plan, session_key=keys[0].decode('ascii'))
    request = json.dumps(small_plan, separators=(',', ':')).encode()
    request_size = len(request)
    del keys, small_plan, result
    reply = remote(['python3', REMOTE, 'verify-private'], request)
    del request
    receipt = json.loads(reply)
    for key in ('run_id', 'source_commit', 'os_build', 'ZIP_bytes', 'ZIP_sha256',
                'cipher_member', 'cipher_bytes', 'cipher_sha256'):
        assert receipt[key] == plan[key]
    assert receipt['GPG_returncode'] == 0 and 'DECRYPTION_OKAY' in receipt['event_names_only']
    return receipt, {
        'HK_to_JP_verification_request_bytes': request_size,
        'JP_to_HK_encrypted_header_bytes': len(prefix),
        'header_was_already_cached_during_protocol_diagnosis': use_cache,
        'additional_header_network_bytes_this_invocation': 0 if use_cache else len(prefix),
        'JP_to_HK_hash_receipt_bytes': len(reply),
        'prefix_GPG_returncode_expected_truncation': prefix_rc,
        'prefix_only_is_not_authentication': True,
        'truncated_encrypted_packet_length_reframed_for_key_extraction_only': True,
        'whole_ZIP_or_cipher_backhaul_bytes': 0,
        'new_GitHub_artifact_download_bytes': 0,
        'counts_are_application_payload_exclude_SSH_overhead': True,
    }


def main():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    old_path = R / 'repo/research/hdr-native/evidence/s93/run/archive-receipt.json'
    old = json.loads(old_path.read_text())
    a = next(x for x in old['artifacts'] if x['name'].endswith('encrypted-outputs'))
    private = old['private_stream_verifications'][0]
    plan = {
        'run_id': old['run_id'], 'source_commit': old['source_commit'], 'os_build': old['os_build'],
        'relative_path': a['storage_relative_path'], 'ZIP_bytes': a['ZIP_bytes'],
        'ZIP_sha256': a['ZIP_sha256'], 'cipher_member': private['cipher_member'],
        'cipher_bytes': private['cipher_bytes'], 'cipher_sha256': private['cipher_sha256'],
    }
    helper, up, down = install_helper()
    receipt, counts = verify_private(plan)
    assert receipt['member_hashes_only'] == private['member_hashes_only']
    assert receipt['private_manifest_SHA256'] == private['private_manifest_SHA256']
    assert receipt['all_manifest_members_verified'] == private['all_manifest_members_verified']
    counts['HK_to_JP_once_only_helper_code_bytes'] = up
    counts['JP_to_HK_helper_install_receipt_bytes'] = down
    report = {
        'created_at_UTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'test': 'existing-S93-cipher-JP-local-verification-no-redownload',
        'coordinator_SHA256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'remote_helper': helper, 'transfer_payload': counts,
        'matches_existing_verified_member_hashes': True,
        'existing_archive_receipt_SHA256': hashlib.sha256(old_path.read_bytes()).hexdigest(),
        'private_key_stayed_on_HK': True, 'session_key_only_ephemeral': True,
        'verification': receipt,
    }
    raw = (json.dumps(report, indent=2) + '\n').encode()
    # Preserve all original receipts; this is an additive transport-only audit.
    for p in (W / 's93-transfer-v2-receipt.json', O / 's93-transfer-v2-receipt.json'):
        with p.open('xb') as f:
            f.write(raw)
    print(json.dumps({'test': report['test'], 'private_members': receipt['all_manifest_members_verified'],
                      'all_hashes_match': True, 'transfer_payload': counts,
                      'remote_max_RSS_KiB': receipt['remote_max_RSS_KiB'],
                      'child_max_RSS_KiB': receipt['child_max_RSS_KiB']}))


if __name__ == '__main__':
    try:
        main()
    except BaseException as exc:
        # subprocess input/stderr can contain session material; never dump them.
        print('HK-coordinator-failed: ' + type(exc).__name__, file=sys.stderr)
        sys.exit(1)
