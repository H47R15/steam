"""Post-process protoc's ``_pb2.py`` and ``_pb2.pyi`` output.

Invoked by ``scripts/pb_compile.py`` after ``protoc`` runs.  Idempotent —
running it twice on the same file is a no-op — so a partial ``pb_compile``
retry doesn't double-apply anything.

Dispatches on file extension: ``.py`` (currently a no-op — see below) and
``.pyi`` (strips the ``DESCRIPTOR`` override).  Unknown extensions are
ignored.

### ``.py`` fixups

1. Append ``# pyright: ignore[reportArgumentType]`` to the
   ``_builder.BuildServices(DESCRIPTOR, name, _globals)`` line so
   Pylance stops flagging the third arg on every generated file.  An
   earlier iteration of this script rewrote the call to pass
   ``sys.modules[__name__]`` instead (to satisfy typeshed's
   ``ModuleType`` annotation on that param).  Turned out
   ``BuildServices`` at protobuf 6.33 does ``module[name] = ...``
   internally — item-assignment, which requires a ``dict`` and
   crashes on a real module at import time.  The typeshed signature
   is buggy; the runtime protoc output is correct, so we keep the
   dict argument AND silence the false positive per-line rather than
   file-wide (a file-wide suppression would hide other legitimate
   warnings that appear in the same generated file).  Idempotent:
   the regex requires the comment to be absent, so repeated post-
   processing of the same file is a no-op.  (See git history for
   the failing traceback from the earlier rewrite attempt.)

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


# Match ``_builder.BuildServices(DESCRIPTOR, 'foo_pb2', _globals)`` at
# any indentation but only when the ``# pyright: ignore`` suffix isn't
# already present, so the substitution is idempotent under repeated
# post-processing.  ``(?![^\n]*# pyright:)`` is a negative lookahead
# scoped to the current line via ``[^\n]*`` so a pyright comment
# elsewhere in the file doesn't accidentally suppress the rewrite on
# an unrelated BuildServices call (defensive — steam has one per file
# in practice, but generated code shape can shift with protoc bumps).
_BUILD_SERVICES_RE = re.compile(
    r'^([ \t]*_builder\.BuildServices\([^\n]*\))(?![^\n]*# pyright:)$',
    re.MULTILINE,
)


def post_process_py(path: pathlib.Path) -> None:
    """Add a per-line pyright suppression to the ``BuildServices``
    call — see module docstring for rationale.  Idempotent."""
    src = path.read_text()
    fixed = _BUILD_SERVICES_RE.sub(
        r'\1  # pyright: ignore[reportArgumentType]',
        src,
    )
    if fixed != src:
        path.write_text(fixed)


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
