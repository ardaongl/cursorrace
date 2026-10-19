"""Test-only startup instrumentation. Copied as sitecustomize in isolated runs.

Records denied attempts even if caught. This is a Python-level observation
boundary, not a claim to observe every possible native/OS operation.
"""
import atexit
import json
import os
import posix
import sys

ATTEMPTS = []
CACHE_OPERATIONS = []
FD_PATHS = {}
ROOTS = tuple(os.environ.get('CURSORRACE_GUARD_CACHE_ROOTS','').split(os.pathsep))


def _name(value):
    if isinstance(value,int): return FD_PATHS.get(value,f'fd:{value}')
    return os.fsdecode(os.fspath(value))


def _import_cache(paths):
    paths = [_name(p) for p in paths]
    if not all(any(p.startswith(root+os.sep) for root in ROOTS if root) for p in paths): return False
    if not all('__pycache__' in p.split(os.sep) for p in paths): return False
    frame = sys._getframe(1)
    while frame:
        if frame.f_globals.get('__name__') in ('_frozen_importlib_external','importlib._bootstrap_external') and frame.f_code.co_name in ('_write_atomic','_cache_bytecode'):
            return True
        frame = frame.f_back
    return False


def _mutation(event,paths):
    names = [_name(p) for p in paths]
    if _import_cache(paths):
        CACHE_OPERATIONS.append([event,names])
        return
    ATTEMPTS.append([event,names])
    raise PermissionError('test guard: forbidden application mutation')


def hook(event,args):
    if event == 'open':
        path,mode,flags=args
        if (flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)) or (mode and any(c in mode for c in 'wax+')):
            _mutation(event,[path])
    elif event in ('os.remove','os.rmdir','os.mkdir','os.truncate','os.chmod','os.chown','os.utime','os.link','os.symlink'):
        _mutation(event,[args[0]])
    elif event == 'os.rename':
        _mutation(event,args[:2])
    elif event.startswith('socket.'):
        ATTEMPTS.append([event,[]])
        raise PermissionError('test guard: network denied')


_original_open = os.open
_original_write = os.write
_original_ftruncate = os.ftruncate


def guarded_open(path,flags,*args,**kwargs):
    fd = _original_open(path,flags,*args,**kwargs)
    FD_PATHS[fd] = _name(path)
    return fd


def guarded_write(fd,data):
    if fd not in (1,2): _mutation('os.write',[fd])
    return _original_write(fd,data)


def guarded_ftruncate(fd,length):
    _mutation('os.ftruncate',[fd])


def finish():
    payload=json.dumps({'attempts':ATTEMPTS,'bytecode_operations':CACHE_OPERATIONS},sort_keys=True).encode()
    _original_write(2,b'\nCURSORRACE_GUARD_RESULT='+payload+b'\n')


sys.addaudithook(hook)
posix.open = guarded_open
os.open = guarded_open
os.write = guarded_write
os.ftruncate = guarded_ftruncate
atexit.register(finish)
