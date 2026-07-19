"""
Methods to call service methods, also known as unified messages

Example code:

.. code:: python

    # the easy way
    response = client.send_um_and_wait('Player.GetGameBadgeLevels#1', {
        'property': 1,
        'something': 'value',
        })

    print(response.body)

    # the other way
    jobid = client.send_um('Player.GetGameBadgeLevels#1', {'something': 1})
    response = client.wait_event(jobid)

The backend might error out, but we still get response. Here is how to check for error:

.. code:: python

    if response.header.eresult != EResult.OK:
        print(response.header.error_message)

"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from steam.core.msg import MsgProto, get_um
from steam.enums.emsg import EMsg
from steam.utils.proto import proto_fill_from_dict


class _UnifiedMessagesMixinHost:  # pragma: no cover
    """Structural type describing the surface the :class:`UnifiedMessages`
    mixin requires from its host class (typically :class:`SteamClient`
    which inherits from :class:`CMClient` and :class:`EventEmitter`).

    ``UnifiedMessages`` is a mixin — it never runs standalone; it's
    always combined into a ``SteamClient`` MRO where these methods
    live on the co-mixed base classes.  Declaring them on a
    Protocol-ish base class here lets Pylance resolve
    ``self.send_job(...)`` / ``self.wait_msg(...)`` under
    ``TYPE_CHECKING`` without dragging the concrete ``SteamClient`` /
    ``CMClient`` types into a runtime import (which would cause a
    circular import at load time — the ``steam.client`` package
    imports this module during its own ``__init__``).

    Only referenced from the ``TYPE_CHECKING``-guarded ``_HostBase``
    alias below, so this class body is dead code at runtime.
    """
    def send_job(self, message: MsgProto, body_params: Optional[dict] = None) -> str:
        """Send a message as a job and return the ``jobid`` event
        identifier.  Implemented on :class:`.SteamClient`."""
        ...

    def wait_msg(self, event: Any, timeout: Optional[float] = None, raises: bool = False) -> Any:
        """Wait for a message identified by ``event`` and return it,
        or :class:`None` on timeout (unless ``raises`` is ``True``).
        Implemented on :class:`.SteamClient`."""
        ...


# ``UnifiedMessages`` is a mixin — at runtime it derives from
# ``object`` (so instances placed in the SteamClient MRO don't add
# another ancestor beyond the concrete bases already there).  Under
# ``TYPE_CHECKING`` we pretend it derives from the host-surface stub
# above so Pylance resolves the co-mixed attributes cleanly.
if TYPE_CHECKING:
    _HostBase = _UnifiedMessagesMixinHost
else:
    _HostBase = object


class UnifiedMessages(_HostBase):
    def __init__(self, *args, **kwargs):
        super(UnifiedMessages, self).__init__(*args, **kwargs)

    def send_um(self, method_name, params=None):
        """Send service method request

        :param method_name: method name (e.g. ``Player.GetGameBadgeLevels#1``)
        :type  method_name: :class:`str`
        :param params: message parameters
        :type  params: :class:`dict`
        :return: ``job_id`` identifier
        :rtype: :class:`str`

        Listen for ``jobid`` on this object to catch the response.
        """
        proto = get_um(method_name)

        if proto is None:
            raise ValueError("Failed to find method named: %s" % method_name)

        message = MsgProto(EMsg.ServiceMethodCallFromClient)
        message.header.target_job_name = method_name
        message.body = proto()

        if params:
            proto_fill_from_dict(message.body, params)

        return self.send_job(message)

    def send_um_and_wait(self, method_name, params=None, timeout=10, raises=False):
        """Send service method request and wait for response

        :param method_name: method name (e.g. ``Player.GetGameBadgeLevels#1``)
        :type  method_name: :class:`str`
        :param params: message parameters
        :type  params: :class:`dict`
        :param timeout: (optional) seconds to wait
        :type  timeout: :class:`int`
        :param raises: (optional) On timeout if :class:`False` return :class:`None`, else raise :class:`gevent.Timeout`
        :type  raises: :class:`bool`
        :return: response message
        :rtype: proto message instance
        :raises: :class:`gevent.Timeout`
        """
        job_id = self.send_um(method_name, params)
        return self.wait_msg(job_id, timeout, raises=raises)
