"""Regenerate ``vcr/webauth_user_pass_only_*.yaml`` cassettes.

Prompts interactively for a Steam username + password (via ``getpass``),
records:

  * ``webauth_user_pass_only_success.yaml`` — the login flow WITH the
    real password, expected to succeed.
  * ``webauth_user_pass_only_fail.yaml`` — the same flow with an invalid
    password (real password + ``'123'`` appended), expected to raise
    ``LoginIncorrect``.

**Steam Guard is handled inline.**  If the account has Mobile 2FA enabled
the script prompts for the 6-character code; if Steam demands an email
code instead, it prompts for that.  Captcha is not automated — if you hit
a captcha challenge, either retry from a different IP or use a fresh
throwaway account whose IP isn't rate-limited.

The recorded cassettes get PII-scrubbed inline — SteamID, cookies, and
transfer tokens are swapped for placeholder values, though Steam Guard
codes themselves land in the cassette request bodies (VCR body scrubbing
doesn't support arbitrary field replacement).  **Always eyeball the
resulting yaml files before committing** and, if a 2FA / email code got
captured verbatim in a request payload, either regenerate a new code
before pushing (codes expire in ~30s / minutes) or scrub by hand.

Run from the package root:

    poetry run vcr-webauth
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys
from getpass import getpass

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
VCR_DIR = REPO_ROOT / 'vcr'


def _request_scrubber(r):
    r.headers.pop('Cookie', None)
    r.headers['Accept-Encoding'] = 'identity'
    r.body = ''
    return r


def _response_scrubber(r):
    # Case-insensitive pops — different Steam endpoints send different
    # casings (steamcommunity.com uses lowercase, store/help send
    # capitalized ``Set-Cookie`` / ``Date``).  Iterate a snapshot of keys
    # so mutation during iteration doesn't skip.
    for key in list(r['headers'].keys()):
        lower = key.lower()
        if lower in ('date', 'expires'):
            r['headers'].pop(key, None)

    # Scrub set-cookie values by INSPECTING each cookie's contents rather
    # than trusting the header key exactly.  This handles ALL three known
    # variations Steam sends (``set-cookie`` / ``Set-Cookie`` /
    # theoretically ``SET-COOKIE``) plus any endpoint that sets a
    # ``steamLogin*`` cookie without the same key naming convention.
    #
    # Rewrite rule for each cookie in a set-cookie header list:
    #   * ``steamLogin<X>=<steamid>%7C%7C<token>`` → replaced with
    #     ``steamLogin<X>=0%7C%7C<placeholder>`` (steamid → 0, token →
    #     fixed-width A/B fill).
    #   * ``steamMachineAuth<steamid>=<hex>`` → the steamid is in the key
    #     NAME so the whole cookie name is replaced with
    #     ``steamMachineAuth0=<placeholder>``.
    #   * Any other cookie (session id, birthtime, etc.) — pass through
    #     since it isn't PII-shaped.
    def scrub_one_cookie(cookie: str) -> str:
        m = re.match(
            r'(?P<name>steamLogin\w*)=(?P<sid>[0-9]+)%7C%7C(?P<tok>[A-Fa-f0-9]+)(?P<rest>.*)',
            cookie,
        )
        if m:
            placeholder = ('A' if m['name'] == 'steamLogin' else 'B') * len(m['tok'])
            return f"{m['name']}=0%7C%7C{placeholder}{m['rest']}"
        m = re.match(r'steamMachineAuth[0-9]+=[A-Fa-f0-9]+(?P<rest>.*)', cookie)
        if m:
            return f"steamMachineAuth0={'C' * 16}{m['rest']}"
        return cookie

    for key in list(r['headers'].keys()):
        if key.lower() == 'set-cookie':
            r['headers'][key] = [scrub_one_cookie(c) for c in r['headers'][key]]

    body = r.get('body') or {}
    raw = body.get('string')
    if not raw:
        return r

    # The login flow issues follow-up requests to ``store.steampowered.com``
    # and ``help.steampowered.com`` transfer endpoints — those return
    # gzip-compressed HTML (starts with the ``0x1f 0x8b`` magic bytes) or
    # plain text, not JSON.  Only scrub bodies that actually parse as JSON;
    # everything else passes through untouched (the URL scrubber above
    # already stripped cookies and other PII from the response headers).
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return r

    if 'token_gid' in data:
        data['token_gid'] = 0
    if 'timestamp' in data:
        data['timestamp'] = 12345678
    if 'transfer_parameters' in data:
        data['transfer_parameters']['steamid'] = '0'
        data['transfer_parameters']['token'] = 'A' * 16
        data['transfer_parameters']['token_secure'] = 'B' * 16
        data['transfer_parameters']['auth'] = 'Z' * 16

    body_out = json.dumps(data)
    r['body']['string'] = body_out
    r['headers']['content-length'] = [str(len(body_out))]

    print('--- response ---------')
    print(r)
    return r


def main() -> int:
    os.chdir(REPO_ROOT)
    sys.path.insert(0, str(REPO_ROOT))

    import vcr
    from vcr.record_mode import RecordMode

    from steam import webauth as wa

    VCR_DIR.mkdir(exist_ok=True)

    anon_vcr = vcr.VCR(
        before_record=_request_scrubber,
        before_record_response=_response_scrubber,
        serializer='yaml',
        # ``ALL`` overwrites the existing cassette from scratch each time.
        # ``NEW_EPISODES`` (the historical default) would append to any
        # cassette on disk — meaning stale interactions from a previous
        # run get mixed into the new recording, so playback later replays
        # a Frankenstein of old + new episodes.  ``ALL`` is the right mode
        # for a full re-record.
        record_mode=RecordMode.ALL,
        cassette_library_dir=str(VCR_DIR),
    )

    print('Steam credentials (Steam Guard 2FA / email codes are handled below).')
    username = input('Username: ')
    password = getpass('Password (no echo): ')

    def _login_with_guard_prompts(u: str, p: str, expect_success: bool) -> None:
        """Drive one login attempt, prompting for Steam Guard codes as needed.

        ``expect_success`` controls what "done" means:
          * ``True``  — the caller is recording the SUCCESS cassette; keep
            re-attempting with new Guard codes until login completes or a
            terminal error surfaces.
          * ``False`` — the caller is recording the FAIL cassette (invalid
            password appended).  Steam may still 2FA-gate first; enter the
            same code again, then the terminal error will be
            ``LoginIncorrect`` from the wrong password.

        Records the full call sequence — RSA-key request, dologin attempt,
        Guard-challenge dologin retry — into whatever cassette is currently
        active on ``anon_vcr``.
        """
        auth = wa.WebAuth(u, p)
        twofactor_code = ''
        email_code = ''
        captcha = ''
        while True:
            try:
                auth.login(
                    twofactor_code=twofactor_code,
                    email_code=email_code,
                    captcha=captcha,
                )
                return
            except wa.TwoFactorCodeRequired:
                if not expect_success and twofactor_code:
                    raise  # already gave a code; fail path shouldn't loop
                twofactor_code = input(
                    'Steam Guard Mobile 2FA code (6 chars, from the app): '
                ).strip()
            except wa.EmailCodeRequired:
                if not expect_success and email_code:
                    raise
                email_code = input(
                    'Steam Guard email code (5 chars, from the email Steam sent): '
                ).strip()
            except wa.CaptchaRequired:
                # Steam's anti-abuse gate — usually triggered by too many
                # failed logins recently.  Download the challenge PNG to a
                # tmp file so the user can open it locally with one
                # click, type the characters, retry.  The scrubbers wipe
                # the captcha field from the request body before write
                # so the correct answer never ends up in the cassette.
                path = auth.save_captcha_image()
                print()
                print(f'  Captcha required — image saved:')
                print(f'    file://{path}')
                print(f'    or run:  open {path}')
                captcha = input('  Captcha text: ').strip()
            except wa.CaptchaRequiredLoginIncorrect:
                if not expect_success:
                    # FAIL path with a wrong password + captcha demand —
                    # we're recording the incorrect-password flow, so
                    # bailing here is the intended terminal state.
                    raise
                path = auth.save_captcha_image()
                print()
                print(f'  Captcha wrong AND password wrong — reload both.')
                print(f'    file://{path}')
                captcha = input('  Captcha text: ').strip()
                new_pw = getpass('  Password (fresh — no echo): ')
                auth = wa.WebAuth(u, new_pw)
            except wa.LoginIncorrect as exc:
                # ``LoginIncorrect`` from a null-body response fires when
                # Steam's anti-abuse cooldown is still active — often
                # right after a captcha solve.  Prompt to wait rather
                # than looping and re-triggering the cooldown timer.
                msg = str(exc)
                if 'unexpected dologin body' in msg or 'NoneType' in msg:
                    print()
                    print('  Steam returned an empty response — rate-limit cooldown is active.')
                    print('  Wait 30-60 minutes with no login attempts, then re-run this script.')
                    print('  Every retry NOW extends the cooldown timer.')
                    raise SystemExit(1)
                raise

    @anon_vcr.use_cassette('webauth_user_pass_only_success.yaml')
    def _rec_success(u: str, p: str) -> None:
        _login_with_guard_prompts(u, p, expect_success=True)

    @anon_vcr.use_cassette('webauth_user_pass_only_fail.yaml')
    def _rec_fail(u: str, p: str) -> None:
        # The FAIL cassette records "login rejected" — Steam can reject in
        # multiple shapes: ``LoginIncorrect`` (wrong password), ``HTTPError``
        # (rate-limit, transient 5xx), or one of the Guard prompts if Steam
        # gates 2FA before checking the password.  Any of those is fine as
        # "expected failure" for the fixture, so catch broadly.  If the
        # unexpected happens (e.g. Steam accepts the wrong password —
        # shouldn't but not our bug), we let it propagate.
        try:
            _login_with_guard_prompts(u, p, expect_success=False)
        except (wa.LoginIncorrect, wa.HTTPError, wa.TwoFactorCodeRequired,
                wa.EmailCodeRequired, wa.CaptchaRequired,
                wa.CaptchaRequiredLoginIncorrect):
            pass

    print('\n--- recording SUCCESS cassette (login with valid credentials) ---')
    _rec_success(username, password)

    print('\n--- recording FAIL cassette (login with invalid password) ---')
    _rec_fail(username, password + '123')

    print()
    print('recorded:')
    print(f'  {(VCR_DIR / "webauth_user_pass_only_success.yaml").relative_to(REPO_ROOT)}')
    print(f'  {(VCR_DIR / "webauth_user_pass_only_fail.yaml").relative_to(REPO_ROOT)}')
    print()
    print('EYEBALL the yaml files before committing — the inline scrubbers')
    print('cover the most-common leak surfaces but not everything.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
