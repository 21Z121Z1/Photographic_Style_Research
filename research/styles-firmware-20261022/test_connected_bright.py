"""S30 no-new-pipeline tests over saved MODEL records and rejection contracts."""
from pathlib import Path
from unittest.mock import patch
import copy,tempfile,unittest
import numpy as np
import complete_forward
from baseline_archive import encoded,sha
from bright_point_profile import Profile
from connected_bright import Dispatch,clone,source_run
from context_color_api import load
from leaf_numeric import V,DomainUnknown
from pixel_bright import BrightStats

R=Path(__file__).parent
E=R/'evidence'


def model_arguments(record):
    # Reconstitute a saved MODEL-produced tuple for unit dispatch tests only.
    args=[]
    for r in record['model_inputs']:
        ut,ft=('u2','f2')if r['precision']=='h'else('u4','f4')
        a=np.array(r['bits'],dtype=ut).view(ft).reshape(r['shape'])
        args.append(V.value(a,r['precision']))
    return (*args[:5],BrightStats(*args[5:]))


class ConnectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=load(E/'connected-bright-plan-s30a.json')
        cls.result=load(E/'connected-bright-result-s30b.json')
        cls.profile=Profile(E/cls.plan['profile'],cls.plan['profile_sha256'])
        cls.targets=[v for r in cls.result['rows']for v in r['visits']if v['mode']=='S29_profile_target']

    def test_four_complete_model_inputs_reach_original_whitelist_exactly(self):
        self.assertEqual(len(self.targets),4)
        approved=self.profile.checked()['points']
        for v in self.targets:
            self.assertTrue(v['guard_admitted']and v['exact_full_input_match'])
            self.assertEqual(v['model_input_key'],v['expected_input_key'])
            self.assertEqual(v['model_inputs'],approved[v['expected_input_key']]['complete_inputs'])
            self.assertEqual(v['input_differences'],[])

    def test_all_bright_checkpoints_and_full_observations_match(self):
        for v in self.targets:
            self.assertEqual(len(v['saved_bright_checkpoint_comparison']),52)
            self.assertTrue(all(s['bit_mismatches']==0 for s in v['saved_bright_checkpoint_comparison']))
        for row in self.result['rows']:
            self.assertEqual(row['status'],'model_source_to_bright_connected')
            self.assertEqual(row['compared_components'],1938)
            self.assertTrue(row['all_saved_observations_equal'])
            self.assertIsNone(row['first_differing_saved_checkpoint'])
            self.assertEqual(row['pixel_unknowns'],{})
            self.assertEqual(row['internal_unknowns'],{})

    def test_actual_writer_is_skin_branch_not_bright_selected_proof(self):
        for row in self.result['rows']:
            o=row['model_observations']
            self.assertEqual(o['selected404']['model_half_bits'],o['skin393']['model_half_bits'])
            self.assertEqual(row['writer_half_bit_mismatches'],0)
            self.assertFalse(row['bright_selected_to_writer_certified'])
        self.assertFalse(self.result['bright_selected_into_writer_tested'])

    def test_only_three_complete_model_runs_and_no_native_calls(self):
        self.assertEqual(self.result['full_model_calls'],3)
        self.assertEqual(self.result['new_kernel_calls'],0)
        self.assertEqual(self.result['new_compilations'],0)
        self.assertFalse(self.result['native_arrays_used_as_model_inputs'])
        self.assertTrue(self.result['full_frame_reference_phase_started_only_after_all_models_completed'])
        self.assertEqual(sum(len(r['visits'])for r in self.result['rows']),36)
        self.assertEqual(sum(v['mode']=='unchanged_v3_non_target'for r in self.result['rows']for v in r['visits']),32)

    def test_admitted_dispatch_uses_model_tuple_no_native_argument_builder_or_saved137(self):
        v=self.targets[0];args=model_arguments(v)
        dispatch=Dispatch(self.profile,{tuple(v['grid']):v['expected_input_key']})
        with patch('bright_saved_replay.arguments',side_effect=AssertionError('no native argument builder')), \
             patch('bright137_witness.Saved137.apply',side_effect=AssertionError('no saved operand application')), \
             patch('ctypes.CDLL',side_effect=AssertionError('no original library load')):
            out=dispatch(*args,grid=v['grid'])
        self.assertEqual(out.lo.astype('f2').view('u2').tolist(),v['bright_output_bits'])
        self.assertTrue(dispatch.visits[0]['guard_admitted'])

    def test_neighbor_target_rejected_before_profile_and_no_v3_fallback(self):
        v=self.targets[0];args=list(model_arguments(v));a=args[0].lo.astype('f2').view('u2').copy();a[0]+=1
        args[0]=V.value(a.view('f2'));dispatch=Dispatch(self.profile,{tuple(v['grid']):v['expected_input_key']})
        with patch.object(Profile,'forward',side_effect=AssertionError('must reject before arithmetic')), \
             patch('complete_forward.bright',side_effect=AssertionError('no target fallback')):
            with self.assertRaises(DomainUnknown):dispatch(*args,grid=v['grid'])
        self.assertEqual(len(dispatch.failures),1)
        self.assertFalse(dispatch.visits[0]['guard_admitted'])
        self.assertEqual(dispatch.visits[0]['input_differences'][0]['argument_index'],0)

    def test_available_writer_cannot_turn_rejected_target_into_pass(self):
        v=self.targets[0];args=list(model_arguments(v));args[0]=V.value([0,0,0])
        def fixture_clone(dispatch):
            def fixture_forward(context,*,point):
                try:dispatch(*args,grid=v['grid'])
                except DomainUnknown:pass
                return complete_forward.Result({},None,{}, {'fixture:bright400':'rejected target'},object(),True)
            return fixture_forward
        with patch('connected_bright.clone',side_effect=fixture_clone):
            _,record=source_run(E/self.plan['context'],self.plan['controls'][0],self.profile,self.plan)
        self.assertTrue(record['writer_generated'])
        self.assertFalse(record['target_input_connection_complete'])
        self.assertEqual(record['status'],'failed_or_unknown_no_oracle_fallback')
        self.assertFalse(record['native_intermediate_arrays_used_as_inputs'])

    def test_wrong_context_and_undeclared_control_rejected_before_model(self):
        with tempfile.TemporaryDirectory(prefix='psr-s30-context-')as name:
            p=Path(name)/'context.json';d=load(E/self.plan['context']);d['images_half_bits'][0][0][0][0]^=1;p.write_bytes(encoded(d))
            with patch('connected_bright.clone',side_effect=AssertionError('must reject before model')):
                with self.assertRaises(ValueError):source_run(p,self.plan['controls'][0],self.profile,self.plan)
        other=copy.deepcopy(self.plan['controls'][0]);other['raw_f32_bits']+=1
        with self.assertRaises(ValueError):source_run(E/self.plan['context'],other,self.profile,self.plan)

    def test_clone_does_not_patch_original_pipeline_or_bright(self):
        original=complete_forward.forward;bright=complete_forward.bright
        copied=clone(Dispatch(self.profile,{}))
        self.assertIsNot(copied,original)
        self.assertIs(complete_forward.forward,original)
        self.assertIs(complete_forward.bright,bright)

    def test_v3_243_sources_s29_profile_and_historical_evidence_unchanged(self):
        p=load(E/'model-precision-v3-s25c6.json')
        self.assertEqual(len(p['model_source_sha256']),243)
        self.assertTrue(all(sha(R/n)==h for n,h in p['model_source_sha256'].items()))
        old=load(E/'verification-s29.json')
        self.assertTrue(all(sha(E/n)==h for n,h in old['evidence_sha256'].items()))
        self.profile.checked()


if __name__=='__main__':unittest.main()
