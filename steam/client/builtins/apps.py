from __future__ import annotations

from binascii import hexlify
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Optional

import vdf
from steam.enums import EResult, EServerType
from steam.enums.emsg import EMsg
from steam.core.msg import MsgProto
from steam.utils.proto import proto_fill_from_dict


class _AppsMixinHost:  # pragma: no cover
    """Structural type describing the surface the :class:`Apps` mixin
    requires from its host class (typically :class:`SteamClient`
    which inherits from :class:`CMClient` and :class:`EventEmitter`).

    ``Apps`` is a mixin — it never runs standalone; it's always
    combined into a ``SteamClient`` MRO where these attributes /
    methods live on the co-mixed base classes.  Declaring them on
    a Protocol-ish base class here lets Pylance resolve
    ``self.on(...)`` / ``self.send_job(...)`` / ``self.wait_event(...)``
    etc. under ``TYPE_CHECKING`` without dragging the concrete
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

    def send_job(
        self,
        message: MsgProto,
        body_params: Optional[dict] = None,
    ) -> Any:
        """Fire-and-forget a job-flagged message and return the job id.
        Implemented on :class:`.SteamClient`."""
        ...

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

    def wait_event(
        self,
        event: Any,
        timeout: Optional[float] = None,
        raises: bool = False,
    ) -> Any:
        """Block until ``event`` fires and return the event payload.
        Implemented on :class:`gevent_eventemitter.EventEmitter`."""
        ...


# ``Apps`` is a mixin — at runtime it derives from ``object`` (so
# instances placed in the SteamClient MRO don't add another ancestor
# beyond the concrete bases already there).  Under ``TYPE_CHECKING``
# we pretend it derives from the host-surface stub above so Pylance
# resolves the co-mixed attributes cleanly.
if TYPE_CHECKING:
    _HostBase = _AppsMixinHost
else:
    _HostBase = object


class Apps(_HostBase):
    """PICS product info, licenses, access tokens, and ticket flows.

    ``Apps`` is a mixin composed into :class:`.SteamClient` — you don't
    instantiate it directly, you get its methods via a ``SteamClient``
    instance.  Everything here is CM protocol (not HTTP), so it needs
    an active CM session (see ``anonymous_login`` / ``cli_login`` /
    ``login`` on the client).

    The headline method is :meth:`get_product_info`, which fetches the
    canonical Steam metadata for a batch of apps and / or packages —
    name, type, oslist, launch configs, depots, DRM, everything Steam
    keeps in its PICS catalogue.  See the `PICS wiki page
    <https://github.com/H47R15/steam/wiki/PICS>`_ for the full recipe
    and a comparison of when to use PICS vs. store HTTP vs. Web API.

    Also on this mixin:

    * :meth:`get_player_count` — current concurrent players for an app.
    * :meth:`get_access_tokens` — per-app / per-package tokens used to
      unlock the licensed portions of a PICS response.
    * :meth:`get_changes_since` — poll for what's changed in PICS since
      a known change-number; the primitive Steam's own launcher uses.
    * :meth:`get_app_ticket` / :meth:`get_encrypted_app_ticket` — app
      ownership tickets.
    * :meth:`get_depot_key` — depot decryption key for CDN downloads.
    """

    licenses: dict = {}  #: :class:`dict` Accounts' package licenses

    def __init__(self, *args, **kwargs):
        super(Apps, self).__init__(*args, **kwargs)
        self.licenses = {}
        self.on(self.EVENT_DISCONNECTED, self.__handle_disconnect)
        self.on(EMsg.ClientLicenseList, self._handle_licenses)

    def __handle_disconnect(self):
        self.licenses = {}

    def _handle_licenses(self, message):
        for entry in message.body.licenses:
            self.licenses[entry.package_id] = entry

    def get_player_count(self, app_id, timeout=5):
        """Get numbers of players for app id

        :param app_id: app id
        :type app_id: :class:`int`
        :return: number of players
        :rtype: :class:`int`, :class:`.EResult`
        """
        resp = self.send_job_and_wait(MsgProto(EMsg.ClientGetNumberOfCurrentPlayersDP),
                                      {'appid': app_id},
                                      timeout=timeout
                                      )
        if resp is None:
            return EResult.Timeout
        elif resp.eresult == EResult.OK:
            return resp.player_count
        else:
            return EResult(resp.eresult)

    def get_product_info(self, apps=[], packages=[], meta_data_only=False, raw=False, auto_access_tokens=True, timeout=15):
        """Fetch PICS product info for a batch of apps and / or packages.

        This is the batched entry point to Steam's authoritative app /
        package metadata catalogue.  Passes list-of-appids in over the
        CM protocol, gets ``{name, type, oslist, depots, config, …}``
        back per entry.  Hundreds of apps per call — Steam pages large
        batches across multiple response chunks internally, still one
        method invocation from the caller's side.

        For a full walkthrough — recipe patterns, change-number polling,
        access-token gating, when to use PICS vs. store HTTP vs.
        Web API — see the `PICS wiki page
        <https://github.com/H47R15/steam/wiki/PICS>`_.

        :param apps: appids to fetch.  Each item is either an ``int`` or
            a ``dict`` like ``{'appid': 570, 'access_token': ...}`` for
            licensed content.
        :type  apps: :class:`list`
        :param packages: same shape but with ``packageid`` keys.  Package
            tokens live on ``client.licenses[<packageid>].access_token``
            after login — see :attr:`licenses`.
        :type  packages: :class:`list`
        :param meta_data_only: skip the VDF payload; response only
            carries ``_change_number``, ``_sha``, ``_size``,
            ``_missing_token``.  Fast when you're just checking whether
            an app has changed since your last read.
        :type  meta_data_only: :class:`bool`
        :param raw: return the payload as raw bytes under ``_buffer``
            instead of parsing the VDF.  Apps buffer is text VDF,
            package buffer is binary VDF.
        :type  raw: :class:`bool`
        :param auto_access_tokens: default ``True`` — the client calls
            :meth:`get_access_tokens` first and threads them in.  Turn
            off when you already have tokens or want to skip the extra
            round-trip.
        :type  auto_access_tokens: :class:`bool`
        :param timeout: seconds per response chunk (not per call).  A
            batch of 500 apps arrives across several chunks; each chunk
            respects this timeout.
        :type  timeout: :class:`int`
        :return: ``{'apps': {appid: {...}, ...}, 'packages': {pkgid: {...}, ...}}``,
            or ``None`` if both lists were empty.  Each entry carries
            the VDF payload plus ``_change_number`` / ``_sha`` /
            ``_size`` / ``_missing_token`` bookkeeping.
        :rtype: :class:`dict` or :class:`None`

        The **common recipe** — anonymous batched name lookup:

        .. code:: python

            client = SteamClient()
            assert client.anonymous_login() == client.EResult.OK

            resp = client.get_product_info(
                apps=[570, 730, 553850],   # Dota 2, CS2, Helldivers 2
                timeout=30,
            )
            names = {aid: info['common']['name']
                     for aid, info in resp['apps'].items()}
            # {570: 'Dota 2', 730: 'Counter-Strike 2', 553850: 'HELLDIVERS™ 2'}

        **Licensed content** — entries come back with
        ``_missing_token=True`` when the token wasn't supplied.  With
        ``auto_access_tokens=True`` (default) the client requests them
        automatically; if you want to bring your own or handle it
        yourself:

        .. code:: python

            result = client.get_product_info(apps=[123], auto_access_tokens=False)
            if result['apps'][123]['_missing_token']:
                tokens = client.get_access_tokens(app_ids=[123])
                result = client.get_product_info(apps=[{
                    'appid': 123,
                    'access_token': tokens['apps'][123],
                }])

        **Package tokens** live on the account's license list:

        .. code:: python

            result = client.get_product_info(packages=[{
                'packageid': 123,
                'access_token': client.licenses[123].access_token,
            }])
        """
        if not apps and not packages:
            return

        if auto_access_tokens:
            tokens = self.get_access_tokens(app_ids=list(map(lambda app: app['appid'] if isinstance(app, dict) else app, apps)),
                                            package_ids=list(map(lambda pkg: pkg['packageid'] if isinstance(pkg, dict) else pkg, packages))
                                            )
        else:
            tokens = None

        message = MsgProto(EMsg.ClientPICSProductInfoRequest)

        for app in apps:
                app_info = message.body.apps.add()

                if tokens:
                    app_info.access_token = tokens['apps'].get(app['appid'] if isinstance(app, dict) else app, 0)

                if isinstance(app, dict):
                        proto_fill_from_dict(app_info, app)
                else:
                        app_info.appid = app

        for package in packages:
                package_info = message.body.packages.add()

                if tokens:
                    package_info.access_token = tokens['packages'].get(package['packageid'] if isinstance(package, dict) else package, 0)

                if isinstance(package, dict):
                        proto_fill_from_dict(package_info, package)
                else:
                        package_info.packageid = package

        message.body.meta_data_only = meta_data_only
        message.body.num_prev_failed = 0
        # ``supports_package_tokens`` was renamed to ``OBSOLETE_supports_package_tokens``
        # upstream ~2022; Steam CMs ignore whatever value clients set here.  Line
        # dropped to avoid ``AttributeError`` under the regenerated protobufs
        # (the un-prefixed name no longer resolves at runtime).

        job_id = self.send_job(message)

        data = dict(apps={}, packages={})

        while True:
            chunk = self.wait_event(job_id, timeout=timeout, raises=True)

            chunk = chunk[0].body

            for app in chunk.apps:
                if app.buffer and not raw:
                    data['apps'][app.appid] = vdf.loads(app.buffer[:-1].decode('utf-8', 'replace'))['appinfo']
                else:
                    data['apps'][app.appid] = {}

                data['apps'][app.appid]['_missing_token'] = app.missing_token
                data['apps'][app.appid]['_change_number'] = app.change_number
                data['apps'][app.appid]['_sha'] = hexlify(app.sha).decode('ascii')
                data['apps'][app.appid]['_size'] = app.size

                if app.buffer and raw:
                    data['apps'][app.appid]['_buffer'] = app.buffer

            for pkg in chunk.packages:
                if pkg.buffer and not raw:
                    data['packages'][pkg.packageid] = vdf.binary_loads(pkg.buffer[4:]).get(str(pkg.packageid), {})
                else:
                    data['packages'][pkg.packageid] = {}

                data['packages'][pkg.packageid]['_missing_token'] = pkg.missing_token
                data['packages'][pkg.packageid]['_change_number'] = pkg.change_number
                data['packages'][pkg.packageid]['_sha'] = hexlify(pkg.sha).decode('ascii')
                data['packages'][pkg.packageid]['_size'] = pkg.size

                if pkg.buffer and raw:
                    data['packages'][pkg.packageid]['_buffer'] = pkg.buffer

            if not chunk.response_pending:
                break

        return data

    def get_changes_since(self, change_number, app_changes=True, package_changes=False):
        """Get changes since a change number

        :param change_number: change number to use as stating point
        :type change_number: :class:`int`
        :param app_changes: whether to inclued app changes
        :type app_changes: :class:`bool`
        :param package_changes: whether to inclued package changes
        :type package_changes: :class:`bool`
        :return: `CMsgClientPICSChangesSinceResponse <https://github.com/ValvePython/steam/blob/39627fe883feeed2206016bacd92cf0e4580ead6/protobufs/steammessages_clientserver.proto#L1171-L1191>`_
        :rtype: proto message instance, or :class:`None` on timeout
        """
        return self.send_job_and_wait(MsgProto(EMsg.ClientPICSChangesSinceRequest),
                                      {
                                       'since_change_number': change_number,
                                       'send_app_info_changes': app_changes,
                                       'send_package_info_changes': package_changes,
                                      },
                                      timeout=10
                                      )

    def get_app_ticket(self, app_id):
        """Get app ownership ticket

        :param app_id: app id
        :type app_id: :class:`int`
        :return: `CMsgClientGetAppOwnershipTicketResponse <https://github.com/ValvePython/steam/blob/39627fe883feeed2206016bacd92cf0e4580ead6/protobufs/steammessages_clientserver.proto#L158-L162>`_
        :rtype: proto message
        """
        return self.send_job_and_wait(MsgProto(EMsg.ClientGetAppOwnershipTicket),
                                      {'app_id': app_id},
                                      timeout=10
                                      )

    def get_encrypted_app_ticket(self, app_id, userdata):
        """Gets the encrypted app ticket
        :param app_id: app id
        :type  app_id: :class:`int`
        :param userdata: userdata
        :type  userdata: :class:`bytes`
        :return: `EncryptedAppTicket <https://github.com/ValvePython/steam/blob/39627fe883feeed2206016bacd92cf0e4580ead6/protobufs/encrypted_app_ticket.proto>_`
        :rtype: proto message
        """
        return self.send_job_and_wait(MsgProto(EMsg.ClientRequestEncryptedAppTicket),
                                      {'app_id': app_id, 'userdata': userdata},
                                      timeout=10
                                      )

    def get_depot_key(self, app_id, depot_id):
        """Get depot decryption key

        :param app_id: app id
        :type  app_id: :class:`int`
        :param depot_id: depot id
        :type  depot_id: :class:`int`
        :return: `CMsgClientGetDepotDecryptionKeyResponse <https://github.com/ValvePython/steam/blob/39627fe883feeed2206016bacd92cf0e4580ead6/protobufs/steammessages_clientserver_2.proto#L533-L537>`_
        :rtype: proto message
        """
        return self.send_job_and_wait(MsgProto(EMsg.ClientGetDepotDecryptionKey),
                                      {
                                       'app_id': app_id,
                                       'depot_id': depot_id,
                                      },
                                      timeout=10
                                      )

    def get_cdn_auth_token(self, depot_id, hostname):
        """Get CDN authentication token

        .. note::
            This token is no longer needed for access to CDN files

        :param depot_id: depot id
        :type  depot_id: :class:`int`
        :param hostname: cdn hostname
        :type  hostname: :class:`str`
        :return: `CMsgClientGetCDNAuthTokenResponse <https://github.com/ValvePython/steam/blob/39627fe883feeed2206016bacd92cf0e4580ead6/protobufs/steammessages_clientserver_2.proto#L585-L589>`_
        :rtype: proto message
        """
        return self.send_job_and_wait(MsgProto(EMsg.ClientGetCDNAuthToken),
                                      {
                                       'depot_id': depot_id,
                                       'host_name': hostname,
                                      },
                                      timeout=10
                                      )

    def get_access_tokens(self, app_ids=[], package_ids=[]):
        """Get access tokens

        :param app_ids: list of app ids
        :type  app_ids: :class:`list`
        :param package_ids: list of package ids
        :type  package_ids: :class:`list`
        :return: dict with ``apps`` and ``packages`` containing their access tokens, see example below
        :rtype: :class:`dict`, :class:`None`

        .. code:: python

            {'apps':     {123: 8888888886, ...},
             'packages': {456: 6666666666, ...}
            }
        """
        if not app_ids and not package_ids:
            return

        resp = self.send_job_and_wait(MsgProto(EMsg.ClientPICSAccessTokenRequest),
                                      {
                                       'appids': map(int, app_ids),
                                       'packageids': map(int, package_ids),
                                      },
                                      timeout=10
                                      )

        if resp:
            return {'apps': dict(map(lambda app: (app.appid, app.access_token), resp.app_access_tokens)),
                    'packages': dict(map(lambda pkg: (pkg.packageid, pkg.access_token), resp.package_access_tokens)),
                    }

    def register_product_key(self, key):
        """Register/Redeem a CD-Key

        :param key: CD-Key
        :type  key: :class:`str`
        :return: format ``(eresult, result_details, receipt_info)``
        :rtype: :class:`tuple`

        Example ``receipt_info``:

        .. code:: python

            {'BasePrice': 0,
              'CurrencyCode': 0,
              'ErrorHeadline': '',
              'ErrorLinkText': '',
              'ErrorLinkURL': '',
              'ErrorString': '',
              'LineItemCount': 1,
              'PaymentMethod': 1,
              'PurchaseStatus': 1,
              'ResultDetail': 0,
              'Shipping': 0,
              'Tax': 0,
              'TotalDiscount': 0,
              'TransactionID': UINT_64(111111111111111111),
              'TransactionTime': 1473000000,
              'lineitems': {'0': {'ItemDescription': 'Half-Life 3',
                'TransactionID': UINT_64(11111111111111111),
                'packageid': 1234}},
              'packageid': -1}
        """
        resp = self.send_job_and_wait(MsgProto(EMsg.ClientRegisterKey),
                                      {'key': key},
                                      timeout=30,
                                      )

        if resp:
            details = vdf.binary_loads(resp.purchase_receipt_info).get('MessageObject', None)
            return EResult(resp.eresult), resp.purchase_result_details, details
        else:
            return EResult.Timeout, None, None

    def request_free_license(self, app_ids):
        """ Request license for free app(s)

        :param app_ids: list of app ids
        :type  app_ids: :class:`list`
        :return: format (:class:`.EResult`, result_details, receipt_info)
        :rtype: :class:`tuple`
        """
        resp = self.send_job_and_wait(MsgProto(EMsg.ClientRequestFreeLicense),
                                      {'appids': map(int, app_ids)},
                                      timeout=10,
                                      )

        if resp:
            return EResult(resp.eresult), resp.granted_appids, resp.granted_packageids

        else:
            return EResult.Timeout, None, None
