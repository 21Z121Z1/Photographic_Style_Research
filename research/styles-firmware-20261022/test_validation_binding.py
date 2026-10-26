"""Receipt mutation checks on synthetic evidence, without native calls."""
from pathlib import Path
import tempfile
import unittest

from validate_portable import evidence_manifest, run


class EvidenceBindingTests(unittest.TestCase):
    def test_nested_mutation_addition_and_removal_change_identity(self):
        with tempfile.TemporaryDirectory() as folder:
            repository = Path(folder)
            root = repository / 'evidence'
            nested = root / 'scene' / 'input.json'
            nested.parent.mkdir(parents=True)
            nested.write_text('original')
            before = evidence_manifest(root, repository)
            self.assertEqual(set(before), {'evidence/scene/input.json'})
            nested.write_text('changed')
            self.assertNotEqual(before, evidence_manifest(root, repository))
            nested.write_text('original')
            added = root / 'new.bin'
            added.write_bytes(b'synthetic')
            self.assertNotEqual(before, evidence_manifest(root, repository))
            added.unlink()
            self.assertEqual(before, evidence_manifest(root, repository))
            nested.unlink()
            self.assertNotEqual(before, evidence_manifest(root, repository))

    def test_output_cannot_mutate_the_evidence_tree(self):
        import validate_portable
        output = validate_portable.ROOT / 'evidence' / 'must-not-be-created'
        self.assertFalse(output.exists())
        with self.assertRaises(ValueError):
            run(output)
        self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
