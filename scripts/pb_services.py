"""Regenerate the ``ServiceName -> _pb2 module`` map in ``steam/core/msg/unified.py``.

The dict body between the ``# MARK_SERVICE_START`` and ``# MARK_SERVICE_END``
inline-comment markers is overwritten from a fresh scan of every ``.proto``
file's top-level ``service`` declarations.  Preserves the surrounding
``service_lookup = {`` opening and ``}`` closing lines untouched.

Run from the package root (after ``pb_compile``):

    poetry run python scripts/pb_services.py
"""
from __future__ import annotations

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PROTO_DIR = REPO_ROOT / 'protobufs'
UNIFIED_PY = REPO_ROOT / 'steam' / 'core' / 'msg' / 'unified.py'

_SERVICE_DECL_RE = re.compile(r'^\s*service\s+(\w+)\s*{', re.MULTILINE)
_MARK_START = 'MARK_SERVICE_START'
_MARK_END = 'MARK_SERVICE_END'
_FIELD_WIDTH = 35  # matches the historical awk ``%-35s`` alignment


def _collect_services() -> list[tuple[str, str]]:
    """Return (ServiceName, ``steam.protobufs.X_pb2``) pairs in .proto order."""
    pairs: list[tuple[str, str]] = []
    for proto in sorted(PROTO_DIR.glob('*.proto')):
        module = f'steam.protobufs.{proto.stem}_pb2'
        for match in _SERVICE_DECL_RE.finditer(proto.read_text()):
            pairs.append((match.group(1), module))
    return pairs


def main() -> int:
    src = UNIFIED_PY.read_text()
    lines = src.splitlines(keepends=True)

    start_idx = end_idx = -1
    for i, line in enumerate(lines):
        if _MARK_START in line:
            start_idx = i
        elif _MARK_END in line:
            end_idx = i
            break

    if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
        print(f'markers missing (or out of order) in {UNIFIED_PY}', file=sys.stderr)
        return 1

    services = _collect_services()

    entries = [
        "    {:<{width}} '{}',\n".format(f"'{name}':", module, width=_FIELD_WIDTH)
        for name, module in services
    ]

    UNIFIED_PY.write_text(
        ''.join(lines[: start_idx + 1] + entries + lines[end_idx:])
    )
    print(f'wrote {len(services)} service registrations to {UNIFIED_PY.name}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
