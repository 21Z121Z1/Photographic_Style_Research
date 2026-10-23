"""Bind ONE new call of the exact S25 Apple CPU-recompiled pow shim.

No libm fallback, historical FPCR certification, GPU claim, or pipeline claim.
``preflight`` is safe on Linux. ``run`` needs the original private sealed dylib,
an explicitly pinned Apple OS build, and a new private directory outside Git.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import platform
from pathlib import Path
import re
import struct
import subprocess
import time

from baseline_archive import Archive, encoded, sha
from square132_contract import value, power_certificate

R = Path(__file__).resolve().parent
REPO = R.parents[1]
SEALED_SHA = '47185c09c0407d7c96aa9dc55e0581ae4e781836951c8b236d17f2ac6f8efbbe'
BASE_HALF, EXPONENT_HALF = 0x2b8f, 0x36aa
BASE_SINGLE, EXPONENT_SINGLE = 0x3d71e000, 0x3ed54000


@dataclass(frozen=True)
class StaticIdentity:
    uuid: str
    shim_offset: int
    tail_offset: int
    stub_offset: int
    got_offset: int
    indirect_symbol_index: int
    import_symbol: str


def static_identity(data: bytes, *, expected_sha: str = SEALED_SHA) -> StaticIdentity:
    """Read only a thin little-endian ARM64 Mach-O. Reject any changed artifact.

    Import identity comes from LC_DYSYMTAB, not nearest-symbol disassembly text.
    Exact fixed offsets are permitted only after the historical SHA gate.
    """
    if hashlib.sha256(data).hexdigest() != expected_sha:
        raise ValueError('sealed binary SHA mismatch; no substitute artifact accepted')
    if len(data) < 32:
        raise ValueError('truncated Mach-O header')
    magic, cpu, _, _, count, size, _, _ = struct.unpack_from('<8I', data)
    if magic != 0xfeedfacf or cpu != 0x100000c or size > len(data) - 32:
        raise ValueError('thin ARM64 Mach-O required')
    end, cursor = 32 + size, 32
    segments, sections, uuids, symtabs, dysymtabs = [], [], [], [], []
    for _ in range(count):
        if cursor + 8 > end:
            raise ValueError('truncated load command')
        cmd, n = struct.unpack_from('<2I', data, cursor)
        if n < 8 or cursor + n > end:
            raise ValueError('invalid load command size')
        if cmd == 0x1b:
            if n != 24:
                raise ValueError('invalid UUID command')
            uuids.append(data[cursor+8:cursor+24].hex())
        elif cmd == 0x19:
            if n < 72:
                raise ValueError('invalid segment')
            vm, vm_size, off, file_size = struct.unpack_from('<4Q', data, cursor+24)
            nsects = struct.unpack_from('<I', data, cursor+64)[0]
            if n != 72 + 80*nsects or off + file_size > len(data):
                raise ValueError('invalid segment range')
            segments.append((vm, vm_size, off, file_size))
            for i in range(nsects):
                p = cursor + 72 + i*80
                sect, seg, addr, length, sectoff, _, _, _, flags, r1, r2, _ = struct.unpack_from('<16s16sQQ8I', data, p)
                sections.append((sect.rstrip(b'\0'), seg.rstrip(b'\0'), addr, length, sectoff, flags, r1, r2))
        elif cmd == 2:
            if n != 24:
                raise ValueError('invalid symbol table command')
            symtabs.append(struct.unpack_from('<4I', data, cursor+8))
        elif cmd == 0xb:
            if n != 80:
                raise ValueError('invalid dynamic symbol command')
            dysymtabs.append(struct.unpack_from('<18I', data, cursor+8))
        cursor += n
    if cursor != end or len(uuids) != 1 or len(symtabs) != 1 or len(dysymtabs) != 1:
        raise ValueError('unique UUID and symbol tables required')

    def readvm(address: int, n: int) -> bytes:
        candidates = [data[o+address-v:o+address-v+n] for v, _, o, s in segments if v <= address and address+n <= v+s]
        if len(candidates) != 1 or len(candidates[0]) != n:
            raise ValueError('unmapped/ambiguous machine-code range')
        return candidates[0]

    tail = struct.unpack('<I', readvm(0x15904, 4))[0]
    if tail & 0xfc000000 != 0x14000000:
        raise ValueError('shim must be an unconditional tail branch')
    imm = tail & 0x03ffffff
    if imm & (1 << 25):
        imm -= 1 << 26
    stub = 0x15904 + imm*4
    if stub != 0x16244:
        raise ValueError('historical stub target changed')
    adrp, ldr, br = struct.unpack('<3I', readvm(stub, 12))
    if adrp & 0x9f00001f != 0x90000010 or ldr & 0xffc003ff != 0xf9400210 or br != 0xd61f0200:
        raise ValueError('unsupported stub; no authenticated-stub or dlsym fallback')
    page = ((adrp >> 5) & 0x7ffff) << 2 | ((adrp >> 29) & 3)
    if page & (1 << 20):
        page -= 1 << 21
    got = (stub & ~4095) + page*4096 + ((ldr >> 10) & 0xfff)*8
    stubs = [s for s in sections if s[0:2] == (b'__stubs', b'__TEXT') and s[2] <= stub < s[2]+s[3]]
    slots = [s for s in sections if s[5] & 0xff in (6, 7) and s[2] <= got <= s[2]+s[3]-8]
    if len(stubs) != 1 or len(slots) != 1 or stubs[0][7] != 12:
        raise ValueError('stub/GOT section binding unavailable')
    st = stubs[0]
    if (stub - st[2]) % 12:
        raise ValueError('unaligned stub')
    indirect_offset, indirect_count = dysymtabs[0][12:14]
    entry = st[6] + (stub-st[2])//12
    if entry >= indirect_count or indirect_offset + indirect_count*4 > len(data):
        raise ValueError('invalid indirect symbol range')
    index = struct.unpack_from('<I', data, indirect_offset+entry*4)[0]
    slot_entry = slots[0][6] + (got-slots[0][2])//8
    if (got-slots[0][2]) % 8 or slot_entry >= indirect_count or struct.unpack_from('<I',data,indirect_offset+slot_entry*4)[0] != index:
        raise ValueError('stub and actual GOT slot imports disagree')
    symoff, nsyms, stroff, strsize = symtabs[0]
    if index != 136 or index >= nsyms or symoff+nsyms*16 > len(data) or stroff+strsize > len(data):
        raise ValueError('historical indirect symbol index mismatch')
    strx = struct.unpack_from('<I', data, symoff+index*16)[0]
    if strx >= strsize:
        raise ValueError('invalid symbol string')
    symbol = data[stroff+strx:stroff+strsize].split(b'\0', 1)[0]
    if symbol != b'_powf':
        raise ValueError('historical import is not _powf')
    entries = []
    for i in range(nsyms):
        strx, typ, _, _, entry = struct.unpack_from('<IBBHQ', data, symoff+i*16)
        if strx >= strsize:
            raise ValueError('invalid symbol string offset')
        name = data[stroff+strx:stroff+strsize].split(b'\0', 1)[0]
        if name == b'_psr_pow_scalar' and typ & 0xe == 0xe:
            entries.append(entry)
    if len(entries) != 1 or not 0x15904-64 <= entries[0] <= 0x15904 or entries[0] % 4:
        raise ValueError('actual shim symbol entry is not bound to the historical tail')
    prefix = readvm(entries[0], 0x15904-entries[0])
    for (word,) in struct.iter_unpack('<I', prefix):
        if (word & ~31 == 0xd51b4400 or word & 0x7c000000 == 0x14000000 or
            word & 0xff000010 == 0x54000000 or word & 0x7e000000 in (0x34000000,0x36000000) or
            word & 0xfe000000 == 0xd6000000):
            raise ValueError('unexpected call/branch/FPCR write before the shim tail')
    return StaticIdentity(uuids[0], entries[0], 0x15904, stub, got, index, symbol.decode())


def single_value(bits: int) -> Fraction:
    if type(bits) is not int or not 0 <= bits < 0x7f800000:
        raise ValueError('finite nonnegative f32 required')
    exp, mant = bits >> 23, bits & 0x7fffff
    if exp:
        mant += 1 << 23
        shift = exp - 150
    else:
        shift = -149
    return Fraction(mant << shift, 1) if shift >= 0 else Fraction(mant, 1 << -shift)


def classify_result(d: dict[str, object], identity: StaticIdentity) -> dict:
    """Check a captured result; no native loading or floating-point pow."""
    exact = {'source_uuid': identity.uuid, 'got_image_offset': identity.got_offset,
             'got_stable': 1, 'native_return_code': 0, 'original_call_count': 1,
             'self_equal': 1, 'query_before': 0, 'query_after': 0,
             'base_half_bits': BASE_HALF, 'exponent_half_bits': EXPONENT_HALF,
             'base_single_bits': BASE_SINGLE, 'exponent_single_bits': EXPONENT_SINGLE}
    if any(type(d.get(k)) is not type(v) or d[k] != v for k, v in exact.items()):
        raise ValueError('raw capture does not match the bound call/input contract')
    if not re.fullmatch('[0-9a-f]{32}', str(d.get('target_uuid', ''))):
        raise ValueError('target loaded image UUID missing')
    for name in ['target_symbol','target_image_basename']:
        if type(d.get(name)) is not str or not d[name] or '\n' in d[name]:
            raise ValueError('actual target symbol/image identity missing')
    for name in ['target_image_offset','target_symbol_exact']:
        if type(d.get(name)) is not int or d[name] < 0:
            raise ValueError('actual target offset/symbol precision missing')
    if d['target_symbol_exact'] not in (0,1):
        raise ValueError('invalid target symbol precision')
    if type(d.get('thread_before')) is not int or d['thread_before'] <= 0 or d['thread_before'] != d.get('thread_after'):
        raise ValueError('same native thread not bound')
    before, after = d.get('fpcr_before'), d.get('fpcr_after')
    if type(before) is not int or before != after or before < 0 or before >= 1 << 64 or before & ((3 << 22) | (1 << 26)):
        raise ValueError('unchanged RN/IEEE-half FPCR not bound')
    bits, half = d.get('output_single_bits'), d.get('output_half_bits')
    x = single_value(bits)
    if not 0 < bits < 0x7f7fffff or type(half) is not int:
        raise ValueError('unexpected nonpositive/overflow result')
    # IEEE RN-even narrowing of this *observed f32*. No libm call occurs here.
    narrowed = struct.unpack('<H', struct.pack('<e', float(x)))[0]
    if half != narrowed:
        raise ValueError('observed FCVT narrowing disagrees with RN-even')
    c, exponent = value(BASE_HALF), value(EXPONENT_HALF)
    lower = (single_value(bits-1) + x)/2
    upper = (x + single_value(bits+1))/2
    target = c ** exponent.numerator
    a = target - lower ** exponent.denominator
    b = upper ** exponent.denominator - target
    ideal_single = (a > 0 or a == 0 and bits % 2 == 0) and (b > 0 or b == 0 and bits % 2 == 0)
    cert = power_certificate(BASE_HALF, 0x34ed)
    return {'status': 'one_current_Apple_CPU_shim_call_bound',
            'ideal_real_power_correctly_RN_to_f32_for_this_input': ideal_single,
            'ideal_real_power_half_bits': cert['power_half_bits'],
            'observed_half_matches_ideal_real_power_half': half == cert['power_half_bits'],
            'f32_rounding_check': 'exact c^853 versus f32-cell-midpoints^2048; no floating pow',
            'observed_f32_minus_lower_half_midpoint': list((x-Fraction(2521,8192)).as_integer_ratio()),
            'upper_half_midpoint_minus_observed_f32': list((Fraction(2523,8192)-x).as_integer_ratio()),
            'historical_calls_GPU_full_helper_or_pipeline_certified': False,
            'new_wrapper_owns_half_conversions': True,
            'target_symbol_interpretation': 'exact_symbol_start' if d['target_symbol_exact'] else 'nearest_symbol_only',
            'target_image_disk_sha256': None,
            'target_identity_scope': 'loaded LC_UUID, OS build, basename and actual GOT target image offset; no single-file SHA claimed for dyld-cache image'}


def check_wrapper(disassembly: str) -> dict:
    if re.search(r'\bmsr\s+FPCR\b', disassembly, re.I):
        raise ValueError('FPCR write found')
    match = re.search(r'^_psr_pow_read_call:\s*\n(.*?)(?=^_\w[^\n]*:\s*$|\Z)', disassembly, re.M | re.S)
    if not match:
        raise ValueError('wrapper body unavailable')
    lines = match[1].splitlines()
    reads = [i for i, line in enumerate(lines) if re.search(r'\bmrs\s+[^,]+,\s*FPCR\b', line, re.I)]
    if len(reads) != 2:
        raise ValueError('two FPCR reads required')
    window = lines[reads[0]+1:reads[1]]
    calls = [i for i, line in enumerate(window) if re.search(r'\b(?:bl|blr|blraa|blrab)\b', line)]
    if len(calls) != 1 or not re.search(r'\bblr\b', window[calls[0]]):
        raise ValueError('exactly one synchronous function-pointer call required')
    if sum(bool(re.search(r'\bfcvt\s+s\d+,\s*h\d+', l)) for l in window[:calls[0]]) != 2 or not any(re.search(r'\bfcvt\s+h\d+,\s*s\d+', l) for l in window[calls[0]+1:]):
        raise ValueError('two half inputs and one half output must convert inside the FPCR window')
    return {'FPCR_writes': 0, 'FPCR_reads': 2, 'critical_calls': 1,
            'instruction_window_sha256': hashlib.sha256(encoded(window)).hexdigest()}


def preflight(binary: Path | None, expected_os_build: str | None) -> dict:
    reasons = []
    host = {'system': platform.system(), 'architecture': platform.machine(), 'release': platform.release()}
    if host['system'] != 'Darwin' or host['architecture'] != 'arm64':
        reasons.append('requires Apple Darwin arm64; Linux/Intel/libm substitutes rejected')
    build = None
    if host['system'] == 'Darwin':
        build = subprocess.check_output(['sw_vers', '-buildVersion'], text=True).strip()
    host['OS_build'] = build
    if not expected_os_build or build != expected_os_build:
        reasons.append('actual Apple OS build must match the explicitly supplied expected build')
    if binary is None or not binary.is_file():
        reasons.append('original private sealed S25 dylib is absent')
    elif sha(binary) != SEALED_SHA:
        reasons.append('supplied dylib SHA differs from the original sealed S25 product')
    return {'status': 'blocked_before_compile_load_or_call' if reasons else 'ready_for_one_new_current_call',
            'host': host, 'required_product_sha256': SEALED_SHA, 'blockers': reasons,
            'source_sha256': sha(Path(__file__)),
            'native_calls': 0, 'compilations': 0,
            'standard_GitHub_runner_cannot_supply_private_sealed_artifact': True,
            'another_Apple_OS_pow_cannot_certify_historical_target': True,
            'candidate': {'base_half_bits': BASE_HALF, 'base_rational': [1935,32768],
                          'exponent_half_bits': EXPONENT_HALF, 'exponent_rational': [853,2048],
                          'context': 'S31 conditional encode/square boundary witness, not a historical pow call'}}


def run(binary: Path, private: Path, expected_os_build: str) -> dict:
    gate = preflight(binary, expected_os_build)
    if gate['blockers']:
        raise RuntimeError(json.dumps(gate))
    sealed_data = binary.read_bytes()
    identity = static_identity(sealed_data)
    a = Archive(private, create=True, repo=REPO)
    a.input('inputs/sealed.dylib', sealed_data, 'unchanged sealed S25 product, never upload')
    a.input('inputs/pow_read_call.c', (R/'pow_read_call.c').read_bytes(), 'new collector source')
    a.input('inputs/pow_runtime_binding.py', Path(__file__).read_bytes(), 'exact driver source')
    a.input('inputs/plan.json', encoded({'gate':gate,'identity':identity.__dict__,'maximum_calls':1}), 'frozen input/identity before compile')
    a.seal({'scope':__doc__, 'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()})
    compiler = subprocess.check_output(['xcrun','--find','clang'],text=True).strip()
    compiler_sha = sha(Path(compiler).resolve())
    command = [compiler,'-arch','arm64','-std=c17','-O0','-frounding-math','-ffp-contract=off',
               '-Wall','-Wextra','-Werror',str(a.path('inputs/pow_read_call.c')),'-o',str(a.path('collector'))]
    a.write('compile-command.json',encoded({'argv':command,'compiler_sha256':compiler_sha}))
    compile_result = subprocess.run(command,capture_output=True,timeout=60)
    a.write('compile.stdout',compile_result.stdout);a.write('compile.stderr',compile_result.stderr)
    if compile_result.returncode:
        raise RuntimeError('collector compile failed; logs retained, zero target calls')
    dis = subprocess.run(['xcrun','otool','-tvV',str(a.path('collector'))],capture_output=True,timeout=30)
    a.write('disassembly.stdout',dis.stdout);a.write('disassembly.stderr',dis.stderr)
    if dis.returncode:
        raise RuntimeError('static collector inspection failed; zero target calls')
    window = check_wrapper(dis.stdout.decode())
    products = {'collector': {'sha256':sha(a.path('collector'))}}
    a.proof('before-load',products)
    if sha(R/'pow_read_call.c') != sha(a.path('inputs/pow_read_call.c')) or sha(Path(__file__)) != sha(a.path('inputs/pow_runtime_binding.py')):
        raise RuntimeError('live driver or wrapper changed after preparation; zero target calls')
    if sha(Path(compiler).resolve()) != compiler_sha:
        raise RuntimeError('compiler changed')
    # Exclusive marker is created before starting any process that can dlopen.
    a.write('run-started.private.json',encoded({'maximum_calls':1,'time_unix':time.time()}),mode=0o400)
    native = subprocess.run([str(a.path('collector')),str(a.path('inputs/sealed.dylib')),str(identity.shim_offset)],capture_output=True,timeout=30)
    a.write('native.stdout',native.stdout);a.write('native.stderr',native.stderr)
    a.proof('after-call',products)
    if sha(R/'pow_read_call.c') != sha(a.path('inputs/pow_read_call.c')) or sha(Path(__file__)) != sha(a.path('inputs/pow_runtime_binding.py')):
        raise RuntimeError('live driver or wrapper changed; preserve run, never automatically retry')
    if native.returncode:
        raise RuntimeError('native binding failed; preserve run, never automatically retry')
    fields = {}
    strings = {'source_uuid','target_uuid','target_symbol','target_image_basename'}
    for line in native.stdout.decode().splitlines():
        k, v = line.split(' ',1)
        if k in fields:
            raise ValueError('duplicate native output key')
        fields[k] = v if k in strings else int(v)
    result = {'preflight':gate,'source_sha256':sha(Path(__file__)),'wrapper_source_sha256':sha(R/'pow_read_call.c'),
              'collector_sha256':products['collector']['sha256'],'static_identity':identity.__dict__,
              'wrapper_static_check':window,'capture':fields,'validation':classify_result(fields,identity),
              'compile_command_sha256':sha(a.path('compile-command.json')),
              'native_stdout_sha256':sha(a.path('native.stdout')),'native_stderr_sha256':sha(a.path('native.stderr'))}
    a.write('result.json',encoded(result),mode=0o400)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['preflight','run'])
    parser.add_argument('--binary', type=Path)
    parser.add_argument('--expected-os-build')
    parser.add_argument('--private', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('output must not exist')
    if args.mode == 'run' and (not args.binary or not args.private or not args.expected_os_build):
        parser.error('run requires --binary, --private and --expected-os-build')
    result = preflight(args.binary,args.expected_os_build) if args.mode == 'preflight' else run(args.binary,args.private,args.expected_os_build)
    with args.output.open('xb') as f:
        f.write(encoded(result))
    print(json.dumps({'status':result.get('status',result.get('validation',{}).get('status')),'output':str(args.output)}))
