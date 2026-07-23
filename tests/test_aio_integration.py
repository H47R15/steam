"""Live integration smoke test for :class:`steam.aio.AsyncSteamClient`.

Skipped by default.  Set ``RUN_LIVE=1`` in the environment to run.

Rationale
---------

Every other test in this suite mocks the sync client — that catches
wiring bugs in the async bridge but says nothing about whether the
whole stack still works against real Steam servers.  Steam changes
their CM protocol, their content-manager list, their persisted-
query hashes, and their proto shapes multiple times a year.  When
they do, only a live test fails.

The test itself is deliberately narrow:

1. Anonymous-login to a real CM.  Anonymous is the safest choice
   for CI — no credentials to protect, no rate-limit risk against
   a real account.
2. Fetch ``get_product_info(apps=[440])`` — Team Fortress 2, a
   permanent app that will still exist in 2035.
3. Assert we got a response shaped like ``{"apps": {440: {...}}}``.
4. Close cleanly, no thread leak.

Why not run this in CI by default: it takes 5-15 seconds, needs
outbound TCP to a Steam CM, and gets flaky when Steam is having a
bad day.  Gate behind an env var so nightly / manual runs pick it
up but PR CI stays fast and deterministic.
"""

from __future__ import annotations

import asyncio
import os
import time
import unittest

_RUN_LIVE = os.getenv("RUN_LIVE", "").lower() in {"1", "true", "yes"}


@unittest.skipUnless(_RUN_LIVE, "set RUN_LIVE=1 to run live Steam integration tests")
class LiveIntegrationTests(unittest.TestCase):
    """Live test suite.  One test only — a burning smoke test that
    proves the whole async stack can hold a real CM session and
    make a real RPC.  If this passes, the mocked tests aren't
    lying about what the real client does."""

    def test_anonymous_login_and_get_product_info(self) -> None:
        from steam.aio import AsyncSteamClient

        async def _main() -> dict:
            async with AsyncSteamClient() as client:
                t0 = time.monotonic()
                await client.anonymous_login()
                self.assertTrue(
                    client.logged_on,
                    "anonymous_login returned but ``logged_on`` is False — "
                    "the sync client's state didn't propagate through the "
                    "runner thread",
                )
                self.assertTrue(
                    client.connected,
                    "logged in but ``connected`` is False",
                )
                # 440 = Team Fortress 2 — permanent app, safe pick.
                info = await client.get_product_info(apps=[440], timeout=15)
                elapsed = time.monotonic() - t0
                self.assertLess(
                    elapsed,
                    30.0,
                    f"end-to-end login + get_product_info took {elapsed:.1f}s — "
                    "well over the reasonable ceiling; something is very slow",
                )
                return info

        info = asyncio.run(_main())
        # Response shape sanity: ``get_product_info`` returns
        # ``{"apps": {app_id: {...}}}``.  ``440`` is TF2 — its
        # ``common.name`` has been "Team Fortress 2" for over a
        # decade; if that changes, Steam has bigger problems than
        # our test.
        self.assertIn("apps", info)
        self.assertIn(440, info["apps"])
        tf2 = info["apps"][440]
        # ``common`` may be gated behind an access token that
        # anonymous accounts don't have — don't hard-require the
        # nested "name" key.  What we DO require is that some
        # top-level field came back per app (proves the RPC round-
        # tripped, not just that a hollow shell arrived).
        self.assertTrue(
            tf2,
            f"got empty response for app 440: {tf2!r}",
        )


if __name__ == "__main__":
    unittest.main()
