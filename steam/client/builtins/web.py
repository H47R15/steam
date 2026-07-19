"""
Web related features
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, ClassVar, Optional

from steam.webapi import post as webapi_post
from steam.core.msg import MsgProto
from steam.enums.emsg import EMsg
from steam.core.crypto import generate_session_key, symmetric_encrypt
from steam.utils.web import make_requests_session, generate_session_id


if TYPE_CHECKING:
    import logging
    from steam.steamid import SteamID


class _WebMixinHost:  # pragma: no cover
    """Structural type describing the surface the :class:`Web` mixin
    requires from its host class (typically :class:`SteamClient`
    which inherits from :class:`CMClient` and :class:`EventEmitter`).

    ``Web`` is a mixin — it never runs standalone; it's always
    combined into a ``SteamClient`` MRO where these attributes /
    methods live on the co-mixed base classes.  Declaring them on
    a Protocol-ish base class here lets Pylance resolve
    ``self.on(...)`` / ``self._LOG`` / ``self.steam_id`` etc. under
    ``TYPE_CHECKING`` without dragging the concrete
    ``SteamClient`` / ``CMClient`` types into a runtime import
    (which would cause a circular import at load time — the
    ``steam.client`` package imports this module during its own
    ``__init__``).

    Only referenced from the ``TYPE_CHECKING``-guarded ``_HostBase``
    alias below, so this class body is dead code at runtime.
    """
    #: Event emitter's method-registration entry point (from
    #: ``gevent_eventemitter.EventEmitter`` via ``CMClient``).
    on: Callable[..., Any]

    #: Class constant from :class:`.CMClient`.
    EVENT_DISCONNECTED: ClassVar[str]

    #: Module logger from :class:`.CMClient`.
    _LOG: ClassVar["logging.Logger"]

    #: Current user's SteamID — populated after a successful logon.
    steam_id: "SteamID"

    #: Set to ``True`` while the client is logged on to Steam.
    logged_on: bool

    def send_job_and_wait(
        self,
        message: MsgProto,
        body_params: Optional[dict] = None,
        timeout: Optional[float] = None,
        raises: bool = False,
    ) -> Any:
        """Round-trip a job-flagged message and block until the
        response arrives.  Implemented on :class:`.SteamClient`."""
        ...


# ``Web`` is a mixin — at runtime it derives from ``object`` (so
# instances placed in the SteamClient MRO don't add another ancestor
# beyond the concrete bases already there).  Under ``TYPE_CHECKING``
# we pretend it derives from the host-surface stub above so Pylance
# resolves the co-mixed attributes cleanly.
if TYPE_CHECKING:
    _HostBase = _WebMixinHost
else:
    _HostBase = object


class Web(_HostBase):
    _web_session: Any = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.on(self.EVENT_DISCONNECTED, self.__handle_disconnect)

    def __handle_disconnect(self):
        self._web_session = None

    def get_web_session_cookies(self) -> Optional[dict]:
        """Get web authentication cookies via WebAPI's ``AuthenticateUser``

        .. note::
            The cookies are valid only while :class:`.SteamClient` instance is logged on.

        :return: dict with authentication cookies
        :rtype: :class:`dict`, :class:`None`
        """
        if not self.logged_on: return None

        resp = self.send_job_and_wait(MsgProto(EMsg.ClientRequestWebAPIAuthenticateUserNonce), timeout=7)

        if resp is None: return None

        skey, ekey = generate_session_key()

        data = {
            'steamid': self.steam_id,
            'sessionkey': ekey,
            'encrypted_loginkey': symmetric_encrypt(resp.webapi_authenticate_user_nonce.encode('ascii'), skey),
        }

        try:
            auth_resp = webapi_post('ISteamUserAuth', 'AuthenticateUser', 1, params=data)
        except Exception as exp:
            self._LOG.debug("get_web_session_cookies error: %s" % str(exp))
            return None

        return {
            'steamLogin': auth_resp['authenticateuser']['token'],
            'steamLoginSecure': auth_resp['authenticateuser']['tokensecure'],
        }

    def get_web_session(self, language='english'):
        """Get a :class:`requests.Session` that is ready for use

        See :meth:`get_web_session_cookies`

        .. note::
            Auth cookies will only be send to ``(help|store).steampowered.com`` and ``steamcommunity.com`` domains

        .. note::
            The session is valid only while :class:`.SteamClient` instance is logged on.

        :param language: localization language for steam pages
        :type language: :class:`str`
        :return: authenticated Session ready for use
        :rtype: :class:`requests.Session`, :class:`None`
        """
        if self._web_session:
            return self._web_session

        cookies = self.get_web_session_cookies()
        if cookies is None:
            return None

        self._web_session = session = make_requests_session()
        session_id = generate_session_id()

        for domain in ['store.steampowered.com', 'help.steampowered.com', 'steamcommunity.com']:
            for name, val in cookies.items():
                secure = (name == 'steamLoginSecure')
                session.cookies.set(name, val, domain=domain, secure=secure)

            session.cookies.set('Steam_Language', language, domain=domain)
            session.cookies.set('birthtime', '-3333', domain=domain)
            session.cookies.set('sessionid', session_id, domain=domain)

        return session
