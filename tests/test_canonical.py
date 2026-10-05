import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from canonical_lab.canonical import canonicalize
from canonical_lab.contract import InputError
from canonical_lab.report import compare, render

ROOT=Path(__file__).resolve().parents[1]


class CanonicalTests(unittest.TestCase):
    def test_original_provenance_and_golden_pairs(self):
        manifest=json.loads((ROOT/'tests/vectors/manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(len(manifest['records']),7)
        for record in manifest['records']:
            raw=(ROOT/record['local']).read_bytes()
            self.assertEqual(len(raw),record['length'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(),record['sha256'])
            self.assertEqual(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw,usedforsecurity=False).hexdigest(),record['git_blob'])
        for name in ('arrays','french','unicode'):
            raw=(ROOT/f'tests/vectors/original/input/{name}.json').read_bytes()
            expected=(ROOT/f'tests/vectors/original/output/{name}.json').read_bytes()
            self.assertEqual(canonicalize(raw).canonical,expected)

    def test_utf16_order(self):
        raw=b'{"\\ue000":2,"\\ud83d\\ude00":1}'
        expected='{"\U0001f600":1,"\ue000":2}'.encode('utf-8')
        self.assertEqual(canonicalize(raw).canonical,expected)
        # Published RFC 8785 §3.2.3 property order, all values replaced with 0.
        raw=b'{"\\ufb33":0,"\\ud83d\\ude00":0,"\\u00f6":0,"\\u20ac":0,"\\u0080":0,"1":0,"\\r":0}'
        expected='{"\\r":0,"1":0,"\u0080":0,"\u00f6":0,"\u20ac":0,"\U0001f600":0,"\ufb33":0}'.encode('utf-8')
        self.assertEqual(canonicalize(raw).canonical,expected)

    def test_normalization_not_performed(self):
        self.assertEqual(compare(b'"\\u00e9"',b'"e\\u0301"')[1],1)
        self.assertEqual(canonicalize(b'"e\\u0301"').canonical,b'"e\xcc\x81"')

    def test_escaping_and_literals(self):
        self.assertEqual(canonicalize(b'"\\u0000\\b\\t\\n\\f\\r\\u001f\\\\\\\"\\/"').canonical,
                         b'"\\u0000\\b\\t\\n\\f\\r\\u001f\\\\\\\"/"')
        self.assertEqual(canonicalize(b'[null,true,false,-7,0]').canonical,b'[null,true,false,-7,0]')
        self.assertEqual(canonicalize(b'[{"b":2,"a":1}]').canonical,b'[{"a":1,"b":2}]')

    def test_equivalent_and_distinct(self):
        for left,right in ((b'{"b":2,"a":1}',b' {"a":1,"b":2} '),
                           (b'"\\u0061\\/"',b'"a/"'),(b'"\\ud83d\\ude00"','"\U0001f600"'.encode('utf-8'))):
            report,code=compare(left,right)
            self.assertEqual(code,0);self.assertFalse(report['raw_bytes_equal'])
            self.assertEqual(report['left']['canonical_hex'],report['right']['canonical_hex'])
        for left,right in ((b'true',b'1'),(b'1',b'"1"'),(b'[1,2]',b'[2,1]'),(b'null',b'false')):
            self.assertEqual(compare(left,right)[1],1)

    def test_both_documents_invalid_precedence(self):
        for invalid in (b'{"a":1,"a":2}',b'"\\ud800"',b'[1,]',b'['+b'0,'*64+b'0]'):
            for left,right in ((b'1.0',invalid),(invalid,b'1.0')):
                with self.assertRaises(InputError):compare(left,right)
        report,code=compare(b'1.0',b'1')
        self.assertEqual(code,3);self.assertIsNone(report['left']['canonical_hex'])
        self.assertEqual(report['right']['canonical_hex'],'31')
        report,code=compare(b'-0',b'-0')
        self.assertEqual(code,3);self.assertTrue(report['raw_bytes_equal'])
        self.assertEqual(report['canonical_relation'],'unsupported')

    def test_hash_input_and_report_contract(self):
        report,code=compare(b'1 ',b'1')
        self.assertEqual(code,0);self.assertFalse(report['origin_authenticated'])
        self.assertEqual(report['left']['raw_sha256'],hashlib.sha256(b'1 ').hexdigest())
        self.assertEqual(report['left']['canonical_sha256'],hashlib.sha256(b'1').hexdigest())
        self.assertNotEqual(report['left']['raw_sha256'],report['left']['canonical_sha256'])
        self.assertIn('reversible',report['limitation'])
        self.assertTrue(render(report).isascii())
        self.assertEqual(set(report),{'report_version','profile','hash_algorithm','status','raw_bytes_equal','canonical_relation','left','right','origin_authenticated','limitation'})

    def test_defensive_output_guard_seams(self):
        # These large defensive caps are unreachable under tighter normal shape
        # bounds. Exercise the actual guard narrowly, without end-to-end claims.
        with patch('canonical_lab.canonical._serialize',return_value='x'*32769):
            with self.assertRaises(InputError):canonicalize(b'1')
        with self.assertRaises(InputError):render({'x':'x'*262144})


if __name__=='__main__':unittest.main()
