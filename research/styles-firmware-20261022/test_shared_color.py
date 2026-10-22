import hashlib,json,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from leaf_numeric import V,DomainUnknown
from joint_lab import JointRGB,concave_power,clipped
from guided_affine import A
from neutral_color_joint import enclose as color_enclose
from selective_neutral_joint import Inputs,enclose
from pixel_selective import SelectiveTexture
from semantic_tone import Curve1D
from whites_joint_ratio import enclose as whites_enclose

ROOT=Path(__file__).parent;E=ROOT/'evidence'


class SharedColorTests(unittest.TestCase):
    def test_source_checked_smooth_precision_and_original_whites_order(self):
        r=json.loads((E/'color-joint-contract-s20a.json').read_text());self.assertTrue(r['all_match']);self.assertEqual(len(r['constant_rows']),13);self.assertTrue(all(r['precision_checks'].values()));self.assertTrue(all(r['whites_order_checks'].values()));self.assertEqual(r['native_calls'],0)

    def test_same_saved_RGB_and_displacement_survive_original_mix_order(self):
        row=json.loads((E/'shared-color-s20b.json').read_text())['color_rows'][0];v=lambda d:V(np.array(d['lo']),np.array(d['hi']),'h',False);r=color_enclose(v(row['input_FG354']),v(row['weight389']));self.assertIsInstance(r.saturated,JointRGB);self.assertIsInstance(r.mixed,JointRGB);self.assertTrue(r.proof['source_RGB_shared_with_saturated_and_difference']);self.assertTrue(r.proof['original_half_subtract_multiply_add_order']);self.assertLess(float(np.max(r.mixed.hi-r.mixed.lo)),.7)

    def test_full_frozen_twelve_pixels_are_propagated_without_observed_input_substitution(self):
        r=json.loads((E/'shared-color-s20b.json').read_text());self.assertEqual(len(r['selective_rows']),12);self.assertTrue(all(v['JointRGB_reaches_warm409']for v in r['selective_rows']));self.assertFalse(r['observed_host_warm_cloud_used_as_input']);self.assertFalse(r['input_substitution_or_domain_shrink'])
        stages={v['name']:v for v in r['stages']}
        for name in ['saturated374','output392','warm409']:self.assertLess(stages[name]['max_width'],stages[name]['previous_S19_width']);self.assertEqual(stages[name]['clamped_box_RGB110_pixels'],0)
        self.assertTrue(all(v.get('range_covered',True)for v in r['set']['observations'].values()));self.assertTrue(all(v['half_bit_mismatches']==0 for v in r['point']['observations'].values()));self.assertEqual(len(r['set']['pixel_unknowns']),12);self.assertEqual(len(r['converted_negative_outer_pixels']),12);self.assertFalse(r['writer_set_really_generated'])

    def test_shared_root_proof_still_covers_saved_full_clamp_negative_witness(self):
        w=json.loads((E/'selective-domain-s18b.json').read_text());H=lambda x:V.value(x,point=False);r=enclose(Inputs(H(w['witness_rgb_half']),H(.4),H(.25),H(.2),SelectiveTexture(np.zeros((4,360,4),dtype='f2'),'zero lookup'),tuple(H([0,0])for _ in range(3)),H([0,0,0]),H(0)));native=np.array(w['native_converted_half']);self.assertTrue(np.all(native>=r.converted.lo)and np.all(native<=r.converted.hi));self.assertLess(r.converted.lo[2],0)

    def test_real_concave_secant_keeps_shared_input_and_nonlinear_remainder(self):
        def conditional_bounds(source,result,value):
            key=next(iter(source.terms));epsilon=(value-source.c)/source.terms[key];center=result.c+result.terms.get(key,0)*epsilon;radius=sum(abs(v)for k,v in result.terms.items()if k!=key)
            return center-radius,center+radius
        x=A.box(0,1);p=.4300000071525574;r=concave_power(x,p);lo,hi=r.bounds();self.assertLessEqual(lo,0);self.assertGreaterEqual(hi,1)
        self.assertIn(next(iter(x.terms)),r.terms)
        for t in [0,.01,.1,.4,.8,1]:
            low,high=conditional_bounds(x,r,t);self.assertLessEqual(low,t**p);self.assertGreaterEqual(high,t**p)
        source=A.box(-.2,1.2);result=clipped(source,-.2,1.2)
        for t in [-.2,0,.1,.5,.9,1,1.2]:
            low,high=conditional_bounds(source,result,t);expected=min(max(t,0),1);self.assertLessEqual(low,expected);self.assertGreaterEqual(high,expected)
        self.assertGreater(r.radius(),0);self.assertLess(x.add(x.neg()).bounds()[1]-x.add(x.neg()).bounds()[0],1e-10)

    def test_whites_product_is_finite_before_original_quotient_and_next_failure_retained(self):
        r=json.loads((E/'whites-joint-s20c.json').read_text());rows=[x for x in r['leaf_trace']if x['leaf']=='whites_curve'];self.assertEqual(len(rows),2)
        for row in rows:
            p=row['whites_observations']['joint_quotient_proof'];self.assertTrue(p['product_proved_finite_before_quotient']);self.assertTrue(p['original_product_then_divide_order_preserved']);self.assertLess(max(p['original_product42_absolute_upper']),65504);self.assertLess(max(p['original_quotient45_absolute_upper']),65504);self.assertGreater(p['original_z_hi'],1);self.assertLess(max(p['original_mix_intermediate_absolute_upper'].values()),65504)
        self.assertTrue(r['BG352_conditional_set_produced']);self.assertFalse(r['FG354_conditional_set_produced']);self.assertEqual(r['unknown_stage'],'FG354');self.assertEqual(r['first_unhandled_leaf']['leaf'],'contrast');self.assertFalse(r['complete_BG_runtime_verified']);self.assertTrue(all(x['covered']for x in r['known_prefix_coverage'].values()))

    def test_whites_nonzero_origin_and_outside_amount_fail_closed(self):
        c=V.bounds([0,0,0],[1,1,1]);z=V.bounds(2**-24,1);amount=V.bounds(.04,.04)
        with self.assertRaises(DomainUnknown):whites_enclose(c,z,amount,Curve1D((.001,.5,1),'nonzero origin'))
        with self.assertRaises(DomainUnknown):whites_enclose(c,z,V.bounds(-.1,-.1),Curve1D((0,.5,1),'zero origin'))
        with self.assertRaises(DomainUnknown):whites_enclose(V.bounds([0,0,0],[65504,1,1]),z,amount,Curve1D((0,.5,1),'zero origin'))
        with self.assertRaises(DomainUnknown):whites_enclose(c,V.bounds(.1,65504),amount,Curve1D((0,.5,1),'zero origin'))

    def test_neutral_shared_color_guard_does_not_relabel_nonzero_raw_parameter(self):
        from pre_skin_color import forward
        rgb=V.bounds([.2,.2,.2],[.3,.3,.3]);person=V.bounds(.4,.4);color=V.bounds(-2**-149,2**-149,'f');boost=V.bounds(4,4,'f')
        with patch('neutral_color_joint.enclose',side_effect=AssertionError('not exact raw zero')):r=forward(rgb,person,color,boost)
        self.assertNotIsInstance(r.output392,JointRGB)

    def test_this_test_source_was_hashed_before_test_execution(self):
        p=E/'test-binding-s20d.pre.json';r=json.loads(p.read_text());self.assertEqual(r['source_sha256_before_execution'][Path(__file__).name],hashlib.sha256(Path(__file__).read_bytes()).hexdigest());self.assertIn('unittest',r['command']);self.assertTrue(r['prior_S19_source_binding_limitation_preserved'])


if __name__=='__main__':unittest.main()
