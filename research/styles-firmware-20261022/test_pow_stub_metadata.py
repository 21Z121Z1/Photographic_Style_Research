"""S33 regression for saved Mach-O stub parsing, zero tool/native execution."""
from pathlib import Path
import unittest
from baseline_archive import Archive,sha
from context_color_api import load
from verify_fpcr_binding import resolve_stub_rows

R=Path(__file__).parent
E=R/'evidence'


class SavedStubTests(unittest.TestCase):
    def test_saved_zero_padded_0x_address_matches_powf(self):
        d=load(E/'pow-stub-s33f.json')
        a=Archive(R.parents[1].parent/d['private_storage_relative_to_task'])
        p=a.path('pow-stub/metadata.stdout');self.assertEqual(sha(p),d['metadata_stdout_sha256'])
        rows=resolve_stub_rows(p.read_text(),0x16244)
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['symbol'],'_powf')
        self.assertEqual(rows[0]['index'],136)
        self.assertEqual(d['stub_row_count'],0) # the failed initial parser remains recorded

    def test_GOT_symbol_is_not_accepted_as_stub_identity(self):
        text='Indirect symbols for (__DATA_CONST,__got) 1 entries\n0x0000016244 136 _powf\n'
        self.assertEqual(resolve_stub_rows(text,0x16244),[])

    def test_missing_and_duplicate_stub_rows_stay_detectable(self):
        text='Indirect symbols for (__TEXT,__stubs) 1 entries\n0x0000016244 136 _powf\n'
        self.assertEqual(resolve_stub_rows(text,0x16245),[])
        self.assertEqual(len(resolve_stub_rows(text+'0x16244 999 _other\n',0x16244)),2)


if __name__=='__main__':unittest.main()
