"""S33 saved-report and failure-path tests. No new native load/call/compile."""
from pathlib import Path
from unittest.mock import patch
import copy,ctypes,re,tempfile,unittest
from baseline_archive import Archive,sha
from context_color_api import load
from fpcr_binding import Report,run
from verify_fpcr_binding import check_report,check_window

R=Path(__file__).parent
E=R/'evidence'


class FPCRBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prepared=load(E/'fpcr-prepared-s33a.json');cls.current=load(E/'fpcr-current-run-s33b.json')
        cls.archive=Archive(R.parents[1].parent/cls.prepared['private_storage_relative_to_task'])
        cls.raw=cls.archive.path('run/report.bin').read_bytes();cls.plan=cls.prepared['plan']
        cls.expected=next(r for r in load(E/'sqrt-domain-certificate-s32c.json')['rows']if r['input_half_bits']==0x3880)

    def check(self,p=None,d=None):
        return check_report(bytes(p)if p is not None else self.raw,d or self.current,self.plan,self.expected)

    def report(self):return Report.from_buffer_copy(self.raw)

    def test_saved_report_is_one_current_native_thread_with_RN_no_new_load(self):
        with patch('ctypes.CDLL',side_effect=AssertionError('No native load in report replay')):
            p=self.check()
        self.assertEqual(len(self.raw),ctypes.sizeof(Report));self.assertEqual(len(self.raw),72)
        self.assertEqual(p.fpcr_before,0);self.assertEqual(p.fpcr_after,0)
        self.assertEqual(p.thread_before,4036989);self.assertEqual(p.thread_after,4036989)
        self.assertEqual(p.original_call_count,1)

    def test_wrong_or_truncated_ABI_is_rejected(self):
        for raw in [b'',self.raw[:-1],self.raw+b'\0']:
            with self.assertRaises(ValueError):check_report(raw,self.current,self.plan,self.expected)

    def test_failed_thread_query_is_not_same_thread_evidence(self):
        p=self.report();p.thread_query_after=-1
        with self.assertRaisesRegex(ValueError,'query failed'):self.check(p)

    def test_different_thread_or_pthread_identity_is_rejected(self):
        p=self.report();p.thread_after+=1
        with self.assertRaisesRegex(ValueError,'same thread'):self.check(p)
        p=self.report();p.self_after+=8
        with self.assertRaisesRegex(ValueError,'same thread'):self.check(p)

    def test_changed_FPCR_at_boundary_is_rejected(self):
        p=self.report();p.fpcr_after=1<<22
        with self.assertRaisesRegex(ValueError,'RN binding'):self.check(p)

    def test_stable_nonRN_is_not_relabelled_RN(self):
        for mode in [1,2,3]:
            p=self.report();p.fpcr_before=p.fpcr_after=mode<<22
            with self.assertRaisesRegex(ValueError,'RN binding'):self.check(p)

    def test_zero_or_multiple_calls_violate_the_fixed_budget(self):
        for count in [0,2]:
            p=self.report();p.original_call_count=count
            with self.assertRaisesRegex(ValueError,'budget'):self.check(p)

    def test_exact_input_and_both_output_formats_are_checked(self):
        p=self.report();self.assertEqual(p.input_half_bits,0x3880)
        self.assertEqual(p.input_single_bits,0x3f100000)
        self.assertEqual(p.output_single_bits,0x3f400000);self.assertEqual(p.output_half_bits,0x3a00)
        for field in ['input_half_bits','input_single_bits','output_single_bits','output_half_bits']:
            p=self.report();setattr(p,field,getattr(p,field)+1)
            with self.assertRaises(ValueError):self.check(p)

    def test_public_success_label_cannot_mask_raw_or_derived_metadata_mismatch(self):
        for field,value in [('output_half_bits',0x3a01),('same_thread_binding',False),('native_return_code',-3),('RMode_after',1)]:
            d=copy.deepcopy(self.current);d[field]=value
            with self.assertRaises(ValueError):self.check(d=d)

    def test_actual_static_window_and_injected_FPCR_write_or_extra_call(self):
        text=self.archive.path('logs/disassembly.stdout').read_text()
        d=check_window(text)
        self.assertEqual(d['critical_instruction_sha256'],self.prepared['critical_window_instruction_sha256'])
        self.assertEqual(d['FPCR_write_count'],0)
        with self.assertRaisesRegex(ValueError,'write'):check_window(text+'\n0: msr FPCR, x0\n')
        corrupt=re.sub(r'(508:\s+blr\s+x8)',r'\1\n     50a: bl 0x0',text)
        self.assertNotEqual(corrupt,text)
        with self.assertRaisesRegex(ValueError,'One synchronous'):check_window(corrupt)

    def test_existing_one_call_marker_prevents_even_loading_or_writing_again(self):
        with tempfile.TemporaryDirectory(prefix='psr-s33-marker-test-')as tmp, \
             patch('ctypes.CDLL',side_effect=AssertionError('Native library must not load')), \
             patch.object(Archive,'write',side_effect=AssertionError('Existing run must not write')):
            with self.assertRaisesRegex(RuntimeError,'already started'):
                run(E/'fpcr-prepared-s33a.json',Path(tmp)/'never-created.json')

    def test_scope_remains_current_primitive_with_new_wrapper_FCVTs(self):
        self.assertTrue(self.current['half_conversions_are_new_wrapper_not_old_half_helper'])
        self.assertFalse(self.current['historical_runs_other_threads_GPU_or_pipeline_certified'])
        self.assertEqual(self.current['FPCR_writes_or_mode_changes'],0)
        self.assertFalse(load(E/'sqrt-static-s32a.json')['FPCR_runtime_state_measured'])
        self.assertFalse(load(E/'verification-s32.json')['actual_FPCR_measured'])
        sources=(R/'fpcr_read_call.c').read_text().lower()
        self.assertNotIn('msr ',sources);self.assertNotIn('fesetround',sources)

    def test_v3_and_old_evidence_are_immutable(self):
        v3=load(E/'model-precision-v3-s25c6.json')
        self.assertEqual(len(v3['model_source_sha256']),243)
        self.assertTrue(all(sha(R/n)==h for n,h in v3['model_source_sha256'].items()))
        self.assertTrue(all(sha(E/n)==h for n,h in load(E/'verification-s32.json')['evidence_sha256'].items()))


if __name__=='__main__':unittest.main()
