import hashlib,json,tempfile,unittest
from pathlib import Path
import numpy as np
from active_color import Color,replace_color,half_cell
from complete_fixture import decode
from complete_forward import forward
from guided_affine import A
from semantic_shared import cap_one,mix
from bound_validation import run

ROOT=Path(__file__).parent;E=ROOT/'evidence'
load=lambda n:json.loads((E/n).read_text())


class ActiveControlTests(unittest.TestCase):
    def test_internal_typed_control_changes_only_raw_field3(self):
        base=decode(load('complete-context-s15a.json'));new=replace_color(base,Color(np.float32(.3)));self.assertEqual(np.flatnonzero(base.params.view('u4')!=new.params.view('u4')).tolist(),[3]);self.assertTrue(all(np.array_equal(a,b)for a,b in zip(base.images,new.images)))
        for invalid in [.3,np.float64(.3),np.float32(-.1),np.float32(np.nan)]:
            with self.assertRaises(TypeError):Color(invalid)

    def test_half_bin_exact_endpoints_and_even_odd_ties(self):
        for center in [np.float16(.3),np.nextafter(np.float16(.3),np.float16(np.inf))]:
            cell=half_cell(Color(np.float32(center)));first=np.array(cell['first_f32_bits'],dtype='u4').view('f4')[()];last=np.array(cell['last_f32_bits'],dtype='u4').view('f4')[()]
            self.assertEqual(np.float16(first),center);self.assertEqual(np.float16(last),center);self.assertNotEqual(np.float16(np.nextafter(first,np.float32(-np.inf))),center);self.assertNotEqual(np.float16(np.nextafter(last,np.float32(np.inf))),center)
            self.assertEqual(cell['lower_closed'],int(center.view('u2'))%2==0)
        self.assertEqual(half_cell(Color(np.float32(.3)))['f32_values'],8191)

    def test_exact_pointer_audit_tracks_nested_full_params_callee(self):
        r=load('color-contract-s21b.json');self.assertTrue(r['all_checks_pass']);self.assertEqual(len(r['original_pointer_paths']),6);child=next(v for v in r['original_pointer_paths']if 'getBWChannelMixFromStats'in v['function']);self.assertEqual([v['field']for v in child['fields']],[0]);self.assertFalse(r['GPU_verified'])

    def test_nonzero_effect_is_observed_before_and_after_writer(self):
        r=load('active-analysis-s21d.json');active=r['rows'][3];self.assertEqual(active['native_effect_vs_raw_zero']['saturated374']['different_half_components'],36);self.assertEqual(active['native_effect_vs_raw_zero']['output392']['different_half_components'],36);self.assertEqual(active['native_effect_vs_raw_zero']['writer']['different_half_components'],35)
        host=load('native-active-s21c.json');self.assertEqual(host['metrics']['contexts'],5);self.assertEqual(host['metrics']['original_kernel_calls'],510);self.assertEqual(host['metrics']['observer_writer_half_bit_mismatches'],0)
        for row in r['rows']:self.assertEqual(sum(v['half_bit_mismatches']for v in row['point']['observations'].values()),0)

    def test_two_different_half_controls_have_same_original_writer(self):
        r=load('active-analysis-s21d.json');pair=next(v for v in r['pairs']if v['indices']==[1,2]);self.assertEqual(pair['classification'],'indistinguishable_at_saved_host_writer');self.assertTrue(pair['all_scientific_RGB_intermediates_equal']);self.assertNotEqual(r['rows'][1]['control']['half357_bits'],r['rows'][2]['control']['half357_bits']);self.assertEqual(r['rows'][1]['control']['gain364_bits'],r['rows'][2]['control']['gain364_bits']);self.assertFalse(pair['unique_parameter_recovery_proved'])

    def test_bounded_platform_is_not_unique_or_unknown_source_inverse(self):
        r=load('active-analysis-s21d.json');p=r['positive_gain_one_plateau'];self.assertTrue(p['strictly_below_midpoint']);self.assertTrue(p['protection_f32_max_selects_constant_point2']);self.assertLess(p['one_plus_square_upper'],p['half_one_next_midpoint']);self.assertIn('unknown-source',r['conditional_inverse_status']['unproved']);self.assertFalse(r['original_GPU_or_real_frame_verified'])

    def test_original_min_has_no_added_lower_clamp_and_shares_same_value(self):
        x=A.box(-.2,1.2);r=cap_one(x);self.assertLess(r.bounds()[0],0)
        key=next(iter(x.terms))
        for value in [-.2,0,.5,1,1.2]:
            center=r.c+r.terms.get(key,0)*(value-x.c)/x.terms[key];radius=sum(abs(v)for k,v in r.terms.items()if k!=key);self.assertLessEqual(center-radius,min(value,1));self.assertGreaterEqual(center+radius,min(value,1))
        self.assertIs(mix(x,x,A.box(0,1)),x)

    def test_auxiliary_relation_is_opt_in_and_keeps_first_unknown(self):
        r=load('active-analysis-s21d.json')['auxiliary_shared_semantic'];self.assertFalse(r['default_backend_changed']);self.assertLess(r['independent_vs_shared_widths']['FG354']['shared'],.1);self.assertFalse(r['writer_set_really_generated'])
        for result in r['results'].values():self.assertEqual(result['first_unknown'][1]['operator'],'outer color355..392');self.assertFalse(result['writer_known'])
        c=decode(load('active-contexts-s21b.json')['rows'][3]['context']);point=forward(c,point=True,shared_semantic=True);self.assertTrue(point.writer is not None)

    def test_explicit_input_binding_detects_mutation_and_keeps_failed_receipt(self):
        with tempfile.TemporaryDirectory(prefix='psr-binding-test-')as name:
            root=Path(name);source=root/'input';source.write_text('before');target=root/'result.json'
            with self.assertRaises(RuntimeError):run('expected-input-mutation',target,['python3','-c','from pathlib import Path;Path('+repr(str(source))+').write_text("after")'],explicit_inputs=[source])
            self.assertFalse(json.loads(target.read_text())['explicit_inputs_unchanged_during_command']);self.assertTrue(target.with_name('result.pre.json').exists())

    def test_this_test_file_and_inputs_were_bound_before_running(self):
        r=load('test-binding-s21f.pre.json');self.assertEqual(r['source_sha256_before_execution'][Path(__file__).name],hashlib.sha256(Path(__file__).read_bytes()).hexdigest());self.assertIn('native-active-s21c.json',r['input_sha256_before_execution']);self.assertIn('unittest',r['command'])


if __name__=='__main__':unittest.main()
