import hashlib,json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from baseline_archive import Archive,sha,compile_saved
from baseline_field3 import raw_scope,value_users

E=Path(__file__).parent/'evidence'
load=lambda n:json.loads((E/n).read_text())


class TraceableBaselineTests(unittest.TestCase):
    def fixture(self,name):
        root=Path(name);repo=root/'repo';repo.mkdir();compiler=root/'compiler';compiler.write_bytes(b'fixture compiler');a=Archive(root/'private'/'run',create=True,repo=repo,reserve_bytes=0,maximum_bytes=2**20);a.input('inputs/a.ll',b'fixture IR\n','synthetic compiler input');a.input('inputs/shim.c',b'int f(void){return 1;}\n','synthetic C');a.seal({'compiler':{'resolved_path':str(compiler.resolve()),'sha256':sha(compiler)}});return a,compiler,repo

    def fake_compile(self,args,**kwargs):
        for p in args[args.index('-dynamiclib')+1:args.index('-o')]:self.assertTrue(Path(p).is_file())
        Path(args[-1]).write_bytes(b'fixture compiled artifact');return SimpleNamespace(returncode=0,stdout=b'compile stdout',stderr=b'compile stderr')

    def test_private_archive_rejects_checkout_path_and_existing_run(self):
        with tempfile.TemporaryDirectory(prefix='psr-baseline-test-')as name:
            a,c,repo=self.fixture(name)
            with self.assertRaises(ValueError):Archive(repo/'bad',create=True,repo=repo,reserve_bytes=0)
            with self.assertRaises(FileExistsError):Archive(a.root,create=True,repo=repo,reserve_bytes=0)

    def test_exact_bytes_sealed_before_compile_and_never_overwritten(self):
        with tempfile.TemporaryDirectory(prefix='psr-baseline-test-')as name:
            a,c,repo=self.fixture(name);self.assertTrue(a.manifest()['sealed_before_compilation']);self.assertEqual(a.manifest()['files']['inputs/a.ll']['sha256'],hashlib.sha256(b'fixture IR\n').hexdigest());self.assertTrue(a.verify()['all_SHA_match'])
            with self.assertRaises(FileExistsError):a.write('inputs/a.ll',b'replacement')
            with self.assertRaises(ValueError):a.path('../escape')

    def test_precompile_input_tamper_stops_before_compiler(self):
        with tempfile.TemporaryDirectory(prefix='psr-baseline-test-')as name:
            a,c,repo=self.fixture(name);p=a.path('inputs/a.ll');p.unlink();p.write_bytes(b'changed')
            with patch('baseline_archive.subprocess.run')as call:
                with self.assertRaises(RuntimeError):compile_saved(a,c,['inputs/a.ll','inputs/shim.c'],'artifacts/lib','tamper')
                call.assert_not_called()

    def test_compiler_reads_persisted_files_and_logs_and_product_survive(self):
        with tempfile.TemporaryDirectory(prefix='psr-baseline-test-')as name:
            a,c,repo=self.fixture(name)
            with patch('baseline_archive.subprocess.run',side_effect=self.fake_compile):r=compile_saved(a,c,['inputs/a.ll','inputs/shim.c'],'artifacts/lib','ok')
            self.assertTrue(r['reads_only_persisted_inputs']);self.assertTrue(a.path('logs/ok.stderr').is_file());self.assertTrue(a.path('commands/ok.json').is_file());self.assertTrue(a.path('artifacts/lib').is_file());self.assertIn('<private_run>/inputs/a.ll',r['argv_redacted'])

    def test_postcompile_input_mutation_fails_with_logs_retained(self):
        with tempfile.TemporaryDirectory(prefix='psr-baseline-test-')as name:
            a,c,repo=self.fixture(name)
            def bad(args,**kw):
                p=a.path('inputs/a.ll');p.unlink();p.write_bytes(b'mutated by fixture');return self.fake_compile(args,**kw)
            with patch('baseline_archive.subprocess.run',side_effect=bad):
                with self.assertRaises(RuntimeError):compile_saved(a,c,['inputs/a.ll','inputs/shim.c'],'artifacts/lib','bad')
            self.assertTrue(a.path('logs/bad.stderr').exists());self.assertTrue(a.path('prepared.private.json').exists())

    def test_loaded_product_identity_is_checked_separately_from_inputs(self):
        with tempfile.TemporaryDirectory(prefix='psr-baseline-test-')as name:
            a,c,repo=self.fixture(name)
            with patch('baseline_archive.subprocess.run',side_effect=self.fake_compile):r=compile_saved(a,c,['inputs/a.ll','inputs/shim.c'],'artifacts/lib','ok')
            product={'artifacts/lib':r['product']};self.assertEqual(a.verify(product)['products_verified'],1);a.path('artifacts/lib').write_bytes(b'tampered product')
            with self.assertRaises(RuntimeError):a.verify(product)

    def test_memory_buffer_is_not_accepted_as_compiler_input_path(self):
        with tempfile.TemporaryDirectory(prefix='psr-baseline-test-')as name:
            a,c,repo=self.fixture(name)
            with patch('baseline_archive.subprocess.run')as call:
                with self.assertRaises(ValueError):compile_saved(a,c,['not-sealed.ll'],'artifacts/lib','bad')
                call.assert_not_called()

    def test_unknown_raw_parameter_alias_is_rejected(self):
        body='define void @f(ptr addrspace(1) %9){\n  %1 = bitcast ptr addrspace(1) %9 to ptr addrspace(1)\nret void\n}'
        with self.assertRaises(ValueError):raw_scope(body,'%9')

    def test_observation_sink_cannot_hide_an_extra_control_consumer(self):
        body='define void @f(half %357,ptr %observations){\n%obs_f0=fpext half %357 to float\n%obs_p0=getelementptr float,ptr %observations,i64 0\nstore float %obs_f0,ptr %obs_p0\nret void\n}'
        r=value_users(body,'%357',set());self.assertEqual(r[0]['kind'],'isolated observation store')
        with self.assertRaises(ValueError):value_users(body.replace('ret void','%bad=load float,ptr %obs_p0\nret void'),'%357',set())

    def test_fresh_actual_file_contract_covers_observed_and_plain_main(self):
        p=load('prepared-baseline-s24a.json');c=p['new_field3_contract'];self.assertTrue(c['all_checks_pass']);self.assertTrue(c['actual_persisted_files_audited']);self.assertFalse(c['producer']['raw_field3_read']);self.assertEqual(len(c['observed_main']['raw_pointer_scopes']),5);self.assertEqual(len(c['plain_main']['raw_pointer_scopes']),5);self.assertFalse(c['historical_whole_module_equality']);self.assertEqual(len(p['actual_compiler_inputs']),7)

    def test_only_eight_existing_controls_add_new_witness_layer(self):
        r=load('traceable-baseline-s24b.json');self.assertEqual(r['status'],'passed_new_finite_boundary_baseline');self.assertEqual(len(r['rows']),8);self.assertEqual(r['total_completed_original_kernel_calls'],270);self.assertEqual(r['new_146_state_search_calls'],0);self.assertFalse(r['original_host_all146_states_exhaustively_verified']);self.assertTrue(all(p['all_SHA_match']for p in r['input_and_product_proofs']));self.assertEqual(r['input_and_product_proofs'][-1]['name'],'after-run-final')

    def test_targeted_test_source_and_new_baseline_inputs_were_prebound(self):
        r=load('test-binding-s24d.pre.json');self.assertEqual(r['source_sha256_before_execution'][Path(__file__).name],sha(Path(__file__)));self.assertIn('prepared-baseline-s24a.json',r['input_sha256_before_execution']);self.assertIn('traceable-baseline-s24b.json',r['input_sha256_before_execution'])


if __name__=='__main__':unittest.main()
