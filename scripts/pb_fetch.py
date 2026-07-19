"""Fetch and normalize Steam ``.proto`` sources from SteamDatabase/SteamTracking.

Reads ``protobuf_list.txt`` (comment/blank lines skipped), downloads each URL
into ``protobufs/``, and applies the same normalizations the old Makefile
target did:

  * rename ``*.steamclient.proto`` → ``*.proto``
  * prepend ``syntax = "proto2";`` when missing (idempotent)
  * swap ``cc_generic_services`` → ``py_generic_services``
  * rewrite intra-file ``.steamclient.proto`` refs to ``.proto``

Locally-maintained ``.proto`` files (currently ``gc.proto`` /
``test_messages.proto``) are set aside via ``.notouch`` rename before download
and restored after, so upstream 404s never leave partial state.

Run from the package root:

    poetry run python scripts/pb_fetch.py
"""
from __future__ import annotations

import concurrent.futures
import pathlib
import re
import sys
import urllib.error
import urllib.request

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PROTO_DIR = REPO_ROOT / 'protobufs'
URL_LIST = REPO_ROOT / 'protobuf_list.txt'
NOTOUCH = ['gc.proto', 'test_messages.proto']


def _read_urls() -> list[str]:
    urls: list[str] = []
    for line in URL_LIST.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        urls.append(line)
    return urls


def _download(url: str) -> tuple[str, bytes | None, str | None]:
    fname = url.rsplit('/', 1)[-1]
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return fname, resp.read(), None
    except urllib.error.HTTPError as e:
        return fname, None, f'HTTP {e.code}'
    except Exception as e:
        return fname, None, str(e)


def _apply_transforms(path: pathlib.Path) -> None:
    src = path.read_text()

    if not re.match(r'\s*syntax\s*=', src):
        src = 'syntax = "proto2";\n' + src

    src = src.replace('cc_generic_services', 'py_generic_services')
    src = src.replace('.steamclient.proto', '.proto')

    path.write_text(src)


def main() -> int:
    PROTO_DIR.mkdir(parents=True, exist_ok=True)

    for name in NOTOUCH:
        p = PROTO_DIR / name
        if p.exists():
            p.rename(PROTO_DIR / f'{name}.notouch')

    urls = _read_urls()
    print(f'fetching {len(urls)} .proto files...')

    ok = miss = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        for fname, body, err in ex.map(_download, urls):
            if body is None:
                print(f'  MISS {fname}: {err}')
                miss += 1
                continue
            (PROTO_DIR / fname).write_bytes(body)
            ok += 1

    print(f'downloaded {ok} ok, {miss} missing (see comments in protobuf_list.txt)')

    for p in PROTO_DIR.glob('*.steamclient.proto'):
        p.rename(str(p).replace('.steamclient.proto', '.proto'))

    for p in PROTO_DIR.glob('*.proto'):
        _apply_transforms(p)

    for p in PROTO_DIR.glob('*.proto.notouch'):
        p.rename(str(p).removesuffix('.notouch'))

    return 0


if __name__ == '__main__':
    sys.exit(main())
