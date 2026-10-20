"""Recover exact text files from the authorized GitHub job-log response."""
import argparse
import base64
import hashlib
import json
import pathlib
import re
import zlib


def recover(raw, expected_head):
    lines = [re.sub(r'^\ufeff?\d{4}-\d\d-\d\dT\S+Z ?', '', line)
             for line in raw.splitlines()]
    files, active, chunks, last_end = {}, None, [], -1
    for index, line in enumerate(lines):
        if line.startswith('PRODUCER_FILE_BEGIN '):
            if active is not None:
                raise ValueError('nested file')
            active = line.removeprefix('PRODUCER_FILE_BEGIN ')
            path = pathlib.PurePosixPath(active)
            if path.is_absolute() or '..' in path.parts or str(path) != active or active in files:
                raise ValueError('invalid or duplicate path')
            chunks = []
        elif line.startswith('PRODUCER_FILE_END '):
            if active is None or line.removeprefix('PRODUCER_FILE_END ') != active:
                raise ValueError('mismatched file end')
            compressed = base64.b64decode(''.join(chunks), validate=True)
            decoder = zlib.decompressobj()
            payload = decoder.decompress(compressed) + decoder.flush()
            if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
                raise ValueError('incomplete or extra compressed bytes')
            payload.decode('utf-8')
            files[active] = payload
            active, last_end = None, index
        elif active is not None:
            chunks.append(line)
    if active is not None or not files:
        raise ValueError('truncated or empty evidence')
    manifest = None
    for index in range(last_end + 1, len(lines)):
        if lines[index] != '{':
            continue
        try:
            value, _ = json.JSONDecoder().raw_decode('\n'.join(lines[index:]))
        except ValueError:
            continue
        if value.get('schema') == 'texture-producer-evidence-v1':
            manifest = value
            break
    if not manifest or manifest['head_sha'] != expected_head:
        raise ValueError('missing manifest or wrong source')
    if {row['path'] for row in manifest['files']} != set(files):
        raise ValueError('manifest file set mismatch')
    for row in manifest['files']:
        value = files[row['path']]
        if len(value) != row['size'] or hashlib.sha256(value).hexdigest() != row['sha256']:
            raise ValueError('payload hash or length mismatch: ' + row['path'])
    return files, manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('log', type=pathlib.Path)
    parser.add_argument('--head', required=True)
    parser.add_argument('--out', type=pathlib.Path, required=True)
    args = parser.parse_args()
    files, manifest = recover(args.log.read_bytes().decode('utf-8'), args.head)
    args.out.mkdir(parents=True, exist_ok=False)
    for name, payload in files.items():
        output = args.out / name
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(payload)
    (args.out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'verified_files': len(files), 'head_sha': manifest['head_sha'],
                      'run_id': manifest['run_id'], 'output': str(args.out)}))


if __name__ == '__main__':
    main()
