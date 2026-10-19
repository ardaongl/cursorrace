import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from tests.support import FIXTURES,ROOT


def inventory(root):
    result={}
    for p in root.rglob('*'):
        if p.is_file():
            s=p.stat();result[p.relative_to(root).as_posix()]=('file',hashlib.sha256(p.read_bytes()).hexdigest(),s.st_mode,s.st_mtime_ns)
        elif p.is_dir(): result[p.relative_to(root).as_posix()]=('directory',p.stat().st_mode)
    return result


class SafetyMixin:
    def sandbox(self,mode,case='pass-empty',form='module',control=None,input_io=False):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);site=root/'site';guard=root/'guard';work=root/'work'
            for path in [site,guard,work,root/'home',root/'tmp']:path.mkdir()
            installed=Path(importlib.util.find_spec('cursorrace').origin).parent
            shutil.copytree(installed,site/'cursorrace',ignore=shutil.ignore_patterns('__pycache__'))
            (guard/'sitecustomize.py').write_bytes((ROOT/'tests/guard.py').read_bytes())
            source=FIXTURES/(case+'.json');target=work/'input.pyc'  # Filename alone is never an exception.
            target.write_bytes(source.read_bytes())
            (work/'snapshot').write_bytes(b'unchanged snapshot')
            env={k:v for k,v in os.environ.items() if k not in ('PYTHONPATH','PYTHONDONTWRITEBYTECODE')}
            env.update(PYTHONPATH=os.pathsep.join([str(guard),str(site)]),HOME=str(root/'home'),TMPDIR=str(root/'tmp'),CURSORRACE_GUARD_CACHE_ROOTS=os.pathsep.join([str(site),str(guard)]))
            input_path=work/'missing' if input_io else target
            if control is not None: command=[sys.executable,'-c',control]
            elif form=='console': command=[str(Path(sys.executable).parent/'cursorrace'),'check',str(input_path)]
            else: command=[sys.executable,'-m','cursorrace','check',str(input_path)]
            if mode=='environment': env['PYTHONDONTWRITEBYTECODE']='1'
            elif mode=='flag': command.insert(1,'-B')
            before=inventory(root)
            process=subprocess.run(command,cwd=work,env=env,capture_output=True,timeout=15)
            after=inventory(root)
            marker=b'\nCURSORRACE_GUARD_RESULT='
            self.assertIn(marker,process.stderr,process.stderr)
            stderr,meta=process.stderr.rsplit(marker,1);meta=json.loads(meta)
            changes={p for p in before.keys()|after.keys() if before.get(p)!=after.get(p)}
            for name in changes:
                self.assertTrue(name.startswith(('site/cursorrace/__pycache__/','guard/__pycache__/')) or name in ('site/cursorrace/__pycache__','guard/__pycache__'),name)
            self.assertEqual(target.read_bytes(),source.read_bytes())
            if mode!='ordinary':
                self.assertFalse(changes,changes);self.assertFalse(meta['bytecode_operations'])
            else:
                self.assertTrue(meta['bytecode_operations'],'cold-cache import classification not exercised')
            return process.returncode,process.stdout,stderr,meta

    def test_ordinary_cold_cache_and_suppressed_audit_outcomes(self):
        cases=json.loads((FIXTURES/'manifest.json').read_text())['cases']
        # Every canonical outcome under the network/mutation guard; both entrypoints
        # and both pre-startup suppression mechanisms additionally covered below.
        for case in cases:
            with self.subTest(case=case['id']):
                code,out,err,meta=self.sandbox('ordinary',case['id'])
                self.assertEqual(meta['attempts'],[])
                self.assertEqual((code,out,err),(case['exit_code'],(FIXTURES/case['stdout']).read_bytes(),b''))
        for case in ['pass-snapshot','fail-delete-gap','invalid-ledger']:
            for mode,form in [('ordinary','console'),('environment','console'),('flag','module')]:
                with self.subTest(case=case,mode=mode,form=form):
                    code,out,err,meta=self.sandbox(mode,case,form)
                    entry=next(c for c in cases if c['id']==case)
                    self.assertEqual((code,out,err),(entry['exit_code'],(FIXTURES/entry['stdout']).read_bytes(),b''))
                    self.assertEqual(meta['attempts'],[])

    def test_guards_detect_caught_attempts_and_transient_writes(self):
        control='''
import os, socket, cursorrace, logging, tempfile
original=open('input.pyc','rb').read()
def rewrite():
    with open('input.pyc','r+b') as stream: stream.write(original)
def transient():
    open('temporary','w').close()
    os.unlink('temporary')
def restore():
    os.rename('snapshot','other')
    os.rename('other','snapshot')
for operation in [rewrite, transient, restore, lambda: os.mkdir('__pycache__'), lambda: os.truncate('input.pyc',0), lambda: os.write(0,b'x'), lambda: os.ftruncate(0,0), lambda: socket.socket(), lambda: open('log.pyc','w'), lambda: logging.FileHandler('audit.log'), lambda: tempfile.NamedTemporaryFile(dir=os.environ["TMPDIR"])]:
    try: operation()
    except PermissionError: pass
'''
        code,out,err,meta=self.sandbox('ordinary',control=control)
        self.assertEqual((code,out,err),(0,b'',b''))
        self.assertEqual(len(meta['attempts']),11)
        self.assertTrue(any(event[0]=='open' for event in meta['attempts']))

    def test_input_io_failure_is_read_only(self):
        for mode,form in [('ordinary','module'),('environment','console'),('flag','module')]:
            with self.subTest(mode=mode):
                code,out,err,meta=self.sandbox(mode,form=form,input_io=True)
                self.assertEqual((code,out,err),(3,b'',b'cursorrace: INPUT_IO\n'))
                self.assertEqual(meta['attempts'],[])
