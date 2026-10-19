"""Run immutable goldens through real installed console and module processes."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from .support import FIXTURES


def run_gate(python=None, console=None, fixtures=FIXTURES, cwd=None):
    python = Path(python or sys.executable).absolute()
    console = Path(console or python.parent/'cursorrace')
    cases = json.loads((fixtures/'manifest.json').read_text())['cases']
    assert len(cases) == 17 and len({c['id'] for c in cases}) == 17, 'fixture inventory drift'
    results = []
    env = {k:v for k,v in os.environ.items() if k != 'PYTHONPATH'}
    with tempfile.TemporaryDirectory() as folder:
        for case in cases:
            target = (fixtures/case['input']).absolute()
            expected = (fixtures/case['stdout']).read_bytes()
            for command in [[str(console),'check',str(target)], [str(python),'-m','cursorrace','check',str(target)]]:
                process = subprocess.run(command,cwd=cwd or folder,env=env,capture_output=True,timeout=15)
                actual = process.returncode,process.stdout,process.stderr
                wanted = case['exit_code'],expected,case['stderr'].encode()
                assert actual == wanted, (case['id'],command,actual,wanted)
            results.append({'id':case['id'],'exit_code':case['exit_code'],'stdout_sha256':hashlib.sha256(expected).hexdigest()})
    return results


def main():
    results = run_gate()
    print(json.dumps({'gate':'fixtures','cases':len(results),'processes':len(results)*2,'status':'PASS','results':results},sort_keys=True))


if __name__ == '__main__': main()
