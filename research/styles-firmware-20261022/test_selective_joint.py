import json,unittest,tempfile
from dataclasses import replace
from decimal import Decimal,localcontext
from pathlib import Path
import numpy as np
from leaf_numeric import V,DomainUnknown
from pixel_selective import SelectiveTexture
from selective_neutral_joint import Inputs,enclose,POWER,INVERSE_POWER,P,N,Q,M
from contrast_span_joint import enclose as contrast_enclose
from complete_fixture import decode
from diagnose_internal_pixel import model_probes

ROOT=Path(__file__).parent/'evidence'


def fixture():
    b=json.loads((ROOT/'selective-baseline-s17a.json').read_text())['pixel_traces'][0];raw=b['input_raw'];rgb=V(np.array(raw['lo']),np.array(raw['hi']),'h',False);masks=[V(np.asarray(x['lo']),np.asarray(x['hi']),'h',False)for x in b['input_masks']];c=decode(json.loads((ROOT/'complete-context-s15a.json').read_text()));H=lambda x:V.bounds(x,x)
    return Inputs(rgb,*masks,SelectiveTexture(c.images[9],'saved zero lookup'),tuple(H([0,0])for _ in range(3)),H([0,0,0]),H(0))


class SelectiveJointTests(unittest.TestCase):
    def test_whole_source_and_gamma_joint_enclosure_never_clamps_negative_base(self):
        i=fixture();r=enclose(i);self.assertFalse(r.source.point);np.testing.assert_array_equal(r.source.lo,[0,0,0]);np.testing.assert_array_equal(r.source.hi,[1,1,1]);self.assertEqual(float(r.gamma.lo),1);self.assertEqual(float(r.gamma.hi),1)
        self.assertLess(float(np.max(r.converted.hi-r.converted.lo)),1.9);self.assertTrue(np.any(r.converted.lo<0))
        with self.assertRaises(DomainUnknown):r.converted.pow(r.gamma)
        self.assertNotEqual(POWER*INVERSE_POWER,1);self.assertGreater(np.max(abs(P@N-np.eye(3))),0);self.assertGreater(np.max(abs(Q@M-np.eye(3))),0)
        self.assertTrue(np.all(np.array(r.proof['RGB_before_half_error'])>0))

    def test_nonzero_lookup_or_offsets_fail_the_strict_neutral_contract(self):
        i=fixture();a=i.texture.values.copy();a[0,0,3]=np.float16(2**-24)
        with self.assertRaises(DomainUnknown):replace(i,texture=SelectiveTexture(a,'nonzero lookup'))
        with self.assertRaises(DomainUnknown):replace(i,amplitudes=V.bounds([0,.001,0],[0,.001,0]))
        with self.assertRaises(DomainUnknown):replace(i,output_mix=V.bounds(.1,.1))
        with self.assertRaises(TypeError):enclose(i.rgb)

    def test_first_saved_native_probes_and_static_constants_are_covered(self):
        receipt=json.loads((ROOT/'selective-one-pixel-s17a.json').read_text());r=enclose(fixture());byname={x['name']:x for x in receipt['rows']}
        self.assertEqual(sum(len(x['native_bits'])for x in receipt['rows']),33);self.assertTrue(all(x['point_bit_mismatches']==0 for x in receipt['rows']))
        for name,v in [('inverse_v',r.inverse_v),('inverse_root',r.inverse_root),('converted',r.converted),('gamma',r.gamma)]:
            row=byname[name];actual=np.array(row['native_bits'],dtype='u2'if row['precision']=='half'else'u4').view('f2'if row['precision']=='half'else'f4');self.assertTrue(np.all(actual>=v.lo)and np.all(actual<=v.hi),name)
        self.assertFalse(any(receipt['observer_stability'].values()));self.assertTrue(json.loads((ROOT/'color-constant-links-s17a.json').read_text())['all_match'])

    def test_remaining_bright_first_divergence_has_an_independent_native_target(self):
        c=decode(json.loads((ROOT/'complete-context-s15a.json').read_text()));saved=json.loads((ROOT/'native-complete-s15a.json').read_text());native={k:np.array(a,dtype='u2').view('f2')for k,a in saved['native_half_bits'].items()};receipt=json.loads((ROOT/'bright-residual-pixel-s17b.json').read_text());self.assertEqual(receipt['rows']['bright']['first_divergence']['SSA'],150)
        models,_=model_probes(c,native,(1,0));row=next(s for s in receipt['rows']['bright']['stages']if s['SSA']==150);actual=np.array(row['native_bits'],dtype='u2').view('f2');self.assertTrue(np.all(actual>0)and np.all(actual<1));self.assertEqual(row['bit_mismatches'],1);np.testing.assert_array_equal(models['bright'][1][149].lo.astype('f2').view('u2'),row['native_bits'])

    def test_BG_cell0_quotient_is_finite_before_the_product_and_else_is_kept(self):
        old=json.loads((ROOT/'bg-dependency-s15c.json').read_text());cell=next(c for c in old['partition']['unknown_subsets']if c['cell']==0);r=contrast_enclose(V(np.array(cell['input_lo']),np.array(cell['input_hi']),'h',False),V.value(old['amount_half'],point=False));p=r.proof
        self.assertTrue(p['half_quotient_finiteness_proved_before_product']);self.assertLess(float(r.quotient.hi),65504);self.assertLess(p['original_product_upper'],65504);self.assertTrue(np.all(r.output.lo<=r.changed.lo)and np.all(r.output.hi>=r.changed.hi));self.assertIn('else union',p['branch'])
        # Independent high-precision scalar error chains check the joint
        # inequality endpoints; these are not new leaf/native input cases.
        with localcontext()as ctx:
            ctx.prec=70;D=lambda x:Decimal.from_float(float(x));e=Decimal(2)**-10;t=Decimal(2)**-24;A=D(p['A_sqrt_D']);B=D(p['B_absolute']);L=D(min(r.changed.lo));H=D(max(r.changed.hi));C=H-L
            for sigma in [D(p['strict_span_lower']),Decimal('0.001'),Decimal('0.1'),Decimal('0.25')]:
                span=(sigma+t)/(1-e);newspan=min((1+e)*(span+A*span.sqrt()+B)+t,(1+e)*C+t);q=(1+e)*newspan/sigma+t;delta=(1+e)*span+t;product=(1+e)*delta*q+t
                self.assertLessEqual(q,D(r.quotient.hi));self.assertLessEqual(product,D(p['original_product_upper']))

    def test_native_probe_refuses_a_context_pairing_mismatch_before_compilation(self):
        from native_selective_pixel import check
        with tempfile.TemporaryDirectory(prefix='psr-pair-test-')as t:
            p=Path(t);data=json.loads((ROOT/'complete-context-s15a.json').read_text());data['identity']['build']='unverified';(p/'context.json').write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'do not match'):
                check(p/'missing-source.ll',p/'context.json',ROOT/'native-complete-s15a.json',ROOT/'selective-baseline-s17a.json',p/'output.json')
            self.assertFalse((p/'output.json').exists())
            from replay_selective_joint import check as replay
            with self.assertRaisesRegex(ValueError,'do not match'):
                replay(p/'context.json',ROOT/'native-complete-s15a.json',ROOT/'selective-baseline-s17a.json',ROOT/'selective-one-pixel-s17a.json',p/'output.json')
            self.assertFalse((p/'output.json').exists())

    def test_nine_consumers_are_unfinished_software_not_hardware_waits(self):
        r=json.loads((ROOT/'unresolved-software-s17.json').read_text());self.assertEqual(r['category'],'unfinished software tracking');self.assertFalse(r['hardware_wait_required_to_continue_static_tracking']);self.assertEqual(len(r['items']),9);self.assertEqual([v['SSRParams_byte']for v in r['items']],[512,536,540,544,548,552,560,604,608]);self.assertTrue(all('not unused'in v['status']for v in r['items']))


if __name__=='__main__':unittest.main()
