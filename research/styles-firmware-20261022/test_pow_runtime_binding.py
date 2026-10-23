"""Synthetic metadata/report tests only; no Apple pow execution is claimed."""
import copy
import hashlib
import platform
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from pow_runtime_binding import (StaticIdentity, static_identity, classify_result,
                                 check_wrapper, preflight, run, single_value)


def synthetic_macho():
    """A tiny generated Mach-O shape, never executable Apple code."""
    data = bytearray(0x21000)
    commands = []
    section = lambda sect,seg,addr,size,off,flags,r1,r2: struct.pack('<16s16sQQ8I',sect,seg,addr,size,off,2,0,0,flags,r1,r2,0)
    text = struct.pack('<II16sQQQQiiII',0x19,152,b'__TEXT',0,0x20000,0,0x20000,7,5,1,0)
    text += section(b'__stubs',b'__TEXT',0x16244,12,0x16244,8,0,12)
    commands.append(text)
    dat = struct.pack('<II16sQQQQiiII',0x19,152,b'__DATA_CONST',0x20000,0x1000,0x20000,0x1000,3,3,1,0)
    dat += section(b'__got',b'__DATA_CONST',0x20000,8,0x20000,6,1,0)
    commands.append(dat)
    commands.append(struct.pack('<II16s',0x1b,24,b'abcdefghijklmnop'))
    commands.append(struct.pack('<6I',2,24,0x18000,138,0x19000,64))
    d = [0]*18;d[12:14] = [0x1a000,2]
    commands.append(struct.pack('<2I18I',0xb,80,*d))
    blob = b''.join(commands)
    struct.pack_into('<8I',data,0,0xfeedfacf,0x100000c,0,6,len(commands),len(blob),0,0)
    data[32:32+len(blob)] = blob
    struct.pack_into('<I',data,0x15904,0x14000000 | ((0x16244-0x15904)//4))
    struct.pack_into('<2I',data,0x158fc,0xd503201f,0xd503201f)
    # ADRP x16, +10 pages; LDR x16,[x16,#0]; BR x16.
    page = (0x20000-0x16000)//4096
    adrp = 0x90000010 | ((page & 3)<<29) | ((page>>2)<<5)
    struct.pack_into('<3I',data,0x16244,adrp,0xf9400210,0xd61f0200)
    struct.pack_into('<I',data,0x18000+136*16,1)
    data[0x19000:0x19007] = b'\0_powf\0'
    data[0x19007:0x19017] = b'_psr_pow_scalar\0'
    struct.pack_into('<IBBHQ',data,0x18000+137*16,7,0xf,1,0,0x158fc)
    struct.pack_into('<2I',data,0x1a000,136,136)
    return bytes(data)


IDENTITY = StaticIdentity('6162636465666768696a6b6c6d6e6f70',0x158fc,0x15904,0x16244,0x20000,136,'_powf')
CAPTURE = dict(source_uuid=IDENTITY.uuid,target_uuid='0'*32,got_image_offset=0x20000,
               got_stable=1,native_return_code=0,original_call_count=1,self_equal=1,
               query_before=0,query_after=0,base_half_bits=0x2b8f,exponent_half_bits=0x36aa,
               base_single_bits=0x3d71e000,exponent_single_bits=0x3ed54000,
               thread_before=42,thread_after=42,fpcr_before=0,fpcr_after=0,
               output_single_bits=0x3e9da000,output_half_bits=0x34ed)
CAPTURE.update(target_symbol='powf',target_symbol_exact=1,target_image_basename='libsystem_m.dylib',target_image_offset=4096)
DISASSEMBLY = '''_psr_pow_read_call:
0000000100001000 mrs x8, FPCR
0000000100001004 fcvt s0, h0
0000000100001008 fcvt s1, h1
000000010000100c blr x8
0000000100001010 fcvt h0, s0
0000000100001014 mrs x8, FPCR
_main:
0000000100001020 ret
'''


class PowRuntimeTests(unittest.TestCase):
    def identity(self,data):
        return static_identity(data,expected_sha=hashlib.sha256(data).hexdigest())

    def test_generated_static_shape_maps_tail_stub_and_import(self):
        self.assertEqual(self.identity(synthetic_macho()),IDENTITY)

    def test_real_SHA_gate_precedes_even_metadata_parsing(self):
        with self.assertRaisesRegex(ValueError,'SHA mismatch'):
            static_identity(synthetic_macho())

    def test_wrong_CPU_truncated_commands_and_stubs_are_rejected(self):
        original=synthetic_macho()
        for offset,value in [(4,7),(36,0),(0x15904,0xd65f03c0),(0x16244+8,0xd61f0220),(0x1a000,135),
                             (0x158fc,0xd51b4400),(0x158fc,0xd63f0100)]:
            b=bytearray(original);struct.pack_into('<I',b,offset,value)
            with self.subTest(offset=offset),self.assertRaises(ValueError):self.identity(bytes(b))
        for b in [b'',original[:28],original[:256]]:
            with self.assertRaises(ValueError):self.identity(b)

    def test_forged_import_label_is_rejected(self):
        b=bytearray(synthetic_macho());b[0x19001:0x19006]=b'_sqrt'
        with self.assertRaisesRegex(ValueError,'not _powf'):self.identity(bytes(b))

    def test_candidate_type_context_is_exact_and_does_not_call_pow(self):
        with patch('ctypes.CDLL',side_effect=AssertionError('no native load')):
            d=classify_result(CAPTURE,IDENTITY)
        self.assertFalse(d['historical_calls_GPU_full_helper_or_pipeline_certified'])
        self.assertTrue(d['observed_half_matches_ideal_real_power_half'])
        # This synthetic f32 is merely the rounded HALF widened to f32. The
        # exact-power test must reject its claim to be correctly rounded f32.
        self.assertFalse(d['ideal_real_power_correctly_RN_to_f32_for_this_input'])
        self.assertEqual(single_value(0x3d71e000).as_integer_ratio(),(1935,32768))
        self.assertEqual(single_value(0x3ed54000).as_integer_ratio(),(853,2048))

    def test_changed_inputs_count_thread_FPCR_GOT_or_UUID_fail_closed(self):
        for k,v in [('base_half_bits',0x2b90),('exponent_single_bits',0),('original_call_count',2),
                    ('thread_after',43),('fpcr_after',1),('fpcr_before',1<<22),('got_stable',0),
                    ('source_uuid','f'*32),('target_uuid','unknown'),('self_equal',True)]:
            d=copy.deepcopy(CAPTURE);d[k]=v
            with self.subTest(key=k),self.assertRaises(ValueError):classify_result(d,IDENTITY)

    def test_actual_target_identity_fields_are_mandatory_and_nearest_is_explicit(self):
        for k in ['target_image_basename','target_image_offset','target_symbol','target_symbol_exact']:
            d=copy.deepcopy(CAPTURE);del d[k]
            with self.subTest(key=k),self.assertRaises(ValueError):classify_result(d,IDENTITY)
        d=copy.deepcopy(CAPTURE);d['target_symbol_exact']=0
        self.assertEqual(classify_result(d,IDENTITY)['target_symbol_interpretation'],'nearest_symbol_only')

    def test_nonfinite_output_and_wrong_half_narrowing_rejected(self):
        for k,v in [('output_single_bits',0x7f800000),('output_single_bits',0x7fc00000),
                    ('output_single_bits',0x80000000),('output_half_bits',0x34ee)]:
            d=copy.deepcopy(CAPTURE);d[k]=v
            with self.subTest(key=k),self.assertRaises(ValueError):classify_result(d,IDENTITY)

    def test_machine_window_not_C_source_order_establishes_boundary(self):
        self.assertEqual(check_wrapper(DISASSEMBLY)['critical_calls'],1)
        for bad in [DISASSEMBLY+'\nmsr FPCR, x0\n',DISASSEMBLY.replace('blr x8','bl _powf'),
                    DISASSEMBLY.replace('blr x8','blr x8\nbl _other'),
                    DISASSEMBLY.replace('fcvt s1, h1','nop'),
                    DISASSEMBLY.replace('mrs x8, FPCR','nop',1)]:
            with self.assertRaises(ValueError):check_wrapper(bad)

    def test_Linux_preflight_and_run_cannot_load_or_compile_a_substitute(self):
        with tempfile.TemporaryDirectory() as tmp,patch('platform.system',return_value='Linux'), \
             patch('platform.machine',return_value='x86_64'), \
             patch('subprocess.run',side_effect=AssertionError('must not compile/load')):
            p=Path(tmp)
            d=preflight(p/'absent.dylib','26A434')
            self.assertEqual(d['native_calls'],0)
            self.assertEqual(d['status'],'blocked_before_compile_load_or_call')
            self.assertEqual(len(d['blockers']),3)
            with self.assertRaisesRegex(RuntimeError,'blocked_before'):
                run(p/'absent.dylib',p/'never-created','26A434')
            self.assertFalse((p/'never-created').exists())

    def test_collector_has_no_pow_substitution_or_FPCR_setter(self):
        source=Path(__file__).with_name('pow_read_call.c').read_text()
        self.assertNotIn('powf(',source)
        self.assertNotIn('fesetround',source)
        self.assertNotIn('msr ',source.lower())


if __name__ == '__main__':unittest.main()
