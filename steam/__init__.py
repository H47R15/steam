__version__ = "1.8.2"
__author__ = "Rossen Georgiev"

version_info = (1, 4, 4)

# Re-export the ``webapi`` submodule so ``from steam import webapi``
# is resolvable by type-checkers (Pylance / pyright).  At runtime the
# statement always worked because Python auto-binds submodules onto
# their parent package on import, but static analysers only pick up
# what's explicitly named in ``__init__.py``.
from . import webapi

__all__ = ["webapi"]
