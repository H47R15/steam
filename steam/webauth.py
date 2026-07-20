# -*- coding: utf-8 -*-
"""
This module simplifies the process of obtaining an authenticated session for steam websites.
After authentication is completed, a :class:`requests.Session` is created containing the auth cookies.
The session can be used to access ``steamcommunity.com``, ``store.steampowered.com``, and ``help.steampowered.com``.

.. warning::
    A web session may expire randomly, or when you login from different IP address.
    Some pages will return status code `401` when that happens.
    Keep in mind if you are trying to write robust code.

.. note::
    If you are using :class:`.SteamClient` take a look at :meth:`.SteamClient.get_web_session()`

.. note::
    If you need to authenticate as a mobile device for things like trading confirmations
    use :class:`MobileWebAuth` instead. The login process is identical, and in addition
    you will get :attr:`.oauth_token`.


Example usage:

.. code:: python

    import steam.webauth as wa

    user = wa.WebAuth('username')

    # At a console, cli_login can be used to easily perform all login steps
    session = user.cli_login('password')
    session.get('https://store.steampowered.com/account/history')

    # Or the login steps be implemented for other situation like so
    try:
        user.login('password')
    except (wa.CaptchaRequired, wa.LoginIncorrect) as exp:
        if isinstance(exp, LoginIncorrect):
            # ask for new password
        else:
            password = self.password

        if isinstance(exp, wa.CaptchaRequired):
            print user.captcha_url
            # ask a human to solve captcha
        else:
            captcha = None

        user.login(password=password, captcha=captcha)
    except wa.EmailCodeRequired:
        user.login(email_code='ZXC123')
    except wa.TwoFactorCodeRequired:
        user.login(twofactor_code='ZXC123')

    user.session.get('https://store.steampowered.com/account/history/')

"""
import json
from time import time
from base64 import b64encode
from getpass import getpass
import requests

from steam.steamid import SteamID
from steam.utils.web import make_requests_session, generate_session_id
from steam.core.crypto import rsa_publickey, pkcs1v15_encrypt

intBase = int
_cli_input = input


