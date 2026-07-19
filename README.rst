steam
=====

Python client for the Steam network — CM protocol, PICS / CDN, WebAuth,
Web API, Steam Guard, SteamIDs, master-server queries.

**This is a fork of** `ValvePython/steam <https://github.com/ValvePython/steam>`_
maintained under `H47R15/steam <https://github.com/H47R15/steam>`_.  The
upstream project is largely inactive; this fork exists to keep the library
working against modern Python and current Steam wire protocols.

What changed vs. upstream
-------------------------

* **Python 3.13+ only.**  Dropped the py2 / py<3.4 compat shims (``six``,
  ``six.moves``, ``raw_input``, ``xrange``, ``long``, ``win_inet_pton``,
  ``backports.lzma``, ``enum34``, …).
* **Modern protobuf runtime + regenerated ``_pb2`` files.**  Bumped from
  ``protobuf==3.20.3`` to ``>=5.26,<7`` and re-ran ``protoc`` (v33.2) against
  fresh SteamDB proto sources.  The old per-message
  ``_reflection.GeneratedProtocolMessageType`` codegen shrunk ~20× to the
  modern ``_descriptor_pool.AddSerializedFile`` + ``_builder`` pattern
  (``steammessages_base_pb2.py``: 2 200 → 96 lines).
* **Full ``.pyi`` type stubs** for every ``_pb2`` file via ``mypy-protobuf``
  — ``msg.field`` accesses now type-check under Pylance / pyright.
* **Poetry-first workflow.**  ``pip`` + ``Makefile`` + ``setup.py``
  replaced by a single ``pyproject.toml``; regeneration steps registered as
  ``poetry run pb-*`` console scripts (details below).
* **~50 new proto files** picked up from upstream since the fork was last
  synced (family groups, game recording, remote client, SteamOS webui
  messages, HTML messages, virtual controller, community messages, and
  more).  ``steam/enums/proto.py`` grew from 90 → 247 enums.
* Real latent bug fixes surfaced while porting — e.g. a ``list + map(...)``
  ``TypeError`` in ``struct.py``, a tuple-vs-int mismatch in
  ``MarketingMessage.flags``, ``hexlify(None)`` in avatar-URL fallback,
  broken ``CookieJar`` iteration in ``WebAuth``.

Requirements
------------

* Python **3.13.11** (pinned via ``pyproject.toml``).  Any newer 3.13.x is
  fine.  Older Pythons are not supported.
* `Poetry <https://python-poetry.org/>`_ for dependency management.
* ``protoc`` on ``PATH`` — required only when regenerating the ``_pb2``
  files (``poetry run pb-compile``).  Install via ``brew install protobuf``
  on macOS or the equivalent from your distro.

Install
-------

Clone the repo and install with poetry:

.. code:: bash

    git clone https://github.com/H47R15/steam.git
    cd steam
    poetry install --with dev --extras client

The ``client`` extra pulls in ``gevent`` + ``protobuf`` + ``gevent-eventemitter``
— required by ``SteamClient`` and CDN.  Without it, only the
``requests``-based subset (WebAPI / WebAuth / SteamID / master-server
query) is functional.

Features
--------

* **SteamClient** — CM protocol client on top of gevent.  Login flows
  (password / QR / refresh token), PICS product info, friends list, chat,
  game coordinator hooks.
* **CDNClient** — content depot downloads with manifest parsing.
* **WebAuth / MobileWebAuth** — obtain authenticated ``requests.Session``
  cookies for ``store.steampowered.com`` / ``steamcommunity.com``.
* **WebAPI** — thin wrapper around Steam's ``api.steampowered.com`` that
  introspects the interface catalogue at construction time.
* **SteamAuthenticator** — enable / disable / verify Steam Guard 2FA.
* **SteamID** — parse and convert between the 32-bit / 64-bit /
  ``STEAM_X:Y:Z`` / community-URL representations.
* **Master server query protocol** — query masters directly or through
  ``SteamClient``.

Dev workflow (poetry)
---------------------

All commands run from the repo root.

.. code:: bash

    poetry install --with dev --extras client   # install everything
    poetry run pytest                           # run the test suite (~83 tests, ~1s)
    poetry run pytest -k test_webauth           # filter to a subset
    poetry run pytest --tb=short -q             # concise output

    poetry run pylint steam                     # optional lint pass

