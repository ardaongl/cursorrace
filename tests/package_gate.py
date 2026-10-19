"""Pinned isolated wheel/sdist builds and installed behavior, outside checkout.

Network is permitted only for the explicit backend-wheel bootstrap. All product
runs and both fresh installations have networking denied at Python startup.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile

from .fixture_gate import run_gate
from .support import ROOT

BACKEND_SHA256 = '062d34222ad13e0cc312a4c02d73f059e86a4acbfbdea8f8f76b28c99f306922'
COMMANDS = []


def run(args,cwd=None,env=None):
    p=subprocess.run([str(a) for a in args],cwd=cwd,env=env,capture_output=True,text=True,timeout=120)
    COMMANDS.append({'command':[str(a) for a in args],'cwd':str(cwd or ROOT),'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    if p.returncode: raise AssertionError(COMMANDS[-1])
    return p.stdout.strip()


def venv(path):
    run([sys.executable,'-m','venv',path])
    python=path/'bin/python'
    assert run([python,'-c','import sys; assert sys.version_info[:3]==(3,14,8); import importlib.metadata as m; print(m.version("pip"))'])=='26.2.1'
    return python


def no_network(python):
    # Persist a test-only startup guard in the isolated venv, not in product data.
    site=Path(run([python,'-c','import sysconfig; print(sysconfig.get_path("purelib"))']))
    (site/'sitecustomize.py').write_text('import sys\ndef deny(event,args):\n if event.startswith("socket."): raise RuntimeError("package gate: network forbidden")\nsys.addaudithook(deny)\n')
    return site


def build(python,source,out,hook):
    out.mkdir(parents=True,exist_ok=True)
    return out/run([python,'-c',f'from setuptools import build_meta; print(build_meta.{hook}({str(out)!r}))'],cwd=source).splitlines()[-1]


def artifact_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    evidence=ROOT/'.local-verification/build/package'
    evidence.mkdir(parents=True,exist_ok=True)
    result={'gate':'package','status':'IN_PROGRESS','commands':COMMANDS,'artifacts':{},'installed':[]}
    try:
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp); source=tmp/'source'
            shutil.copytree(ROOT,source,ignore=shutil.ignore_patterns('.venv','.git','.local-verification','__pycache__','*.egg-info','build','dist'))
            backend=venv(tmp/'backend')
            wheelhouse=tmp/'wheelhouse';wheelhouse.mkdir()
            # The sole explicitly network-permitted dependency acquisition step.
            run([backend,'-m','pip','download','--no-cache-dir','--no-deps','--only-binary=:all:','--dest',wheelhouse,'setuptools==80.9.0'])
            backend_wheel=next(wheelhouse.glob('*.whl'))
            assert artifact_hash(backend_wheel)==BACKEND_SHA256,'unexpected pinned backend content'
            shutil.copy2(backend_wheel,evidence/backend_wheel.name)
            run([backend,'-m','pip','install','--no-index','--no-deps',backend_wheel])
            no_network(backend)
            wheel=build(backend,source,tmp/'wheel','build_wheel')
            sdist=build(backend,source,tmp/'sdist','build_sdist')
            # Reject traversal, links and special files before extracting our sdist.
            extracted=tmp/'extracted';extracted.mkdir()
            with tarfile.open(sdist) as archive:
                for member in archive.getmembers():
                    path=Path(member.name)
                    assert not path.is_absolute() and '..' not in path.parts
                    assert member.isfile() or member.isdir(),member.name
                archive.extractall(extracted,filter='data')
            unpacked=next(extracted.iterdir())
            for required in ['README.md','LICENSE','GOAL.md','AGENTS.md','docs/03-contracts.md','tests/test_reporting.py','tests/fixture_gate.py','tests/package_gate.py','fixtures/manifest.json','schemas/trace-v1.schema.json']:
                assert (unpacked/required).is_file(),required
            # Fresh-cache build environment for the sdist-derived wheel too.
            rebuild_python=venv(tmp/'rebuild')
            run([rebuild_python,'-m','pip','install','--no-index','--no-deps',backend_wheel])
            no_network(rebuild_python)
            rebuilt=build(rebuild_python,unpacked,tmp/'rebuilt','build_wheel')
            for label,path in [('wheel',wheel),('sdist',sdist),('sdist-wheel',rebuilt)]:
                target=evidence/(label+'-'+path.name);shutil.copy2(path,target)
                result['artifacts'][label]={'path':str(target.relative_to(ROOT)),'sha256':artifact_hash(target)}
            with zipfile.ZipFile(wheel) as z:
                names=z.namelist()
                assert 'cursorrace/README.md' in names
                assert all('cursorrace/schemas/'+p.name in names for p in (ROOT/'schemas').glob('*.json'))
                assert any(n.endswith('/licenses/LICENSE') for n in names)
            clean_env={k:v for k,v in os.environ.items() if k!='PYTHONPATH'}
            for label,artifact in [('wheel',wheel),('sdist',rebuilt)]:
                python=venv(tmp/('installed-'+label));site=no_network(python)
                run([python,'-m','pip','install','--no-index','--no-deps',artifact],cwd=tmp,env=clean_env)
                metadata=run([python,'-c','import cursorrace,importlib.metadata as m; from importlib.resources import files; d=m.distribution("cursorrace"); assert d.version=="0.1.0"; assert not d.requires; assert set(d.metadata["Requires-Python"].split(","))=={">=3.14.8","<3.15"}; assert d.metadata["License-Expression"]=="MIT"; assert files("cursorrace").joinpath("README.md").is_file(); assert files("cursorrace").joinpath("schemas/trace-v1.schema.json").is_file(); print(cursorrace.__file__)'],cwd=tmp,env=clean_env)
                assert str(site) in metadata and str(ROOT) not in metadata
                for flag in ['--help','--version']:
                    text=run([python.parent/'cursorrace',flag],cwd=tmp,env=clean_env)
                    assert 'Usage:' in text if flag=='--help' else text=='cursorrace 0.1.0'
                cases=run_gate(python=python,console=python.parent/'cursorrace',fixtures=unpacked/'fixtures',cwd=tmp)
                result['installed'].append({'artifact':label,'cases':len(cases),'processes':2*len(cases),'network':'denied by isolated venv startup hook','runtime_dependencies':[]})
            result['backend_sha256']=BACKEND_SHA256
            result['status']='PASS'
    except Exception as exc:
        result['status']='FAIL'
        result['failure']=str(exc)
        raise
    finally:
        (evidence/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='commands'},sort_keys=True))


if __name__=='__main__': main()