class WebAuth(object):
    username: str
    password: str
    timestamp: int  #: rsa timestamp, populated by :meth:`_load_key`
    key = None
    logged_on = False    #: whether authentication has been completed successfully
    session: requests.Session  #: :class:`requests.Session` populated in ``__init__`` via :func:`make_requests_session`
    session_id: "str | None" = None   #: :class:`str`, session id string
    captcha_gid = -1
    captcha_code = ''
    steam_id = None     #: :class:`.SteamID` (after auth is completed)

    def __init__(self, username, password=''):
        self.__dict__.update(locals())
        self.session = make_requests_session()
        self._session_setup()

    def _session_setup(self):
        pass

    @property
    def captcha_url(self):
        """If a captch is required this property will return url to the image, or ``None``"""
        if self.captcha_gid == -1:
            return None
        else:
            return "https://steamcommunity.com/login/rendercaptcha/?gid=%s" % self.captcha_gid

    def save_captcha_image(self, dest_dir=None):
        """Download the pending captcha PNG to a local file and return the path.

        Fetches ``https://steamcommunity.com/login/rendercaptcha/?gid=<gid>``
        using this WebAuth's session (already carries any cookies /
        headers Steam expects), writes the response bytes to
        ``<dest_dir>/steam_captcha_<gid>.png``, and returns the local
        ``pathlib.Path``.

        ``dest_dir`` defaults to the system tmp directory
        (``tempfile.gettempdir()`` — ``/tmp`` on macOS/Linux).  Pass an
        explicit dir if you want the file somewhere persistent.

        Returns ``None`` when there's no active captcha challenge
        (``captcha_gid == -1``) so callers can guard with a truthy
        check.

        Typical usage from an interactive login handler::

            try:
                auth.login(password=..., captcha=captcha_text)
            except CaptchaRequired:
                path = auth.save_captcha_image()
                print(f"Captcha needed — open  file://{path}")
                captcha_text = input("Captcha text: ")
                # retry
        """
        if self.captcha_gid == -1:
            return None

        import pathlib
        import tempfile

        # ``captcha_url`` is ``str | None`` per its property signature —
        # narrow to ``str`` here.  The ``captcha_gid == -1`` guard above
        # rules out the None branch, but Pylance / mypy don't correlate
        # the two, so bind to a local and assert.
        url = self.captcha_url
        assert url is not None  # invariant: guarded by captcha_gid check

        dest_dir = pathlib.Path(dest_dir) if dest_dir else pathlib.Path(tempfile.gettempdir())
        dest_dir.mkdir(parents=True, exist_ok=True)
        path = dest_dir / ("steam_captcha_%s.png" % self.captcha_gid)

        try:
            resp = self.session.get(url, timeout=15)
        except requests.exceptions.RequestException as e:
            raise HTTPError(str(e))
        resp.raise_for_status()
        path.write_bytes(resp.content)
        return path

    def get_rsa_key(self, username):
        """Get rsa key for a given username

        :param username: username
        :type  username: :class:`str`
        :return: json response
        :rtype: :class:`dict`
        :raises HTTPError: any problem with http request, timeouts, 5xx, 4xx etc
        """
        try:
            resp = self.session.post('https://steamcommunity.com/login/getrsakey/',
                                     timeout=15,
                                     data={
                                         'username': username,
                                         'donotcache': int(time() * 1000),
                                         },
                                     ).json()
        except requests.exceptions.RequestException as e:
            raise HTTPError(str(e))

        return resp

    def _load_key(self):
        if not self.key:
            resp = self.get_rsa_key(self.username)

            self.key = rsa_publickey(intBase(resp['publickey_mod'], 16),
                                     intBase(resp['publickey_exp'], 16),
                                     )
            self.timestamp = resp['timestamp']

    def _send_login(self, password='', captcha='', email_code='', twofactor_code=''):
        data = {
            'username': self.username,
            "password": b64encode(pkcs1v15_encrypt(self.key, password.encode('ascii'))),
            "emailauth": email_code,
            "emailsteamid": str(self.steam_id) if email_code else '',
            "twofactorcode": twofactor_code,
            "captchagid": self.captcha_gid,
            "captcha_text": captcha,
            "loginfriendlyname": "python-steam webauth",
            "rsatimestamp": self.timestamp,
            "remember_login": 'true',
            "donotcache": int(time() * 100000),
        }

        try:
            response = self.session.post(
                'https://steamcommunity.com/login/dologin/', data=data, timeout=15
            )
        except requests.exceptions.RequestException as e:
            raise HTTPError(str(e))
        # Steam occasionally returns a JSON ``null`` body when it rejects
        # a retry (rate-limit, replayed 2FA code, invalid client state, …).
        # ``requests.Response.json()`` maps that to Python ``None`` —
        # leaving ``login()`` to crash with a bare
        # ``TypeError: 'NoneType' is not subscriptable`` on ``resp['success']``.
        # Wrap into a proper ``LoginIncorrect`` so callers get an actionable
        # exception matching the shape of every other login-error branch.
        try:
            parsed = response.json()
        except ValueError as e:
            raise HTTPError(f'Steam returned non-JSON dologin body: {e}')
        if not isinstance(parsed, dict):
            raise LoginIncorrect(
                f'Steam returned an unexpected dologin body '
                f'({type(parsed).__name__}: {parsed!r}) — usually means '
                f'rate-limit / replayed 2FA code / invalid session'
            )
        return parsed

    def _finalize_login(self, login_response):
        """Extract ``self.steam_id`` from a successful ``dologin`` response.

        Steam has shipped multiple response shapes here over the years, so
        this method probes each in turn:

          1. Legacy: ``transfer_parameters`` (a single object with
             ``steamid``).  Used by pre-2020 Steam login responses and
             still returned for some account types.
          2. Modern: ``transfer_info`` (a list of ``{url, params}``,
             replacing the older ``transfer_urls`` + ``transfer_parameters``
             split).  Each entry's ``params.steamid`` carries the same
             value.
          3. Fallback: parse from the ``steamLogin`` /
             ``steamLoginSecure`` cookie value — Steam encodes it as
             ``<steamid>%7C%7C<token>`` regardless of response shape.

        Silent on absolute failure — ``self.steam_id`` stays ``None``
        (its class-level default) if none of the three sources yield a
        value.  The session cookies set by ``dologin`` still work for
        subsequent requests either way; only ``.steam_id`` bookkeeping
        is affected.  Callers that need the ID should ``assert
        auth.steam_id is not None`` after ``login()`` returns.
        """
        steamid_raw = None

        params = login_response.get('transfer_parameters')
        if isinstance(params, dict):
            steamid_raw = params.get('steamid')

        if not steamid_raw:
            for info in login_response.get('transfer_info') or []:
                candidate = (info.get('params') or {}).get('steamid')
                if candidate:
                    steamid_raw = candidate
                    break

        if not steamid_raw:
            for cookie in self.session.cookies:
                if cookie.name in ('steamLogin', 'steamLoginSecure') and cookie.value:
                    candidate = cookie.value.split('%7C%7C', 1)[0]
                    if candidate.isdigit():
                        steamid_raw = candidate
                        break

        if steamid_raw:
            self.steam_id = SteamID(steamid_raw)

    def login(self, password='', captcha='', email_code='', twofactor_code='', language='english'):
        """Attempts web login and returns on a session with cookies set

        :param password: password, if it wasn't provided on instance init
        :type  password: :class:`str`
        :param captcha: text reponse for captcha challenge
        :type  captcha: :class:`str`
        :param email_code: email code for steam guard
        :type  email_code: :class:`str`
        :param twofactor_code: 2FA code for steam guard
        :type  twofactor_code: :class:`str`
        :param language: select language for steam web pages (sets language cookie)
        :type  language: :class:`str`
        :return: a session on success and :class:`None` otherwise
        :rtype: :class:`requests.Session`, :class:`None`
        :raises HTTPError: any problem with http request, timeouts, 5xx, 4xx etc
        :raises LoginIncorrect: wrong username or password
        :raises CaptchaRequired: when captcha is needed
        :raises CaptchaRequiredLoginIncorrect: when captcha is needed and login is incorrect
        :raises EmailCodeRequired: when email is needed
        :raises TwoFactorCodeRequired: when 2FA is needed
        """
        if self.logged_on:
            return self.session

        if password:
            self.password = password
        elif self.password:
            password = self.password
        else:
            raise LoginIncorrect("password is not specified")

        if not captcha and self.captcha_code:
            captcha = self.captcha_code

        self._load_key()
        resp = self._send_login(password=password, captcha=captcha, email_code=email_code, twofactor_code=twofactor_code)

        if resp['success'] and resp['login_complete']:
            self.logged_on = True
            self.password = self.captcha_code = ''
            self.captcha_gid = -1

            # RequestsCookieJar mixes CookieJar (yields Cookie) with MutableMapping[str, str]
            # (yields str) — iter() picks the CookieJar overload so the loop is typed as Cookie.
            for cookie in list(iter(self.session.cookies)):
                if cookie.value is None:
                    continue
                for domain in ['store.steampowered.com', 'help.steampowered.com', 'steamcommunity.com']:
                    self.session.cookies.set(cookie.name, cookie.value, domain=domain, secure=cookie.secure)

            self.session_id = generate_session_id()

            for domain in ['store.steampowered.com', 'help.steampowered.com', 'steamcommunity.com']:
                self.session.cookies.set('Steam_Language', language, domain=domain)
                self.session.cookies.set('birthtime', '-3333', domain=domain)
                self.session.cookies.set('sessionid', self.session_id, domain=domain)

            self._finalize_login(resp)

            return self.session
        else:
            if resp.get('captcha_needed', False):
                self.captcha_gid = resp['captcha_gid']
                self.captcha_code = ''

                if resp.get('clear_password_field', False):
                    self.password = ''
                    raise CaptchaRequiredLoginIncorrect(resp['message'])
                else:
                    raise CaptchaRequired(resp['message'])
            elif resp.get('emailauth_needed', False):
                self.steam_id = SteamID(resp['emailsteamid'])
                raise EmailCodeRequired(resp['message'])
            elif resp.get('requires_twofactor', False):
                raise TwoFactorCodeRequired(resp['message'])
            elif 'too many login failures' in resp.get('message', ''):
                raise TooManyLoginFailures(resp['message'])
            else:
                self.password = ''
                raise LoginIncorrect(resp['message'])

    def cli_login(self, password='', captcha='', email_code='', twofactor_code='', language='english'):
        """Generates CLI prompts to perform the entire login process

        :param password: password, if it wasn't provided on instance init
        :type  password: :class:`str`
        :param captcha: text reponse for captcha challenge
        :type  captcha: :class:`str`
        :param email_code: email code for steam guard
        :type  email_code: :class:`str`
        :param twofactor_code: 2FA code for steam guard
        :type  twofactor_code: :class:`str`
        :param language: select language for steam web pages (sets language cookie)
        :type  language: :class:`str`
        :return: a session on success and :class:`None` otherwise
        :rtype: :class:`requests.Session`, :class:`None`

        .. code:: python

            In [3]: user.cli_login()
            Enter password for 'steamuser':
            Solve CAPTCHA at https://steamcommunity.com/login/rendercaptcha/?gid=1111111111111111111
            CAPTCHA code: 123456
            Invalid password for 'steamuser'. Enter password:
            Solve CAPTCHA at https://steamcommunity.com/login/rendercaptcha/?gid=2222222222222222222
            CAPTCHA code: abcdef
            Enter 2FA code: AB123
            Out[3]: <requests.sessions.Session at 0x6fffe56bef0>

        """

        # loop until successful login
        while True:
            try:
                return self.login(password, captcha, email_code, twofactor_code, language)
            except (LoginIncorrect, CaptchaRequired) as exp:
                email_code = twofactor_code = ''

                if isinstance(exp, LoginIncorrect):
                    prompt = ("Enter password for %s: " if not password else
                              "Invalid password for %s. Enter password: ")
                    password = getpass(prompt % repr(self.username))
                if isinstance(exp, CaptchaRequired):
                    prompt = "Solve CAPTCHA at %s\nCAPTCHA code: " % self.captcha_url
                    captcha = _cli_input(prompt)
                else:
                    captcha = ''
            except EmailCodeRequired:
                prompt = ("Enter email code: " if not email_code else
                          "Incorrect code. Enter email code: ")
                email_code, twofactor_code = _cli_input(prompt), ''
            except TwoFactorCodeRequired:
                prompt = ("Enter 2FA code: " if not twofactor_code else
                          "Incorrect code. Enter 2FA code: ")
                email_code, twofactor_code = '', _cli_input(prompt)


