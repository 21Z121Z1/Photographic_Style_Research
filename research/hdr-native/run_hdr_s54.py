"""Runner-only scalar ARM replay; not native iOS or an image inverse test."""
from pathlib import Path
import hashlib
import json
import math
import os
import random
import struct
import subprocess
import sys
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm64_const import *
from producer_curve_record_s54 import (quantize_node, node_preimage,
    first_nonnegative_bits_at_code, from_bits, decode_global_record,
    ios_gtc_input_ratios, quantize_bits)

assert sys.platform == 'darwin'
assert subprocess.check_output(['sw_vers', '-buildVersion'], text=True).strip() == '26A434'
D = Path('research/hdr-native')
O = Path(os.environ['W']) / 'out'
fixture = json.loads((D / 'evidence/s53/curve-record-fixture.json').read_text())
code = bytes.fromhex(fixture['quantizer']['instruction_hex'])
assert hashlib.sha256(code).hexdigest() == fixture['quantizer']['sha256']
CODE = int(fixture['quantizer']['start'], 16)
END = int(fixture['quantizer']['end_exclusive'], 16)
uc = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
for start, size in [(CODE & ~4095, 8192), (0x256bc8000, 4096),
                    (0x30000000, 0x30000), (0x30100000, 0x2000),
                    (0x30200000, 0x2000), (0x50000000, 0x10000)]:
    uc.mem_map(start, size)
uc.mem_write(CODE, code)
uc.mem_write(0x256bc8398, bytes.fromhex(fixture['quantizer']['scale_hex']))
uc.reg_write(UC_ARM64_REG_CPACR_EL1, 3 << 20)
uc.reg_write(UC_ARM64_REG_FPCR, 0)


def arm_quantize(a, b, first_bits=None):
    """Unmodified loop at cc68..cce4, original float32 input/output layout."""
    assert len(a) == len(b) == 257
    uc.mem_write(0x30018504, struct.pack('<257f', *a))
    uc.mem_write(0x30018908, struct.pack('<257f', *b))
    if first_bits is not None:
        for location in [0x30018504, 0x30018908]:
            uc.mem_write(location, struct.pack('<I', first_bits))
    uc.mem_write(0x30100000, bytes(516))
    uc.mem_write(0x30200000, bytes(516))
    uc.reg_write(UC_ARM64_REG_X19, 0x30300000)
    uc.reg_write(UC_ARM64_REG_X25, 0x30000000)
    uc.reg_write(UC_ARM64_REG_X22, 0x30100000)
    uc.reg_write(UC_ARM64_REG_X23, 0x30200000)
    uc.reg_write(UC_ARM64_REG_SP, 0x5000fff0)
    uc.emu_start(CODE, END, count=100000)
    assert uc.reg_read(UC_ARM64_REG_PC) == END
    return [bytes(uc.mem_read(x, 516)) for x in [0x30100000, 0x30200000]]


# Quantizer bounds are computed without image data. Every uint16 interior
# transition is checked on both sides against original ARM instructions.
probes = []
lower_bits = []
for q in range(1, 65536):
    k = first_nonnegative_bits_at_code(q)
    lower_bits.append(k)
    probes.extend([(k - 1, q - 1), (k, q)])
assert all(a < b for a, b in zip(lower_bits, lower_bits[1:]))
bad = 0
records = 0
digest = hashlib.sha256()
for pos in range(0, len(probes), 514):
    batch = probes[pos:pos + 514]
    batch += [(0, 0)] * (514 - len(batch))
    values = [from_bits(k) for k, q in batch]
    raw = arm_quantize(values[:257], values[257:])
    for buf, expected in zip(raw, [batch[:257], batch[257:]]):
        words = struct.unpack('<258H', buf)
        assert words[0] == 257
        bad += sum(a != b[1] for a, b in zip(words[1:], expected))
        digest.update(buf)
    records += 2
assert bad == 0

# Explicit nonfinite/clamp cases are a separate obligation from physical
# curves. Signaling-NaN input is injected as bits, not trusted to Python.
checkpoint={'uint16_transitions':65535,'ARM_boundary_probes':len(probes),'different_uint16_components':bad,'records':records,'record_digest':digest.hexdigest()}
(O/'boundary-checkpoint-s54.json').write_text(json.dumps(checkpoint,indent=2)+chr(10))

special_bits = [0xff800000, 0xbf800000, 0x80000000, 0, 1,
                0x3f800000, 0x40000000, 0x7f800000, 0x7fc00001,
                0xffc00001, 0x7f800001, 0xff800001]
special_expected = [0, 0, 0, 0, 0, 65535, 65535, 65535, 65535, 65535, 0, 0]
special_rows = []
for bits, expected in zip(special_bits, special_expected):
    assert quantize_bits(bits)==expected
    v = from_bits(bits)
    stages=[]
    def stage_hook(u,address,size,data):
        if u.reg_read(UC_ARM64_REG_X8)==0 and address in [0x256b8cca8,0x256b8ccac,0x256b8ccb0,0x256b8ccb4,0x256b8ccb8,0x256b8ccbc]:
            stages.append({'next_instruction':hex(address),'S2_bits':f'{u.reg_read(UC_ARM64_REG_S2):08x}','FPSR':u.reg_read(UC_ARM64_REG_FPSR)})
    h=uc.hook_add(UC_HOOK_CODE,stage_hook)
    uc.reg_write(UC_ARM64_REG_FPSR,0)
    # Exact raw bits preserve signaling NaN at the first source location.
    values = [v] * 257
    raw_a, raw_b = arm_quantize(values, values, first_bits=bits)
    uc.hook_del(h)
    actual = struct.unpack_from('<H', raw_a, 2)[0]
    special_rows.append({'input_bits': f'{bits:08x}', 'expected': expected,
                         'arm_code': actual, 'stages':stages, 'pass': actual == expected})
