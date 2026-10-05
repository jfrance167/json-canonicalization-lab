"""Reproduce eight fixed synthetic cases; --check reads exact artifacts only.

Write mode replaces only fixed samples/demo-cases.json and demo-report.json.
No user paths or real documents. Canonical hex is reversible, not redacted.
"""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from canonical_lab.contract import InputError
from canonical_lab.report import compare, render

CASES=(
    ('format-order',b'{"b":2,"a":1}',b' {"a":1,"b":2} ',0),
    ('astral-escape',b'"\\ud83d\\ude00"','"\U0001f600"'.encode('utf-8'),0),
    ('utf16-order',b'{"\\ue000":2,"\\ud83d\\ude00":1}',b'{"\\ud83d\\ude00":1,"\\ue000":2}',0),
    ('unicode-preserved',b'"\\u00e9"',b'"e\\u0301"',1),
    ('boolean-integer',b'true',b'1',1),
    ('array-order',b'[1,2]',b'[2,1]',1),
    ('numeric-subset',b'1.0',b'1e0',3),
    ('decoded-duplicate',b'1.0',b'{"a":1,"\\u0061":2}',2),
)


def artifacts() -> dict[str,str]:
    inputs=[];results=[]
    for name,left,right,expected in CASES:
        inputs.append(dict(case=name,left_hex=left.hex(),right_hex=right.hex(),expected_exit=expected))
        try:
            report,code=compare(left,right)
            result=dict(case=name,exit=code,report=report)
        except InputError as error:
            code=2;result=dict(case=name,exit=code,error=str(error))
        if code!=expected:raise RuntimeError('synthetic expected exit mismatch: '+name)
        results.append(result)
    return {'demo-cases.json':render(dict(synthetic_only=True,cases=inputs)),
            'demo-report.json':render(dict(synthetic_only=True,cases=results))}


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    for name,content in artifacts().items():
        path=ROOT/'samples'/name
        if args.check:
            if not path.is_file() or path.read_bytes()!=content.encode('ascii'):
                print('sample differs: '+name);return 1
        else:
            path.parent.mkdir(exist_ok=True);path.write_bytes(content.encode('ascii'))
    print('eight cases / two artifacts verified' if args.check else 'eight cases / two artifacts generated')
    return 0


if __name__=='__main__':raise SystemExit(main())
