#!/usr/bin/env python3
"""Replay the reconstructed consumer MSL against Apple's native renderer at several tone biases.

Run on macOS 26A434-class hosts from the repository root, for example:
  python3 consumer-model/harness/run_tone_sweep.py out/tone-sweep \
      Apple_Native_Samples/IMG_0032.HEIC --tones -1 -0.35 0 0.35 1

For each photo and tone it extracts HEIF inputs (research/vm-native/extract_inputs.py),
runs native_renderer_trace with VM_CONSUMER_MSL set, and compares msl-output.f16
(reconstructed model) with _outputImageTexture.bin (Apple's original output) over RGB.
Adapted from research/vm-native/runner/run-discovery.py; new file, not yet run on a runner.
"""
from pathlib import Path
import argparse, json, os, subprocess, sys
import numpy as np

here = Path(__file__).resolve().parent
model = here.parent / 'msl' / 'consumer-model.metal'
root = Path.cwd()

p = argparse.ArgumentParser()
p.add_argument('out', type=Path)
p.add_argument('photos', nargs='+', type=Path)
p.add_argument('--tones', nargs='+', type=float, default=[-1.0, 0.0, 1.0])
p.add_argument('--msl', type=Path, default=model)
a = p.parse_args()
a.out.mkdir(parents=True, exist_ok=True)

def run(args, log, env=None):
    with open(log, 'w') as f:
        try:
            return subprocess.run([str(x) for x in args], stdout=f, stderr=subprocess.STDOUT, timeout=240, env=env).returncode
        except subprocess.TimeoutExpired:
            return 'timeout'

binary = Path(os.environ.get('RUNNER_TEMP', '/tmp')) / 'native_renderer_trace'
flags = ['clang', '-fobjc-arc', '-O1', '-framework', 'Foundation', '-framework', 'CoreImage', '-framework', 'CoreMedia',
         '-framework', 'ImageIO', '-framework', 'Metal', '-Wl,-undefined,dynamic_lookup']
if run(flags + [here / 'native_renderer_trace.m', '-o', binary], a.out / 'build.log') != 0:
    sys.exit('build failed, see ' + str(a.out / 'build.log'))

rows = []
for photo in a.photos:
    stem = photo.stem
    case = a.out / stem
    case.mkdir(exist_ok=True)
    resources = Path(os.environ.get('RUNNER_TEMP', '/tmp')) / 'photo-resources' / stem
    rc = run(['python3', root / 'research/vm-native/extract_inputs.py', photo, resources], case / 'extract.log')
    if rc != 0:
        rows.append({'photo': stem, 'error': 'extract_inputs returncode %s' % rc}); continue
    for tone in a.tones:
        tdir = case / ('tone-%g' % tone)
        env = os.environ.copy()
        env.update({'VM_CONSUMER_MSL': str(a.msl.resolve()), 'XD_TONE_THUMB_MODE': 'native-stage-mirror',
                    'XD_TONE_BIAS': str(tone), 'XD_TONE_MAX_EDGE': '512', 'XD_TONE_GUIDED_REPLAY': '0'})
        rc = run([binary, photo, resources, tdir], case / ('tone-%g.log' % tone), env)
        r = {'photo': stem, 'tone': tone, 'returncode': rc}
        rd = tdir / 'renderer-0'
        msl, orig = rd / 'msl-output.f16', rd / '_outputImageTexture.bin'
        if msl.exists() and orig.exists():
            m = np.fromfile(msl, '<f2'); o = np.fromfile(orig, '<f2')
            if m.size == o.size and m.size % 4 == 0:
                m = m.reshape(-1, 4)[:, :3]; o = o.reshape(-1, 4)[:, :3]
                d = m.astype(float) - o.astype(float)
                r.update({'components': int(d.size),
                          'differing_components': int(np.count_nonzero(m.view('u2') != o.view('u2'))),
                          'max_abs': float(np.max(np.abs(d))),
                          'psnr_peak1_db': float(-10 * np.log10(np.mean(d ** 2))) if np.any(d) else 'inf'})
            else:
                r['error'] = 'size mismatch %d vs %d' % (m.size, o.size)
        else:
            r['error'] = 'missing ' + ', '.join(str(x.name) for x in (msl, orig) if not x.exists())
        rows.append(r); print(json.dumps(r))
(a.out / 'tone-sweep.json').write_text(json.dumps(rows, indent=2) + '\n')
