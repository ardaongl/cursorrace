"""Process boundary: bounded regular-file reads and exact channels/exit statuses."""
import os
import stat
import sys

from . import __version__
from .check import check
from .decode import MAX_BYTES, decode
from .ledger import validate
from .model import InputError
from .report import error, serialize

_HELP = """Usage: cursorrace check [--] PATH
       cursorrace --help | --version
Audit one offline snapshot trace; '-' is a literal filename.
Exit codes: 0 pass, 1 findings, 2 invalid input/arguments, 3 IO/internal, 130 interrupt.
"""


class ExecutionError(Exception):
    pass


def read_input(path):
    # Open nonblocking, then inspect the actual descriptor. No stat/open race and
    # a substituted FIFO cannot hang or be consumed. Regular symlinks are allowed.
    try:
        path.encode("utf-8")
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise OSError("nonregular input")
            chunks = []
            remaining = MAX_BYTES + 1
            while remaining:
                chunk = os.read(fd, min(65536, remaining))
                if not chunk:
                    break
                chunks.append(chunk)
                remaining -= len(chunk)
            return b"".join(chunks)
        finally:
            os.close(fd)
    except (OSError, UnicodeError, ValueError):
        raise ExecutionError("INPUT_IO") from None


def _execute(args):
    if args in (["--help"], ["check", "--help"]):
        return _HELP, 0
    if args == ["--version"]:
        return f"cursorrace {__version__}\n", 0
    if len(args) == 3 and args[:2] == ["check", "--"]:
        path = args[2]
    elif len(args) == 2 and args[0] == "check" and (not args[1].startswith("-") or args[1] == "-"):
        path = args[1]
    else:
        raise InputError("ARGUMENT", None)
    trace = decode(read_input(path))
    validate(trace)
    result = check(trace)
    return serialize(result), 0 if result["status"] == "pass" else 1


def _diagnostic(code, status=3):
    if sys.stderr is None:
        return 3
    try:
        sys.stderr.write(f"cursorrace: {code}\n")
        sys.stderr.flush()
    except (OSError, ValueError):
        sys.stderr = None  # Avoid another failing stream flush at interpreter exit.
        return 3
    return status


def main(argv=None):
    try:
        try:
            payload, status = _execute(list(sys.argv[1:] if argv is None else argv))
        except InputError as exc:
            payload, status = serialize(error(exc.code, exc.pointer)), 2
        if sys.stdout is None:
            return _diagnostic("OUTPUT_IO")
        try:
            sys.stdout.write(payload)
            sys.stdout.flush()
        except (OSError, ValueError):
            sys.stdout = None  # No /dev/null file creation and no final EPIPE retry.
            return _diagnostic("OUTPUT_IO")
        return status
    except KeyboardInterrupt:
        return _diagnostic("INTERRUPTED", 130)
    except ExecutionError as exc:
        return _diagnostic(str(exc))
    except Exception:
        return _diagnostic("INTERNAL")
