"""Synthetic contracts. Real-media numbers are produced by the temporal command."""
from __future__ import annotations

import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from livephoto_hdr import NATIVE_BLOCK
from livephoto_hdr.apple_log import (
    BETA, C, DELTA, GAMMA, R0, RT, exponent_inverse, piecewise_inverse,
    piecewise_inverse_float32, toe_inverse, toe_threshold, unpack_code,
)
from livephoto_hdr.classify import classify
from livephoto_hdr.metrics import translation
from livephoto_hdr.motion import forward_backward_confidence, scene_flow
from livephoto_hdr.qt import _sensitive
from livephoto_hdr.safe_output import OutputRefused, allocate_output
from livephoto_hdr.timebase import alpha, edit_presentation, rational


class AppleLogTests(unittest.TestCase):
    def test_constants_and_continuity(self):
        self.assertEqual(R0, -0.05641088)
        self.assertEqual(RT, 0.01)
        self.assertEqual(C, 47.28711236)
        threshold = toe_threshold()
        self.assertAlmostEqual(float(exponent_inverse(threshold)), float(toe_inverse(threshold)), places=8)
        shadow = piecewise_inverse(np.array([0.0, threshold / 2]))
        self.assertTrue(np.allclose(shadow, toe_inverse(np.array([0.0, threshold / 2]))))
        bright = piecewise_inverse(np.array([threshold, DELTA]))
        self.assertTrue(np.allclose(bright, exponent_inverse(np.array([threshold, DELTA]))))

    def test_full_and_legal_ranges_differ(self):
        code = np.array([64, 512, 940])
        full = unpack_code(code, 10, "full")
        legal = unpack_code(code, 10, "legal")
        self.assertFalse(np.allclose(full, legal))
        self.assertAlmostEqual(full[1], 512 / 1023)

    def test_float32_path_is_separate(self):
        values = np.array([0.0, toe_threshold(), 0.5], dtype=np.float64)
        wide = piecewise_inverse(values)
        narrow = piecewise_inverse_float32(values)
        self.assertEqual(narrow.dtype, np.float32)
        self.assertTrue(np.max(np.abs(wide - narrow)) < 1e-5)


class TimeTests(unittest.TestCase):
    def test_rational_alpha_and_still_edit(self):
        self.assertEqual(alpha(Fraction(881, 600), Fraction(880, 600), Fraction(900, 600)), Fraction(1, 20))
        still = edit_presentation(0, [(746, -1), (1, 0)], 600, 600)
        self.assertEqual(still, Fraction(746, 600))
        self.assertEqual(rational(440, 600), Fraction(11, 15))
        self.assertEqual(rational(780, 600), Fraction(13, 10))

    def test_native_block_is_not_success(self):
        self.assertFalse(NATIVE_BLOCK["executed"])
        self.assertFalse(NATIVE_BLOCK["success"])
        self.assertEqual(NATIVE_BLOCK["cmImagingSPI"], "blocked")


class ClassifyTests(unittest.TestCase):
    def test_explicit_modes(self):
        self.assertEqual(classify(bypassed=True, delta_present=False, style_metadata_present=True, scene_thumbnail_present=True)["mode"], "bypassed")
        self.assertEqual(classify(bypassed=False, delta_present=True, style_metadata_present=True, scene_thumbnail_present=True)["mode"], "native-delta-coefficients")
        self.assertEqual(classify(bypassed=False, delta_present=False, style_metadata_present=True, scene_thumbnail_present=True)["mode"], "styled-scene-fallback")
        self.assertEqual(classify(bypassed=None, delta_present=True, style_metadata_present=True, scene_thumbnail_present=True)["mode"], "bypass-flag-absent")
        self.assertFalse(classify(bypassed=False, delta_present=True, style_metadata_present=True, scene_thumbnail_present=True)["nativeInverseExecuted"])


class SafeOutputTests(unittest.TestCase):
    def test_refuses_existing_and_protected_inputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            created = allocate_output(root / "new-output")
            self.assertTrue(created.is_dir())
            with self.assertRaises(OutputRefused):
                allocate_output(created)
            protected = root / "sample"
            protected.mkdir()
            with self.assertRaises(OutputRefused):
                allocate_output(protected / "inside", protected=[protected])


class MotionTests(unittest.TestCase):
    def test_translation_sign_and_flow(self):
        earlier = np.zeros((48, 64))
        earlier[10:30, 8:24] = 1
        later = np.roll(earlier, 5, axis=1)
        found = translation(earlier, later)
        self.assertAlmostEqual(found["dx"], 5, delta=0.2)
        self.assertAlmostEqual(found["dy"], 0, delta=0.2)
        image = earlier[::2, ::2]
        flow = scene_flow(image, image)
        self.assertEqual(flow.shape, (24, 32, 2))
        self.assertLess(float(np.mean(np.abs(flow))), 0.5)
        confidence = forward_backward_confidence(flow, flow)
        self.assertGreater(float(np.mean(confidence)), 0.5)


class PrivacyTests(unittest.TestCase):
    def test_location_keys_are_sensitive(self):
        self.assertTrue(_sensitive("com.apple.quicktime.location.ISO6709"))
        self.assertTrue(_sensitive("GPSLatitude"))
        self.assertFalse(_sensitive("com.apple.quicktime.content.identifier"))


if __name__ == "__main__":
    unittest.main()
