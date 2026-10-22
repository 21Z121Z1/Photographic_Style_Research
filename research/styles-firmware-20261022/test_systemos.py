import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from decrypt_systemos import decrypt


class SystemOSAdmissionTests(unittest.TestCase):
    def sources(self,root):
        entry={'name':'test.dmg.aea','method':0,'compressed_bytes':3,'uncompressed_bytes':3,'crc32':'00000000','local_header_offset':0}
        manifest={'source_url':'https://updates.cdn-apple.com/test.ipsw','build_manifest_sha256':'manifest',
                  'identities':[{'variant':'Customer Erase Install (IPSW)','components':{'Cryptex1,SystemOS':entry['name']}}],'image_entries':[entry]}
        receipt={'completed':True,'zip_crc_verified':True,'entry':entry,'source_url':manifest['source_url'],
                 'build_manifest_sha256':'manifest','sha256':'expected'}
        m=root/'metadata.json';m.write_text(json.dumps(manifest));(root/'download.json').write_text(json.dumps(receipt))
        return m,receipt

    def test_incomplete_or_changed_manifest_stops_before_any_decrypt_tool(self):
        for change in [{'completed':False},{'source_url':'https://elsewhere.invalid/other'}, {'build_manifest_sha256':'other'}]:
            with tempfile.TemporaryDirectory() as t,patch('decrypt_systemos.subprocess.run') as run:
                root=Path(t);m,r=self.sources(root);r.update(change);(root/'download.json').write_text(json.dumps(r))
                with self.assertRaisesRegex(ValueError,'exact manifest'):
                    decrypt(root,m,root/'private-keys.json',root/'out')
                run.assert_not_called();self.assertFalse((root/'out').exists())

    def test_changed_component_stops_before_reading_key_database_or_tool(self):
        with tempfile.TemporaryDirectory() as t,patch('decrypt_systemos.subprocess.run') as run:
            root=Path(t);m,_=self.sources(root);(root/'test.dmg.aea').write_bytes(b'bad')
            with self.assertRaisesRegex(ValueError,'component changed'):
                decrypt(root,m,root/'nonexistent-keys.json',root/'out')
            run.assert_not_called();self.assertFalse((root/'out').exists())


if __name__=='__main__':unittest.main()
