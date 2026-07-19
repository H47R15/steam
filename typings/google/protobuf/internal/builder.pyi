"""Local stub override — fixes a typeshed bug in the google-stubs builder stub.

Upstream ``google-stubs`` (types-protobuf 7.34.x) declares
``BuildServices(..., module: ModuleType)`` but the runtime implementation
at ``google/protobuf/internal/builder.py`` does ``module[name] = ...``,
which requires a ``MutableMapping``, not a real ``types.ModuleType``.  The
other three ``Build*`` functions in the same file already ship the correct
``dict[str, Any]`` annotation — this stub just aligns ``BuildServices``
with them.

Symptom without this override: every ``steam/protobufs/*_pb2.py`` with a
``service`` declaration reports ``reportArgumentType`` on the
``_globals`` argument to ``BuildServices``, even though the runtime code
is correct.

Pyright / Pylance discovers this file automatically via the default
``typings/`` local-stubs convention (see ``[tool.pyright].stubPath`` in
``pyproject.toml``).  Filed against types-protobuf: no upstream fix as of
publication of this stub — remove this override once typeshed lands the
same correction on ``BuildServices``.
"""
from typing import Any

from google.protobuf.descriptor import FileDescriptor

def BuildMessageAndEnumDescriptors(file_des: FileDescriptor, module: dict[str, Any]) -> None: ...
def BuildTopDescriptorsAndMessages(file_des: FileDescriptor, module_name: str, module: dict[str, Any]) -> None: ...
def AddHelpersToExtensions(file_des: FileDescriptor) -> None: ...
def BuildServices(file_des: FileDescriptor, module_name: str, module: dict[str, Any]) -> None: ...