(O/'special-checkpoint-s54.json').write_text(json.dumps(special_rows,indent=2)+chr(10))
assert all(x['pass'] for x in special_rows)

with (O/'native-build.log').open('x')as log:
    subprocess.run(['clang','-O2','-fno-fast-math',str(D/'quantizer_native_s54.c'),'-o',str(Path(os.environ['W'])/'native-quantizer')],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
subprocess.run([str(Path(os.environ['W'])/'native-quantizer'),str(O/'native-special-s54.json')],check=True,timeout=60)
native_special=json.loads((O/'native-special-s54.json').read_text())
assert native_special['FPCR']==0 and native_special['native_AArch64']
for row,emu in zip(native_special['rows'],special_rows,strict=True):
    assert row['input_bits']==emu['input_bits'] and row['code']==emu['arm_code']
    assert row['after_min_bits']==emu['stages'][1]['S2_bits'] and row['after_max_bits']==emu['stages'][2]['S2_bits']
    if row['input_bits']in['7f800001','ff800001']:assert row['FPSR']&1


# Exact integer-scaled records demonstrate a loss of normalization amplitude;
# this is a synthetic record ambiguity, not a matching camera j counterfactual.
base_codes = [127 * i for i in range(257)]
r1 = struct.pack('<258H', 257, *base_codes)
r2 = struct.pack('<258H', 257, *[x * 2 for x in base_codes])
ratios_identical = ios_gtc_input_ratios(r1) == ios_gtc_input_ratios(r2)
assert r1 != r2 and ratios_identical
tail = bytearray(r1)
struct.pack_into('<H', tail, 514, 65535)
tail_omitted = ios_gtc_input_ratios(r1) == ios_gtc_input_ratios(bytes(tail))
assert tail_omitted
zero = struct.pack('<258H', 257, *([0] * 257))
try:
    ios_gtc_input_ratios(zero)
    raise AssertionError('zero divisor was silently accepted')
except ValueError as e:
    zero_rejected = 'zero normalization divisor' in str(e)
assert zero_rejected
sample_bounds = [node_preimage(q) for q in [0, 1, 2, 127, 32767, 32768, 65534, 65535]]
out = {
    'status': '已验证数值',
    'scope': 'Scalar writer ARM instruction replay under explicit FPCR=0, not native iOS execution, full consumer, or scene recovery',
    'runner_os_build': '26A434', 'image_version': os.environ.get('ImageVersion'),
    'source_os_build': '24A446', 'source_device': 'iPhone12,1 reference; differs from IMG_2810',
    'unicorn_version': __import__('unicorn').__version__,
    'conditional_monotonic_proof': {
        'contract': 'nonnegative binary32 bit order; RN positive-scale multiply then floor; clamp extends endpoint sets',
        'FPCR': 0, 'original_camera_FPCR_captured': False,
        'uint16_transitions': 65535, 'original_ARM_boundary_probes': len(probes),
        'two_output_arrays': True, 'records_replayed': records,
        'different_uint16_components': bad, 'record_digest_sha256': digest.hexdigest(),
        'endpoints': sample_bounds,
        'not_global_consumer_certificate': True,
    },
    'special_cases': special_rows,
    'normalization_information_loss': {
        'stage': 'iOS 257-header CMI ratio stage, before transfer decode and half store',
        'different_record_codes_same_ratios': ratios_identical,
        'divisor_word_index': 256, 'read_word_indices_inclusive': [1, 256],
        'last_writer_word257_unused_at_this_stage': tail_omitted,
        'zero_divisor_requires_nonfinite_path': zero_rejected,
        'records_sha256': [hashlib.sha256(x).hexdigest() for x in [r1, r2]],
        'no_binding_proof_to_IMG2810_key3_or_camera_exposure': True,
    },
    'fixture_sha256': hashlib.sha256((D / 'evidence/s53/curve-record-fixture.json').read_bytes()).hexdigest(),
    'native_special_comparison':native_special,
    'source_modules_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [D / 'run_hdr_s53.py', D / 'producer_curve_record_s54.py']},
    'photos_processed': 0, 'acceptance_complete': False, 'A_phase_complete': False,
    'old_gates_or_masks_changed': False,
    'S53_failure':{'run_id':39300758676,'artifact_id':12211821267,'ZIP_SHA256':'d1563d63c48a5f8c9c2183bb1b126f25be4d72988b76d048912d384767621db1','cause':'S53 conflated signaling and quiet NaNs; no S53 successful complete replay claim'},
    'ARM_primary_contract':'https://documentation-service.arm.com/static/67e40f3398aa3c3b6eea6a85',
}
(O / 'analysis-s54.json').write_text(json.dumps(out, indent=2, allow_nan=False) + '\n')
print(json.dumps({'boundary_probes': len(probes), 'different_uint16_components': bad,
                  'records': records, 'native_iOS': False}))
