"""This module contains various value enumerations.

They are all based on :py:class:`IntEnum`, which gives them :py:class:`int` properties.
They can be compared to :py:class:`int` and used in places there :py:class:`int` is required.
Like for example, protobuf message.
They also provide a easy way to resolve a name or value for a specific enum.

.. code:: python

    >>> EResult.OK
    <EResult.OK: 1>
    >>> EResult(1)
    <EResult.OK: 1>
    >>> EResult['OK']
    <EResult.OK: 1>
    >>> EResult.OK == 1
    True

.. note::
    all enums from :py:mod:`steam.enum.common` can be imported directly from :py:mod:`steam.enum`
"""

# Explicit re-exports mirror ``steam.enums.common.__all__`` — a wildcard
# ``from steam.enums.common import *`` also works at runtime but Pylance
# flags it with ``reportWildcardImportFromLibrary`` and can't trace the
# individual symbols for auto-complete / go-to-definition on consumers.
# Keep this list in sync with ``steam/enums/common.py::__all__`` when adding
# a new enum class there.
from steam.enums.common import (
    EAccountFlags,
    EAppType,
    EBillingType,
    EChatEntryType,
    EChatRoomEnterResponse,
    EClientPersonaStateFlag,
    EClientUIMode,
    ECurrencyCode,
    EDepotFileFlag,
    EFriendFlags,
    EFriendRelationship,
    EInstanceFlag,
    ELeaderboardDataRequest,
    ELeaderboardDisplayType,
    ELeaderboardSortMethod,
    ELeaderboardUploadScoreMethod,
    ELicenseFlags,
    ELicenseType,
    EOSType,
    EPackageStatus,
    EPaymentMethod,
    EPersonaState,
    EPersonaStateFlag,
    EProtoAppType,
    EPublishedFileInappropriateProvider,
    EPublishedFileInappropriateResult,
    EPublishedFileQueryType,
    EPublishedFileVisibility,
    EPurchaseResultDetail,
    EResult,
    EServerType,
    ETwoFactorTokenType,
    EType,
    EUniverse,
    EUserBadge,
    EVanityUrlType,
    EWorkshopFileType,
    WorkshopEnumerationType,
)

__all__ = [
    'EAccountFlags',
    'EAppType',
    'EBillingType',
    'EChatEntryType',
    'EChatRoomEnterResponse',
    'EClientPersonaStateFlag',
    'EClientUIMode',
    'ECurrencyCode',
    'EDepotFileFlag',
    'EFriendFlags',
    'EFriendRelationship',
    'EInstanceFlag',
    'ELeaderboardDataRequest',
    'ELeaderboardDisplayType',
    'ELeaderboardSortMethod',
    'ELeaderboardUploadScoreMethod',
    'ELicenseFlags',
    'ELicenseType',
    'EOSType',
    'EPackageStatus',
    'EPaymentMethod',
    'EPersonaState',
    'EPersonaStateFlag',
    'EProtoAppType',
    'EPublishedFileInappropriateProvider',
    'EPublishedFileInappropriateResult',
    'EPublishedFileQueryType',
    'EPublishedFileVisibility',
    'EPurchaseResultDetail',
    'EResult',
    'EServerType',
    'ETwoFactorTokenType',
    'EType',
    'EUniverse',
    'EUserBadge',
    'EVanityUrlType',
    'EWorkshopFileType',
    'WorkshopEnumerationType',
]
