"""Regenerate ``vcr/webapi.yaml`` from live Steam Web API traffic.

Replays the same HTTP calls that ``tests/test_webapi.py`` makes at test
time and records each response into ``vcr/webapi.yaml``.  The API key is
scrubbed via VCR's ``filter_query_parameters=['key']`` filter, so the
resulting cassette is safe to commit.

Requires a real Steam Web API key in the environment.  Reads ``.env``
(via ``python-dotenv``) if present, then falls back to the process env.

Run from the package root:

    poetry run vcr-webapi

Prereqs:
    1. Copy ``.env.example`` -> ``.env`` and set ``STEAM_API_KEY=<32 hex chars>``.
       See ``.env.example`` for where to get a key.
    2. Network access to ``https://api.steampowered.com``.

The endpoints exercised (mirroring ``tests/test_webapi.py``):
    * ``ISteamWebAPIUtil.GetSupportedAPIList`` — interface discovery, done
      by ``WebAPI(...)`` at construction time.
    * ``ISteamWebAPIUtil.GetServerInfo`` (v1 + vdf format).
    * ``ISteamUser.ResolveVanityURL(vanityurl='valve', url_type=2)``.
    * ``ISteamRemoteStorage.GetPublishedFileDetails(itemcount=5, ...)``.
    * Module-level ``webapi_get`` / ``webapi_post`` for the same two endpoints.
"""
from __future__ import annotations

import os
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
VCR_DIR = REPO_ROOT / 'vcr'
CASSETTE = VCR_DIR / 'webapi.yaml'


def _load_env() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    env_path = REPO_ROOT / '.env'
    if env_path.exists():
        load_dotenv(env_path)


def _get_api_key() -> str:
    _load_env()
    key = os.environ.get('STEAM_API_KEY', '').strip()
    if not key:
        sys.exit(
            'STEAM_API_KEY not set.  Copy .env.example to .env and set the key '
            '(see .env.example for how to obtain one), or export STEAM_API_KEY '
            'in your shell.'
        )
    if len(key) != 32 or any(c not in '0123456789ABCDEFabcdef' for c in key):
        sys.exit(
            f'STEAM_API_KEY looks malformed ({len(key)} chars).  Steam Web API '
            'keys are exactly 32 hex characters.'
        )
    return key


def _scrub_req(request):
    request.headers.pop('Cookie', None)
    request.headers.pop('date', None)
    return request


def _scrub_resp(response):
    response['headers'].pop('set-cookie', None)
    response['headers'].pop('date', None)
    response['headers'].pop('expires', None)
    return response


def main() -> int:
    api_key = _get_api_key()

    # Imported lazily so ``poetry run vcr-webapi --help`` (etc.) doesn't
    # need the client extras just to fail early on a missing key.
    import vcr
    from vcr.record_mode import RecordMode

    from steam.webapi import WebAPI, get as webapi_get, post as webapi_post

    VCR_DIR.mkdir(exist_ok=True)
    if CASSETTE.exists():
        print(f'removing existing cassette: {CASSETTE.relative_to(REPO_ROOT)}')
        CASSETTE.unlink()

    rec_vcr = vcr.VCR(
        record_mode=RecordMode.ALL,
        serializer='yaml',
        filter_query_parameters=['key'],
        filter_post_data_parameters=['key'],
        cassette_library_dir=str(VCR_DIR),
        before_record_request=_scrub_req,
        before_record_response=_scrub_resp,
    )

    with rec_vcr.use_cassette('webapi.yaml'):
        print('  * WebAPI(...) -> ISteamWebAPIUtil.GetSupportedAPIList')
        api = WebAPI(api_key)
        api.session.headers['Accept-Encoding'] = 'identity'

        print('  * ISteamWebAPIUtil.GetServerInfo_v1()')
        api.ISteamWebAPIUtil.GetServerInfo_v1()

        print('  * ISteamWebAPIUtil.GetServerInfo(format=vdf)')
        api.ISteamWebAPIUtil.GetServerInfo(format='vdf')

        print("  * ISteamUser.ResolveVanityURL(vanityurl='valve', url_type=2)")
        api.ISteamUser.ResolveVanityURL(vanityurl='valve', url_type=2)

        print('  * ISteamRemoteStorage.GetPublishedFileDetails(itemcount=5, ...)')
        api.ISteamRemoteStorage.GetPublishedFileDetails(
            itemcount=5, publishedfileids=[1, 1, 1, 1, 1]
        )

        print("  * webapi_get('ISteamUser', 'ResolveVanityURL', 1, ...)")
        webapi_get(
            'ISteamUser', 'ResolveVanityURL', 1,
            session=api.session,
            params={'key': api_key, 'vanityurl': 'valve', 'url_type': 2},
        )

        print("  * webapi_post('ISteamRemoteStorage', 'GetPublishedFileDetails', 1, ...)")
        webapi_post(
            'ISteamRemoteStorage', 'GetPublishedFileDetails', 1,
            session=api.session,
            params={
                'key': api_key,
                'itemcount': 5,
                'publishedfileids': [1, 1, 1, 1, 1],
            },
        )

    size_kb = CASSETTE.stat().st_size / 1024
    print(f'\nwrote {CASSETTE.relative_to(REPO_ROOT)} ({size_kb:.1f} KB)')

    with CASSETTE.open() as fh:
        text = fh.read()
    if api_key in text:
        print('WARNING: API key found in cassette — scrubber failed!', file=sys.stderr)
        return 1
    print('key scrub verified — no plaintext API key in the cassette')
    return 0


if __name__ == '__main__':
    sys.exit(main())
