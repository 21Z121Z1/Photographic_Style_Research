"""Aligned synthetic capture tests; no native GPU is invoked by this suite."""
import base64
import copy
import hashlib
from pathlib import Path
import tempfile
import unittest

import numpy as np

from native_texture_reference import (CASES, DOMAIN, LIBRARY_SHA256, MaskMode, NativeCase,
                                      blob, unblob, operands, prepare, compare_native,
                                      bit_mismatch_examples, weight_diagnostics)
from texture_style_adapter import HalfRGB


class NativeTextureReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = tempfile.TemporaryDirectory()
        cls.path,cls.inputs = prepare(Path(cls.folder.name)/'aligned-inputs')
        cls.raw = {'status':'native_under_eye_final_mix_completed','library_sha256':LIBRARY_SHA256,
                   'library_unchanged':True,'input_manifest_sha256':cls.inputs['input_manifest_sha256'],
                   'GPU_dispatches':len(cls.inputs['cases']),'rows':[]}
        for case in cls.inputs['cases']:
            model = unblob(case['model_output'])
            data = np.concatenate((model,np.ones((8,12,1),dtype='f2')),axis=-1).astype('<f2').tobytes()
            params=np.zeros(13,dtype='<f4');params[2]=case['brightness_mix']
            stats=np.zeros(12,dtype='<f4');stats[3]=case['strength']
            cls.raw['rows'].append({'name':case['name'],'command_status':4,
                'input_sha256':{n:r['sha256'] for n,r in case['inputs'].items()},
                'params_sha256':hashlib.sha256(params.tobytes()).hexdigest(),
                'stats_sha256':hashlib.sha256(stats.tobytes()).hexdigest(),
                'output_sha256':hashlib.sha256(data).hexdigest(),
                'output_f16_base64':base64.b64encode(data).decode()})

    @classmethod
    def tearDownClass(cls):
        cls.folder.cleanup()

    def test_source_to_writer_inputs_have_real_ROI_and_every_half_file_is_bound(self):
        self.assertEqual(len(self.inputs['contexts']),2)
        self.assertEqual(len(self.inputs['cases']),18)
        for scene in self.inputs['contexts'].values():
            self.assertEqual(scene['upstream_native_calls'],0)
            writer=unblob(scene['writer'])
            y0,x0,y1,x1=scene['written_roi_yxyx']
            self.assertEqual(writer[y0:y1,x0:x1].shape,(8,12,4))
        import json
        manifest=json.loads(self.path.read_text())
        for native,case in zip(manifest['cases'],self.inputs['cases']):
            for name,file in native['files'].items():
                self.assertEqual(hashlib.sha256((self.path.parent/file).read_bytes()).hexdigest(),
                                 case['inputs'][name]['sha256'])

    def test_full_spatial_and_zero_masks_and_parameter_types(self):
        source=HalfRGB(np.full((8,12,3),.5,dtype='f2'),DOMAIN)
        full=operands(source,NativeCase(MaskMode.FULL,np.float32(1),np.float32(1)))
        self.assertTrue(np.all(full.masks.face.values==1))
        self.assertFalse(np.any(full.masks.hair.values))
        self.assertEqual(len(CASES),9)
        with self.assertRaises(TypeError):NativeCase('spatial',np.float32(1),np.float32(1))
        with self.assertRaises(TypeError):NativeCase(MaskMode.SPATIAL,.5,np.float32(1))

    def test_exact_generated_capture_is_aligned_without_promoting_upstream(self):
        result=compare_native(self.raw,self.inputs)
        self.assertEqual(result['GPU_dispatches'],18)
        self.assertTrue(result['all_observed_RGB_half_bits_match_continuous_model'])
        self.assertFalse(result['upstream_native_verified'])
        self.assertFalse(result['full_Texture_pipeline_verified'])
        self.assertFalse(result['Apple_capture_order_verified'])
        self.assertGreater(max(r['native_effect_from_input']['max_absolute_error'] for r in result['rows']),0)

    def test_changed_inputs_parameters_output_and_library_are_rejected(self):
        for kind in ('inputs','params','output','library','missing'):
            raw=copy.deepcopy(self.raw)
            if kind=='inputs':raw['rows'][0]['input_sha256']['source']='0'*64
            if kind=='params':raw['rows'][0]['params_sha256']='0'*64
            if kind=='output':raw['rows'][0]['output_sha256']='0'*64
            if kind=='library':raw['library_unchanged']=False
            if kind=='missing':raw['rows'].pop()
            with self.subTest(kind=kind),self.assertRaises(ValueError):compare_native(raw,self.inputs)

    def test_failed_native_capture_has_no_invented_metric(self):
        result=compare_native({'status':'blocked','GPU_dispatches':0,'error':'unsupported ABI'},self.inputs)
        self.assertEqual(result['status'],'blocked_or_incomplete')
        self.assertFalse(result['accuracy_verified'])
        self.assertNotIn('rows',result)

    def test_half_blob_preserves_signed_zero_and_rejects_changes(self):
        a=np.array([0.,-0.,.5],dtype='f2')
        np.testing.assert_array_equal(unblob(blob(a)).view('u2'),a.view('u2'))
        record=blob(a);record['sha256']='0'*64
        with self.assertRaises(ValueError):unblob(record)

    def test_weight_probe_is_separate_and_its_raw_bytes_are_verified(self):
        raw=copy.deepcopy(self.raw)
        raw['weight_probe_dispatches']=18;raw['GPU_dispatches']=36
        zero=np.zeros((8,12,4),dtype='<f2').tobytes()
        raw['weight_probe_source_sha256']=hashlib.sha256(zero).hexdigest()
        raw['weight_probe_edited_sha256']=hashlib.sha256(np.ones((8,12,4),dtype='<f2').tobytes()).hexdigest()
        for row in raw['rows']:
            row['weight_f16_base64']=base64.b64encode(zero).decode()
            row['weight_sha256']=hashlib.sha256(zero).hexdigest()
        self.assertEqual(compare_native(raw,self.inputs)['GPU_dispatches'],36)
        diagnostic=weight_diagnostics(raw,self.inputs)
        self.assertEqual(len(diagnostic['rows']),18)
        self.assertFalse(diagnostic['native_weight_used_by_main_model'])
        raw['rows'][0]['weight_sha256']='0'*64
        with self.assertRaises(ValueError):weight_diagnostics(raw,self.inputs)

    def test_one_half_bit_failure_is_retained_below_numeric_threshold(self):
        raw=copy.deepcopy(self.raw)
        data=bytearray(base64.b64decode(raw['rows'][0]['output_f16_base64']))
        data[0]^=1
        raw['rows'][0]['output_f16_base64']=base64.b64encode(data).decode()
        raw['rows'][0]['output_sha256']=hashlib.sha256(data).hexdigest()
        result=compare_native(raw,self.inputs)['rows'][0]['native_minus_model']
        self.assertEqual(result['half_bit_mismatches'],1)
        self.assertEqual(result['exceedance_components'],0)
        examples=bit_mismatch_examples(raw,self.inputs)[raw['rows'][0]['name']]
        self.assertEqual(len(examples),1)
        self.assertEqual(examples[0]['channel'],0)


if __name__=='__main__':unittest.main()
