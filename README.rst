.. image:: https://raw.githubusercontent.com/H47R15/steam/master/.github/cover.png
   :alt: pysteam-client
   :align: center

|ci-badge| |codeql-badge| |scorecard-badge| |pypi-badge| |python-badge| |mcp-badge| |license-badge|

.. |ci-badge| image:: https://github.com/H47R15/steam/actions/workflows/testing_initiative.yml/badge.svg?branch=master
   :alt: CI status
   :target: https://github.com/H47R15/steam/actions/workflows/testing_initiative.yml
.. |codeql-badge| image:: https://github.com/H47R15/steam/actions/workflows/codeql.yml/badge.svg?branch=master
   :alt: CodeQL SAST
   :target: https://github.com/H47R15/steam/actions/workflows/codeql.yml
.. |scorecard-badge| image:: https://api.securityscorecards.dev/projects/github.com/H47R15/steam/badge
   :alt: OpenSSF Scorecard
   :target: https://api.securityscorecards.dev/projects/github.com/H47R15/steam
.. |pypi-badge| image:: https://img.shields.io/pypi/v/pysteam-client.svg
   :alt: PyPI version
   :target: https://pypi.org/project/pysteam-client/
.. |python-badge| image:: https://img.shields.io/pypi/pyversions/pysteam-client.svg
   :alt: Python versions
   :target: https://pypi.org/project/pysteam-client/
.. |mcp-badge| image:: https://img.shields.io/badge/MCP-tools_included-8A2BE2?logo=anthropic&logoColor=white
   :alt: MCP tools included
   :target: https://github.com/H47R15/steam/wiki/MCP
.. |license-badge| image:: https://img.shields.io/pypi/l/pysteam-client.svg
   :alt: License
   :target: https://github.com/H47R15/steam/blob/master/LICENSE


pysteam-client
==============

Modern Python client for the Steam network — CM protocol, PICS, CDN, WebAuth,
Web API, Steam Guard, SteamIDs — plus a fully-async facade for FastAPI /
TaskIQ and an MCP tool set for LLM agents.

Maintained fork of `ValvePython/steam <https://github.com/ValvePython/steam>`_
for Python 3.13+ and current Steam wire protocols.  Full docs in the
`Wiki <https://github.com/H47R15/steam/wiki>`_.

Install
-------

.. code:: bash

    pip install pysteam-client[client]

``[client]`` pulls in the gevent-based ``SteamClient`` (login, PICS, CDN).
Without it the ``requests``-only subset (WebAPI / WebAuth / SteamID /
master-server query) still works.

Quick start
-----------

**Sync** (script, CLI, batch jobs):

.. code:: python

    from steam.client import SteamClient

    client = SteamClient()
    client.anonymous_login()
    info = client.get_product_info(apps=[440], timeout=15)
    print(info["apps"][440]["common"]["name"])
    client.logout()

**Async** (FastAPI, TaskIQ, any asyncio app):

.. code:: python

    from steam.aio import AsyncSteamClient

    async with AsyncSteamClient() as client:
        await client.anonymous_login()
        info = await client.get_product_info(apps=[440])

**MCP** (expose to an LLM agent):

.. code:: python

    from mcp.server.fastmcp import FastMCP
    from steam.aio import AsyncSteamClient
    from steam.mcp import register_steam_tools

    server = FastMCP("Steam")
    client = AsyncSteamClient()
    await client.start()
    await client.anonymous_login()
    register_steam_tools(server, client)   # steam.status, steam.get_product_info, steam.send_um

Documentation
-------------

Full documentation lives in the
`Wiki <https://github.com/H47R15/steam/wiki>`_.  Highlights:

**Getting started**

* `Installation <https://github.com/H47R15/steam/wiki/Installation>`_
* `First script <https://github.com/H47R15/steam/wiki/First-script>`_

**Client APIs**

* `SteamClient <https://github.com/H47R15/steam/wiki/SteamClient>`_ — sync gevent client (the original)
* `PICS <https://github.com/H47R15/steam/wiki/PICS>`_ — app / package metadata
* `CDNClient <https://github.com/H47R15/steam/wiki/CDNClient>`_ — depot downloads
* `WebAuth <https://github.com/H47R15/steam/wiki/WebAuth>`_ — authenticated session
* `WebAPI <https://github.com/H47R15/steam/wiki/WebAPI>`_ — ``api.steampowered.com`` wrapper
* `SteamAuthenticator <https://github.com/H47R15/steam/wiki/SteamAuthenticator>`_ — 2FA
* `SteamID <https://github.com/H47R15/steam/wiki/SteamID>`_ — parse / convert Steam IDs
* `Master Server Queries <https://github.com/H47R15/steam/wiki/Master-Server-Queries>`_

**Async / FastAPI / MCP** (new in 1.6)

* `AsyncSteamClient <https://github.com/H47R15/steam/wiki/AsyncSteamClient>`_ — asyncio facade
* `Pool <https://github.com/H47R15/steam/wiki/Pool>`_ — multi-account
* `FastAPI Integration <https://github.com/H47R15/steam/wiki/FastAPI-Integration>`_
* `TaskIQ Integration <https://github.com/H47R15/steam/wiki/TaskIQ-Integration>`_
* `MCP <https://github.com/H47R15/steam/wiki/MCP>`_ — Model Context Protocol tools + FastMCP adapter

**Advanced**

* `Regenerating Protobufs <https://github.com/H47R15/steam/wiki/Regenerating-Protobufs>`_
* `Type Checking <https://github.com/H47R15/steam/wiki/Type-Checking>`_
* `Contributing <https://github.com/H47R15/steam/wiki/Contributing>`_
* `Fork Changes <https://github.com/H47R15/steam/wiki/Fork-Changes>`_
* `FAQ <https://github.com/H47R15/steam/wiki/FAQ>`_

Security
--------

Every push, PR, and release runs the following gates before any wheel ships
to PyPI: ``ruff`` + ``black`` (style), ``mypy --strict`` (types),
``pytest`` (unit + integration), ``deptry`` (deps hygiene),
``bandit`` (Python SAST), ``pip-audit`` (CVEs), CodeQL (cross-file SAST),
OpenSSF Scorecard (repo posture).  A failing gate blocks the publish step.

**Report a vulnerability**: use
`GitHub Security Advisories <https://github.com/H47R15/steam/security/advisories/new>`_
(private, coordinated disclosure).  Full policy in
`SECURITY.md <https://github.com/H47R15/steam/blob/master/SECURITY.md>`_.
**Do NOT open a public GitHub issue for security reports.**

License
-------

MIT — see `LICENSE <https://github.com/H47R15/steam/blob/master/LICENSE>`_.
Unchanged from upstream.
