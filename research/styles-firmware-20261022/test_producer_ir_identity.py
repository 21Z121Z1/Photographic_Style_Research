import hashlib,json,tempfile,unittest
from pathlib import Path
from producer_ir_identity import original_file,compare_originals

E=Path(__file__).parent/'evidence';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


class ProducerIdentityTests(unittest.TestCase):
    def test_missing_originals_never_get_normalized_hash_or_semantic_pass(self):
        r=compare_originals(None,None,'a'*64,'b'*64);self.assertFalse(r['raw_comparison_executed']);self.assertIsNone(r['normalized_pair_sha256']);self.assertEqual(r['semantic_equality'],'not established');self.assertFalse(r['whole_pipeline_equality'])

    def test_wrong_SHA_is_not_accepted_despite_provenance_declaration(self):
        with tempfile.TemporaryDirectory(prefix='psr-identity-test-')as name:
            p=Path(name)/'original.ll';p.write_text('define void @f(){ret void}\n');r=original_file(p,'f'*64,retained_execution_provenance=True);self.assertEqual(r['status'],'recorded_SHA_mismatch');self.assertFalse(r['admissible_historical_original'])

    def test_matching_reconstruction_bytes_cannot_masquerade_as_execution_input(self):
        with tempfile.TemporaryDirectory(prefix='psr-identity-test-')as name:
            p=Path(name)/'rebuilt.ll';p.write_text('define void @f(){ret void}\n');r=original_file(p,sha(p));self.assertTrue(r['sha_verified']);self.assertFalse(r['admissible_historical_original']);self.assertIn('origin_unproved',r['status'])

    def test_verified_raw_difference_keeps_FP_and_attribute_changes_unclassified(self):
        with tempfile.TemporaryDirectory(prefix='psr-identity-test-')as name:
            a=Path(name)/'a.ll';b=Path(name)/'b.ll';a.write_text('define float @f(float %x){%y=fadd fast float %x,1.0\nret float %y}\n');b.write_text('define float @f(float %x){%y=fadd float %x,2.0\nret float %y}\n');r=compare_originals(a,b,sha(a),sha(b),retained_execution_provenance=True);self.assertTrue(r['raw_comparison_executed']);self.assertFalse(r['byte_identical']);self.assertEqual(r['normalization_rules'],[]);self.assertIsNone(r['normalized_pair_sha256']);self.assertIn('unclassified',r['classification'])

    def test_raw_identity_does_not_imply_whole_pipeline_identity(self):
        with tempfile.TemporaryDirectory(prefix='psr-identity-test-')as name:
            p=Path(name)/'a.ll';p.write_text('define void @f(){ret void}\n');r=compare_originals(p,p,sha(p),sha(p),retained_execution_provenance=True);self.assertTrue(r['byte_identical']);self.assertFalse(r['whole_pipeline_equality'])

    def test_historical_audit_and_own_test_source_are_prebound(self):
        r=json.loads((E/'producer-identity-s23a.json').read_text());self.assertFalse(r['actual_pair']['raw_comparison_executed']);self.assertIsNone(r['normalized_pair_sha256']);self.assertEqual(r['new_original_kernel_calls'],0);self.assertEqual(r['unchanged_evidence_scope']['model_interface_states_exhaustively_searched'],146)
        p=json.loads((E/'test-binding-s23b.pre.json').read_text());self.assertEqual(p['source_sha256_before_execution'][Path(__file__).name],sha(Path(__file__)))


if __name__=='__main__':unittest.main()
