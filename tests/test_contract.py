import json
import unittest
from canonical_lab.contract import InputError, parse


def encoded(value):
    return json.dumps(value, ensure_ascii=True).encode('ascii')


class AdmissionTests(unittest.TestCase):
    def test_numeric_supported_and_unsupported(self):
        for raw in (b'0',b'1',b'-1',b'9007199254740991',b'-9007199254740991'):
            self.assertEqual(parse(raw).reasons,())
        for raw,reason in ((b'-0','negative-zero'),(b'1.0','fraction-or-exponent'),
                          (b'1e0','fraction-or-exponent'),(b'1e999999999999999','fraction-or-exponent'),
                          (b'9007199254740992','unsafe-integer'),(b'-9007199254740992','unsafe-integer')):
            self.assertEqual(parse(raw).reasons,(reason,))
        self.assertEqual(parse(b'[1.0,-0,9007199254740992,1e0]').reasons,
                         ('fraction-or-exponent','unsafe-integer','negative-zero'))

    def test_invalid_grammar_and_exact_bytes(self):
        for raw in (b'',b'{',b'1 2',b'01',b'+1',b'NaN',b'Infinity',b'-Infinity',b'1.',b'1e',
                    b'/*x*/1',b'[1,]',b'"\xff"',b'\xef\xbb\xbf1',b'\xff\xfe1\x00'):
            with self.subTest(raw=raw),self.assertRaises(InputError):parse(raw)
        for value in ('{}',bytearray(b'{}'),{},[1]):
            with self.assertRaises(InputError):parse(value)

    def test_duplicates_decoded_and_nested(self):
        for raw in (b'{"a":1,"a":2}',b'{"a":1,"\\u0061":2}',
                    b'[{"x":{"k":1,"k":2}}]',b'[1.0,{"x":1,"x":2}]'):
            with self.assertRaises(InputError):parse(raw)
        self.assertFalse(parse(b'{"\\u00e9":1,"e\\u0301":2}').reasons)

    def test_unicode_invalid_and_pair_control(self):
        for value in ('\ud800','\udc00','\udc00\ud800','\ufdd0','\ufdef','\ufffe','\uffff','\U0001ffff','\U0010ffff'):
            for document in ([value],{value:1}):
                with self.assertRaises(InputError):parse(encoded(document))
        self.assertEqual(parse(b'"\\ud83d\\ude00"').value,'\U0001f600')
        self.assertEqual(parse(b'"\\ufffd"').value,'\ufffd')

    def test_byte_depth_numeric_bounds(self):
        self.assertFalse(parse(b'0'+b' '*(16384-1)).reasons)
        with self.assertRaises(InputError):parse(b'0'+b' '*16384)
        self.assertFalse(parse(b'['*8+b'0'+b']'*8).reasons)
        with self.assertRaises(InputError):parse(b'['*9+b'0'+b']'*9)
        self.assertFalse(parse(b'"[[[[[[[[["').reasons)
        self.assertEqual(parse(b'9'*64).reasons,('unsafe-integer',))
        with self.assertRaises(InputError):parse(b'9'*65)
        with self.assertRaises(InputError):parse(b'1e'+b'9'*63)

    def test_container_bound(self):
        self.assertFalse(parse(encoded([0]*64)).reasons)
        with self.assertRaises(InputError):parse(encoded([0]*65))
        self.assertFalse(parse(encoded({str(i):0 for i in range(64)})).reasons)
        with self.assertRaises(InputError):parse(encoded({str(i):0 for i in range(65)}))

    def test_node_and_string_bounds(self):
        # root + 4 lists + 251 leaves = exactly 256 nodes.
        good=[[0]*64,[0]*64,[0]*64,[0]*59]
        self.assertFalse(parse(encoded(good)).reasons)
        good[-1].append(0)
        with self.assertRaises(InputError):parse(encoded(good))
        self.assertFalse(parse(encoded('a'*1024)).reasons)
        with self.assertRaises(InputError):parse(encoded('a'*1025))
        self.assertFalse(parse(encoded(['a'*1024]*4)).reasons)
        with self.assertRaises(InputError):parse(encoded(['a'*1024]*4+['a']))


if __name__=='__main__':unittest.main()