class MobileWebAuth(WebAuth):
    """Identical to :class:`WebAuth`, except it authenticates as a mobile device."""
    oauth_token = None  #: holds oauth_token after successful login

    def _send_login(self, password='', captcha='', email_code='', twofactor_code=''):
        data = {
            'username': self.username,
            "password": b64encode(pkcs1v15_encrypt(self.key, password.encode('ascii'))),
            "emailauth": email_code,
            "emailsteamid": str(self.steam_id) if email_code else '',
            "twofactorcode": twofactor_code,
            "captchagid": self.captcha_gid,
            "captcha_text": captcha,
            "loginfriendlyname": "python-steam webauth",
            "rsatimestamp": self.timestamp,
            "remember_login": 'true',
            "donotcache": int(time() * 100000),
            "oauth_client_id": "DE45CD61",
            "oauth_scope": "read_profile write_profile read_client write_client",
        }

        self.session.cookies.set('mobileClientVersion', '0 (2.1.3)')
        self.session.cookies.set('mobileClient', 'android')

        # Same null-body / non-dict defensive handling as WebAuth._send_login
        # above.  The ``try/finally`` here also has to unset the mobile
        # cookies regardless of outcome, so structure is a bit denser.
        try:
            try:
                response = self.session.post(
                    'https://steamcommunity.com/login/dologin/', data=data, timeout=15
                )
            except requests.exceptions.RequestException as e:
                raise HTTPError(str(e))
            try:
                parsed = response.json()
            except ValueError as e:
                raise HTTPError(f'Steam returned non-JSON dologin body: {e}')
            if not isinstance(parsed, dict):
                raise LoginIncorrect(
                    f'Steam returned an unexpected dologin body '
                    f'({type(parsed).__name__}: {parsed!r}) — usually means '
                    f'rate-limit / replayed 2FA code / invalid session'
                )
            return parsed
        finally:
            self.session.cookies.pop('mobileClientVersion', None)
            self.session.cookies.pop('mobileClient', None)

    def _finalize_login(self, login_response):
        data = json.loads(login_response['oauth'])
        self.steam_id = SteamID(data['steamid'])
        self.oauth_token = data['oauth_token']

    def oauth_login(self, oauth_token='', steam_id='', language='english'):
        """Attempts a mobile authenticator login using an oauth token, which can be obtained from a previously logged-in
        `MobileWebAuth`

        :param oauth_token: oauth token string, if it wasn't provided on instance init
        :type  oauth_token: :class:`str`
        :param steam_id: `SteamID` of the account to log into, if it wasn't provided on instance init
        :type  steam_id: :class:`str` or :class:`SteamID`
        :param language: select language for steam web pages (sets language cookie)
        :type  language: :class:`str`
        :return: a session on success and :class:`None` otherwise
        :rtype: :class:`requests.Session`, :class:`None`
        :raises HTTPError: any problem with http request, timeouts, 5xx, 4xx etc
        :raises LoginIncorrect: Invalid token or SteamID
        """
        if oauth_token:
            self.oauth_token = oauth_token
        elif self.oauth_token:
            oauth_token = self.oauth_token
        else:
            raise LoginIncorrect('token is not specified')

        if steam_id:
            self.steam_id = SteamID(steam_id)
        elif not self.steam_id:
            raise LoginIncorrect('steam_id is not specified')

        steam_id = self.steam_id.as_64

        data = {
            'access_token': oauth_token
        }

        try:
            resp = self.session.post('https://api.steampowered.com/IMobileAuthService/GetWGToken/v0001', data=data)
        except requests.exceptions.RequestException as e:
            raise HTTPError(str(e))

        try:
            resp_data = resp.json()['response']
        except json.decoder.JSONDecodeError as e:
            if 'Please verify your <pre>key=</pre> parameter.' in resp.text:
                raise LoginIncorrect('invalid token')
            else:
                raise e

        self.session_id = generate_session_id()

        for domain in ['store.steampowered.com', 'help.steampowered.com', 'steamcommunity.com']:
            self.session.cookies.set('birthtime', '-3333', domain=domain)
            self.session.cookies.set('sessionid', self.session_id, domain=domain)
            self.session.cookies.set('mobileClientVersion', '0 (2.1.3)', domain=domain)
            self.session.cookies.set('mobileClient', 'android', domain=domain)
            self.session.cookies.set('steamLogin', str(steam_id) + "%7C%7C" + resp_data['token'], domain=domain)
            self.session.cookies.set('steamLoginSecure', str(steam_id) + "%7C%7C" + resp_data['token_secure'],
                                     domain=domain, secure=True)
            self.session.cookies.set('Steam_Language', language, domain=domain)

        self.logged_on = True

        return self.session


class WebAuthException(Exception):
    pass

class HTTPError(WebAuthException):
    pass

class LoginIncorrect(WebAuthException):
    pass

class CaptchaRequired(WebAuthException):
    pass

class CaptchaRequiredLoginIncorrect(CaptchaRequired, LoginIncorrect):
    pass

class EmailCodeRequired(WebAuthException):
    pass

class TwoFactorCodeRequired(WebAuthException):
    pass

class TooManyLoginFailures(WebAuthException):
    pass
