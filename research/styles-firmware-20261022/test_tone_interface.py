from dataclasses import replace
import unittest
import numpy as np
from negative_tone import ToneStats,NegativeToneContext,coefficients as negative
from positive_tone import PositiveToneContext,coefficients as positive
from positive_tone_skin import forward as old_skin
from tone_interface import RendererControls,ResolvedSceneType,SuppliedToneStats,ToneFrameContext,scale_controls,evaluate


def frame():
    return ToneFrameContext(SuppliedToneStats(ToneStats(.4,.5,.08,.06,.003,.05,.02,.008,.5),.4,.05),tuple([0.]*66))


class ToneInterfaceTests(unittest.TestCase):
    def test_distinct_scene_scaling_and_tuning_codes_without_hidden_clamp(self):
        tun=np.zeros(66);tun[59:65]=[.5,.25,.75,-.5,.5,.25]
        x=RendererControls(.8,.6,-.4)
        for code,expected in [(0,[.8,.6,-.4]),(3,[.6,.3,-.1]),(21,[.2,-.3,-.2])]:
            r=scale_controls(x,ResolvedSceneType(code),tuple(tun));np.testing.assert_allclose([r.intensity,r.tone,r.color],expected,rtol=2e-7)
        c=replace(frame(),tone_tuning=tuple(tun));r=evaluate(x,ResolvedSceneType(21),c)
        self.assertEqual(r.branch,'negative');self.assertEqual(r.controls.scene_type.code,21)

    def test_both_signs_reuse_existing_models_and_offsets_pack_exactly(self):
        c=frame()
        for tone in (-.5,0.,.5):
            r=evaluate(RendererControls(.5,tone,0),ResolvedSceneType(0),c)
            if tone<0:expected=negative(tone,NegativeToneContext(c.stats.negative_fields,c.tone_tuning))
            else:expected=positive(tone,PositiveToneContext(c.stats.positive_fields(),c.tone_tuning))
            np.testing.assert_array_equal(r.values,expected.values());self.assertEqual(len(r.ssr_block_f32(allow_approximation=True)),160)
            np.testing.assert_array_equal(np.frombuffer(r.ssr_block_f32(allow_approximation=True),dtype='<f4'),r.values.astype('f4'))
            self.assertEqual(r.named_fields()['fg.skinHighLights']['byte_offset'],592)
            self.assertEqual(r.named_fields()['semantic.personHR']['byte_offset'],644)
            self.assertFalse(r.pixel_pipeline_verified)

    def test_skin_adapter_reuses_only_two_fields_and_preserves_scope(self):
        r=evaluate(RendererControls(.5,.5,0),ResolvedSceneType(0),frame())
        rgb=np.array([[.2,.3,.4],[.7,.6,.5]],dtype='f4')
        np.testing.assert_array_equal(r.skin_only_forward(rgb,.4,.3,allow_approximation=True),old_skin(rgb,.4,.3,tone=.5))
        with self.assertRaises(ValueError):r.values[0]=3

    def test_domain_rejects_wrong_codes_scaled_outside_domain_and_negative_gap(self):
        c=frame()
        for code in (True,-1,2**32):
            with self.assertRaises(ValueError):ResolvedSceneType(code)
        with self.assertRaises(ValueError):evaluate(RendererControls(.5,-2**-25,0),ResolvedSceneType(0),c)
        tun=list(c.tone_tuning);tun[59]=16
        with self.assertRaises(ValueError):evaluate(RendererControls(.5,.5,0),ResolvedSceneType(3),replace(c,tone_tuning=tuple(tun)))
        with self.assertRaises(ValueError):evaluate(RendererControls(np.nan,0,0),ResolvedSceneType(0),c)


if __name__=='__main__':unittest.main()
