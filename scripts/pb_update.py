"""Full protobuf refresh: fetch → compile → services → gen_enums.

Convenience runner equivalent to the old ``make pb_update`` target.  Chains
the four scripts in order and short-circuits on any non-zero exit code so a
partial refresh doesn't leave the tree in a mixed state.

Run from the package root:

    poetry run python scripts/pb_update.py
"""
from __future__ import annotations

import sys

from scripts import pb_compile, pb_fetch, pb_gen_enums, pb_services

_STEPS = [
    ('pb_fetch',     pb_fetch.main),
    ('pb_compile',   pb_compile.main),
    ('pb_services',  pb_services.main),
    ('pb_gen_enums', pb_gen_enums.main),
]


def main() -> int:
    for name, fn in _STEPS:
        print(f'\n=== {name} ===')
        rc = fn()
        if rc != 0:
            print(f'{name} failed (rc={rc}) — aborting', file=sys.stderr)
            return rc
    return 0


if __name__ == '__main__':
    sys.exit(main())
