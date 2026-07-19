"""Regenerate ``steam/enums/proto.py`` from compiled ``*_pb2`` modules.

Scans every ``steam/protobufs/*_pb2.py`` for ``EnumTypeWrapper``-typed
top-level objects (i.e. proto-defined enums), filters out any that are
already declared in ``steam.enums.common``, strips the ``k_<EnumName>_``
prefix that Valve puts on member names, and emits a Python file of proper
``SteamIntEnum`` classes.

Members that would collide with Python keywords or start with a digit fall
back to the factory form ``SteamIntEnum(name, {member: value, ...})``
because the ``class X(SteamIntEnum): NAME = VALUE`` syntax can't express
those.

Was ``generate_enums_from_proto.py`` at the repo root, printing to stdout
for shell redirection.  Moved here + writes directly to the output file so
the poetry entrypoint is self-contained.

Run from the package root (after ``pb_compile``):

    poetry run python scripts/pb_gen_enums.py
"""
from __future__ import annotations

import pathlib
import re
import sys
from keyword import kwlist as _python_keywords

from google.protobuf.internal.enum_type_wrapper import EnumTypeWrapper

from steam.enums import common as common_enums

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PB2_DIR = REPO_ROOT / 'steam' / 'protobufs'
OUT_FILE = REPO_ROOT / 'steam' / 'enums' / 'proto.py'

RESERVED = set(_python_keywords) | {'None'}


def _collect() -> dict[str, tuple[dict[str, int], bool]]:
    """{ClassName: ({member: value, ...}, needs_factory_form)}."""
    module_names = sorted(
        p.stem for p in PB2_DIR.glob('*_pb2.py') if p.stem != '__init__'
    )
    parent = __import__('steam.protobufs', globals(), locals(), module_names, 0)

    classes: dict[str, tuple[dict[str, int], bool]] = {}

    for mod_name in module_names:
        proto = getattr(parent, mod_name)
        for class_name, value in vars(proto).items():
            if not isinstance(value, EnumTypeWrapper):
                continue
            if hasattr(common_enums, class_name):
                continue

            attrs: dict[str, int] = {}
            needs_factory = False
            for key, val in value.items():
                key = re.sub(r'^(k_)?(%s_)?' % re.escape(class_name), '', key)
                attrs[key] = val
                if key[:1].isdigit() or key in RESERVED:
                    needs_factory = True

            classes[class_name] = (attrs, needs_factory)

    return classes


def _emit(classes: dict[str, tuple[dict[str, int], bool]]) -> str:
    out: list[str] = ['from steam.enums.base import SteamIntEnum']

    for name in sorted(classes, key=lambda x: x.lower()):
        attrs, factory = classes[name]
        if factory:
            out.append(f'\n{name} = SteamIntEnum({name!r}, {{')
            for k, v in attrs.items():
                out.append(f'    {k!r}: {v!r},')
            out.append('    })')
        else:
            out.append(f'\nclass {name}(SteamIntEnum):')
            for k, v in attrs.items():
                out.append(f'    {k} = {v}')

    out.append('\n__all__ = [')
    for name in sorted(classes, key=lambda x: x.lower()):
        out.append(f'    {name!r},')
    out.append('    ]')
    return '\n'.join(out) + '\n'


def main() -> int:
    classes = _collect()
    OUT_FILE.write_text(_emit(classes))
    print(f'wrote {len(classes)} enum classes to {OUT_FILE.relative_to(REPO_ROOT)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
