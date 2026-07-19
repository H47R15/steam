"""Compile ``protobufs/*.proto`` -> ``steam/protobufs/*_pb2.{py,pyi}``.

Wipes the output dir first (so a failure surfaces as "no files written"
instead of a mix of stale + new), then runs a single ``protoc`` invocation
with ``--python_out`` (runtime code) and ``--mypy_out`` (type stubs).  Then
delegates per-file cleanup to ``pb_postprocess.py``:

  * ``.py`` — sibling imports get the ``steam.protobufs.`` prefix,
    ``_globals`` arg to ``BuildServices`` becomes ``sys.modules[__name__]``,
    and ``import sys`` is injected when the rewrite introduces a
    ``sys.modules`` reference.
  * ``.pyi`` — sibling imports get the same prefix; per-message
    ``DESCRIPTOR: _descriptor.Descriptor`` overrides are stripped (they
    trip ``reportIncompatibleVariableOverride`` under types-protobuf 7.34+).

Run from the package root:

    poetry run python scripts/pb_compile.py
"""
from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
import sys

from scripts import pb_postprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PROTO_DIR = REPO_ROOT / 'protobufs'
OUT_DIR = REPO_ROOT / 'steam' / 'protobufs'

_PY_SIBLING_IMPORT_RE = re.compile(r'^import ([a-z][a-z_0-9]*_pb2)', re.MULTILINE)
_PYI_SIBLING_IMPORT_RE = re.compile(
    r'^import ([a-z][a-z_0-9]*_pb2) as (_[a-z_0-9]+)$',
    re.MULTILINE,
)


def _prefix_py_imports(path: pathlib.Path) -> None:
    src = path.read_text()
    original = src

    def _sub(match: re.Match[str]) -> str:
        line_start = src.rfind('\n', 0, match.start()) + 1
        line_end = src.find('\n', match.end())
        line = src[line_start:line_end if line_end != -1 else len(src)]
        if line.strip().startswith('import sys'):
            return match.group(0)
        return f'import steam.protobufs.{match.group(1)}'

    src = _PY_SIBLING_IMPORT_RE.sub(_sub, src)
    if src != original:
        path.write_text(src)


def _prefix_pyi_imports(path: pathlib.Path) -> None:
    src = path.read_text()
    new_src = _PYI_SIBLING_IMPORT_RE.sub(
        r'import steam.protobufs.\1 as \2',
        src,
    )
    if new_src != src:
        path.write_text(new_src)


def main() -> int:
    protos = sorted(PROTO_DIR.glob('*.proto'))
    if not protos:
        print(f'no .proto files in {PROTO_DIR}', file=sys.stderr)
        return 1

    for p in list(OUT_DIR.glob('*_pb2.py')) + list(OUT_DIR.glob('*_pb2.pyi')):
        p.unlink()

    if shutil.which('protoc') is None:
        print('protoc not found on PATH — install via `brew install protobuf`', file=sys.stderr)
        return 1

    result = subprocess.run(
        [
            'protoc',
            f'--python_out={OUT_DIR}',
            f'--mypy_out={OUT_DIR}',
            f'--proto_path={PROTO_DIR}',
            *[str(p) for p in protos],
        ],
        check=False,
    )
    if result.returncode != 0:
        return result.returncode

    for p in sorted(OUT_DIR.glob('*_pb2.py')):
        _prefix_py_imports(p)
    for p in sorted(OUT_DIR.glob('*_pb2.pyi')):
        _prefix_pyi_imports(p)

    for p in sorted(OUT_DIR.glob('*_pb2.py')):
        pb_postprocess.post_process(p)
    for p in sorted(OUT_DIR.glob('*_pb2.pyi')):
        pb_postprocess.post_process(p)

    n_py = len(list(OUT_DIR.glob('*_pb2.py')))
    n_pyi = len(list(OUT_DIR.glob('*_pb2.pyi')))
    print(f'compiled {n_py} .py + {n_pyi} .pyi under {OUT_DIR.relative_to(REPO_ROOT)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
