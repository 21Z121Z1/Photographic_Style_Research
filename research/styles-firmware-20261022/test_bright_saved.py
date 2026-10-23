"""Saved bright diagnostics/profile tests; no original-host entrypoint runs."""
from pathlib import Path
import unittest
from unittest.mock import patch
import numpy as np
from baseline_archive import encoded,sha
from bright137_witness import require_inverse_scope
from bright_low_host import forward as low
from bright_point_profile import Profile
from bright_saved_replay import arguments,bits,fingerprint,traced_forward
from context_color_api import load
from leaf_numeric import V

R=Path(__file__).parent
E=R/'evidence'


class SavedBrightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory=load(E/'bright-saved-replay-s29a.json')
        cls.result=load(E/'bright-residual-attribution-s29c.json')
        cls.profile=Profile(E/'bright-point-profile-s29c.json',sha(E/'bright-point-profile-s29c.json'))

    def args(self):
        d=load(E/'native-targets-s25c.json')
        return arguments(E/'second-context-s25a.json',d,d['rows'][0],0,1)[0]

    def test_original_certified137_downstream_all_saved_checkpoints_match(self):
        self.assertTrue(all(s['corrected_bit_mismatches']==0 for s in self.inventory['stages']))
        self.assertEqual(self.inventory['corrected_final_bits'],[8389,11169,9854])
        self.assertEqual(self.inventory['old_final_bits'],[8383,11170,9853])

    def test_residual_inventory_exactly_6_plus18_four_complete_inputs(self):
        self.assertEqual([r['half_bit_mismatches']for r in self.inventory['residual_rows']],
                         [6,0,3,6,6,3,0,0,0,0])
        self.assertEqual(len(self.inventory['unique_residual_inputs']),4)
        self.assertEqual(len(self.result['all24_residual_occurrences']),24)
        self.assertTrue(all(r['corrected_matches_saved_host']for r in self.result['all24_residual_occurrences']))

    def test_three_new_host_observers_stable_and_first_checkpoint137(self):
        d=load(E/'bright-traces-s29b.json')
        self.assertEqual(d['new_original_host_main_calls'],3)
        self.assertEqual(d['new_compilations'],0)
        self.assertFalse(d['original_iOS_or_GPU'])
        self.assertTrue(all(c['observer_stable']and c['first_observed_checkpoint_divergence']['SSA']==137 for c in d['calls']))
        for c in d['calls']:
            self.assertTrue(all(s['bit_mismatches']==0 for s in c['stages']if s['SSA']<=136))

    def test_independent_leaf_matches_all_saved_134_to138_nodes(self):
        for p in self.result['unique_points'].values():
            x=V.value(np.array(p['native132_half_bits'],dtype='u2').view('f2'))
            v=low(x)
            self.assertEqual(bits(v.s135),p['native135_half_bits'])
            self.assertEqual(bits(v.s136),p['native136_half_bits'])
            self.assertEqual(bits(v.s137),p['native137_half_bits'])
            self.assertEqual(bits(v.s138),next(s['host_bits']for s in p['corrected_stages']if s['SSA']==138))
            self.assertNotEqual(p['old_separate137_half_bits'],p['native137_half_bits'])

    def test_leaf_domain_boundary_and_type_rejections(self):
        r=low(V.value(np.array([1/16,.375,1],dtype='f2')))
        self.assertEqual(bits(r.s135),np.array([-11,-6,4],dtype='f2').view('u2').tolist())
        self.assertEqual(bits(r.s137),np.array([3.3125,1.75,8],dtype='f2').view('u2').tolist())
        for value in [V.value([.01,.2,.3]),V.value([.2,.3,1.01])]:
            with self.assertRaises(ValueError):low(value)
        for value in [V.value(.2),V.value([.2,.3,.4],'f'),V.bounds([.2,.3,.4],[.2,.3,.4],'h')]:
            with self.assertRaises(TypeError):low(value)

    def test_profile_replays_one_complete_input_without_native_or_global_patch(self):
        import pixel_bright
        original=pixel_bright.forward
        args=self.args()
        with patch('ctypes.CDLL',side_effect=AssertionError('no original execution in tests')):
            stages={}
            result=self.profile.forward(*args,observations=stages)
        self.assertEqual(bits(result),[8389,11169,9854])
        self.assertIs(pixel_bright.forward,original)
        old=traced_forward()(*args)
        self.assertEqual(bits(old),[8383,11170,9853])

    def test_profile_rejects_neighbor_wrong_working_stats_and_set(self):
        args=self.args()
        for position in [0,1,2,3,4]:
            values=list(args);raw=values[position].lo.astype('f2').view('u2').copy()
            if raw.shape:raw.flat[0]+=1
            else:raw=np.array(int(raw)+1,dtype='u2')
            values[position]=V.value(raw.view('f2'))
            with self.assertRaises(ValueError):self.profile.forward(*values)
        from dataclasses import replace
        values=list(args);values[5]=replace(args[5],s2_4=V.value(float(args[5].s2_4.lo)+.001,'f'))
        with self.assertRaises(ValueError):self.profile.forward(*values)
        values=list(args);values[0]=V.bounds(args[0].lo,args[0].lo,'h')
        with self.assertRaises(TypeError):self.profile.forward(*values)

    def test_profile_wrong_sha_rejected(self):
        with self.assertRaises(ValueError):Profile(self.profile.file,'0'*64).forward(*self.args())

    def test_static_register_map_is_pinned_to_exact_host_binary(self):
        d=load(E/'bright-machine-map-s29e2.json')
        self.assertEqual(d['SSA137_FMA_address'],'0xd014')
        self.assertEqual(d['SSA135_FMA_address'],'0xcfb8')
        self.assertEqual(d['trace_store_byte_offsets']['137'],480)
        self.assertTrue(d['register_lifetimes_checked_no_calls_or_operand_overwrites'])
        self.assertIn('FPCR was not measured',d['rounding_mode'])
        self.assertFalse(d['original_GPU_or_unobserved_SSA_full_graph_proof'])

    def test_v3_and_old_evidence_unchanged_and_inverse_guards_retained(self):
        p=load(E/'model-precision-v3-s25c6.json')
        self.assertTrue(all(sha(R/n)==h for n,h in p['model_source_sha256'].items()))
        old=load(E/'verification-s28.json')
        self.assertTrue(all(sha(E/n)==h for n,h in old['evidence_sha256'].items()))
        for cast,fields in [(16,frozenset({3})),(0,frozenset({2,3}))]:
            with self.assertRaises(ValueError):require_inverse_scope(cast,fields)


if __name__=='__main__':unittest.main()
