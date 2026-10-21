"""Four missing full-frame fixed-view diagnostics, from actual S101 files.

S90's completed IMG2600 case is reused by SHA, never recomputed. No new image
output is archived: target EXR, native rasters and display arrays are scratch.
"""
from pathlib import Path
import ast
import hashlib
import json
import math
import os
import platform
import shutil
import subprocess
import sys
import numpy as np
import OpenEXR
import Imath
import PyOpenColorIO as ocio

R = Path.cwd()
D = R / 'research/hdr-native'
W = Path(os.environ['W'])
O = W / 'out'
SCRATCH = W / 'scratch'
sys.path[:0] = [str(R), str(D)]
from input_archive_s105 import download, decrypt_photo
from tools.heif_dump import parse_heif

ROWS = 32
Y = np.array([.2289745641, .6917385218, .0792869141])

def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def save(path, value):
    with Path(path).open('x') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')

def call(args, logfile):
    with Path(logfile).open('x') as f:
        subprocess.run(list(map(str, args)), stdout=f, stderr=subprocess.STDOUT, check=True, timeout=1800)

assert platform.system() == 'Darwin'
assert subprocess.check_output(['sw_vers', '-buildVersion'], text=True).strip() == '26A434'
policy = json.loads((D / 'final_image_retention.json').read_text())
assert policy['diagnostic_only_runs'].startswith('Upload aggregate text evidence only')
selected = ['IMG_2604', 'IMG_0032', 'IMG_2608', 'IMG_0033']
cases = {c['photo']: c for c in json.loads((D / 'inputs-s89.json').read_text())['cases']}
old_rows = {r['photo']: r for r in json.loads((D / 'evidence/s101/run/analysis.json').read_text())['rows']}
tree = ast.parse((D / 'run_hdr_s90.py').read_text())
nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in ['histogram_q', 'hist_summary', 'Bins', 'view_metrics']]
assert len(nodes) == 4
module = ast.Module(body=nodes, type_ignores=[])
ns = dict(np=np, math=math, hashlib=hashlib, Y=Y, ROWS=ROWS)
exec(compile(module, 'S90-unchanged-statistics-definitions', 'exec'), ns)
cfg = ocio.Config.CreateFromBuiltinConfig('cg-config-v2.2.0_aces-v1.3_ocio-v2.4')
cfg_sha = hashlib.sha256(cfg.serialize().encode()).hexdigest()
assert cfg_sha == '5aefc668796eabb1902b9593340496231758eceaec18ce290e12901042bd4440'
cpu = cfg.getProcessor('Linear P3-D65', 'sRGB - Display', 'ACES 1.0 - SDR Video', ocio.TRANSFORM_DIR_FORWARD).getDefaultCPUProcessor()
sources = ['run_hdr_s107.py', 'input_archive_s105.py', 'input_archive_s103.py', 'read_original_s103.m', 'run_hdr_s90.py', 'source_s37.m', 'carrier_readback_s87.m', 'hdr_headroom_s29.m', 'inputs-s89.json', 'final_image_retention.json']
freeze = {'os_build': '26A434', 'image_version': os.environ.get('ImageVersion'), 'source_commit': os.environ['GITHUB_SHA'], 'source_SHA256': {n: sha(D / n) for n in sources}, 'photos': selected, 'no_new_holdouts': True, 'reuse_IMG2600': 'evidence/s101/S90-reuse-binding.json and completed S90 10bit statistics; no rerun or 12bit retry', 'statistics_AST_SHA256': hashlib.sha256(ast.dump(module, include_attributes=False).encode()).hexdigest(), 'statistics_original_nodes_unmodified': True, 'headrooms': [1, 2, 8], 'fixed_display': {'config': 'cg-config-v2.2.0_aces-v1.3_ocio-v2.4', 'config_sha256': cfg_sha, 'source': 'Linear P3-D65', 'display': 'sRGB - Display', 'view': 'ACES 1.0 - SDR Video', 'exposure_ev': 0}, 'ideal_headroom': '(S+original_fullprecision_offset)*exp2(log2(headroom)/3*log2((H+offset)/(S+offset)))-offset; same S89/S90 formula, no encoded-offset substitution', 'predeclared_practical_display_diagnostic': {'name': 'fraction of full-frame pixels with max RGB difference <=1 code in the fixed 8bit ACES view', 'at_least': .99, 'scope': 'Display transport diagnostic only; not scene recovery or actual HDR display acceptance. No clipping of source inputs.'}, 'edge_brightness_diagnostics': 'Unmodified S90 gradient/reference-edge>=4/Laplacian proxies and brightness bins. No invented halo-visibility or per-bin acceptance threshold.', 'old_gates_or_masks_changed': False, 'image_archival': 'None. Reuse existing final HEIC; all decoded arrays/EXR/display images temporary runner scratch, cleanup on success/failure', 'engineering_accepted': False, 'A_phase_complete': False, 'acceptance_complete': False}
freeze['S105_transport_change'] = 'Bounded HTTP206 virtual ZIP, four selected ciphers; cipher SHA and full GPG unchanged. No full200 fallback, whole ZIP SHA not rehashed here. Same S103/S90 numeric body.'
save(O / 'suite-freeze.json', freeze)
frozen_sha = sha(O / 'suite-freeze.json')
flags = ['clang', '-O2', '-fobjc-arc', '-framework', 'Foundation', '-framework', 'CoreImage', '-framework', 'CoreMedia', '-framework', 'ImageIO', '-framework', 'Metal', '-framework', 'CoreGraphics', '-lz']
call(flags + [D / 'carrier_readback_s87.m', '-o', SCRATCH / 'oracle'], O / 'oracle-build.log')
call(flags + [D / 'read_original_s103.m', '-o', SCRATCH / 'source'], O / 'source-build.log')
archive, receipt = download(SCRATCH)
save(O / 'input-download.json', receipt)
sessions = json.loads(os.environ.pop('HDR_S107_ARCHIVE_SESSIONS'))
assert set(sessions) == set(selected)
rows = []
for photo in selected:
    case = cases[photo]
    folder = SCRATCH / photo
    folder.mkdir()
    public = O / photo
    public.mkdir()
    row = {'photo': photo, 'role': case['role'], 'new_holdout': False, 'completed': False}
    rows.append(row)
    try:
        auth = decrypt_photo(archive, folder, photo, sessions.pop(photo), old_rows[photo]['encrypted'])
        save(public / 'input-authentication.json', auth)
        carrier = folder / 'independent-HDR.heic'
        target_exr = folder / 'independent-HDR-target.exr'
        target_record = json.loads((folder / 'target-EXR-readback.json').read_text())
        old = json.loads((D / 'evidence/s101/run' / photo / 'analysis.json').read_text())
        assert sha(carrier) == old['carrier_sha256'] and sha(target_exr) == target_record['sha256']
        source = R / case['source_path']
        assert sha(source) == case['source_sha256']
        call([SCRATCH / 'source', source, folder], public / 'source.log')
        source_record = json.loads((folder / 'original-facts.json').read_text())
        h, w = case['shape'][:2]
        assert source_record['shape'] == [h, w, 4]
        source_path = folder / 'original-sdr.f32'
        assert sha(source_path) == old['source_pixel_SHA_before_after_unchanged']['original-sdr.f32']
        target_path = folder / 'HDR.f32'
        target = np.memmap(target_path, dtype='<f4', mode='w+', shape=(h, w, 3))
        exr = OpenEXR.InputFile(str(target_exr))
        float_type = Imath.PixelType(Imath.PixelType.FLOAT)
        for top in range(0, h, ROWS):
            stop = min(h, top + ROWS)
            for i, channel in enumerate('RGB'):
                target[top:stop, :, i] = np.frombuffer(exr.channel(channel, float_type, top, stop - 1), dtype='<f4').reshape(stop - top, w)
        exr.close()
        target.flush()
        del target
        assert sha(target_path) == target_record['source_f32_SHA256'] == old['source_pixel_SHA_before_after_unchanged']['HDR.f32']
        native_dir = folder / 'native'
        native_dir.mkdir()
        call([SCRATCH / 'oracle', source, carrier, native_dir], public / 'native.log')
        native = json.loads((native_dir / 'native.json').read_text())
        save(public / 'native.json', native)
        assert native['success'] and native['ImageIO_full_SDR']['decoded_sdr_max0_verified']
        old_native = json.loads((D / 'evidence/s101/run' / photo / 'native.json').read_text())
        observed_specs = [*native['files'].values(), *native['headrooms']]
        previous = {q['file']: q for q in [*old_native['files'].values(), *old_native['headrooms']]}
        for spec in observed_specs:
            assert spec['sha256'] == previous[spec['file']]['sha256'] == sha(native_dir / spec['file'])
        parsed = parse_heif(source.read_bytes())
        turn = parsed['items'][str(parsed['primary_item_id'])].get('irot', {}).get('angle_ccw_degrees', 0) // 90
        sraw = np.memmap(source_path, dtype='<f4', mode='r', shape=(h, w, 4))
        raw_target = np.memmap(target_path, dtype='<f4', mode='r', shape=(h, w, 3))
        sr = np.rot90(sraw[..., :3], k=turn)
        hr = np.rot90(raw_target, k=turn)
        height, width = native['height'], native['width']
        assert sr.shape == hr.shape == (height, width, 3)
        offset = json.loads((D / 'evidence/s101/run' / photo / 'analysis-s47.json').read_text())['common_offset']
        baseline = {str(p.relative_to(folder)): sha(p) for p in [source_path, target_path, target_exr, carrier, *[native_dir / q['file'] for q in observed_specs]]}
        row['headrooms'] = {}
        for spec in native['headrooms']:
            head = spec['headroom']
            arr = np.memmap(native_dir / spec['file'], dtype='<f4', mode='r', shape=(height, width, 4))
            ideal_path = folder / ('ideal-h' + str(head) + '.f32')
            ideal = np.memmap(ideal_path, dtype='<f4', mode='w+', shape=(height, width, 3))
            bins = ns['Bins'](folder)
            for top in range(0, height, ROWS):
                stop = min(height, top + ROWS)
                s = sr[top:stop].astype('f8')
                H = hr[top:stop].astype('f8')
                ratio = (H + offset) / (s + offset)
                assert np.isfinite(ratio).all() and (ratio > 0).all()
                reference = (s + offset) * np.exp2(math.log2(head) / 3 * np.log2(ratio)) - offset
                ideal[top:stop] = reference.astype('f4')
                bins.add(arr[top:stop, :, :3], reference)
            ideal.flush()
            brightness = bins.finish()
            display, unused_a, unused_b = ns['view_metrics'](arr, ideal, cpu, folder, 'h' + str(head))
            del unused_a, unused_b
            assert display['display_pixel_max_RGB_code_error']['n'] == height * width
            row['headrooms'][str(head)] = {'display': display, 'brightness_bins': brightness, 'diagnostic_fraction_within_one_code': 1 - display['pixel_fractions_error_gt_codes']['1'], 'diagnostic_at_least_99pct_within_one_code': display['pixel_fractions_error_gt_codes']['1'] <= .01, 'new_image_output_archived': False}
            del ideal, arr, bins
            ideal_path.unlink()
        assert baseline == {name: sha(folder / name) for name in baseline}
        assert sha(source) == case['source_sha256']
        row.update(completed=True, shape=[height, width, 3], original_offset=offset, ImageIO_full_SDR_max0=True, identical_S101_carrier_target_original_SDR_and_native_arrays=True, all_input_SHA_unchanged=True, input_SHA_baseline=baseline, new_image_output_archived=False)
        del sr, hr, sraw, raw_target
    except Exception as error:
        row.update(failure_type=type(error).__name__, failure=str(error), completed=False)
    finally:
        save(public / 'analysis.json', row)
        assert folder.parent == SCRATCH and folder.name == photo
        shutil.rmtree(folder)
    if not row['completed']:
        break
save(O / 'input-range-receipt.json', archive.receipt())
archive.close()
assert sha(O / 'suite-freeze.json') == frozen_sha
summary = {'os_build': '26A434', 'source_commit': os.environ['GITHUB_SHA'], 'image_version': os.environ.get('ImageVersion'), 'completed': len(rows) == 4 and all(r['completed'] for r in rows), 'rows': rows, 'reused_IMG2600': 'S90 exact-file binding from S101, not rerun', 'diagnostic_only': True, 'image_output_archival': 'none', 'engineering_accepted': False, 'A_phase_complete': False, 'acceptance_complete': False}
save(O / 'analysis.json', summary)
print(json.dumps({'completed_photos': sum(r['completed'] for r in rows), 'new_image_outputs': 0, 'engineering_accepted': False}))
sys.exit(0 if summary['completed'] else 1)
