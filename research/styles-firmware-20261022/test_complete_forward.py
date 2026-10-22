import inspect,json,unittest
from dataclasses import replace
from itertools import product
from pathlib import Path
import numpy as np
from complete_fixture import context,encode,decode
from complete_forward import forward
from native_complete_check import comparisons
from leaf_numeric import V
from leaf_correlations import channel_span
from guided_precision import stages
from guided_conditioned import legacy
from native_ltm_roi_chain import fixture,model_inputs,EPSILON
from full_ltm_chain import generate

ROOT=Path(__file__).parent


class CompleteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context=decode(json.loads((ROOT/'evidence/complete-context-s15a.json').read_text()));cls.saved=json.loads((ROOT/'evidence/native-complete-s15a.json').read_text());cls.native={k:np.array(a,dtype='u2').view('f2')for k,a in cls.saved['native_half_bits'].items()}

    def test_saved_point_connection_observes_internal_errors_and_final_writer(self):
        r=forward(self.context,point=True);m=comparisons(self.native,r);self.assertFalse(r.pixel_unknowns);self.assertTrue(m['writer_known'])
        for n in ['raw_BG','raw_FG','BG_a','FG_a','FG_mean_a','precomputed335','output392','BW477','channel567','output600','writer']:self.assertEqual(m['observations'][n]['half_bit_mismatches'],0,n)
        # Final equality must not erase unselected/internal arithmetic differences.
        self.assertEqual(m['observations']['bright400']['half_bit_mismatches'],24);self.assertEqual(m['observations']['tonal468']['half_bit_mismatches'],7)
        np.testing.assert_array_equal(r.observations['writer'].lo[0],self.context.output_initial[0])

    def test_whole_set_stays_unknown_without_an_oracle_writer(self):
        r=forward(self.context,point=False);self.assertEqual(len(r.pixel_unknowns),12);self.assertIsNone(r.writer);self.assertNotIn('writer',r.observations);self.assertEqual(r.pixel_unknowns['0,0']['operator'],'selective413')
        self.assertTrue(all(v.get('range_covered',True)for v in comparisons(self.native,r)['observations'].values()))
        self.assertNotIn('maps',inspect.signature(forward).parameters)

    def test_raw_context_roundtrip_and_invalid_identity_or_buffers_rejected(self):
        c=context();d=decode(encode(c));np.testing.assert_array_equal(c.params.view('u4'),d.params.view('u4'));self.assertFalse(d.images[0].flags.writeable)
        with self.assertRaises(ValueError):replace(c,build='unknown')
        with self.assertRaises(TypeError):replace(c,stats=np.zeros(2659,dtype='f4'))
        with self.assertRaises(ValueError):replace(c,output_initial=np.full((5,6,3),0,dtype='f2'))
        p=c.params.copy();p.view('u4')[163]=7;self.assertEqual(int(replace(c,params=p).params.view('u4')[163]),7);self.assertEqual(c.params.view('u4')[163],2)

    def test_span_correlation_keeps_shared_vector_and_all_box_corners(self):
        for lo,hi in [([0,0,0],[1,.2,.3]),([.3,.4,.5],[.6,.7,.8]),([-.5,.1,2],[-.2,.3,3])]:
            x=V.bounds(lo,hi);r=channel_span(x);naive=x.max_channels()-x.min_channels();self.assertGreaterEqual(float(r.lo),0);self.assertLessEqual(float(r.hi),float(naive.hi))
            for corner in product(*zip(x.lo,x.hi)):
                p=V.value(corner);v=channel_span(p);self.assertGreaterEqual(float(v.lo),float(r.lo));self.assertLessEqual(float(v.hi),float(r.hi))
        same=V.bounds([.2]*3,[.2]*3);self.assertEqual(float(channel_span(same).lo),0)

    def test_saved_guided_all_f32_checkpoints_not_just_half_output(self):
        old=json.loads((ROOT/'evidence/guided-first-divergence-s15b.json').read_text())
        for row in old['rows']:
            f=fixture(row['fixture']);args,kw=model_inputs(f,(0,0),.2,True);g=generate(*args,**{k:v for k,v in kw.items()if k not in['consumer_semantic7','roi','reference196','person96']});d=stages(g.raw_fg.pixels.lo.astype('f2'),f['guide'],EPSILON,legacy);x,y=row['grid']
            for stage in row['stages']:np.testing.assert_array_equal(d[stage['name']][y,x].view('u4'),stage['native_f32_bits'])


if __name__=='__main__':unittest.main()
