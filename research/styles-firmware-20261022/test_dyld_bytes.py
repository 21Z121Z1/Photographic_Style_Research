from pathlib import Path
import struct
import tempfile
import unittest
from dyld_bytes import CacheBytes,verify_disassembly


class DyldMappingTests(unittest.TestCase):
    def sample(self,root,*,bad_span=False):
        data=bytearray(256);data[:16]=b'dyld_v1  arm64e\0\0';struct.pack_into('<II',data,16,112,1)
        data[88:104]=bytes(range(16));struct.pack_into('<QQQII',data,112,0x180000000,64 if bad_span else 32,224,5,5)
        data[224:232]=bytes.fromhex('1f2003d5c0035fd6');(root/'dyld_shared_cache_arm64e.01').write_bytes(data)

    def test_mapping_offset_rejects_tampered_word_or_noncontiguous_export(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);self.sample(root);cache=CacheBytes(root)
            text='0x180000000:  1f 20 03 d5  nop\n0x180000004:  c0 03 5f d6  ret\n'
            self.assertEqual(verify_disassembly(cache,text)['checked_bytes'],8)
            with self.assertRaises(ValueError):verify_disassembly(cache,text.replace('1f 20','1e 20'))
            with self.assertRaises(ValueError):verify_disassembly(cache,text.replace('180000004','180000008'))
            with self.assertRaises(ValueError):cache.read(0x18000001f,2)

    def test_mapping_span_cannot_exceed_original_file(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);self.sample(root,bad_span=True)
            with self.assertRaisesRegex(ValueError,'file span'):CacheBytes(root)

    def test_v5_initial_byte_offset_next_stride_and_nonchain_integer(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);data=bytearray(12288);data[:16]=b'dyld_v1  arm64e\0\0'
            struct.pack_into('<II',data,16,512,1);struct.pack_into('<II',data,312,544,1)
            struct.pack_into('<QQQII',data,512,0x180000000,4096,4096,3,3)
            struct.pack_into('<6Q2I',data,544,0x180000000,4096,4096,8192,26,0,3,3)
            struct.pack_into('<III4xQH',data,8192,5,4096,1,0x180000000,2048)
            struct.pack_into('<Q',data,4096+2048,(1<<63)|(2<<52)|0x100)
            struct.pack_into('<Q',data,4096+2064,0x200)
            struct.pack_into('<Q',data,4096+8,(1<<63)|0x300)
            (root/'dyld_shared_cache_arm64e.25.dylddata').write_bytes(data)
            cache=CacheBytes(root)
            self.assertEqual(cache.pointer_at(0x180000800),0x180000100)
            self.assertEqual(cache.pointer_at(0x180000810),0x180000200)
            with self.assertRaisesRegex(ValueError,'confirmed chain'):
                cache.pointer_at(0x180000008)


if __name__=='__main__':unittest.main()
