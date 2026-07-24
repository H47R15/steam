import requests
from binascii import hexlify
from os import urandom
# ``random_bytes`` used to come from ``steam.core.crypto``, which
# only re-exports it as ``from os import urandom as random_bytes``.
# Pylance's ``reportPrivateImportUsage`` refuses to see re-imported
# aliases as public exports; importing ``os.urandom`` directly gets
# the same bytes without the private-import complaint.
from steam.core.crypto import sha1_hash

def make_requests_session():
    """
    :returns: requests session
    :rtype: :class:`requests.Session`
    """
    session = requests.Session()

    version = __import__('steam').__version__
    ua = "python-steam/{0} {1}".format(version,
                                session.headers['User-Agent'])
    session.headers['User-Agent'] = ua

    return session

def generate_session_id():
    """
    :returns: session id
    :rtype: :class:`str`
    """
    return hexlify(sha1_hash(urandom(32)))[:32].decode('ascii')