Regenerating protobufs
----------------------

The ``_pb2.py`` and ``_pb2.pyi`` files under ``steam/protobufs`` are
generated from ``.proto`` sources under ``protobufs/``.  Console scripts:

.. code:: bash

    poetry run pb-fetch       # download + normalize .proto files from SteamDB
    poetry run pb-compile     # protoc --python_out --mypy_out + post-process
    poetry run pb-services    # regenerate steam/core/msg/unified.py service map
    poetry run pb-gen-enums   # regenerate steam/enums/proto.py from *_pb2

    poetry run pb-update      # all four in sequence — the usual entry point

``pb-fetch`` reads URLs from ``protobuf_list.txt`` (comments and blank
lines skipped) and downloads them into ``protobufs/``.  Locally-maintained
``.proto`` files (``gc.proto``, ``test_messages.proto``) are set aside via
``.notouch`` rename before the fetch and restored after.

``pb-compile`` wipes ``steam/protobufs/*_pb2.{py,pyi}`` first, then runs a
single ``protoc`` invocation over every ``.proto``.  Post-processing:

* ``.py`` — sibling protobuf imports get the ``steam.protobufs.`` prefix
  so runtime import works without ``steam/protobufs/`` on ``sys.path``.
* ``.pyi`` — ``DESCRIPTOR: _descriptor.Descriptor`` overrides inside each
  message class are stripped (they trip
  ``reportIncompatibleVariableOverride`` under types-protobuf 7.34+; the
  parent ``Message`` class's union type is inherited instead).

VCR fixtures
------------

Web-facing tests (``test_webapi.py``, ``test_webauth.py``,
``test_steamid.py``) replay recorded HTTP fixtures from ``vcr/*.yaml`` in
``RecordMode.NONE`` — no live network, no credentials needed for CI.

To regenerate the ``webapi.yaml`` cassette against a fresh Steam API
response, copy ``.env.example`` to ``.env`` and fill in ``STEAM_API_KEY``
(see the template for instructions on where to get one), then follow the
regen recipe at the top of ``tests/test_webapi.py``.

The ``webauth_*.yaml`` cassettes are regenerated by
``tests/generete_webauth_vcr.py`` — needs real Steam credentials at run
time; run interactively when the anonymized replay drifts from live.

Live smoke test
---------------

Beyond the unit suite, the CM handshake / anonymous-login / PICS-fetch
end-to-end flow can be smoke-tested against live Steam:

.. code:: python

    from steam.client import SteamClient

    client = SteamClient()
    assert client.anonymous_login()
    resp = client.get_product_info(apps=[553850], timeout=15)  # Helldivers 2
    print(resp['apps'][553850]['common']['name'])
    client.logout()
    client.disconnect()

Layout
------

.. code::

    steam/
    ├── steam/              # library source
    │   ├── client/         # SteamClient, CDN, builtins/*
    │   ├── core/           # CM protocol, message framing
    │   ├── enums/          # SteamIntEnum wrappers (common.py hand-written,
    │   │                   #   proto.py auto-generated by pb-gen-enums)
    │   ├── protobufs/      # generated *_pb2.py + *_pb2.pyi
    │   └── utils/
    ├── scripts/            # poetry console-script entry points (pb-*)
    ├── protobufs/          # .proto sources (fetched by pb-fetch)
    ├── typings/            # local pyright stubs (see typings/…/builder.pyi
    │                       #   for the BuildServices typeshed override)
    ├── tests/              # pytest suite
    ├── vcr/                # recorded HTTP fixtures for offline test replay
    ├── docs/               # Sphinx source (rendered at steam.readthedocs.io
    │                       #   — kept in-tree but not currently deployed
    │                       #   from this fork)
    └── pyproject.toml      # poetry config + [tool.pyright]

Upstream links (reference only — refer to this fork for maintained code):

* Upstream: https://github.com/ValvePython/steam
* Old docs: https://steam.readthedocs.io/en/latest/  (mostly still
  applicable — the library shape has not diverged from upstream, only its
  Python-runtime and protobuf-vintage baseline)
* Command-line companion (unmaintained upstream):
  https://github.com/ValvePython/steamctl

License
-------

MIT (unchanged from upstream).  See ``LICENSE``.
