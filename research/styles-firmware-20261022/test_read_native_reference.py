"""Check metadata/transport boundaries, without GitHub or native calls."""
import copy
import json
import unittest

from native_reference import envelope
from read_native_reference import read_report


class NativeCheckReaderTests(unittest.TestCase):
    def setUp(self):
        self.head='a'*40
        self.report={'git':{'HEAD':self.head},'raw_bits':[0,65535,0x3e9da2ca]}
        self.check={'head_sha':self.head,'status':'completed','app':{'slug':'github-actions'},
                    'output':{'text':'```json\n'+json.dumps(envelope(self.report))+'```'}}

    def test_check_preserves_raw_bits_on_the_exact_commit(self):
        self.assertEqual(read_report(self.check,self.head),self.report)

    def test_wrong_commit_unfinished_wrong_app_and_missing_evidence_are_rejected(self):
        for key in ('head','status','app','text'):
            check=copy.deepcopy(self.check)
            if key=='head':check['head_sha']='b'*40
            if key=='status':check['status']='in_progress'
            if key=='app':check['app']['slug']='unknown'
            if key=='text':check['output']['text']=None
            with self.subTest(key=key),self.assertRaises(ValueError):read_report(check,self.head)

    def test_report_cannot_relabel_an_old_HEAD(self):
        self.report['git']['HEAD']='b'*40
        self.check['output']['text']='```json\n'+json.dumps(envelope(self.report))+'```'
        with self.assertRaises(ValueError):read_report(self.check,self.head)


if __name__=='__main__':unittest.main()
