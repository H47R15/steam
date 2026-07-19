"""Post-process protoc's ``_pb2.py`` and ``_pb2.pyi`` output.

Invoked by ``scripts/pb_compile.py`` after ``protoc`` runs.  Idempotent —
running it twice on the same file is a no-op — so a partial ``pb_compile``
retry doesn't double-apply anything.

Dispatches on file extension: ``.py`` (currently a no-op — see below) and
``.pyi`` (strips the ``DESCRIPTOR`` override).  Unknown extensions are
ignored.

### ``.py`` fixups

*None* — the runtime code from ``protoc --python_out`` is left as-is.  An
earlier iteration of this script rewrote
``_builder.BuildServices(DESCRIPTOR, name, _globals)`` to pass
``sys.modules[__name__]`` instead (to satisfy typeshed's ``ModuleType``
annotation on that param).  Turned out ``BuildServices`` at protobuf 6.33
does ``module[name] = ...`` internally — item-assignment, which requires a
``dict`` and crashes on a real module at import time.  The typeshed
signature is buggy; the runtime protoc output is correct, so we leave it
alone and accept the ``reportArgumentType`` Pylance warning on auto-
generated files as a known upstream typeshed issue.  (See git history for
the failing traceback.)

### ``.pyi`` fixups

1. Strip ``DESCRIPTOR: _descriptor.Descriptor`` overrides inside message
   classes at ANY indentation depth.  ``types-protobuf 7.34+`` types the
   base ``Message.DESCRIPTOR`` as ``Descriptor | _upb_Descriptor``; mypy-
   protobuf emits the narrower single-type override, which trips
   ``reportIncompatibleVariableOverride`` because mutable-attribute
   variance forbids narrowing.  Deleting the override lets each Message
   subclass inherit the correctly-typed union.  Module-level
   ``FileDescriptor`` and enum-wrapper ``EnumDescriptor`` overrides are
   left alone (they don't collide).  The ``^\\s+`` regex matches any
   leading whitespace so triply-nested (16-space) or deeper classes are
   covered too.
"""
from __future__ import annotations

import pathlib
import re
import sys

_PYI_DESCRIPTOR_OVERRIDE_RE = re.compile(
    r'^\s+DESCRIPTOR: _descriptor\.Descriptor\n',
    re.MULTILINE,
)


def post_process_py(path: pathlib.Path) -> None:
    """No-op — see module docstring for rationale."""


def post_process_pyi(path: pathlib.Path) -> None:
    src = path.read_text()
    stripped = _PYI_DESCRIPTOR_OVERRIDE_RE.sub('', src)
    if stripped != src:
        path.write_text(stripped)


def post_process(path: pathlib.Path) -> None:
    if path.suffix == '.py':
        post_process_py(path)
    elif path.suffix == '.pyi':
        post_process_pyi(path)


if __name__ == '__main__':
    for arg in sys.argv[1:]:
        post_process(pathlib.Path(arg))
