import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from canonical_lab.__main__ import main, write_checked
from canonical_lab.contract import InputError, read

ROOT=Path(__file__).resolve().parents[1]


class BadSink:
    def __init__(self, failure):self.failure=failure
    def write(self, text):
        if self.failure=='short':return len(text)-1
        if self.failure=='write':raise BrokenPipeError('closed synthetic pipe')
        return len(text)
    def flush(self):
        if self.failure=='flush':raise OSError('synthetic flush failure')
    def __enter__(self):return self
    def __exit__(self,*args):
        if self.failure=='close':raise OSError('synthetic close failure')


class CliTests(unittest.TestCase):
    def setUp(self):
        parent=ROOT/'.private/test-temp';parent.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=parent);self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.left=self.root/'left.json';self.right=self.root/'right.json'
        self.left.write_bytes(b'{"b":2,"a":1}');self.right.write_bytes(b'{"a":1,"b":2}')
        self.arguments=['compare',str(self.left),str(self.right)]

    def call(self,*options):
        mode=['-O'] if sys.flags.optimize else []
        return subprocess.run([sys.executable,*mode,'-m','canonical_lab',*self.arguments,*map(str,options)],
                              cwd=ROOT,capture_output=True,text=True,timeout=10,check=False)

    def test_exit_codes_and_whole_pair_validation(self):
        for left,right,code in ((b'1 ',b'1',0),(b'true',b'1',1),(b'1.0',b'1',3),
                                (b'1.0',b'{"a":1,"a":2}',2),(b'1.0',b'"\\ud800"',2)):
            self.left.write_bytes(left);self.right.write_bytes(right)
            process=self.call();self.assertEqual(process.returncode,code,process.stderr)
            if code==2:self.assertEqual(process.stdout,'')
            else:self.assertFalse(json.loads(process.stdout)['origin_authenticated'])

    def test_same_source_and_exclusive_output(self):
        evidence={path:path.read_bytes() for path in (self.left,self.right)}
        for output in (self.left,self.right):
            self.assertEqual(self.call('--output',output).returncode,2)
        target=self.root/'new.json'
        self.assertEqual(self.call('--output',target).returncode,0)
        saved=target.read_bytes();self.assertEqual(self.call('--output',target).returncode,2)
        self.assertEqual(target.read_bytes(),saved)
        for path,data in evidence.items():self.assertEqual(path.read_bytes(),data)
        self.arguments=['compare',str(self.left),str(self.left)]
        process=self.call();self.assertEqual(process.returncode,0)
        self.assertTrue(json.loads(process.stdout)['raw_bytes_equal'])

    def test_output_hardlink_alias(self):
        alias=self.root/'alias.json';os.link(self.left,alias)
        original=self.left.read_bytes()
        self.assertEqual(self.call('--output',alias).returncode,2)
        self.assertEqual(self.left.read_bytes(),original)

    def test_invalid_output_absent_and_error_inert(self):
        self.right.write_bytes(b'"\\ud800"');self.left.write_bytes(b'1.0')
        target=self.root/'must-not-exist.json'
        process=self.call('--output',target)
        self.assertEqual(process.returncode,2);self.assertFalse(target.exists())
        self.assertEqual(process.stdout,'');self.assertNotIn('Traceback',process.stderr)

    def test_regular_and_bounded_reader(self):
        with self.assertRaises(InputError):read(self.root)
        self.left.write_bytes(b' '*16385)
        with self.assertRaises(InputError):read(self.left)
        # Simulate growth after the file metadata check: actual bounded read
        # still sees limit+1 bytes and must reject.
        with patch('canonical_lab.contract.os.fstat',return_value=SimpleNamespace(st_mode=0o100600,st_size=1)):
            with self.assertRaises(InputError):read(self.left)
        self.arguments=['compare',str(self.root/'missing'),str(self.right)]
        process=self.call();self.assertEqual(process.returncode,2)
        self.assertNotIn('Traceback',process.stderr)

    def test_short_write_flush_and_close_failures(self):
        for failure in ('short','write','flush'):
            with self.assertRaises(OSError):write_checked(BadSink(failure),'abc')
            with patch('sys.stdout',BadSink(failure)),patch('sys.stderr',io.StringIO()):
                self.assertEqual(main(self.arguments),2)
        for failure in ('short','flush','close'):
            with patch('pathlib.Path.open',return_value=BadSink(failure)),patch('sys.stderr',io.StringIO()):
                self.assertEqual(main([*self.arguments,'--output',str(self.root/'new.json')]),2)

    def test_real_closed_pipe_exit(self):
        mode=['-O'] if sys.flags.optimize else []
        process=subprocess.Popen([sys.executable,*mode,'-m','canonical_lab',*self.arguments],cwd=ROOT,
                                 stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        process.stdout.close()
        error=process.stderr.read();process.stderr.close()
        self.assertEqual(process.wait(timeout=10),2,error.decode('utf-8'))


if __name__=='__main__':unittest.main()
