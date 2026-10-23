import json
from dataclasses import replace
from pathlib import Path
import shutil
import tempfile
import unittest

from coordinator import Coordinator, HERE, Intent


class RegistryContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = Path(tempfile.mkdtemp(prefix='probe-', dir=HERE))
        self.input = self.temp/'input.json'
        self.input.write_text(json.dumps({'pattern': 'colors', 'height': 2, 'width': 2,
                                          'field3': 0, 'selection': 'context'}))
        self.coordinator = Coordinator()

    def tearDown(self):
        shutil.rmtree(self.temp)

    def request(self, capability='portable-image', intent=Intent.PORTABLE_MODEL):
        return self.coordinator.prepare(capability, intent, self.input, self.temp/'run')

    def test_real_cli_writes_four_pixels_as_model_only(self):
        result = self.coordinator.run(self.request())
        self.assertEqual(result.status, 'model_only')
        self.assertEqual(result.evidence_level, 'model_only')
        self.assertFalse(result.target_Apple_reference_compared)
        summary = json.loads((self.temp/'run/cli/summary.json').read_text())
        self.assertEqual(summary['runs'][0]['written_pixels'], 4)
        self.assertTrue((self.temp/'run/cli/colors-0/writer-diagnostic.png').is_file())
        self.assertIsNone(result.reason)

    def test_model_capability_cannot_be_promoted_by_native_intent(self):
        result = self.coordinator.run(self.request(intent=Intent.APPLE_NATIVE))
        self.assertEqual(result.status, 'blocked')
        self.assertIsNone(result.evidence_level)
        self.assertFalse((self.temp/'run/cli').exists())

    def test_prepared_native_collector_is_not_executable_evidence(self):
        result = self.coordinator.run(self.request('sealed-pow', Intent.APPLE_NATIVE))
        self.assertEqual(result.status, 'blocked')
        self.assertIn('prepared only', result.reason)
        self.assertFalse((self.temp/'run/cli').exists())

    def test_actual_cross_directory_dependency_is_derived_and_cannot_be_omitted(self):
        request = self.request()
        dependency = 'research/hdr-native/guided_reference_v3.py'
        self.assertIn(dependency, dict(request.source_snapshot))
        forged = replace(request, source_snapshot=tuple((p, h) for p, h in request.source_snapshot if p != dependency))
        result = self.coordinator.run(forged)
        self.assertEqual(result.status, 'blocked')
        self.assertIn('complete dependency set', result.reason)
        self.assertFalse((self.temp/'run/cli').exists())

    def test_one_stale_source_hash_blocks_before_execution(self):
        request = self.request()
        path, _ = request.source_snapshot[0]
        forged = replace(request, source_snapshot=tuple((p, '0'*64 if p == path else h)
                                                       for p, h in request.source_snapshot))
        result = self.coordinator.run(forged)
        self.assertEqual(result.status, 'blocked')
        self.assertFalse((self.temp/'run/cli').exists())

    def test_changed_input_bytes_block_and_existing_output_is_never_replaced(self):
        request = self.request()
        self.input.write_text(self.input.read_text()+'\n')
        result = self.coordinator.run(request)
        self.assertEqual(result.status, 'blocked')
        receipt = self.temp/'run/receipt.json'
        previous = receipt.read_bytes()
        with self.assertRaises(FileExistsError):
            self.coordinator.run(request)
        self.assertEqual(receipt.read_bytes(), previous)

    def test_historical_darwin_profile_does_not_admit_linux(self):
        import platform
        if platform.system() == 'Darwin':
            self.skipTest('This refusal probe specifically exercises Linux against the saved Darwin profile')
        result = self.coordinator.run(self.request('host-point-image'))
        self.assertEqual(result.status, 'blocked')
        self.assertIn('exact historical host profile', result.reason)
        self.assertFalse((self.temp/'run/cli').exists())


if __name__ == '__main__':
    unittest.main()
