import copy,json,tempfile,unittest
from dataclasses import asdict,replace
from pathlib import Path
from unittest.mock import patch
import numpy as np
from baseline_archive import sha,encoded
from context_color_api import BoundCatalog,Target,strict_bits,identity
from joint_color_api import SharedField3,Observation,Contract,compatible,solve_joint,solve_request,FIELD,V3,VERSION
from raw_f32_sets import Interval,real,normalize,intersection,difference,population,same_members

R=Path(__file__).parent;E=R/'evidence'
load=lambda p:json.loads(Path(p).read_text())


def closed(lo,hi):return Interval(lo,hi,real(lo),real(hi),True,True)
def members(items):return {n for a in items for n in range(a.first,a.last+1)}


class RawIntervalTests(unittest.TestCase):
    def test_small_finite_sets_against_independent_integer_enumeration(self):
        samples=[closed(lo,hi)for lo in range(4)for hi in range(lo,5)]
        for a in samples:
            for b in samples:
                self.assertEqual(members(intersection((a,),(b,))),members((a,))&members((b,)))
                self.assertEqual(members(difference((a,),(b,))),members((a,))-members((b,)))
                self.assertEqual(members(normalize((a,b))),members((a,))|members((b,)))

    def test_open_endpoint_geometry_is_preserved(self):
        d=load(E/'changed-class-queries-s26c2.json')['changed_class_queries'];a=Interval.read(d['first:7']['candidate_union'][0]);b=Interval.read(d['second:7']['candidate_union'][0]);result=intersection((a,),(b,));self.assertEqual(population(result),860159);self.assertFalse(result[0].lower_closed);self.assertFalse(result[0].upper_closed);self.assertEqual(result[0].record()['first_f32_hex'],'0x3d961001')

    def test_touching_closed_endpoint_is_singleton_open_touch_is_empty(self):
        a=closed(100,103);b=closed(103,106);one=intersection((a,),(b,));self.assertEqual(population(one),1);self.assertTrue(one[0].lower_closed and one[0].upper_closed);open_upper=Interval(100,102,real(100),real(103),True,False);self.assertEqual(intersection((open_upper,),(b,)),())

    def test_difference_retains_complement_closure_and_population(self):
        whole=closed(100,110);cut=Interval(104,106,real(103),real(107),False,False);pieces=difference((whole,),(cut,));self.assertEqual(population(pieces),8);self.assertTrue(pieces[0].upper_closed);self.assertTrue(pieces[1].lower_closed);self.assertEqual(members(pieces),set(range(100,111))-{104,105,106})

    def test_adjacent_and_overlapping_ranges_do_not_double_count(self):
        r=normalize((closed(100,103),closed(104,106),closed(102,105)));self.assertEqual(population(r),7);self.assertEqual(len(r),1)

    def test_inconsistent_flags_population_and_outside_domain_rejected(self):
        with self.assertRaises(ValueError):Interval(100,103,real(100),real(103),False,True)
        with self.assertRaises(ValueError):Interval(-1,1,0.,real(1),True,True)
        d=closed(100,103).record();d['f32_population']=5
        with self.assertRaises(ValueError):Interval.read(d)
        with self.assertRaises(TypeError):Interval(100,103,real(100),real(103),1,True)


class JointColorAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.precision=E/'model-precision-v3-s25c6.json';cls.plan=E/'color-partition-s22a.json';cls.first=BoundCatalog(E/'complete-context-s15a.json',cls.precision,cls.plan,E/'first-context-catalog-v3-s26c.json',sha(E/'first-context-catalog-v3-s26c.json'));cls.second=BoundCatalog(E/'second-context-s25a.json',cls.precision,cls.plan,E/'context-catalog-s25e.json',sha(E/'context-catalog-s25e.json'));cls.a=cls.first.checked();cls.b=cls.second.checked();cls.declaration=SharedField3(True)

    def observation(self,side,state,name=None,handle=None):
        h=handle or(self.first if side=='first'else self.second);ident=(self.a if side=='first'else self.b)[0];row=(self.a if side=='first'else self.b)[3][state];return Observation(name or side,h,Target(ident,h.expected_catalog_sha256,strict_bits(row['writer_half_bits'])))

    def solve(self,first=7,second=7,first_handle=None):return solve_joint((self.observation('first',first,handle=first_handle),self.observation('second',second)),shared_parameter=self.declaration)

    def partial(self,path,*,missing=(),unknown=()):
        ident,manifest,p,rows=self.a;copied=[]
        for i,row in rows.items():
            if i in missing:continue
            row=copy.deepcopy(row)
            if i in unknown:row['writer_known']=False;row.pop('writer_half_bits',None);row.pop('writer_sha256',None)
            copied.append(row)
        chunk=path/'simulated-chunk.json';chunk.write_bytes(encoded({'identity':asdict(ident),'partition_sha256':sha(self.plan),'rows':copied,'fixture_only':'removal/unknown simulation of existing rows; no new evaluation'}));catalog=path/'simulated-catalog.json';catalog.write_bytes(encoded({'schema':'psr-context-catalog-v1','identity':asdict(ident),'partition_sha256':sha(self.plan),'chunks':[{'name':chunk.name,'sha256':sha(chunk)}],'fixture_only':True,'new_forward_evaluations':0}));return replace(self.first,catalog_file=catalog,expected_catalog_sha256=sha(catalog))

    def test_state7_joint_equals_stronger_second_with_no_extra_gain(self):
        r=self.solve();self.assertEqual(r['confirmed_joint_interface_state_ids'],[7]);self.assertEqual(r['confirmed_model_f32_population'],860159);self.assertEqual(r['possible_f32_population'],860159);self.assertEqual(r['information']['joint_equal_to_single_possible_sets'],['second']);self.assertEqual(r['information']['extra_population_reduction_beyond_smallest_single'],0);self.assertFalse(r['information']['strictly_smaller_than_every_single_possible_set']);self.assertEqual(r['joint_class_acceptance'],'model_only')

    def test_zero_one_platform_stays_multiple(self):
        r=self.solve(0,0);self.assertEqual(r['confirmed_joint_interface_state_ids'],[0,1]);self.assertEqual(r['possible_f32_population'],1018499073);self.assertFalse(r['unique_parameter_claim']);self.assertEqual(r['possible_joint_candidates'][0]['first_f32_bits'],0)

    def test_incompatible_targets_empty_without_individual_invalidity(self):
        r=self.solve(7,93);self.assertEqual(r['possible_joint_candidates'],[]);self.assertTrue(r['all_individual_possible_sets_nonempty']);self.assertFalse(r['single_target_invalidity_claim']);self.assertFalse(r['nearest_fallback_used']);self.assertFalse(r['information']['information_gain_interpretation_applicable'])

    def test_shared_declaration_cannot_be_omitted_false_or_ui_alias(self):
        observations=(self.observation('first',7),self.observation('second',7))
        with self.assertRaises(TypeError):solve_joint(observations)
        with self.assertRaises(TypeError):solve_joint(observations,shared_parameter=None)
        with self.assertRaises(ValueError):SharedField3(False)
        with self.assertRaises(TypeError):SharedField3('same settings')
        with self.assertRaises(ValueError):SharedField3(True,'UI color slider')

    def test_mixed_version_domain_precision_field_and_partition_rejected(self):
        good=Contract(VERSION,V3,(0,0x3ec00000),FIELD,sha(self.plan))
        bad=[replace(good,version=('iPhone17,3','24A445',*VERSION[2:])),replace(good,domain=(0,0x3eb00000)),replace(good,precision_sha256='0'*64),replace(good,field_definition='SSRParams.tone'),replace(good,partition_sha256='0'*64)]
        for other in bad:
            with self.assertRaises(ValueError):compatible([good,other])

    def test_tampered_build_and_domain_files_rejected_on_real_path(self):
        with tempfile.TemporaryDirectory(prefix='psr-joint-invalid-')as name:
            root=Path(name);c=root/'context.json';d=load(self.first.context_file);d['identity']['build']='24A445';c.write_bytes(encoded(d))
            with self.assertRaises(ValueError):self.solve(first_handle=replace(self.first,context_file=c))
            p=root/'precision.json';d=load(self.precision);d['domain']['last_f32_bits']=0x3eb00000;p.write_bytes(encoded(d))
            with self.assertRaises(ValueError):self.solve(first_handle=replace(self.first,precision_file=p))

    def test_wrong_context_target_rejected(self):
        wrong=replace(self.observation('first',7),target=Target(self.b[0],self.first.expected_catalog_sha256,strict_bits(self.a[3][7]['writer_half_bits'])))
        with self.assertRaises(ValueError):solve_joint((wrong,self.observation('second',7)),shared_parameter=self.declaration)

    def test_missing_matching_states_remain_possible_candidates(self):
        with tempfile.TemporaryDirectory(prefix='psr-joint-partial-')as name:
            h=self.partial(Path(name),missing={7,8,9});r=self.solve(first_handle=h)
            self.assertEqual(r['confirmed_model_joint_candidates'],[]);self.assertEqual(r['possible_f32_population'],860159);self.assertEqual(r['unresolved_joint_f32_population'],860159);self.assertFalse(r['all_single_catalogs_complete']);self.assertEqual(r['observations'][0]['query']['coverage']['missing_state_ids'],[7,8,9]);self.assertNotIn('no_common',r['status'])

    def test_unknown_matching_state_is_not_excluded_by_known_other_matches(self):
        with tempfile.TemporaryDirectory(prefix='psr-joint-partial-')as name:
            h=self.partial(Path(name),unknown={7});r=self.solve(first_handle=h);self.assertEqual(r['confirmed_model_f32_population'],0);self.assertEqual(r['possible_f32_population'],860159);self.assertEqual(r['observations'][0]['query']['model_matching_state_ids'],[8,9]);self.assertEqual(r['observations'][0]['query']['coverage']['unknown_state_ids'],[7])

    def test_irrelevant_missing_region_not_promoted_to_full_catalog_coverage(self):
        with tempfile.TemporaryDirectory(prefix='psr-joint-partial-')as name:
            h=self.partial(Path(name),missing={93});r=self.solve(first_handle=h);self.assertEqual(r['confirmed_model_f32_population'],860159);self.assertEqual(r['possible_f32_population'],860159);self.assertTrue(r['joint_unresolved_region_empty']);self.assertFalse(r['all_single_catalogs_complete']);self.assertEqual(r['observations'][0]['query']['coverage']['missing_state_ids'],[93])

    def test_missing_region_can_preserve_otherwise_incompatible_pair(self):
        with tempfile.TemporaryDirectory(prefix='psr-joint-partial-')as name:
            h=self.partial(Path(name),missing={93});r=self.solve(7,93,first_handle=h);self.assertEqual(r['confirmed_model_f32_population'],0);self.assertGreater(r['possible_f32_population'],0);self.assertGreater(r['unresolved_joint_f32_population'],0)

    def test_all_unknown_first_catalog_still_retains_second_candidates(self):
        with tempfile.TemporaryDirectory(prefix='psr-joint-partial-')as name:
            h=self.partial(Path(name),unknown=set(range(146)));r=self.solve(first_handle=h);self.assertEqual(r['possible_f32_population'],860159);self.assertEqual(r['confirmed_model_f32_population'],0);self.assertEqual(len(r['observations'][0]['query']['coverage']['unknown_state_ids']),146)

    def test_new_known_writer_cannot_be_injected_into_partial_catalog(self):
        with tempfile.TemporaryDirectory(prefix='psr-joint-provenance-')as name:
            root=Path(name);h=self.partial(root,missing={93});chunk=root/'simulated-chunk.json';d=load(chunk);row=next(r for r in d['rows']if r['state_id']==7);a=np.array(row['writer_half_bits'],dtype='u2');a[0,0,0]^=1;row['writer_half_bits']=a.tolist();row['writer_sha256']=__import__('hashlib').sha256(a.tobytes()).hexdigest();chunk.write_bytes(encoded(d));m=load(h.catalog_file);m['chunks'][0]['sha256']=sha(chunk);h.catalog_file.write_bytes(encoded(m));h=replace(h,expected_catalog_sha256=sha(h.catalog_file))
            with self.assertRaises(ValueError):self.solve(first_handle=h)

    def test_duplicate_labels_or_only_one_context_are_rejected(self):
        with self.assertRaises(ValueError):solve_joint((self.observation('first',7),self.observation('second',7,name='first')),shared_parameter=self.declaration)
        with self.assertRaises(ValueError):solve_joint((self.observation('first',7),self.observation('first',8,name='first-copy')),shared_parameter=self.declaration)

    def test_multiple_observations_do_not_invent_additional_scene_scope(self):
        r=solve_joint((self.observation('first',7),self.observation('second',7),self.observation('first',8,name='same-first-again')),shared_parameter=self.declaration);self.assertEqual(r['distinct_supported_contexts'],2);self.assertEqual(r['possible_f32_population'],860159)

    def test_query_does_not_call_forward_or_original_kernel(self):
        with patch('complete_forward.forward',side_effect=AssertionError('forbidden new forward')),patch('native_color_boundaries.upstream',side_effect=AssertionError('forbidden kernel')),patch('native_color_boundaries.render',side_effect=AssertionError('forbidden kernel')):
            r=self.solve();self.assertEqual(r['new_forward_or_original_kernel_calls'],0)

    def test_json_request_output_round_trip_and_missing_declaration(self):
        with tempfile.TemporaryDirectory(prefix='psr-joint-json-')as name:
            root=Path(name);request=load(E/'joint-request-state7-s27a.json')
            for row in request['observations']:
                for key in ['context','precision','partition','catalog','target']:row[key]=str((E/row[key]).resolve())
            file=root/'request.json';file.write_bytes(encoded(request));result=solve_request(file,root/'result.json');self.assertEqual(load(root/'result.json')['possible_f32_population'],860159);self.assertTrue(result['input_files_unchanged_during_solve']);self.assertEqual(result['request_sha256'],sha(file));del request['shared_parameter'];missing=root/'missing.json';missing.write_bytes(encoded(request))
            with self.assertRaises(ValueError):solve_request(missing,root/'not-created.json')


if __name__=='__main__':unittest.main()
