import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from cursorrace import cli
from tests.support import FIXTURES


class CliTests(unittest.TestCase):
    def invoke(self, args):
        return subprocess.run([sys.executable,'-m','cursorrace',*args],capture_output=True,timeout=10)

    def test_help_version_arguments(self):
        for args in [['--help'],['check','--help']]:
            p=self.invoke(args); self.assertEqual((p.returncode,p.stderr),(0,b'')); self.assertIn(b'Exit codes:',p.stdout)
        p=self.invoke(['--version']);self.assertEqual((p.returncode,p.stdout,p.stderr),(0,b'cursorrace 0.1.0\n',b''))
        for args in [[],['check'],['bad'],['--hel'],['check','a','b'],['check','--version'],['--help','--help'],['check','--help','x'],['check','--unknown']]:
            with self.subTest(args=args):
                p=self.invoke(args);self.assertEqual((p.returncode,p.stdout,p.stderr),(2,b'{"error":{"code":"ARGUMENT","pointer":null},"schema_version":1,"status":"error"}\n',b''))

    def test_input_failures_nonregular_and_symlink(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); fifo=root/'fifo';os.mkfifo(fifo)
            for path in [root/'absent',root,fifo,Path('/dev/null')]:
                p=self.invoke(['check',str(path)])
                self.assertEqual((p.returncode,p.stdout,p.stderr),(3,b'',b'cursorrace: INPUT_IO\n'))
            link=root/'link';link.symlink_to(FIXTURES/'invalid-version.json')
            self.assertEqual(self.invoke(['check',str(link)]).returncode,2)

    def test_open_substitution_cannot_read_fifo_or_directory(self):
        for replacement in ['fifo','directory']:
            with self.subTest(replacement=replacement), tempfile.TemporaryDirectory() as folder:
                path=Path(folder)/'trace';path.write_bytes(b'{}');original=cli.os.open
                def swapped(name,flags):
                    path.unlink()
                    os.mkfifo(path) if replacement=='fifo' else path.mkdir()
                    return original(name,flags)
                with patch.object(cli.os,'open',side_effect=swapped), patch.object(cli.os,'read') as read:
                    with self.assertRaisesRegex(cli.ExecutionError,'INPUT_IO'): cli.read_input(str(path))
                    read.assert_not_called()

    def test_read_failure_and_bound(self):
        with patch.object(cli.os,'open',side_effect=PermissionError):
            with self.assertRaisesRegex(cli.ExecutionError,'INPUT_IO'): cli.read_input('x')
        with tempfile.NamedTemporaryFile() as f:
            f.write(b' '*(cli.MAX_BYTES+4096));f.flush()
            self.assertEqual(len(cli.read_input(f.name)),cli.MAX_BYTES+1)
        with patch.object(cli.os,'read',side_effect=OSError), patch.object(cli.os,'open',return_value=5), patch.object(cli.os,'fstat',return_value=os.stat(FIXTURES/'pass-empty.json')), patch.object(cli.os,'close') as close:
            with self.assertRaises(cli.ExecutionError): cli.read_input('x')
            close.assert_called_once_with(5)

    def test_internal_and_interrupt_channels(self):
        for exception,code,diagnostic in [(RuntimeError('PRIVATE'),3,'INTERNAL'),(KeyboardInterrupt(),130,'INTERRUPTED')]:
            out=io.StringIO();err=io.StringIO()
            with patch.object(cli,'_execute',side_effect=exception),patch.object(sys,'stdout',out),patch.object(sys,'stderr',err):
                self.assertEqual(cli.main([]),code)
            self.assertEqual(out.getvalue(),'');self.assertEqual(err.getvalue(),f'cursorrace: {diagnostic}\n')

    def test_write_and_flush_failure_and_closed_stderr(self):
        class Broken(io.StringIO):
            def flush(self): raise BrokenPipeError()
        for stream in [Broken(),io.StringIO()]:
            if type(stream) is io.StringIO: stream.close()
            err=io.StringIO()
            with patch.object(sys,'stdout',stream),patch.object(sys,'stderr',err):
                self.assertEqual(cli.main(['--version']),3)
            self.assertEqual(err.getvalue(),'cursorrace: OUTPUT_IO\n')
        with patch.object(sys,'stdout',Broken()),patch.object(sys,'stderr',Broken()):
            self.assertEqual(cli.main(['--version']),3)

    def test_literal_paths_and_real_installed_console(self):
        console=str(Path(sys.executable).parent/'cursorrace')
        with tempfile.TemporaryDirectory() as folder:
            for filename in ['-','-trace','with spaces.json']:
                Path(folder,filename).write_bytes((FIXTURES/'pass-empty.json').read_bytes())
                args=['check','--',filename] if filename.startswith('-') and filename!='-' else ['check',filename]
                p=subprocess.run([console,*args],cwd=folder,capture_output=True,timeout=10)
                self.assertEqual((p.returncode,p.stdout,p.stderr),(0,(FIXTURES/'pass-empty.expected.json').read_bytes(),b''))

    def test_actual_pipe_close_exits_three(self):
        import json
        from tests.support import raw,trace,page
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'many.json';target.write_bytes(raw(trace([], [page(['x']*1000)],size=1000)))
            p=subprocess.Popen([str(Path(sys.executable).parent/'cursorrace'),'check',str(target)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            p.stdout.close()
            try:
                error=p.stderr.read();code=p.wait(timeout=10)
            finally:
                p.stderr.close()
            self.assertEqual((code,error),(3,b'cursorrace: OUTPUT_IO\n'))

    @unittest.skipUnless(os.name == 'posix', 'Closed descriptors require POSIX; Windows is outside v1 support')
    def test_closed_descriptors_in_installed_entrypoints(self):
        # preexec_fn runs after pipe setup and before exec: CPython sees genuinely
        # closed descriptors at startup, rather than writable DEVNULL streams.
        console = str(Path(sys.executable).parent/'cursorrace')
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        env.pop('PYTHONPATH', None)
        with tempfile.TemporaryDirectory() as folder:
            missing = str(Path(folder)/'absent')
            cases = [
                ('missing-stderr', ['check', missing], (2,), 3, b'', b''),
                ('version-stdout', ['--version'], (1,), 3, b'', b'cursorrace: OUTPUT_IO\n'),
                ('version-both', ['--version'], (1, 2), 3, b'', b''),
                ('pass-stdout', ['check', str(FIXTURES/'pass-empty.json')], (1,), 3, b'', b'cursorrace: OUTPUT_IO\n'),
                ('fail-stdout', ['check', str(FIXTURES/'fail-multiple.json')], (1,), 3, b'', b'cursorrace: OUTPUT_IO\n'),
                ('invalid-stderr', ['check', str(FIXTURES/'invalid-version.json')], (2,), 2,
                 (FIXTURES/'invalid-version.expected.json').read_bytes(), b''),
                ('invalid-stdout', ['check', str(FIXTURES/'invalid-version.json')], (1,), 3, b'', b'cursorrace: OUTPUT_IO\n'),
                ('pass-stderr', ['check', str(FIXTURES/'pass-empty.json')], (2,), 0,
                 (FIXTURES/'pass-empty.expected.json').read_bytes(), b''),
            ]
            for command in [[console], [sys.executable, '-B', '-m', 'cursorrace']]:
                for name, args, closed, code, out, err in cases:
                    with self.subTest(form=command, case=name):
                        def close_descriptors():
                            for fd in closed:
                                os.close(fd)
                        p = subprocess.run(command+args, cwd=folder, env=env,
                                           capture_output=True, preexec_fn=close_descriptors, timeout=10)
                        self.assertEqual((p.returncode, p.stdout, p.stderr), (code, out, err))

    @unittest.skipUnless(os.name == 'posix', 'Pipe descriptor setup requires POSIX; Windows is outside v1 support')
    def test_preclosed_pipe_peers_in_installed_entrypoints(self):
        console = str(Path(sys.executable).parent/'cursorrace')
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        env.pop('PYTHONPATH', None)
        with tempfile.TemporaryDirectory() as folder:
            for command in [[console], [sys.executable, '-B', '-m', 'cursorrace']]:
                for broken in ['stdout', 'stderr', 'both']:
                    with self.subTest(form=command, broken=broken):
                        # Remove readers before launching: EPIPE cannot race the child.
                        writers = []
                        try:
                            streams = {'stdout': subprocess.PIPE, 'stderr': subprocess.PIPE}
                            for stream in (['stdout', 'stderr'] if broken == 'both' else [broken]):
                                reader, writer = os.pipe()
                                os.close(reader)
                                writers.append(writer)
                                streams[stream] = writer
                            args = ['check', str(Path(folder)/'absent')] if broken == 'stderr' else ['--version']
                            p = subprocess.run(command+args, cwd=folder, env=env, timeout=10, **streams)
                        finally:
                            for writer in writers:
                                os.close(writer)
                        self.assertEqual(p.returncode, 3)
                        self.assertEqual(p.stdout, b'' if broken == 'stderr' else None)
                        self.assertEqual(p.stderr, b'cursorrace: OUTPUT_IO\n' if broken == 'stdout' else None)

    def test_normal_streams_in_installed_entrypoints(self):
        console = str(Path(sys.executable).parent/'cursorrace')
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        env.pop('PYTHONPATH', None)
        with tempfile.TemporaryDirectory() as folder:
            cases = [(['--version'], 0, b'cursorrace 0.1.0\n')]
            for case, code in [('pass-empty', 0), ('fail-multiple', 1), ('invalid-version', 2)]:
                cases.append((['check', str(FIXTURES/(case+'.json'))], code,
                              (FIXTURES/(case+'.expected.json')).read_bytes()))
            for command in [[console], [sys.executable, '-B', '-m', 'cursorrace']]:
                for args, code, out in cases:
                    with self.subTest(form=command, args=args):
                        p = subprocess.run(command+args, cwd=folder, env=env, capture_output=True, timeout=10)
                        self.assertEqual((p.returncode, p.stdout, p.stderr), (code, out, b''))

    def test_subprocess_interrupt(self):
        import signal
        code="""import signal,sys
from cursorrace import cli
def waiting(path):
    print('HARNESS_READY',file=sys.stderr,flush=True)
    signal.pause()
cli.read_input=waiting
sys.exit(cli.main(['check','x']))
"""
        p=subprocess.Popen([sys.executable,'-c',code],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        self.assertEqual(p.stderr.readline(),b'HARNESS_READY\n')
        p.send_signal(signal.SIGINT)
        out,err=p.communicate(timeout=10)
        self.assertEqual((p.returncode,out,err),(130,b'',b'cursorrace: INTERRUPTED\n'))

    def test_substitution_in_bounded_subprocess(self):
        code="""import os,sys
from cursorrace import cli
original=cli.os.open
def swapped(path,flags):
    os.unlink(path)
    os.mkfifo(path)
    return original(path,flags)
cli.os.open=swapped
sys.exit(cli.main(['check',sys.argv[1]]))
"""
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'regular';path.write_bytes(b'{}')
            p=subprocess.run([sys.executable,'-c',code,str(path)],capture_output=True,timeout=5)
            self.assertEqual((p.returncode,p.stdout,p.stderr),(3,b'',b'cursorrace: INPUT_IO\n'))

    def test_cursor_privacy_and_process_determinism(self):
        from tests.support import raw,trace,page
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'trace.json';secret='SECRET_CANARY/!%'
            target.write_bytes(raw(trace(['a'],[page(['a'],request=secret,next=secret)])))
            original=None
            for locale in ['C','C.UTF-8']:
                env=dict(os.environ,LC_ALL=locale)
                p=subprocess.run([sys.executable,'-m','cursorrace','check',str(target)],cwd=folder,env=env,capture_output=True,timeout=10)
                self.assertEqual(p.returncode,1);self.assertNotIn(secret.encode(),p.stdout+p.stderr)
                if original is not None:self.assertEqual(p.stdout,original)
                original=p.stdout
            target.write_bytes(b'{"secret":"'+secret.encode())
            p=self.invoke(['check',str(target)]);self.assertEqual(p.returncode,2);self.assertNotIn(secret.encode(),p.stdout+p.stderr)
