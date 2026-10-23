"""Drive candidate A's public request boundary against actual repository inputs."""
from dataclasses import FrozenInstanceError
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from execution import Study, Selection, RenderedModel, Rejected

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / 'research/styles-firmware-20261022/evidence'
CONTEXT = EVIDENCE / 'complete-context-s15a.json'
PRECISION = EVIDENCE / 'model-precision-v3-s25c6.json'
GUIDED = Path('research/hdr-native/guided_reference_v3.py')


class ExecutionTests(unittest.TestCase):
    def test_saved_Darwin_contract_cannot_be_accepted_on_this_Linux_host(self):
        with tempfile.TemporaryDirectory() as folder:
            result = Study.reference(ROOT, CONTEXT, PRECISION, Path(folder)/'missing.dylib').run(Path(folder)/'run')
            self.assertIsInstance(result, Rejected)
            self.assertEqual(result.code, 'reference_runtime_mismatch')
            self.assertIn('system', result.reasons)
            receipt = json.loads((Path(folder)/'run/receipt.json').read_text())
            self.assertEqual(receipt['intent'], 'apple_cpu_reference')
            self.assertIsNone(receipt['evidence_level'])
            self.assertEqual(receipt['native_calls_performed'], 0)

    def test_real_source_to_writer_is_useful_but_has_only_model_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            request = Study.portable(ROOT, CONTEXT, selection=Selection.BRIGHT16)
            result = request.run(Path(folder)/'run')
            self.assertIsInstance(result, RenderedModel)
            self.assertEqual(result.written_pixels, 12)
            self.assertTrue(result.writer_path.is_file())
            receipt = json.loads((Path(folder)/'run/receipt.json').read_text())
            self.assertEqual(receipt['evidence_level'], 'portable_model')
            self.assertIn(str(GUIDED), receipt['source_sha256'])
            self.assertIn('research/semantic-styles/semantic_curve_inverse.py', receipt['source_sha256'])
            self.assertEqual(receipt['input_sha256'], hashlib.sha256(CONTEXT.read_bytes()).hexdigest())
            self.assertEqual(receipt['native_calls_performed'], 0)
            with self.assertRaises(FrozenInstanceError):
                result.evidence_level = 'native'
            with self.assertRaises(TypeError):
                RenderedModel(result.writer_path, result.writer_sha256, 12, (), evidence_level='native')
            with self.assertRaises(FileExistsError):
                request.run(Path(folder)/'run')

    def mini_repo(self, folder):
        repo = Path(folder)
        (repo/GUIDED).parent.mkdir(parents=True)
        shutil.copyfile(ROOT/GUIDED, repo/GUIDED)
        shutil.copyfile(CONTEXT, repo/'context.json')
        subprocess.run(['git', 'init', '-q', str(repo)], check=True)
        subprocess.run(['git', '-C', str(repo), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(repo), '-c', 'user.name=Prototype', '-c', 'user.email=prototype@example.invalid',
                        'commit', '-qm', 'Track actual historical guided source and context'], check=True)
        return repo

    def test_cross_directory_dependency_edit_blocks_before_model_loading(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = self.mini_repo(folder)
            request = Study.portable(repo, repo/'context.json')
            (repo/GUIDED).write_bytes((repo/GUIDED).read_bytes()+b'\n# changed after preparing exact identity\n')
            with patch('execution._modules', side_effect=AssertionError('No model after changed source')):
                result = request.run(repo/'run')
            self.assertEqual(result.code, 'source_identity_changed')
            self.assertFalse((repo/'run/writer.npy').exists())

    def test_changed_exact_context_blocks_even_when_only_whitespace_changed(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = self.mini_repo(folder)
            request = Study.portable(repo, repo/'context.json')
            (repo/'context.json').write_bytes((repo/'context.json').read_bytes()+b'\n')
            with patch('execution._modules', side_effect=AssertionError('No model after changed input')):
                result = request.run(repo/'run')
            self.assertEqual(result.code, 'input_identity_changed')

    def test_caller_cannot_choose_evidence_level_or_prune_source_capture(self):
        with self.assertRaises(TypeError):
            Study.portable(ROOT, CONTEXT, selection='experimental_bright16')
        with self.assertRaises(TypeError):
            Study.portable(ROOT, CONTEXT, evidence_level='Apple_verified')
        with self.assertRaises(TypeError):
            Study.portable(ROOT, CONTEXT, source_paths=['image_chain.py'])


if __name__ == '__main__':
    unittest.main()
