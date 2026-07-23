"""Framework glue for :mod:`steam.aio`.

Each submodule targets a specific async framework and is safe to
import even when that framework isn't installed — the framework
import happens lazily inside the helper functions, so a caller who
only wants FastAPI won't accidentally pull in TaskIQ.

Submodules:

* :mod:`steam.aio.integrations.fastapi` — ``lifespan`` context
  manager + ``Depends`` provider.
* :mod:`steam.aio.integrations.taskiq` — broker startup/shutdown
  hook + ``TaskiqDepends`` provider.
"""
