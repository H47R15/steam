from steam.enums.base import SteamIntEnum

class E_STAR_GlyphWriteResult(SteamIntEnum):
    Success = 0
    InvalidMessage = 1
    InvalidJSON = 2
    SQLError = 3

class EAccessibilityContrastMode(SteamIntEnum):
    EBrowserContrastMode_NoPreference = 0
    EBrowserContrastMode_More = 1
    EBrowserContrastMode_Less = 2

class EAchievementProgressType(SteamIntEnum):
    Invalid = 0
    Int = 1
    Float = 2

class EACState(SteamIntEnum):
    Unknown = 0
    Disconnected = 1
    Connected = 2
    ConnectedSlow = 3

class EAgreementType(SteamIntEnum):
    Invalid = -1
    GlobalSSA = 0
    ChinaSSA = 1

class EAppCloudStatus(SteamIntEnum):
    EAppCloudStatusInvalid = 0
    EAppCloudStatusDisabled = 1
    EAppCloudStatusUnknown = 2
    EAppCloudStatusSynchronized = 3
    EAppCloudStatusChecking = 4
    EAppCloudStatusOutOfSync = 5
    EAppCloudStatusUploading = 6
    EAppCloudStatusDownloading = 7
    EAppCloudStatusSyncFailed = 8
    EAppCloudStatusConflict = 9
    EAppCloudStatusPendingElsewhere = 10

EAppContentDetectionType = SteamIntEnum('EAppContentDetectionType', {
    'None': 0,
    'AntiCheat': 1,
    'GameEngine': 2,
    })

class EAppControllerSupportLevel(SteamIntEnum):
    EAppControllerSupportLevelNone = 0
    EAppControllerSupportLevelPartial = 1
    EAppControllerSupportLevelFull = 2

class EAppGamepadGyroTrackpadSupportLevel(SteamIntEnum):
    EAppGamepadGyroTrackpadSupportLevelUnknown = -1
    EAppGamepadGyroTrackpadSupportLevelNoGamepad = 0
    EAppGamepadGyroTrackpadSupportLevelGamepad = 1
    EAppGamepadGyroTrackpadSupportLevelSimultaneous = 2

class EAppHDRSupport(SteamIntEnum):
    EHDRSupport_Unknown = 0
    EHDRSupport_SDR = 1
    EHDRSupport_HDR = 2
    EHDRSupport_HDR_Broken = 3
    EHDRSupport_HDR_RequiresUserAction = 4

class EAppReportType(SteamIntEnum):
    Invalid = 0
    Scam = 1
    Malware = 2
    HateSpeech = 3
    Pornography = 4
    NonLabeledAdultContent = 5
    Libelous = 6
    Offensive = 7
    ExploitsChildren = 8
    MtxWithNonSteamWalletPaymentMethods = 9
    CopyrightViolation = 10
    ViolatesLaws = 11
    Other = 12
    Broken = 13
    AIContentReport = 14

class EAppTestType(SteamIntEnum):
    BuildReview = 0
    StorePageReview = 1
    SteamChina_BuildReview = 2
    SteamChina_StorePageReview = 3
    SteamChinaPlatformOperator_StorePageReview = 4
    SteamChinaPlatformOperator_BuildReview = 5
    SteamDeckCompatibilityReview = 6
    SteamFrameCompatibilityReview = 7

class EAssetPropertyType(SteamIntEnum):
    Unknown = 0
    Float = 1
    Int = 2
    String = 3
    MAX = 4

class EAsyncGameSessionUserState(SteamIntEnum):
    EAsyncGameSessionUserStateUnknown = -1
    EAsyncGameSessionUserStateWaitingForOthers = 0
    EAsyncGameSessionUserStateReadyForAction = 1
    EAsyncGameSessionUserStateDone = 2

class EAsyncGameSessionUserVisibility(SteamIntEnum):
    EAsyncGameSessionUserVisibilityEnvelopeAndSessionList = 0
    EAsyncGameSessionUserVisibilitySessionListOnly = 1
    EAsyncGameSessionUserVisibilityDismissed = 2

class EAudioFormat(SteamIntEnum):
    EAudioFormatNone = 0
    EAudioFormat16BitLittleEndian = 1
    EAudioFormatFloat = 2

class EAuthenticationType(SteamIntEnum):
    Unknown = 0
    Password = 1
    QR = 2
    AccountCreation = 3
    GuestAccount = 4

EAuthSessionGuardType = SteamIntEnum('EAuthSessionGuardType', {
    'Unknown': 0,
    'None': 1,
    'EmailCode': 2,
    'DeviceCode': 3,
    'DeviceConfirmation': 4,
    'EmailConfirmation': 5,
    'MachineToken': 6,
    'LegacyMachineAuth': 7,
    })

class EAuthSessionSecurityHistory(SteamIntEnum):
    Invalid = 0
    UsedPreviously = 1
    NoPriorHistory = 2

class EAuthTokenAppType(SteamIntEnum):
    Unknown = 0
    Mobile_SteamApp = 1
    Mobile_ChatApp = 2

class EAuthTokenPlatformType(SteamIntEnum):
    Unknown = 0
    SteamClient = 1
    WebBrowser = 2
    MobileApp = 3

class EAuthTokenRevokeAction(SteamIntEnum):
    EAuthTokenRevokeLogout = 0
    EAuthTokenRevokePermanent = 1
    EAuthTokenRevokeReplaced = 2
    EAuthTokenRevokeSupport = 3
    EAuthTokenRevokeConsume = 4
    EAuthTokenRevokeNonRememberedLogout = 5
    EAuthTokenRevokeNonRememberedPermanent = 6
    EAuthTokenRevokeAutomatic = 7

class EAuthTokenState(SteamIntEnum):
    Invalid = 0
    New = 1
    Confirmed = 2
    Issued = 3
    Denied = 4
    LoggedOut = 5
    Consumed = 6
    Revoked = 99

class EBanContentCheckResult(SteamIntEnum):
    NotScanned = 0
    Reset = 1
    NeedsChecking = 2
    VeryUnlikely = 5
    Unlikely = 30
    Possible = 50
    Likely = 75
    VeryLikely = 100

class EBatteryState(SteamIntEnum):
    Unknown = 0
    Discharging = 1
    Charging = 2
    Full = 3

class EBluetoothDeviceType(SteamIntEnum):
    BluetoothDeviceType_Invalid = 0
    BluetoothDeviceType_Unknown = 1
    BluetoothDeviceType_Phone = 2
    BluetoothDeviceType_Computer = 3
    BluetoothDeviceType_Headset = 4
    BluetoothDeviceType_Headphones = 5
    BluetoothDeviceType_Speakers = 6
    BluetoothDeviceType_OtherAudio = 7
    BluetoothDeviceType_Mouse = 8
    BluetoothDeviceType_Joystick = 9
    BluetoothDeviceType_Gamepad = 10
    BluetoothDeviceType_Keyboard = 11

class EBroadcastChatPermission(SteamIntEnum):
    EBroadcastChatPermissionPublic = 0
    EBroadcastChatPermissionOwnsApp = 1

class EBroadcastEncoderSetting(SteamIntEnum):
    EBroadcastEncoderBestQuality = 0
    EBroadcastEncoderBestPerformance = 1

EBroadcastImageType = SteamIntEnum('EBroadcastImageType', {
    'None': 0,
    'Offline': 1,
    'Standby': 2,
    'Avatar': 3,
    'Summary': 4,
    'Background': 5,
    'Emoticon': 6,
    })

class EBroadcastPermission(SteamIntEnum):
    EBroadcastPermissionDisabled = 0
    EBroadcastPermissionFriendsApprove = 1
    EBroadcastPermissionFriendsAllowed = 2
    EBroadcastPermissionPublic = 3
    EBroadcastPermissionSubscribers = 4

class EBroadcastWatchLocation(SteamIntEnum):
    Invalid = 0
    SteamTV_Tab = 1
    SteamTV_WatchParty = 2
    Chat_Tab = 3
    Chat_WatchParty = 4
    CommunityPage = 5
    StoreAppPage = 6
    InGame = 7
    BigPicture = 8
    SalesPage = 9
    CuratorPage = 10
    DeveloperPage = 11
    Chat_Friends = 12
    SteamTV_Web = 13
    DesktopUI_Overlay = 14
    TrailerCarousel = 15

class EBrowserFeatureStatus(SteamIntEnum):
    Invalid = 0
    NotFound = 1
    Unknown = 2
    DisabledSoftware = 3
    DisabledOff = 4
    DisabledOffOk = 5
    UnavailableSoftware = 6
    UnavailableOff = 7
    UnavailableOffOk = 8
    EnabledReadback = 9
    EnabledForce = 10
    Enabled = 11
    EnabledOn = 12
    EnabledForceOn = 13

class EBrowserGPUStatus(SteamIntEnum):
    Invalid = 0
    Enabled = 1
    DisabledUnknown = 2
    DisabledCrashCount = 4
    DisabledBlocklist = 5
    DisabledJSRequest = 6
    DisabledCommandLine = 7
    DisabledRuntimeDetect = 8
    DisabledChildCommandLine = 9
    DisabledCompositingCommandLine = 10

class ECaptureFailedReason(SteamIntEnum):
    ECaptureFailedReasonNone = 0
    ECaptureFailedReasonUnknown = 1
    ECaptureFailedReasonPipewireRequired = 2
    ECaptureFailedReasonPipewirePermissions = 3
    ECaptureFailedReasonMacOSPermissions = 4

class EChatRoomGroupRank(SteamIntEnum):
    Default = 0
    Viewer = 10
    Guest = 15
    Member = 20
    Moderator = 30
    Officer = 40
    Owner = 50
    TestInvalid = 99

EChatRoomJoinState = SteamIntEnum('EChatRoomJoinState', {
    'Default': 0,
    'None': 1,
    'Joined': 2,
    'TestInvalid': 99,
    })

class EChatRoomMemberStateChange(SteamIntEnum):
    Invalid = 0
    Joined = 1
    Parted = 2
    Kicked = 3
    Invited = 4
    RankChanged = 7
    InviteDismissed = 8
    Muted = 9
    Banned = 10
    RolesChanged = 12

class EChatRoomMessageReactionType(SteamIntEnum):
    Invalid = 0
    Emoticon = 1
    Sticker = 2

class EChatRoomNotificationLevel(SteamIntEnum):
    EChatroomNotificationLevel_Invalid = 0
    EChatroomNotificationLevel_None = 1
    EChatroomNotificationLevel_MentionMe = 2
    EChatroomNotificationLevel_MentionAll = 3
    EChatroomNotificationLevel_AllMessages = 4

class EChatRoomServerMessage(SteamIntEnum):
    EChatRoomServerMsg_Invalid = 0
    EChatRoomServerMsg_RenameChatRoom = 1
    EChatRoomServerMsg_Joined = 2
    EChatRoomServerMsg_Parted = 3
    EChatRoomServerMsg_Kicked = 4
    EChatRoomServerMsg_Invited = 5
    EChatRoomServerMsg_InviteDismissed = 8
    EChatRoomServerMsg_ChatRoomTaglineChanged = 9
    EChatRoomServerMsg_ChatRoomAvatarChanged = 10
    EChatRoomServerMsg_AppCustom = 11
    EChatRoomServerMsg_JoinedMany = 12
    EChatRoomServerMsg_PartedMany = 13
    EChatRoomServerMsg_InvitedMany = 14

class EChatSessionNotice(SteamIntEnum):
    Invalid = 0
    Suspicious = 1

class EChildProcessQueryCommand(SteamIntEnum):
    Invalid = 0
    GpuTopology = 1
    Max = 2

class EChildProcessQueryExitCode(SteamIntEnum):
    Success = 0
    ErrorCommandline = -1
    ErrorOther = -2
    ErrorUnimplemented = -3
    ErrorFileSave = -4
    ErrorNotSupportedByPlatform = -5

class EClanImageFileType(SteamIntEnum):
    Unknown = 0
    JPEG = 1
    GIF = 2
    PNG = 3
    MP4 = 4
    WEBM = 5
    VTT = 6
    SRT = 7
    SVG = 8
    XML = 9
    WEBP = 10

EClanImageGroup = SteamIntEnum('EClanImageGroup', {
    'None': 0,
    'Announcement': 1,
    'Curator': 2,
    })

class EClientExecutionSite(SteamIntEnum):
    EClientExecutionSiteInvalid = 0
    EClientExecutionSiteSteamUI = 1
    EClientExecutionSiteClientdll = 2
    EClientExecutionSiteAny = 3

class EClientNotificationType(SteamIntEnum):
    Invalid = 0
    DownloadCompleted = 1
    FriendInvite = 2
    FriendInGame = 3
    FriendOnline = 4
    Achievement = 5
    LowBattery = 6
    SystemUpdate = 7
    FriendMessage = 8
    GroupChatMessage = 9
    FriendInviteRollup = 10
    FamilySharingStopPlaying = 12
    Screenshot = 14
    CloudSyncFailure = 15
    CloudSyncConflict = 16
    IncomingVoiceChat = 17
    ClaimSteamDeckRewards = 18
    GiftReceived = 19
    ItemAnnouncement = 20
    HardwareSurvey = 21
    LowDiskSpace = 22
    BatteryTemperature = 23
    DockUnsupportedFirmware = 24
    PeerContentUpload = 25
    CannotReadControllerGuideButton = 26
    Comment = 27
    Wishlist = 28
    TradeOffer = 29
    AsyncGame = 30
    General = 31
    HelpRequest = 32
    OverlaySplashScreen = 33
    BroadcastAvailableToWatch = 34
    TimedTrialRemaining = 35
    LoginRefresh = 36
    MajorSale = 37
    TimerExpired = 38
    ModeratorMsg = 39
    SteamInputActionSetChanged = 40
    RemoteClientConnection = 41
    RemoteClientStartStream = 42
    StreamingClientConnection = 43
    FamilyInvite = 44
    PlaytimeWarning = 45
    FamilyPurchaseRequest = 46
    FamilyPurchaseRequestResponse = 47
    ParentalFeatureRequest = 48
    ParentalPlaytimeRequest = 49
    GameRecordingError = 50
    ParentalFeatureResponse = 51
    ParentalPlaytimeResponse = 52
    RequestedGameAdded = 53
    ClipDownloaded = 54
    GameRecordingStart = 55
    GameRecordingStop = 56
    GameRecordingUserMarkerAdded = 57
    GameRecordingInstantClip = 58
    PlaytestInvite = 59
    TradeReversal = 60
    HardwareUpdateAvailable = 61
    ControllerLowBattery = 62
    ControllerConnected = 63
    ControllerDisconnected = 64

class EClientSettingStore(SteamIntEnum):
    Invalid = 0
    ConfigStore_Install = 1
    ConfigStore_UserRoaming = 2
    ConfigStore_UserLocal = 3
    Registry = 4
    CustomFunc = 5

class ECLientTaskListType(SteamIntEnum):
    EClientTask_DownloadClip = 1

class EClipRangeMethod(SteamIntEnum):
    CreateClipButton = 1
    Highlight = 2
    BeginEndButtons = 3
    ContextMenu = 4
    Drag = 5
    EntireClip = 6
    PhaseRecording = 7

class EClipShareMethod(SteamIntEnum):
    Chat = 1
    Clipboard = 2
    File = 3
    SendClip = 4
    SaveToMedia = 5
    CreateLink = 6

class ECloudGamingPlatform(SteamIntEnum):
    ECloudGamingPlatformNone = 0
    ECloudGamingPlatformValve = 1
    ECloudGamingPlatformNVIDIA = 2

class ECloudPendingRemoteOperation(SteamIntEnum):
    ECloudPendingRemoteOperationNone = 0
    ECloudPendingRemoteOperationAppSessionActive = 1
    ECloudPendingRemoteOperationUploadInProgress = 2
    ECloudPendingRemoteOperationUploadPending = 3
    ECloudPendingRemoteOperationAppSessionSuspended = 4

class ECloudStoragePersistState(SteamIntEnum):
    ECloudStoragePersistStatePersisted = 0
    ECloudStoragePersistStateForgotten = 1
    ECloudStoragePersistStateDeleted = 2

class ECodecUsagePlatform(SteamIntEnum):
    ECodecUsagePlatformUnknown = 0
    ECodecUsagePlatformWindows = 1
    ECodecUsagePlatformMacOS = 2
    ECodecUsagePlatformLinux = 3
    ECodecUsagePlatformSteamHardware = 4

class ECodecUsageReason(SteamIntEnum):
    ECodecUsageReasonUnknown = 0
    ECodecUsageReasonRemotePlay = 1
    ECodecUsageReasonBroadcasting = 2
    ECodecUsageReasonGameVideo = 3
    ECodecUsageReasonGameRecording = 4

class EColorGamutLabelSet(SteamIntEnum):
    ColorGamutLabelSet_Default = 0
    ColorGamutLabelSet_sRGB_Native = 1
    ColorGamutLabelSet_Native_sRGB_Boosted = 2

class ECommentDeleteReason(SteamIntEnum):
    Invalid = 0
    User = 1
    ThreadOwner = 2
    Moderator = 3
    Support = 4
    Spam = 5
    AccountDeletion = 6

class ECommentThreadType(SteamIntEnum):
    ECommentThreadTypeInvalid = 0
    ECommentThreadTypeScreenshot_Deprecated = 1
    ECommentThreadTypeWorkshopAccount_Developer = 2
    ECommentThreadTypeWorkshopAccount_Public = 3
    ECommentThreadTypePublishedFile_Developer = 4
    ECommentThreadTypePublishedFile_Public = 5
    ECommentThreadTypeTest = 6
    ECommentThreadTypeForumTopic = 7
    ECommentThreadTypeRecommendation = 8
    ECommentThreadTypeVideo_Deprecated = 9
    ECommentThreadTypeProfile = 10
    ECommentThreadTypeNewsPost = 11
    ECommentThreadTypeClan = 12
    ECommentThreadTypeClanAnnouncement = 13
    ECommentThreadTypeClanEvent = 14
    ECommentThreadTypeUserStatusPublished = 15
    ECommentThreadTypeUserReceivedNewGame = 16
    ECommentThreadTypePublishedFile_Announcement = 17
    ECommentThreadTypeModeratorMessage = 18
    ECommentThreadTypeClanCuratedApp = 19
    ECommentThreadTypeQAndASession = 20
    ECommentThreadTypeMax = 21

class ECommunityItemClass(SteamIntEnum):
    Invalid = 0
    Badge = 1
    GameCard = 2
    ProfileBackground = 3
    Emoticon = 4
    BoosterPack = 5
    Consumable = 6
    GameGoo = 7
    ProfileModifier = 8
    Scene = 9
    SalienItem = 10
    Sticker = 11
    ChatEffect = 12
    MiniProfileBackground = 13
    AvatarFrame = 14
    AnimatedAvatar = 15
    SteamDeckKeyboardSkin = 16
    SteamDeckStartupMovie = 17

ECompromiseDetectionType = SteamIntEnum('ECompromiseDetectionType', {
    'None': 0,
    'TradeEvent': 1,
    'ApiCallRate': 2,
    'Manual': 3,
    'TicketAction': 4,
    'MaliciousRefund': 5,
    'Move2FA': 6,
    'DeviceType': 7,
    })

class EContentCheckProvider(SteamIntEnum):
    Invalid = 0
    Google_DEPRECATED = 1
    Amazon = 2
    Local = 3
    GoogleVertexAI = 4
    GoogleGemini = 5
    SteamLearn = 6

class EContentDeltaChunkDataLocation(SteamIntEnum):
    EContentDeltaChunkDataLocationInProtobuf = 0
    EContentDeltaChunkDataLocationAfterProtobuf = 1

class EContentDescriptorID(SteamIntEnum):
    EContentDescriptor_NudityOrSexualContent = 1
    EContentDescriptor_FrequentViolenceOrGore = 2
    EContentDescriptor_AdultOnlySexualContent = 3
    EContentDescriptor_GratuitousSexualContent = 4
    EContentDescriptor_AnyMatureContent = 5
    EContentDescriptorMAX = 6

EContentHubDiscountFilterType = SteamIntEnum('EContentHubDiscountFilterType', {
    'None': 0,
    'DiscountsOnly': 1,
    'PrioritizeDiscounts': 2,
    })

class EContentModerationSanction(SteamIntEnum):
    Invalid = 0
    Deleted = 1
    CommunityBanned = 2
    HubBanned = 3
    TradeBanned = 4
    CommentHistoryDeleted = 5
    Relabelled = 6
    MarkAsSuspicious = 7
    Warned = 8
    KickedFromGroup = 9
    HarassmentBanned = 10
    MAX = 11

class EContentModeratorLevel(SteamIntEnum):
    Any = 0
    Supervisor = 1
    Valve = 10
    MAX = 11

EContentReportReason = SteamIntEnum('EContentReportReason', {
    'Invalid': 0,
    'None': 1,
    'Unknown': 2,
    'Harassment': 3,
    'BullyingAndIntimidation': 4,
    'Stalking': 5,
    'Doxxing': 6,
    'OtherHarassment': 7,
    'EncouragingViolence': 8,
    'EncouragingSelfHarm': 9,
    'EncouragingSuicide': 10,
    'OtherViolenceOrSelfHarm': 11,
    'PhishingOrAccountTheft': 12,
    'AttemptedScamming': 13,
    'LinkingToMaliciousContent': 14,
    'Impersonation': 15,
    'OtherScamsAndTheft': 16,
    'EncouragingTerrorism': 17,
    'OrganizingTerrorism': 18,
    'OtherTerrorism': 19,
    'TargetedAbuse': 20,
    'NamingAndShaming': 21,
    'Discrimination': 22,
    'OtherAbuse': 23,
    'Trolling': 24,
    'Baiting': 25,
    'Derailing': 26,
    'OtherDisruptive': 27,
    'Spam': 28,
    'Begging': 29,
    'Reposting': 30,
    'OtherOffTopic': 31,
    'CSAMSexualContent': 32,
    'CSAMGroomingOrEnticement': 33,
    'CSAMOther': 34,
    'NudityOrSexualContent': 35,
    'NonConsensualMaterial': 36,
    'Advertising': 37,
    'ReferralLinks': 38,
    'Gambling': 39,
    'Raffles': 40,
    'OtherCommercialActivity': 41,
    'InauthenticReview': 42,
    'HiddenAdvertisementOrCommercialCommunication': 43,
    'MisleadingInformationAboutGoodsOrServices': 44,
    'MisleadingInformationAboutConsumerRights': 45,
    'NoncomplianceWithPricingRegulations': 46,
    'RightToBeForgottenViolation': 47,
    'MissingProcessingGroundForData': 48,
    'OtherDataProtectionAndPrivacyViolation': 49,
    'GenderedHarassment': 50,
    'GenderedBullyingAndIntimidation': 51,
    'GenderedStalking': 52,
    'GenderedDoxxing': 53,
    'GenderedOtherHarassment': 54,
    'GenderedEncouragingViolence': 55,
    'GenderedTargetedAbuse': 56,
    'CSAMFakedSexualContent': 57,
    'GenderedNonConsensualMaterial': 58,
    'FakedGenderedNonConsensualMaterial': 59,
    'FakedNonConsensualMaterial': 60,
    'NegativeEffectonDiscourseOrElections': 61,
    'QuotesModeratedContent': 62,
    'CredibleThreatOfViolence': 63,
    'AutoCreatedOnModeration': 64,
    'MAX': 65,
    })

class EContentReportResolution(SteamIntEnum):
    Unresolved = 0
    Acquitted = 1
    Removed = 2
    Relabelled = 3
    Suspicious = 4
    HarassmentStrike = 5
    Purged = 6
    DisconnectedFromApp = 7
    SuspiciousIncludingUpvoters = 8
    VisibilityChanged = 9
    CountryRestrictionsChanged = 10
    RemoveAndWarn = 11
    RemoveAndBan = 12
    RemoveAndKick = 13
    Sanctioned = 14
    Sustained = 15
    Broken = 16
    MAX = 17

class EContentReportSubjectAction(SteamIntEnum):
    Invalid = 0
    Unresolved = 1
    Sanctioned = 2
    Acquitted = 3
    Cancelled = 4
    Updated = 5
    Escalated = 6
    Disputed = 7
    Sustained = 8
    Locked = 9
    Unlocked = 10
    Deleted = 11
    Warned = 12
    BannedFromHub = 13
    BannedFromCommunity = 14
    TradeBanned = 15
    MarkedAsSuspicious = 16
    ResetContent = 17
    EscalatedForCSAM = 18
    EscalatedForTerrorism = 19
    Claimed = 20
    Released = 21
    PrivateMessaged = 22
    OwnerDisputed = 23

class EContentReportSubjectType(SteamIntEnum):
    Invalid = 0
    ForumPost = 1
    CommentThread = 2
    UGCFile = 3
    FriendChatMsg = 4
    ChatRoomMsg = 5
    ChatGroup = 6
    MAX = 7

EControlledLegalCategoryStatus = SteamIntEnum('EControlledLegalCategoryStatus', {
    'None': 0,
    'Accused': 1,
    'Convicted': 2,
    'Acquitted': 3,
    })

class EControllerElementType(SteamIntEnum):
    EControllerElementTypeNone = -1
    EControllerElementTypeThumb = 0
    EControllerElementTypeButtonSteam = 1
    EControllerElementTypeJoystickLeft = 2
    EControllerElementTypeButtonJoystickLeft = 3
    EControllerElementTypeJoystickRight = 4
    EControllerElementTypeButtonJoystickRight = 5
    EControllerElementTypeDPad = 6
    EControllerElementTypeButtonA = 7
    EControllerElementTypeButtonB = 8
    EControllerElementTypeButtonX = 9
    EControllerElementTypeButtonY = 10
    EControllerElementTypeButtonSelect = 11
    EControllerElementTypeButtonStart = 12
    EControllerElementTypeButtonTriggerLeft = 13
    EControllerElementTypeButtonTriggerRight = 14
    EControllerElementTypeButtonBumperLeft = 15
    EControllerElementTypeButtonBumperRight = 16
    EControllerElementTypeButtonMacro0 = 17
    EControllerElementTypeButtonMacro1 = 18
    EControllerElementTypeButtonMacro2 = 19
    EControllerElementTypeButtonMacro3 = 20
    EControllerElementTypeButtonMacro4 = 21
    EControllerElementTypeButtonMacro5 = 22
    EControllerElementTypeButtonMacro6 = 23
    EControllerElementTypeButtonMacro7 = 24
    EControllerElementTypeTrackpadCenter = 25
    EControllerElementTypeTrackpadLeft = 26
    EControllerElementTypeTrackpadRight = 27
    EControllerElementTypeKeyboard = 28
    EControllerElementTypeMagnifyingGlass = 29
    EControllerElementTypeButtonMacro1Finger = 30
    EControllerElementTypeButtonMacro2Finger = 31
    EControllerElementTypeRecordInput = 32
    EControllerElementTypePlaybackInput = 33
    EControllerElementTypePaste = 34
    EControllerElementTypeMax = 35

class ECPUGovernor(SteamIntEnum):
    Invalid = 0
    Perf = 1
    Powersave = 2
    Manual = 3

class EDiskSpaceType(SteamIntEnum):
    eDiskSpaceType_Recording = 0
    eDiskSpaceType_Clip = 1

class EDisplayManagerRGBRange(SteamIntEnum):
    Automatic = 0
    Full = 1
    Limited = 2

class EDisplayPowerState(SteamIntEnum):
    Invalid = 0
    Off = 1
    On = 2

class EDisplayStatus(SteamIntEnum):
    EDisplayStatusInvalid = 0
    EDisplayStatusLaunching = 1
    EDisplayStatusUninstalling = 2
    EDisplayStatusInstalling = 3
    EDisplayStatusRunning = 4
    EDisplayStatusValidating = 5
    EDisplayStatusUpdating = 6
    EDisplayStatusDownloading = 7
    EDisplayStatusSynchronizing = 8
    EDisplayStatusReadyToInstall = 9
    EDisplayStatusReadyToPreload = 10
    EDisplayStatusReadyToLaunch = 11
    EDisplayStatusRegionRestricted = 12
    EDisplayStatusPresaleOnly = 13
    EDisplayStatusInvalidPlatform = 14
    EDisplayStatusPreloadComplete = 16
    EDisplayStatusBorrowerLocked = 17
    EDisplayStatusUpdatePaused = 18
    EDisplayStatusUpdateQueued = 19
    EDisplayStatusUpdateRequired = 20
    EDisplayStatusUpdateDisabled = 21
    EDisplayStatusDownloadPaused = 22
    EDisplayStatusDownloadQueued = 23
    EDisplayStatusDownloadRequired = 24
    EDisplayStatusDownloadDisabled = 25
    EDisplayStatusLicensePending = 26
    EDisplayStatusLicenseExpired = 27
    EDisplayStatusAvailForFree = 28
    EDisplayStatusAvailToBorrow = 29
    EDisplayStatusAvailGuestPass = 30
    EDisplayStatusPurchase = 31
    EDisplayStatusUnavailable = 32
    EDisplayStatusNotLaunchable = 33
    EDisplayStatusCloudError = 34
    EDisplayStatusCloudOutOfDate = 35
    EDisplayStatusTerminating = 36
    EDisplayStatusOwnerLocked = 37
    EDisplayStatusDownloadFailed = 38
    EDisplayStatusUpdateFailed = 39

class EEnhancedMarketAppearanceStatus(SteamIntEnum):
    EnhancedMarketAppearanceStatus_None = 0
    EnhancedMarketAppearanceStatus_Pending = 1
    EnhancedMarketAppearanceStatus_InProgress = 2
    EnhancedMarketAppearanceStatus_Completed = 3

class EExportCodec(SteamIntEnum):
    Default = 0
    H264 = 1
    H265 = 2

class EExternalSaleEventType(SteamIntEnum):
    Unknown = 0
    Publisher = 1
    Showcase = 2
    Region = 3
    Theme = 4
    Franchise = 5

class EFamilyGroupChangeLogType(SteamIntEnum):
    InvalidChangeType = 0
    FamilyGroupCreated = 1
    FamilyGroupModified = 2
    FamilyGroupDeleted = 3
    AccountInvited = 4
    InviteDeniedByGroupSize = 5
    JoinedFamilyGroup = 6
    JoinDeniedByRegionMismatch = 7
    JoinDeniedByMissingIpAddress = 8
    JoinDeniedByFamilyCooldown = 9
    JoinDeniedByUserCooldown = 10
    JoinDeniedByOtherGroup = 11
    AccountRemoved = 12
    InviteCanceled = 13
    PurchaseRequested = 14
    ParentalSettingsEnabled = 15
    ParentalSettingsDisabled = 16
    ParentalSettingsChanged = 17
    FamilyCooldownOverridesChanged = 18
    PurchaseRequestCanceled = 19
    PurchaseRequestApproved = 20
    PurchaseRequestDeclined = 21
    CooldownSkipConsumed = 22
    FamilyGroupRestored = 23
    JoinDenied = 24
    SupportForceAcceptedInvite = 25

EFamilyGroupRole = SteamIntEnum('EFamilyGroupRole', {
    'None': 0,
    'Adult': 1,
    'Child': 2,
    'MAX': 3,
    })

class EFamilyGroupsTwoFactorMethod(SteamIntEnum):
    EFamilyGroupsTwoFactorMethodNone = 0
    EFamilyGroupsTwoFactorMethodMobile = 1
    EFamilyGroupsTwoFactorMethodEmail = 2

class EForumType(SteamIntEnum):
    Invalid = 0
    General = 1
    ReportedPosts = 2
    Workshop = 3
    PublishedFile = 4
    Trading = 5
    PlayTest = 6
    Event = 7
    Max = 8

class EFrameAccumulatedStat(SteamIntEnum):
    EFrameStatFPS = 0
    EFrameStatCaptureDurationMS = 1
    EFrameStatConvertDurationMS = 2
    EFrameStatEncodeDurationMS = 3
    EFrameStatSteamDurationMS = 4
    EFrameStatServerDurationMS = 5
    EFrameStatNetworkDurationMS = 6
    EFrameStatDecodeDurationMS = 7
    EFrameStatDisplayDurationMS = 8
    EFrameStatClientDurationMS = 9
    EFrameStatFrameDurationMS = 10
    EFrameStatInputLatencyMS = 11
    EFrameStatGameLatencyMS = 12
    EFrameStatRoundTripLatencyMS = 13
    EFrameStatPingTimeMS = 14
    EFrameStatServerBitrateKbitPerSec = 15
    EFrameStatClientBitrateKbitPerSec = 16
    EFrameStatLinkBandwidthKbitPerSec = 17
    EFrameStatPacketLossPercentage = 18

class EFrameRateReportEnabled(SteamIntEnum):
    Unset = 0
    Enabled = 1
    Disabled = 2

class EGameFrameRateReportingPreference(SteamIntEnum):
    Unset = 0
    No = 1
    Yes_Anonymous = 2
    Yes_NonAnonymous = 3

class EGameRecordingErrorType(SteamIntEnum):
    EGameRecordingErrorGeneral = 1
    EGameRecordingErrorLowDiskSpace = 2

class EGameRecordingType(SteamIntEnum):
    Unknown = 0
    NotRecording = 1
    ManualRecording = 2
    BackgroundRecording = 3
    Clip = 4

class EGamescopeBlurMode(SteamIntEnum):
    Disabled = 0
    IfOccluded = 1
    Always = 2

EGameSearchAction = SteamIntEnum('EGameSearchAction', {
    'None': 0,
    'Accept': 1,
    'Decline': 2,
    'Cancel': 3,
    })

class EGameSearchResult(SteamIntEnum):
    Invalid = 0
    SearchInProgress = 1
    SearchFailedNoHosts = 2
    SearchGameFound = 3
    SearchCompleteAccepted = 4
    SearchCompleteDeclined = 5
    SearchCanceled = 6

class EGetChannelsAlgorithm(SteamIntEnum):
    Default = 1
    Friends = 2
    Featured = 3
    Developer = 4
    Following = 5

class EGetGamesAlgorithm(SteamIntEnum):
    Default = 1
    MostPlayed = 2
    PopularNew = 3

class EGpuDriverId(SteamIntEnum):
    Invalid = 0
    Unknown = 1
    AmdProprietary = 2
    AmdOpenSource = 3
    MesaRadv = 4
    NvidiaProprietary = 5
    IntelPropietary = 6
    MesaIntel = 7
    QualcommProprietary = 8
    ArmProprietary = 9
    GoogleSwiftshader = 10
    BroadcomProprietary = 11
    MesaLLVMPipe = 12
    MoltenVK = 13
    MesaTurnip = 14
    MesaPanVK = 15
    MesaVenus = 16
    MesaDozen = 17
    MesaNVK = 18
    MesaHoneyKrisp = 19

class EGPUPerformanceLevel(SteamIntEnum):
    Invalid = 0
    Auto = 1
    Manual = 2
    Low = 3
    High = 4
    Profiling = 5

class EGraphicsPerfOverlayLevel(SteamIntEnum):
    Hidden = 0
    Basic = 1
    Medium = 2
    Full = 3
    Minimal = 4

class EGRAudio(SteamIntEnum):
    Game = 0
    System = 1
    Select = 2

class EGRExportLimitType(SteamIntEnum):
    Native = 0
    FileSize = 1
    Advanced = 2

class EGRMode(SteamIntEnum):
    Never = 0
    Always = 1
    Manual = 2

class EHardwareCompatibilityFeedbackDetails(SteamIntEnum):
    Unset = 0
    Performance = 1
    Stability = 2
    Legibility = 4
    Input = 8
    Other = 16

class EHardwareUpdateDeviceType(SteamIntEnum):
    Triton_BL = 0
    Proteus_BL = 1
    Triton_USB = 2
    Triton_BLE = 3
    Triton_ESB = 4
    Proteus_USB = 5
    Nereid_USB = 6

class EHardwareUpdatePriority(SteamIntEnum):
    Low = 0
    Normal = 1
    Suggested = 2
    Required = 3

class EHDRToneMapOperator(SteamIntEnum):
    Invalid = 0
    Uncharted = 1
    Reinhard = 2

EHDRVisualization = SteamIntEnum('EHDRVisualization', {
    'None': 0,
    'Heatmap': 1,
    'Analysis': 2,
    'HeatmapExtended': 3,
    'HeatmapClassic': 4,
    })

class EHIDDeviceDisconnectMethod(SteamIntEnum):
    EDeviceDisconnectMethodUnknown = 0
    EDeviceDisconnectMethodBluetooth = 1
    EDeviceDisconnectMethodFeatureReport = 2
    EDeviceDisconnectMethodOutputReport = 3

class EHIDDeviceLocation(SteamIntEnum):
    EDeviceLocationLocal = 0
    EDeviceLocationRemote = 2
    EDeviceLocationAny = 3

class EInputMode(SteamIntEnum):
    EInputModeUnknown = 0
    EInputModeMouse = 1
    EInputModeController = 2
    EInputModeMouseAndController = 3

class EJSRegisterMethodType(SteamIntEnum):
    Invalid = 0
    Function = 1
    Callback = 2
    Promise = 3

class EKeyEscrowUsage(SteamIntEnum):
    EKeyEscrowUsageStreamingDevice = 0

class ELEDManagerMode(SteamIntEnum):
    ELEDManagerModeInvalid = 0
    ELEDManagerModeLogon = 1
    ELEDManagerModeIdle = 2
    ELEDManagerModeDownload = 3
    ELEDManagerModeCustomize = 4
    ELEDManagerModeCustomizeStartup = 5

class ELobbyStatus(SteamIntEnum):
    ELobbyStatusInvalid = 0
    ELobbyStatusExists = 1
    ELobbyStatusDoesNotExist = 2
    ELobbyStatusNotAMember = 3

class ELogFileType(SteamIntEnum):
    ELogFileSystemBoot = 0
    ELogFileSystemReset = 1
    ELogFileSystemDebug = 2

class EMarketingMessageAssociationType(SteamIntEnum):
    EMarketingMessageNoAssociation = 0
    EMarketingMessageAppAssociation = 1
    EMarketingMessageSubscriptionAssociation = 2
    EMarketingMessagePublisherAssociation = 3
    EMarketingMessageGenreAssociation = 4
    EMarketingMessageBundleAssociation = 5

class EMarketingMessageClickLocation(SteamIntEnum):
    Unknown = 0
    Image = 1
    Button = 2
    DlcCapsule = 3
    HeaderArea = 4
    GameCapsule = 5
    PartnerEvent = 6

class EMarketingMessageLookupType(SteamIntEnum):
    EMarketingMessageLookupInvalid = 0
    EMarketingMessageLookupByGID = 1
    EMarketingMessageLookupActive = 2
    EMarketingMessageLookupByTitleWithType = 3
    EMarketingMessageLookupByGIDList = 4
    EMarketingMessageLookupByAssociatedID = 5

class EMarketingMessageTemplateType(SteamIntEnum):
    EMarketingMessageTemplate_Unknown = 0
    EMarketingMessageTemplate_Image = 1
    EMarketingMessageTemplate_Animated = 2
    EMarketingMessageTemplate_Featured_Video = 3
    EMarketingMessageTemplate_DLC_Override = 4
    EMarketingMessageTemplate_Replay = 5
    EMarketingMessageTemplate_Event = 6
    EMarketingMessageTemplate_AutoRender = 7
    EMarketingMessageTemplate_MAX = 8

class EMarketingMessageType(SteamIntEnum):
    EMarketingMessageInvalid = 0
    EMarketingMessageNowAvailable = 1
    EMarketingMessageWeekendDeal = 2
    EMarketingMessagePrePurchase = 3
    EMarketingMessagePlayNow = 4
    EMarketingMessagePreloadNow = 5
    EMarketingMessageGeneral = 6
    EMarketingMessageDemoQuit = 7
    EMarketingMessageGifting = 8
    EMarketingMessageEJsKorner = 9
    EMarketingMessageUpdate = 10
    EMarketingMessageMidweekDeal = 11
    EMarketingMessageDailyDeal = 12
    EMarketingMessageNewDLC = 13
    EMarketingMessageFreeWeekend = 14
    EMarketingMessageSalePages = 15
    EMarketingMessagePlaytestAvailable = 16

class EMarketingMessageVisibility(SteamIntEnum):
    EMarketingMessageVisibleBeta = 1
    EMarketingMessageVisiblePublic = 2
    EMarketingMessageVisibleApprovedForPublish = 3

class EMessageReactionType(SteamIntEnum):
    Invalid = 0
    Emoticon = 1
    Sticker = 2

class EMMSLobbyStatus(SteamIntEnum):
    EMMSLobbyStatusInvalid = 0
    EMMSLobbyStatusExists = 1
    EMMSLobbyStatusDoesNotExist = 2
    EMMSLobbyStatusNotAMember = 3

class EMouseMode(SteamIntEnum):
    EMouseModeUnknown = 0
    EMouseModeRelativeCursor_OBSOLETE = 1
    EMouseModeAbsoluteCursor = 2
    EMouseModeTouch = 3
    EMouseModeRelative = 4

class EMsg(SteamIntEnum):
    EMsgInvalid = 0
    EMsgMulti = 1
    EMsgProtobufWrapped = 2
    EMsgBaseGeneral = 100
    EMsgGenericReply = 100
    EMsgDestJobFailed = 113
    EMsgAlert = 115
    EMsgSCIDRequest = 120
    EMsgSCIDResponse = 121
    EMsgJobHeartbeat = 123
    EMsgHubConnect = 124
    EMsgSubscribe = 126
    EMRouteMessage = 127
    EMsgWGRequest = 130
    EMsgWGResponse = 131
    EMsgKeepAlive = 132
    EMsgWebAPIJobRequest = 133
    EMsgWebAPIJobResponse = 134
    EMsgClientSessionStart = 135
    EMsgClientSessionEnd = 136
    EMsgClientSessionUpdate = 137
    EMsgStatsDeprecated = 138
    EMsgPing = 139
    EMsgPingResponse = 140
    EMsgStats = 141
    EMsgRequestFullStatsBlock = 142
    EMsgLoadDBOCacheItem = 143
    EMsgLoadDBOCacheItemResponse = 144
    EMsgInvalidateDBOCacheItems = 145
    EMsgServiceMethod = 146
    EMsgServiceMethodResponse = 147
    EMsgClientPackageVersions = 148
    EMsgTimestampRequest = 149
    EMsgTimestampResponse = 150
    EMsgServiceMethodCallFromClient = 151
    EMsgServiceMethodSendToClient = 152
    EMsgBaseShell = 200
    EMsgAssignSysID = 200
    EMsgExit = 201
    EMsgDirRequest = 202
    EMsgDirResponse = 203
    EMsgZipRequest = 204
    EMsgZipResponse = 205
    EMsgUpdateRecordResponse = 215
    EMsgUpdateCreditCardRequest = 221
    EMsgUpdateUserBanResponse = 225
    EMsgPrepareToExit = 226
    EMsgContentDescriptionUpdate = 227
    EMsgTestResetServer = 228
    EMsgUniverseChanged = 229
    EMsgShellConfigInfoUpdate = 230
    EMsgRequestWindowsEventLogEntries = 233
    EMsgProvideWindowsEventLogEntries = 234
    EMsgShellSearchLogs = 235
    EMsgShellSearchLogsResponse = 236
    EMsgShellCheckWindowsUpdates = 237
    EMsgShellCheckWindowsUpdatesResponse = 238
    EMsgTestFlushDelayedSQL = 240
    EMsgTestFlushDelayedSQLResponse = 241
    EMsgEnsureExecuteScheduledTask_TEST = 242
    EMsgEnsureExecuteScheduledTaskResponse_TEST = 243
    EMsgUpdateScheduledTaskEnableState_TEST = 244
    EMsgUpdateScheduledTaskEnableStateResponse_TEST = 245
    EMsgContentDescriptionDeltaUpdate = 246
    EMsgGMShellAndServerAddressUpdates = 247
    EMsgGMDynamicRoutingUpdate = 248
    EMsgEnsureBillingConfigReload_TEST = 249
    EMsgEnsureBillingConfigReloadResponse_TEST = 250
    EMsgBaseGM = 300
    EMsgHeartbeat = 300
    EMsgShellFailed = 301
    EMsgExitShells = 307
    EMsgExitShell = 308
    EMsgGracefulExitShell = 309
    EMsgLicenseProcessingComplete = 316
    EMsgSetTestFlag = 317
    EMsgQueuedEmailsComplete = 318
    EMsgGMDRMSync = 320
    EMsgPhysicalBoxInventory = 321
    EMsgUpdateConfigFile = 322
    EMsgTestInitDB = 323
    EMsgGMWriteConfigToSQL = 324
    EMsgGMLoadActivationCodes = 325
    EMsgGMQueueForFBS = 326
    EMsgGMSchemaConversionResults = 327
    EMsgGMWriteShellFailureToSQL = 329
    EMsgGMGetServiceMethodRouting = 331
    EMsgGMGetServiceMethodRoutingResponse = 332
    EMsgGMTestNextBuildSchemaConversion = 334
    EMsgGMTestNextBuildSchemaConversionResponse = 335
    EMsgExpectShellRestart = 336
    EMsgHotFixProgress = 337
    EMsgGMStatsForwardToAdminConnections = 338
    EMsgGMGetModifiedConVars = 339
    EMsgGMGetModifiedConVarsResponse = 340
    EMsgGMNeedShellAndServerAddresses = 341
    EMsgBaseAIS = 400
    EMsgAISRequestContentDescription = 402
    EMsgAISGetPackageChangeNumber = 405
    EMsgAISGetPackageChangeNumberResponse = 406
    EMsgAIGetAppGCFlags = 423
    EMsgAIGetAppGCFlagsResponse = 424
    EMsgAIGetAppList = 425
    EMsgAIGetAppListResponse = 426
    EMsgAISUpdateSubordinateContentDescription = 431
    EMsgAISUpdateSubordinateContentDescriptionResponse = 432
    EMsgAISBroadcastSubordinateContentDescription = 434
    EMsgProductInfoChangedNotification = 435
    EMsgProductInfoCacheStatus = 436
    EMsgBaseAM = 500
    EMsgAMUpdateUserBanRequest = 504
    EMsgAMAddLicense = 505
    EMsgAMSendSystemIMToUser = 508
    EMsgAMExtendLicense = 509
    EMsgAMAddMinutesToLicense = 510
    EMsgAMCancelLicense = 511
    EMsgAMInitPurchase = 512
    EMsgAMPurchaseResponse = 513
    EMsgAMGetLegacyGameKey = 516
    EMsgAMGetLegacyGameKeyResponse = 517
    EMsgAMFindHungTransactions = 518
    EMsgAMSetAccountTrustedRequest = 519
    EMsgAMCancelPurchase = 522
    EMsgAMNewChallenge = 523
    EMsgAMFixPendingPurchase = 525
    EMsgAMFixPendingPurchaseResponse = 526
    EMsgAMIsUserBanned = 527
    EMsgAMRegisterKey = 528
    EMsgAMLoadActivationCodes = 529
    EMsgAMLoadActivationCodesResponse = 530
    EMsgAMLookupKeyResponse = 531
    EMsgAMLookupKey = 532
    EMsgAMChatCleanup = 533
    EMsgAMClanCleanup = 534
    EMsgAMFixPendingRefund = 535
    EMsgAMReverseChargeback = 536
    EMsgAMReverseChargebackResponse = 537
    EMsgAMClanCleanupList = 538
    EMsgAMSendCartRepurchase = 541
    EMsgAMSendCartRepurchaseResponse = 542
    EMsgAllowUserToPlayQuery = 550
    EMsgAllowUserToPlayResponse = 551
    EMsgAMVerfiyUser = 552
    EMsgAMClientNotPlaying = 553
    EMsgAMClientRequestFriendship = 554
    EMsgAMRelayPublishStatus = 555
    EMsgAMInitPurchaseResponse = 560
    EMsgAMRevokePurchaseResponse = 561
    EMsgAMRefreshGuestPasses = 563
    EMsgAMGrantGuestPasses = 566
    EMsgAMClanDataUpdated = 567
    EMsgAMReloadAccount = 568
    EMsgAMClientChatMsgRelay = 569
    EMsgAMChatMulti = 570
    EMsgAMClientChatInviteRelay = 571
    EMsgAMChatInvite = 572
    EMsgAMClientJoinChatRelay = 573
    EMsgAMClientChatMemberInfoRelay = 574
    EMsgAMPublishChatMemberInfo = 575
    EMsgAMClientAcceptFriendInvite = 576
    EMsgAMChatEnter = 577
    EMsgAMClientPublishRemovalFromSource = 578
    EMsgAMChatActionResult = 579
    EMsgAMFindAccounts = 580
    EMsgAMFindAccountsResponse = 581
    EMsgAMIsAccountNameInUse = 582
    EMsgAMIsAccountNameInUseResponse = 583
    EMsgAMSetAccountFlags = 584
    EMsgAMCreateClan = 586
    EMsgAMCreateClanResponse = 587
    EMsgAMGetClanDetails = 588
    EMsgAMGetClanDetailsResponse = 589
    EMsgAMSetPersonaName = 590
    EMsgAMSetAvatar = 591
    EMsgAMAuthenticateUser = 592
    EMsgAMAuthenticateUserResponse = 593
    EMsgAMP2PIntroducerMessage = 596
    EMsgClientChatAction = 597
    EMsgAMClientChatActionRelay = 598
    EMsgBaseVS = 600
    EMsgReqChallenge = 600
    EMsgVACResponse = 601
    EMsgReqChallengeTest = 602
    EMsgVSMarkCheat = 604
    EMsgVSAddCheat = 605
    EMsgVSPurgeCodeModDB = 606
    EMsgVSGetChallengeResults = 607
    EMsgVSChallengeResultText = 608
    EMsgVSReportLingerer = 609
    EMsgVSRequestManagedChallenge = 610
    EMsgVSLoadDBFinished = 611
    EMsgBaseDRMS = 625
    EMsgDRMBuildBlobRequest = 628
    EMsgDRMBuildBlobResponse = 629
    EMsgDRMResolveGuidRequest = 630
    EMsgDRMResolveGuidResponse = 631
    EMsgDRMVariabilityReport = 633
    EMsgDRMVariabilityReportResponse = 634
    EMsgDRMStabilityReport = 635
    EMsgDRMStabilityReportResponse = 636
    EMsgDRMDetailsReportRequest = 637
    EMsgDRMDetailsReportResponse = 638
    EMsgDRMProcessFile = 639
    EMsgDRMAdminUpdate = 640
    EMsgDRMAdminUpdateResponse = 641
    EMsgDRMSync = 642
    EMsgDRMSyncResponse = 643
    EMsgDRMProcessFileResponse = 644
    EMsgDRMEmptyGuidCache = 645
    EMsgDRMEmptyGuidCacheResponse = 646
    EMsgBaseCS = 650
    EMsgBaseClient = 700
    EMsgClientLogOn_Deprecated = 701
    EMsgClientAnonLogOn_Deprecated = 702
    EMsgClientHeartBeat = 703
    EMsgClientVACResponse = 704
    EMsgClientGamesPlayed_obsolete = 705
    EMsgClientLogOff = 706
    EMsgClientNoUDPConnectivity = 707
    EMsgClientConnectionStats = 710
    EMsgClientPingResponse = 712
    EMsgClientRemoveFriend = 714
    EMsgClientGamesPlayedNoDataBlob = 715
    EMsgClientChangeStatus = 716
    EMsgClientFriendMsg = 718
    EMsgClientGameConnect_obsolete = 719
    EMsgClientGamesPlayed2_obsolete = 720
    EMsgClientGameEnded_obsolete = 721
    EMsgClientSystemIM = 726
    EMsgClientSystemIMAck = 727
    EMsgClientGetLegacyGameKey = 730
    EMsgClientContentServerLogOn_Deprecated = 731
    EMsgClientGamesPlayed3_obsolete = 738
    EMsgClientAckGuestPass = 740
    EMsgClientRedeemGuestPass = 741
    EMsgClientGamesPlayed = 742
    EMsgClientRegisterKey = 743
    EMsgClientInviteUserToClan = 744
    EMsgClientAcknowledgeClanInvite = 745
    EMsgClientAppUsageEvent = 747
    EMsgClientLogOnResponse = 751
    EMsgClientSetHeartbeatRate = 755
    EMsgClientNotLoggedOnDeprecated = 756
    EMsgClientLoggedOff = 757
    EMsgGSApprove = 758
    EMsgGSDeny = 759
    EMsgGSKick = 760
    EMsgClientPurchaseResponse = 763
    EMsgClientPing = 764
    EMsgClientNOP = 765
    EMsgClientPersonaState = 766
    EMsgClientFriendsList = 767
    EMsgClientAccountInfo = 768
    EMsgClientNewsUpdate = 771
    EMsgClientGameConnectDeny = 773
    EMsgGSStatusReply = 774
    EMsgClientGameConnectTokens = 779
    EMsgClientLicenseList = 780
    EMsgClientVACBanStatus = 782
    EMsgClientGetLegacyGameKeyResponse = 785
    EMsgClientAddFriend = 791
    EMsgClientAddFriendResponse = 792
    EMsgClientAckGuestPassResponse = 796
    EMsgClientRedeemGuestPassResponse = 797
    EMsgClientUpdateGuestPassesList = 798
    EMsgClientChatMsg = 799
    EMsgClientChatInvite = 800
    EMsgClientJoinChat = 801
    EMsgClientChatMemberInfo = 802
    EMsgClientLogOnWithCredentials_Deprecated = 803
    EMsgClientPasswordChangeResponse = 805
    EMsgClientChatEnter = 807
    EMsgClientFriendRemovedFromSource = 808
    EMsgClientCreateChat = 809
    EMsgClientCreateChatResponse = 810
    EMsgClientP2PIntroducerMessage = 813
    EMsgClientChatActionResult = 814
    EMsgClientRequestFriendData = 815
    EMsgClientGetUserStats = 818
    EMsgClientGetUserStatsResponse = 819
    EMsgClientStoreUserStats = 820
    EMsgClientStoreUserStatsResponse = 821
    EMsgClientClanState = 822
    EMsgClientServiceModule = 830
    EMsgClientServiceCall = 831
    EMsgClientServiceCallResponse = 832
    EMsgClientNatTraversalStatEvent = 839
    EMsgClientSteamUsageEvent = 842
    EMsgClientCheckPassword = 845
    EMsgClientResetPassword = 846
    EMsgClientCheckPasswordResponse = 848
    EMsgClientResetPasswordResponse = 849
    EMsgClientSessionToken = 850
    EMsgClientDRMProblemReport = 851
    EMsgClientSetIgnoreFriend = 855
    EMsgClientSetIgnoreFriendResponse = 856
    EMsgClientGetAppOwnershipTicket = 857
    EMsgClientGetAppOwnershipTicketResponse = 858
    EMsgClientGetLobbyListResponse = 860
    EMsgClientServerList = 880
    EMsgClientDRMBlobRequest = 896
    EMsgClientDRMBlobResponse = 897
    EMsgBaseGameServer = 900
    EMsgGSDisconnectNotice = 901
    EMsgGSStatus = 903
    EMsgGSUserPlaying = 905
    EMsgGSStatus2 = 906
    EMsgGSStatusUpdate_Unused = 907
    EMsgGSServerType = 908
    EMsgGSPlayerList = 909
    EMsgGSGetPlayStats = 918
    EMsgGSGetPlayStatsResponse = 919
    EMsgGSGetUserGroupStatus = 920
    EMsgAMGetUserGroupStatus = 921
    EMsgAMGetUserGroupStatusResponse = 922
    EMsgGSGetUserGroupStatusResponse = 923
    EMsgGSGetReputation = 936
    EMsgGSGetReputationResponse = 937
    EMsgGSAssociateWithClan = 938
    EMsgGSAssociateWithClanResponse = 939
    EMsgGSComputeNewPlayerCompatibility = 940
    EMsgGSComputeNewPlayerCompatibilityResponse = 941
    EMsgBaseAdmin = 1000
    EMsgAdminCmd = 1000
    EMsgAdminCmdResponse = 1004
    EMsgAdminLogListenRequest = 1005
    EMsgAdminLogEvent = 1006
    EMsgUniverseData = 1010
    EMsgAdminSpew = 1019
    EMsgAdminConsoleTitle = 1020
    EMsgAdminGCSpew = 1023
    EMsgAdminGCCommand = 1024
    EMsgAdminGCGetCommandList = 1025
    EMsgAdminGCGetCommandListResponse = 1026
    EMsgFBSConnectionData = 1027
    EMsgAdminMsgSpew = 1028
    EMsgBaseFBS = 1100
    EMsgFBSReqVersion = 1100
    EMsgFBSVersionInfo = 1101
    EMsgFBSForceRefresh = 1102
    EMsgFBSForceBounce = 1103
    EMsgFBSDeployPackage = 1104
    EMsgFBSDeployResponse = 1105
    EMsgFBSUpdateBootstrapper = 1106
    EMsgFBSSetState = 1107
    EMsgFBSApplyOSUpdates = 1108
    EMsgFBSRunCMDScript = 1109
    EMsgFBSRebootBox = 1110
    EMsgFBSSetBigBrotherMode = 1111
    EMsgFBSMinidumpServer = 1112
    EMsgFBSDeployHotFixPackage = 1114
    EMsgFBSDeployHotFixResponse = 1115
    EMsgFBSDownloadHotFix = 1116
    EMsgFBSDownloadHotFixResponse = 1117
    EMsgFBSUpdateTargetConfigFile = 1118
    EMsgFBSApplyAccountCred = 1119
    EMsgFBSApplyAccountCredResponse = 1120
    EMsgFBSSetShellCount = 1121
    EMsgFBSTerminateShell = 1122
    EMsgFBSQueryGMForRequest = 1123
    EMsgFBSQueryGMResponse = 1124
    EMsgFBSTerminateZombies = 1125
    EMsgFBSInfoFromBootstrapper = 1126
    EMsgFBSRebootBoxResponse = 1127
    EMsgFBSBootstrapperPackageRequest = 1128
    EMsgFBSBootstrapperPackageResponse = 1129
    EMsgFBSBootstrapperGetPackageChunk = 1130
    EMsgFBSBootstrapperGetPackageChunkResponse = 1131
    EMsgFBSBootstrapperPackageTransferProgress = 1132
    EMsgFBSRestartBootstrapper = 1133
    EMsgFBSPauseFrozenDumps = 1134
    EMsgBaseFileXfer = 1200
    EMsgFileXferRequest = 1200
    EMsgFileXferResponse = 1201
    EMsgFileXferData = 1202
    EMsgFileXferEnd = 1203
    EMsgFileXferDataAck = 1204
    EMsgBaseChannelAuth = 1300
    EMsgChannelAuthChallenge = 1300
    EMsgChannelAuthResponse = 1301
    EMsgChannelAuthResult = 1302
    EMsgChannelEncryptRequest = 1303
    EMsgChannelEncryptResponse = 1304
    EMsgChannelEncryptResult = 1305
    EMsgBaseBS = 1400
    EMsgBSPurchaseStart = 1401
    EMsgBSPurchaseResponse = 1402
    EMsgBSAuthenticateCCTrans = 1403
    EMsgBSAuthenticateCCTransResponse = 1404
    EMsgBSSettleComplete = 1406
    EMsgBSInitPayPalTxn = 1408
    EMsgBSInitPayPalTxnResponse = 1409
    EMsgBSGetPayPalUserInfo = 1410
    EMsgBSGetPayPalUserInfoResponse = 1411
    EMsgBSPaymentInstrBan = 1417
    EMsgBSPaymentInstrBanResponse = 1418
    EMsgBSInitGCBankXferTxn = 1421
    EMsgBSInitGCBankXferTxnResponse = 1422
    EMsgBSCommitGCTxn = 1425
    EMsgBSQueryTransactionStatus = 1426
    EMsgBSQueryTransactionStatusResponse = 1427
    EMsgBSQueryTxnExtendedInfo = 1433
    EMsgBSQueryTxnExtendedInfoResponse = 1434
    EMsgBSUpdateConversionRates = 1435
    EMsgBSPurchaseRunFraudChecks = 1437
    EMsgBSPurchaseRunFraudChecksResponse = 1438
    EMsgBSQueryBankInformation = 1440
    EMsgBSQueryBankInformationResponse = 1441
    EMsgBSValidateXsollaSignature = 1445
    EMsgBSValidateXsollaSignatureResponse = 1446
    EMsgBSQiwiWalletInvoice = 1448
    EMsgBSQiwiWalletInvoiceResponse = 1449
    EMsgBSUpdateInventoryFromProPack = 1450
    EMsgBSUpdateInventoryFromProPackResponse = 1451
    EMsgBSSendShippingRequest = 1452
    EMsgBSSendShippingRequestResponse = 1453
    EMsgBSGetProPackOrderStatus = 1454
    EMsgBSGetProPackOrderStatusResponse = 1455
    EMsgBSCheckJobRunning = 1456
    EMsgBSCheckJobRunningResponse = 1457
    EMsgBSResetPackagePurchaseRateLimit = 1458
    EMsgBSResetPackagePurchaseRateLimitResponse = 1459
    EMsgBSUpdatePaymentData = 1460
    EMsgBSUpdatePaymentDataResponse = 1461
    EMsgBSGetBillingAddress = 1462
    EMsgBSGetBillingAddressResponse = 1463
    EMsgBSGetCreditCardInfo = 1464
    EMsgBSGetCreditCardInfoResponse = 1465
    EMsgBSRemoveExpiredPaymentData = 1468
    EMsgBSRemoveExpiredPaymentDataResponse = 1469
    EMsgBSConvertToCurrentKeys = 1470
    EMsgBSConvertToCurrentKeysResponse = 1471
    EMsgBSInitPurchase = 1472
    EMsgBSInitPurchaseResponse = 1473
    EMsgBSCompletePurchase = 1474
    EMsgBSCompletePurchaseResponse = 1475
    EMsgBSPruneCardUsageStats = 1476
    EMsgBSPruneCardUsageStatsResponse = 1477
    EMsgBSStoreBankInformation = 1478
    EMsgBSStoreBankInformationResponse = 1479
    EMsgBSVerifyPOSAKey = 1480
    EMsgBSVerifyPOSAKeyResponse = 1481
    EMsgBSReverseRedeemPOSAKey = 1482
    EMsgBSReverseRedeemPOSAKeyResponse = 1483
    EMsgBSQueryFindCreditCard = 1484
    EMsgBSQueryFindCreditCardResponse = 1485
    EMsgBSStatusInquiryPOSAKey = 1486
    EMsgBSStatusInquiryPOSAKeyResponse = 1487
    EMsgBSBoaCompraConfirmProductDelivery = 1494
    EMsgBSBoaCompraConfirmProductDeliveryResponse = 1495
    EMsgBSGenerateBoaCompraMD5 = 1496
    EMsgBSGenerateBoaCompraMD5Response = 1497
    EMsgBSCommitWPTxn = 1498
    EMsgBSCommitAdyenTxn = 1499
    EMsgBaseATS = 1500
    EMsgATSStartStressTest = 1501
    EMsgATSStopStressTest = 1502
    EMsgATSRunFailServerTest = 1503
    EMsgATSUFSPerfTestTask = 1504
    EMsgATSUFSPerfTestResponse = 1505
    EMsgATSCycleTCM = 1506
    EMsgATSInitDRMSStressTest = 1507
    EMsgATSCallTest = 1508
    EMsgATSCallTestReply = 1509
    EMsgATSStartExternalStress = 1510
    EMsgATSExternalStressJobStart = 1511
    EMsgATSExternalStressJobQueued = 1512
    EMsgATSExternalStressJobRunning = 1513
    EMsgATSExternalStressJobStopped = 1514
    EMsgATSExternalStressJobStopAll = 1515
    EMsgATSExternalStressActionResult = 1516
    EMsgATSStarted = 1517
    EMsgATSCSPerfTestTask = 1518
    EMsgATSCSPerfTestResponse = 1519
    EMsgBaseDP = 1600
    EMsgDPSetPublishingState = 1601
    EMsgDPUniquePlayersStat = 1603
    EMsgDPCloudStats = 1612
    EMsgDPGetPlayerCount = 1615
    EMsgDPGetPlayerCountResponse = 1616
    EMsgDPGameServersPlayersStats = 1617
    EMsgClientDPCheckSpecialSurvey = 1620
    EMsgClientDPCheckSpecialSurveyResponse = 1621
    EMsgClientDPSendSpecialSurveyResponse = 1622
    EMsgClientDPSendSpecialSurveyResponseReply = 1623
    EMsgDPStoreSaleStatistics = 1624
    EMsgDPPartnerMicroTxns = 1628
    EMsgDPPartnerMicroTxnsResponse = 1629
    EMsgDPVRUniquePlayersStat = 1631
    EMsgBaseCM = 1700
    EMsgCMSetAllowState = 1701
    EMsgCMSpewAllowState = 1702
    EMsgCMSessionRejected = 1703
    EMsgCMSetSecrets = 1704
    EMsgCMGetSecrets = 1705
    EMsgCMRemotePlayReplyPacket = 1706
    EMsgCMRemotePlayOffline = 1707
    EMsgBaseGC = 2200
    EMsgGCCmdRevive = 2203
    EMsgGCCmdDown = 2206
    EMsgGCCmdDeploy = 2207
    EMsgGCCmdDeployResponse = 2208
    EMsgGCCmdSwitch = 2209
    EMsgAMRefreshSessions = 2210
    EMsgGCAchievementAwarded = 2212
    EMsgGCCmdStatus = 2216
    EMsgGCRegisterWebInterfaces_Deprecated = 2217
    EMsgGCGetAccountDetails_DEPRECATED = 2218
    EMsgGCInterAppMessage = 2219
    EMsgGCGetEmailTemplate = 2220
    EMsgGCGetEmailTemplateResponse = 2221
    EMsgGCHRelay = 2222
    EMsgGCHRelayToClient = 2223
    EMsgGCHUpdateSession = 2224
    EMsgGCHRequestUpdateSession = 2225
    EMsgGCHRequestStatus = 2226
    EMsgGCHRequestStatusResponse = 2227
    EMsgGCHAccountVacStatusChange = 2228
    EMsgGCHSpawnGC = 2229
    EMsgGCHSpawnGCResponse = 2230
    EMsgGCHKillGC = 2231
    EMsgGCHKillGCResponse = 2232
    EMsgGCHAccountTradeBanStatusChange = 2233
    EMsgGCHAccountLockStatusChange = 2234
    EMsgGCHVacVerificationChange = 2235
    EMsgGCHAccountPhoneNumberChange = 2236
    EMsgGCHAccountTwoFactorChange = 2237
    EMsgGCHInviteUserToLobby = 2238
    EMsgGCHUpdateMultipleSessions = 2239
    EMsgGCHMarkAppSessionsAuthoritative = 2240
    EMsgGCHRecurringSubscriptionStatusChange = 2241
    EMsgGCHAppCheersReceived = 2242
    EMsgGCHAppCheersGetAllowedTypes = 2243
    EMsgGCHAppCheersGetAllowedTypesResponse = 2244
    EMsgGCHRoutingRulesFromGCHtoGM = 2245
    EMsgGCHRoutingRulesToGCHfromGM = 2246
    EMsgUpdateCMMessageRateRules = 2247
    EMsgBaseP2P = 2500
    EMsgP2PIntroducerMessage = 2502
    EMsgBaseSM = 2900
    EMsgSMExpensiveReport = 2902
    EMsgSMHourlyReport = 2903
    EMsgSMPartitionRenames = 2905
    EMsgSMTestNextBuildSchemaConversion = 2907
    EMsgSMTestNextBuildSchemaConversionResponse = 2908
    EMsgBaseTest = 3000
    EMsgFailServer = 3000
    EMsgJobHeartbeatTest = 3001
    EMsgJobHeartbeatTestResponse = 3002
    EMsgBaseFTSRange = 3100
    EMsgBaseCCSRange = 3150
    EMsgCCSDeleteAllCommentsByAuthor = 3161
    EMsgCCSDeleteAllCommentsByAuthorResponse = 3162
    EMsgBaseLBSRange = 3200
    EMsgLBSSetScore = 3201
    EMsgLBSSetScoreResponse = 3202
    EMsgLBSFindOrCreateLB = 3203
    EMsgLBSFindOrCreateLBResponse = 3204
    EMsgLBSGetLBEntries = 3205
    EMsgLBSGetLBEntriesResponse = 3206
    EMsgLBSGetLBList = 3207
    EMsgLBSGetLBListResponse = 3208
    EMsgLBSSetLBDetails = 3209
    EMsgLBSDeleteLB = 3210
    EMsgLBSDeleteLBEntry = 3211
    EMsgLBSResetLB = 3212
    EMsgLBSResetLBResponse = 3213
    EMsgLBSDeleteLBResponse = 3214
    EMsgBaseOGS = 3400
    EMsgOGSBeginSession = 3401
    EMsgOGSBeginSessionResponse = 3402
    EMsgOGSEndSession = 3403
    EMsgOGSEndSessionResponse = 3404
    EMsgOGSWriteAppSessionRow = 3406
    EMsgBaseBRP = 3600
    EMsgBaseAMRange2 = 4000
    EMsgAMCreateChat = 4001
    EMsgAMCreateChatResponse = 4002
    EMsgAMGetAccountEmailAddress = 4006
    EMsgAMGetAccountEmailAddressResponse = 4007
    EMsgAMRequestClanData = 4008
    EMsgAMRouteToClients = 4009
    EMsgAMLeaveClan = 4010
    EMsgAMClanPermissions = 4011
    EMsgAMClanPermissionsResponse = 4012
    EMsgAMCreateClanEventDummyForRateLimiting = 4013
    EMsgAMUpdateClanEventDummyForRateLimiting = 4015
    EMsgAMSetClanPermissionSettings = 4021
    EMsgAMSetClanPermissionSettingsResponse = 4022
    EMsgAMGetClanPermissionSettings = 4023
    EMsgAMGetClanPermissionSettingsResponse = 4024
    EMsgAMPublishChatRoomInfo = 4025
    EMsgClientChatRoomInfo = 4026
    EMsgAMGetClanHistory = 4039
    EMsgAMGetClanHistoryResponse = 4040
    EMsgAMGetClanPermissionBits = 4041
    EMsgAMGetClanPermissionBitsResponse = 4042
    EMsgAMSetClanPermissionBits = 4043
    EMsgAMSetClanPermissionBitsResponse = 4044
    EMsgAMSessionInfoRequest = 4045
    EMsgAMSessionInfoResponse = 4046
    EMsgAMValidateWGToken = 4047
    EMsgAMGetClanRank = 4050
    EMsgAMGetClanRankResponse = 4051
    EMsgAMSetClanRank = 4052
    EMsgAMSetClanRankResponse = 4053
    EMsgAMGetClanPOTW = 4054
    EMsgAMGetClanPOTWResponse = 4055
    EMsgAMSetClanPOTW = 4056
    EMsgAMSetClanPOTWResponse = 4057
    EMsgAMDumpUser = 4059
    EMsgAMKickUserFromClan = 4060
    EMsgAMAddFounderToClan = 4061
    EMsgAMValidateWGTokenResponse = 4062
    EMsgAMSetAccountDetails = 4064
    EMsgAMGetChatBanList = 4065
    EMsgAMGetChatBanListResponse = 4066
    EMsgAMUnBanFromChat = 4067
    EMsgAMSetClanDetails = 4068
    EMsgUGSGetUserGameStats = 4073
    EMsgUGSGetUserGameStatsResponse = 4074
    EMsgAMCheckClanMembership = 4075
    EMsgAMGetClanMembers = 4076
    EMsgAMGetClanMembersResponse = 4077
    EMsgAMNotifyChatOfClanChange = 4079
    EMsgAMResubmitPurchase = 4080
    EMsgAMAddFriend = 4081
    EMsgAMAddFriendResponse = 4082
    EMsgAMRemoveFriend = 4083
    EMsgAMDumpClan = 4084
    EMsgAMChangeClanOwner = 4085
    EMsgAMCancelEasyCollect = 4086
    EMsgAMCancelEasyCollectResponse = 4087
    EMsgAMClansInCommon = 4090
    EMsgAMClansInCommonResponse = 4091
    EMsgAMIsValidAccountID = 4092
    EMsgAMWipeFriendsList = 4095
    EMsgAMSetIgnored = 4096
    EMsgAMClansInCommonCountResponse = 4097
    EMsgAMFriendsList = 4098
    EMsgAMFriendsListResponse = 4099
    EMsgAMFriendsInCommon = 4100
    EMsgAMFriendsInCommonResponse = 4101
    EMsgAMFriendsInCommonCountResponse = 4102
    EMsgAMClansInCommonCount = 4103
    EMsgAMChallengeVerdict = 4104
    EMsgAMChallengeNotification = 4105
    EMsgAMFindGSByIP = 4106
    EMsgAMFoundGSByIP = 4107
    EMsgAMGiftRevoked = 4108
    EMsgAMUserClanList = 4110
    EMsgAMUserClanListResponse = 4111
    EMsgAMGetAccountDetails2 = 4112
    EMsgAMGetAccountDetailsResponse2 = 4113
    EMsgAMSetCommunityProfileSettings = 4114
    EMsgAMSetCommunityProfileSettingsResponse = 4115
    EMsgAMGetCommunityPrivacyState = 4116
    EMsgAMGetCommunityPrivacyStateResponse = 4117
    EMsgAMCheckClanInviteRateLimiting = 4118
    EMsgAMGetIgnored = 4120
    EMsgAMGetIgnoredResponse = 4121
    EMsgAMSetIgnoredResponse = 4122
    EMsgAMSetFriendRelationshipNone = 4123
    EMsgAMGetFriendRelationship = 4124
    EMsgAMGetFriendRelationshipResponse = 4125
    EMsgAMServiceModulesCache = 4126
    EMsgAMServiceModulesCall = 4127
    EMsgAMServiceModulesCallResponse = 4128
    EMsgCommunityAddFriendNews = 4140
    EMsgAMFindClanUser = 4143
    EMsgAMFindClanUserResponse = 4144
    EMsgAMBanFromChat = 4145
    EMsgAMGetUserNewsSubscriptions = 4147
    EMsgAMGetUserNewsSubscriptionsResponse = 4148
    EMsgAMSetUserNewsSubscriptions = 4149
    EMsgAMSendQueuedEmails = 4152
    EMsgAMSetLicenseFlags = 4153
    EMsgAMGetAccountStatus = 4158
    EMsgAMGetAccountStatusResponse = 4159
    EMsgAMEditBanReason = 4160
    EMsgAMCheckClanMembershipResponse = 4161
    EMsgAMProbeClanMembershipList = 4162
    EMsgAMProbeClanMembershipListResponse = 4163
    EMsgAMGetFriendsLobbies = 4165
    EMsgAMGetFriendsLobbiesResponse = 4166
    EMsgAMGetUserFriendNewsResponse = 4172
    EMsgCommunityGetUserFriendNews = 4173
    EMsgAMGetUserClansNewsResponse = 4174
    EMsgAMGetUserClansNews = 4175
    EMsgAMGetPreviousCBAccount = 4184
    EMsgAMGetPreviousCBAccountResponse = 4185
    EMsgAMGetUserLicenseHistory = 4190
    EMsgAMGetUserLicenseHistoryResponse = 4191
    EMsgAMSupportChangePassword = 4194
    EMsgAMSupportChangeEmail = 4195
    EMsgAMResetUserVerificationGSByIP = 4197
    EMsgAMUpdateGSPlayStats = 4198
    EMsgAMSupportEnableOrDisable = 4199
    EMsgAMGetPurchaseStatus = 4206
    EMsgAMSupportIsAccountEnabled = 4209
    EMsgAMSupportIsAccountEnabledResponse = 4210
    EMsgUGSGetUserStats = 4211
    EMsgAMGSSearch = 4213
    EMsgChatServerRouteFriendMsg = 4219
    EMsgAMTicketAuthRequestOrResponse = 4220
    EMsgAMAddFreeLicense = 4224
    EMsgAMValidateEmailLink = 4231
    EMsgAMValidateEmailLinkResponse = 4232
    EMsgUGSStoreUserStats = 4236
    EMsgAMDeleteStoredCard = 4241
    EMsgAMRevokeLegacyGameKeys = 4242
    EMsgAMGetWalletDetails = 4244
    EMsgAMGetWalletDetailsResponse = 4245
    EMsgAMDeleteStoredPaymentInfo = 4246
    EMsgAMGetStoredPaymentSummary = 4247
    EMsgAMGetStoredPaymentSummaryResponse = 4248
    EMsgAMGetWalletConversionRate = 4249
    EMsgAMGetWalletConversionRateResponse = 4250
    EMsgAMConvertWallet = 4251
    EMsgAMConvertWalletResponse = 4252
    EMsgAMSetPreApproval = 4255
    EMsgAMSetPreApprovalResponse = 4256
    EMsgAMCreateRefund = 4258
    EMsgAMCreateChargeback = 4260
    EMsgAMCreateDispute = 4262
    EMsgAMClearDispute = 4264
    EMsgAMCreateFinancialAdjustment = 4265
    EMsgAMPlayerNicknameList = 4266
    EMsgAMPlayerNicknameListResponse = 4267
    EMsgAMGetUserCurrentGameInfo = 4269
    EMsgAMGetUserCurrentGameInfoResponse = 4270
    EMsgAMGetGSPlayerList = 4271
    EMsgAMGetGSPlayerListResponse = 4272
    EMsgAMGetSteamIDForMicroTxn = 4278
    EMsgAMGetSteamIDForMicroTxnResponse = 4279
    EMsgAMSetPartnerMember = 4280
    EMsgAMRemovePublisherUser = 4281
    EMsgAMGetUserLicenseList = 4282
    EMsgAMGetUserLicenseListResponse = 4283
    EMsgAMReloadGameGroupPolicy = 4284
    EMsgAMAddFreeLicenseResponse = 4285
    EMsgAMVACStatusUpdate = 4286
    EMsgAMGetAccountDetails = 4287
    EMsgAMGetAccountDetailsResponse = 4288
    EMsgAMGetPlayerLinkDetails = 4289
    EMsgAMGetPlayerLinkDetailsResponse = 4290
    EMsgAMGetAccountFlagsForWGSpoofing = 4294
    EMsgAMGetAccountFlagsForWGSpoofingResponse = 4295
    EMsgAMGetClanOfficers = 4298
    EMsgAMGetClanOfficersResponse = 4299
    EMsgAMNameChange = 4300
    EMsgAMGetNameHistory = 4301
    EMsgAMGetNameHistoryResponse = 4302
    EMsgAMSupportRemoveAccountSecurity = 4307
    EMsgAMIsAccountInCaptchaGracePeriod = 4308
    EMsgAMIsAccountInCaptchaGracePeriodResponse = 4309
    EMsgAMAccountPS3Unlink = 4310
    EMsgAMAccountPS3UnlinkResponse = 4311
    EMsgUGSStoreUserStatsResponse = 4312
    EMsgAMGetAccountPSNInfo = 4313
    EMsgAMGetAccountPSNInfoResponse = 4314
    EMsgAMAuthenticatedPlayerList = 4315
    EMsgAMGetUserGifts = 4316
    EMsgAMGetUserGiftsResponse = 4317
    EMsgAMTransferLockedGifts = 4320
    EMsgAMTransferLockedGiftsResponse = 4321
    EMsgAMPlayerHostedOnGameServer = 4322
    EMsgAMGetAccountBanInfo = 4323
    EMsgAMGetAccountBanInfoResponse = 4324
    EMsgAMRecordBanEnforcement = 4325
    EMsgAMRollbackGiftTransfer = 4326
    EMsgAMRollbackGiftTransferResponse = 4327
    EMsgAMHandlePendingTransaction = 4328
    EMsgAMRequestClanDetails = 4329
    EMsgAMDeleteStoredPaypalAgreement = 4330
    EMsgAMGameServerUpdate = 4331
    EMsgAMGameServerRemove = 4332
    EMsgAMGetPaypalAgreements = 4333
    EMsgAMGetPaypalAgreementsResponse = 4334
    EMsgAMGameServerPlayerCompatibilityCheck = 4335
    EMsgAMGameServerPlayerCompatibilityCheckResponse = 4336
    EMsgAMRenewLicense = 4337
    EMsgAMGetAccountCommunityBanInfo = 4338
    EMsgAMGetAccountCommunityBanInfoResponse = 4339
    EMsgAMGameServerAccountChangePassword = 4340
    EMsgAMGameServerAccountDeleteAccount = 4341
    EMsgAMRenewAgreement = 4342
    EMsgAMXsollaPayment = 4344
    EMsgAMXsollaPaymentResponse = 4345
    EMsgAMAcctAllowedToPurchase = 4346
    EMsgAMAcctAllowedToPurchaseResponse = 4347
    EMsgAMSwapKioskDeposit = 4348
    EMsgAMSwapKioskDepositResponse = 4349
    EMsgAMSetUserGiftUnowned = 4350
    EMsgAMSetUserGiftUnownedResponse = 4351
    EMsgAMClaimUnownedUserGift = 4352
    EMsgAMClaimUnownedUserGiftResponse = 4353
    EMsgAMSetClanName = 4354
    EMsgAMSetClanNameResponse = 4355
    EMsgAMGrantCoupon = 4356
    EMsgAMGrantCouponResponse = 4357
    EMsgAMIsPackageRestrictedInUserCountry = 4358
    EMsgAMIsPackageRestrictedInUserCountryResponse = 4359
    EMsgAMHandlePendingTransactionResponse = 4360
    EMsgAMGrantGuestPasses2 = 4361
    EMsgAMGrantGuestPasses2Response = 4362
    EMsgAMGetPlayerBanDetails = 4365
    EMsgAMGetPlayerBanDetailsResponse = 4366
    EMsgAMFinalizePurchase = 4367
    EMsgAMFinalizePurchaseResponse = 4368
    EMsgAMPersonaChangeResponse = 4372
    EMsgAMGetClanDetailsForForumCreation = 4373
    EMsgAMGetClanDetailsForForumCreationResponse = 4374
    EMsgAMGetPendingNotificationCount = 4375
    EMsgAMGetPendingNotificationCountResponse = 4376
    EMsgAMPasswordHashUpgrade = 4377
    EMsgAMBoaCompraPayment = 4380
    EMsgAMBoaCompraPaymentResponse = 4381
    EMsgAMCompleteExternalPurchase = 4383
    EMsgAMCompleteExternalPurchaseResponse = 4384
    EMsgAMResolveNegativeWalletCredits = 4385
    EMsgAMResolveNegativeWalletCreditsResponse = 4386
    EMsgAMPlayerGetClanBasicDetails = 4389
    EMsgAMPlayerGetClanBasicDetailsResponse = 4390
    EMsgAMMOLPayment = 4391
    EMsgAMMOLPaymentResponse = 4392
    EMsgGetUserIPCountry = 4393
    EMsgGetUserIPCountryResponse = 4394
    EMsgNotificationOfSuspiciousActivity = 4395
    EMsgAMDegicaPayment = 4396
    EMsgAMDegicaPaymentResponse = 4397
    EMsgAMEClubPayment = 4398
    EMsgAMEClubPaymentResponse = 4399
    EMsgAMPayPalPaymentsHubPayment = 4400
    EMsgAMPayPalPaymentsHubPaymentResponse = 4401
    EMsgAMTwoFactorRecoverAuthenticatorRequest = 4402
    EMsgAMTwoFactorRecoverAuthenticatorResponse = 4403
    EMsgAMSmart2PayPayment = 4404
    EMsgAMSmart2PayPaymentResponse = 4405
    EMsgAMValidatePasswordResetCodeAndSendSmsRequest = 4406
    EMsgAMValidatePasswordResetCodeAndSendSmsResponse = 4407
    EMsgAMGetAccountResetDetailsRequest = 4408
    EMsgAMGetAccountResetDetailsResponse = 4409
    EMsgAMBitPayPayment = 4410
    EMsgAMBitPayPaymentResponse = 4411
    EMsgAMSendAccountInfoUpdate = 4412
    EMsgAMSendScheduledGift = 4413
    EMsgAMNodwinPayment = 4414
    EMsgAMNodwinPaymentResponse = 4415
    EMsgAMResolveWalletRevoke = 4416
    EMsgAMResolveWalletReverseRevoke = 4417
    EMsgAMFundedPayment = 4418
    EMsgAMFundedPaymentResponse = 4419
    EMsgAMRequestPersonaUpdateForChatServer = 4420
    EMsgAMPerfectWorldPayment = 4421
    EMsgAMPerfectWorldPaymentResponse = 4422
    EMsgAMECommPayPayment = 4423
    EMsgAMECommPayPaymentResponse = 4424
    EMsgAMSetRemoteClientID = 4425
    EMsgAMNuveiPayment = 4426
    EMsgAMNuveiPaymentResponse = 4427
    EMsgBasePSRange = 5000
    EMsgPSIsValidShoppingCart = 5003
    EMsgPSIsValidShoppingCartResponse = 5004
    EMsgPSGetShoppingCartContents = 5009
    EMsgPSGetShoppingCartContentsResponse = 5010
    EMsgPSAddWalletCreditToShoppingCart = 5011
    EMsgPSAddWalletCreditToShoppingCartResponse = 5012
    EMsgPSGetAccountCartContents = 5013
    EMsgPSGetAccountCartContentsResponse = 5014
    EMsgBaseUFSRange = 5200
    EMsgUFSReloadPartitionInfo = 5215
    EMsgUFSSynchronizeFile = 5217
    EMsgUFSSynchronizeFileResponse = 5218
    EMsgClientUFSGetUGCDetails = 5226
    EMsgClientUFSGetUGCDetailsResponse = 5227
    EMsgUFSUpdateFileFlags = 5228
    EMsgUFSUpdateFileFlagsResponse = 5229
    EMsgClientUFSGetSingleFileInfo = 5230
    EMsgClientUFSGetSingleFileInfoResponse = 5231
    EMsgClientUFSShareFile = 5232
    EMsgClientUFSShareFileResponse = 5233
    EMsgUFSReloadAccount = 5234
    EMsgUFSReloadAccountResponse = 5235
    EMsgUFSUpdateRecordBatched = 5236
    EMsgUFSUpdateRecordBatchedResponse = 5237
    EMsgUFSMigrateFile = 5238
    EMsgUFSMigrateFileResponse = 5239
    EMsgUFSGetUGCURLs = 5240
    EMsgUFSGetUGCURLsResponse = 5241
    EMsgUFSHttpUploadFileFinishRequest = 5242
    EMsgUFSHttpUploadFileFinishResponse = 5243
    EMsgUFSDownloadStartRequest = 5244
    EMsgUFSDownloadStartResponse = 5245
    EMsgUFSDownloadChunkRequest = 5246
    EMsgUFSDownloadChunkResponse = 5247
    EMsgUFSDownloadFinishRequest = 5248
    EMsgUFSDownloadFinishResponse = 5249
    EMsgUFSFlushURLCache = 5250
    EMsgUFSMigrateFileAppID = 5253
    EMsgUFSMigrateFileAppIDResponse = 5254
    EMsgBaseClient2 = 5400
    EMsgClientRequestForgottenPasswordEmail = 5401
    EMsgClientRequestForgottenPasswordEmailResponse = 5402
    EMsgClientCreateAccountResponse = 5403
    EMsgClientResetForgottenPassword = 5404
    EMsgClientResetForgottenPasswordResponse = 5405
    EMsgClientInformOfResetForgottenPassword = 5407
    EMsgClientInformOfResetForgottenPasswordResponse = 5408
    EMsgClientAnonUserLogOn_Deprecated = 5409
    EMsgClientGamesPlayedWithDataBlob = 5410
    EMsgClientUpdateUserGameInfo = 5411
    EMsgClientFileToDownload = 5412
    EMsgClientFileToDownloadResponse = 5413
    EMsgClientLBSSetScore = 5414
    EMsgClientLBSSetScoreResponse = 5415
    EMsgClientLBSFindOrCreateLB = 5416
    EMsgClientLBSFindOrCreateLBResponse = 5417
    EMsgClientLBSGetLBEntries = 5418
    EMsgClientLBSGetLBEntriesResponse = 5419
    EMsgClientChatDeclined = 5426
    EMsgClientFriendMsgIncoming = 5427
    EMsgClientAuthList_Deprecated = 5428
    EMsgClientTicketAuthComplete = 5429
    EMsgClientIsLimitedAccount = 5430
    EMsgClientRequestAuthList = 5431
    EMsgClientAuthList = 5432
    EMsgClientStat_Deprecated = 5433
    EMsgClientP2PConnectionInfo = 5434
    EMsgClientP2PConnectionFailInfo = 5435
    EMsgClientGetDepotDecryptionKey = 5438
    EMsgClientGetDepotDecryptionKeyResponse = 5439
    EMsgClientEnableTestLicense = 5443
    EMsgClientEnableTestLicenseResponse = 5444
    EMsgClientDisableTestLicense = 5445
    EMsgClientDisableTestLicenseResponse = 5446
    EMsgClientCheckAppBetaPassword = 5450
    EMsgClientCheckAppBetaPasswordResponse = 5451
    EMsgClientToGC = 5452
    EMsgClientFromGC = 5453
    EMsgClientEmailAddrInfo = 5456
    EMsgClientPasswordChange3 = 5457
    EMsgClientEmailChange3 = 5458
    EMsgClientPersonalQAChange3 = 5459
    EMsgClientResetForgottenPassword3 = 5460
    EMsgClientRequestForgottenPasswordEmail3 = 5461
    EMsgClientNewLoginKey = 5463
    EMsgClientNewLoginKeyAccepted_Deprecated = 5464
    EMsgClientLogOnWithHash_Deprecated = 5465
    EMsgClientStoreUserStats2 = 5466
    EMsgClientStatsUpdated = 5467
    EMsgClientRequestedClientStats_Deprecated = 5480
    EMsgClientStat2Int32_Deprecated = 5481
    EMsgClientStat2_Deprecated = 5482
    EMsgClientDRMDownloadRequest = 5485
    EMsgClientDRMDownloadResponse = 5486
    EMsgClientDRMFinalResult = 5487
    EMsgClientGetFriendsWhoPlayGame = 5488
    EMsgClientGetFriendsWhoPlayGameResponse = 5489
    EMsgClientOGSBeginSession = 5490
    EMsgClientOGSBeginSessionResponse = 5491
    EMsgClientOGSEndSession = 5492
    EMsgClientOGSEndSessionResponse = 5493
    EMsgClientOGSWriteRow = 5494
    EMsgClientGetPeerContentInfo = 5495
    EMsgClientGetPeerContentInfoResponse = 5496
    EMsgClientStartPeerContentServer = 5497
    EMsgClientStartPeerContentServerResponse = 5498
    EMsgClientServerUnavailable = 5500
    EMsgClientServersAvailable = 5501
    EMsgClientRegisterAuthTicketWithCM = 5502
    EMsgClientGCMsgFailed = 5503
    EMsgClientMicroTxnAuthRequest = 5504
    EMsgClientMicroTxnAuthorize = 5505
    EMsgClientMicroTxnAuthorizeResponse = 5506
    EMsgClientGetMicroTxnInfo = 5508
    EMsgClientGetMicroTxnInfoResponse = 5509
    EMsgClientDeregisterWithServer = 5511
    EMsgClientSubscribeToPersonaFeed = 5512
    EMsgClientLogon = 5514
    EMsgClientGetClientDetails = 5515
    EMsgClientGetClientDetailsResponse = 5516
    EMsgClientReportOverlayDetourFailure = 5517
    EMsgClientGetClientAppList = 5518
    EMsgClientGetClientAppListResponse = 5519
    EMsgClientInstallClientApp = 5520
    EMsgClientInstallClientAppResponse = 5521
    EMsgClientUninstallClientApp = 5522
    EMsgClientUninstallClientAppResponse = 5523
    EMsgClientSetClientAppUpdateState = 5524
    EMsgClientSetClientAppUpdateStateResponse = 5525
    EMsgClientRequestEncryptedAppTicket = 5526
    EMsgClientRequestEncryptedAppTicketResponse = 5527
    EMsgClientWalletInfoUpdate = 5528
    EMsgClientLBSSetUGC = 5529
    EMsgClientLBSSetUGCResponse = 5530
    EMsgClientAMGetClanOfficers = 5531
    EMsgClientAMGetClanOfficersResponse = 5532
    EMsgClientFriendProfileInfo = 5535
    EMsgClientFriendProfileInfoResponse = 5536
    EMsgClientScreenshotsChanged = 5543
    EMsgClientLaunchClientApp = 5544
    EMsgClientLaunchClientAppResponse = 5545
    EMsgClientRequestAccountData = 5549
    EMsgClientRequestAccountDataResponse = 5550
    EMsgClientResetForgottenPassword4 = 5551
    EMsgClientHideFriend = 5552
    EMsgClientFriendsGroupsList = 5553
    EMsgClientGetClanActivityCounts = 5554
    EMsgClientGetClanActivityCountsResponse = 5555
    EMsgClientOGSReportString = 5556
    EMsgClientOGSReportBug = 5557
    EMsgClientSentLogs = 5558
    EMsgClientLogonGameServer = 5559
    EMsgAMClientCreateFriendsGroup = 5560
    EMsgAMClientCreateFriendsGroupResponse = 5561
    EMsgAMClientDeleteFriendsGroup = 5562
    EMsgAMClientDeleteFriendsGroupResponse = 5563
    EMsgAMClientManageFriendsGroup = 5564
    EMsgAMClientManageFriendsGroupResponse = 5565
    EMsgAMClientAddFriendToGroup = 5566
    EMsgAMClientAddFriendToGroupResponse = 5567
    EMsgAMClientRemoveFriendFromGroup = 5568
    EMsgAMClientRemoveFriendFromGroupResponse = 5569
    EMsgClientAMGetPersonaNameHistory = 5570
    EMsgClientAMGetPersonaNameHistoryResponse = 5571
    EMsgClientRequestFreeLicense = 5572
    EMsgClientRequestFreeLicenseResponse = 5573
    EMsgClientDRMDownloadRequestWithCrashData = 5574
    EMsgClientAuthListAck = 5575
    EMsgClientItemAnnouncements = 5576
    EMsgClientRequestItemAnnouncements = 5577
    EMsgClientFriendMsgEchoToSender = 5578
    EMsgClientCommentNotifications = 5582
    EMsgClientRequestCommentNotifications = 5583
    EMsgClientPersonaChangeResponse = 5584
    EMsgClientRequestWebAPIAuthenticateUserNonce_Deprecated = 5585
    EMsgClientRequestWebAPIAuthenticateUserNonceResponse_Deprecated = 5586
    EMsgClientPlayerNicknameList = 5587
    EMsgAMClientSetPlayerNickname = 5588
    EMsgAMClientSetPlayerNicknameResponse = 5589
    EMsgClientGetNumberOfCurrentPlayersDP = 5592
    EMsgClientGetNumberOfCurrentPlayersDPResponse = 5593
    EMsgClientServiceMethodLegacy = 5594
    EMsgClientServiceMethodLegacyResponse = 5595
    EMsgClientFriendUserStatusPublished = 5596
    EMsgClientCurrentUIMode = 5597
    EMsgClientVanityURLChangedNotification = 5598
    EMsgClientUserNotifications = 5599
    EMsgBaseDFS = 5600
    EMsgDFSGetFile = 5601
    EMsgDFSInstallLocalFile = 5602
    EMsgDFSConnection = 5603
    EMsgDFSConnectionReply = 5604
    EMsgClientDFSAuthenticateRequest = 5605
    EMsgClientDFSAuthenticateResponse = 5606
    EMsgClientDFSEndSession = 5607
    EMsgDFSPurgeFile = 5608
    EMsgDFSRouteFile = 5609
    EMsgDFSGetFileFromServer = 5610
    EMsgDFSAcceptedResponse = 5611
    EMsgDFSRequestPingback = 5612
    EMsgDFSRecvTransmitFile = 5613
    EMsgDFSSendTransmitFile = 5614
    EMsgDFSRequestPingback2 = 5615
    EMsgDFSResponsePingback2 = 5616
    EMsgClientDFSDownloadStatus = 5617
    EMsgDFSStartTransfer = 5618
    EMsgDFSTransferComplete = 5619
    EMsgDFSRouteFileResponse = 5620
    EMsgClientNetworkingCertRequest = 5621
    EMsgClientNetworkingCertRequestResponse = 5622
    EMsgClientChallengeRequest = 5623
    EMsgClientChallengeResponse = 5624
    EMsgBadgeCraftedNotification = 5625
    EMsgClientNetworkingMobileCertRequest = 5626
    EMsgClientNetworkingMobileCertRequestResponse = 5627
    EMsgBaseMDS = 5800
    EMsgMDSGetDepotDecryptionKey = 5812
    EMsgMDSGetDepotDecryptionKeyResponse = 5813
    EMsgMDSContentServerConfigRequest = 5827
    EMsgMDSContentServerConfig = 5828
    EMsgMDSGetDepotManifest = 5829
    EMsgMDSGetDepotManifestResponse = 5830
    EMsgMDSGetDepotManifestChunk = 5831
    EMsgMDSToCSFlushChunk = 5844
    EMsgMDSMigrateChunk = 5847
    EMsgMDSMigrateChunkResponse = 5848
    EMsgMDSToCSFlushManifest = 5849
    EMsgCSBase = 6200
    EMsgCSPing = 6201
    EMsgCSPingResponse = 6202
    EMsgGMSBase = 6400
    EMsgGMSGameServerReplicate = 6401
    EMsgClientGMSServerQuery = 6403
    EMsgGMSClientServerQueryResponse = 6404
    EMsgAMGMSGameServerUpdate = 6405
    EMsgAMGMSGameServerRemove = 6406
    EMsgGameServerOutOfDate = 6407
    EMsgMMSBase = 6600
    EMsgClientMMSCreateLobby = 6601
    EMsgClientMMSCreateLobbyResponse = 6602
    EMsgClientMMSJoinLobby = 6603
    EMsgClientMMSJoinLobbyResponse = 6604
    EMsgClientMMSLeaveLobby = 6605
    EMsgClientMMSLeaveLobbyResponse = 6606
    EMsgClientMMSGetLobbyList = 6607
    EMsgClientMMSGetLobbyListResponse = 6608
    EMsgClientMMSSetLobbyData = 6609
    EMsgClientMMSSetLobbyDataResponse = 6610
    EMsgClientMMSGetLobbyData = 6611
    EMsgClientMMSLobbyData = 6612
    EMsgClientMMSSendLobbyChatMsg = 6613
    EMsgClientMMSLobbyChatMsg = 6614
    EMsgClientMMSSetLobbyOwner = 6615
    EMsgClientMMSSetLobbyOwnerResponse = 6616
    EMsgClientMMSSetLobbyGameServer = 6617
    EMsgClientMMSLobbyGameServerSet = 6618
    EMsgClientMMSUserJoinedLobby = 6619
    EMsgClientMMSUserLeftLobby = 6620
    EMsgClientMMSInviteToLobby = 6621
    EMsgClientMMSFlushFrenemyListCache = 6622
    EMsgClientMMSFlushFrenemyListCacheResponse = 6623
    EMsgClientMMSSetLobbyLinked = 6624
    EMsgClientMMSSetRatelimitPolicyOnClient = 6625
    EMsgClientMMSGetLobbyStatus = 6626
    EMsgClientMMSGetLobbyStatusResponse = 6627
    EMsgMMSGetLobbyList = 6628
    EMsgMMSGetLobbyListResponse = 6629
    EMsgMMSRoutingOverride = 6630
    EMsgGameServerPolicyUpdate = 6631
    EMsgNonStdMsgBase = 6800
    EMsgNonStdMsgMemcached = 6801
    EMsgNonStdMsgHTTPServer = 6802
    EMsgNonStdMsgHTTPClient = 6803
    EMsgNonStdMsgWGResponse = 6804
    EMsgNonStdMsgPHPSimulator = 6805
    EMsgNonStdMsgChase = 6806
    EMsgNonStdMsgDFSTransfer = 6807
    EMsgNonStdMsgTests = 6808
    EMsgNonStdMsgUMQpipeAAPL = 6809
    EMSgNonStdMsgSyslog = 6810
    EMsgNonStdMsgSteam2Emulator = 6812
    EMsgNonStdMsgRTMPServer = 6813
    EMsgNonStdMsgWebSocket = 6814
    EMsgNonStdMsgRedis = 6815
    EMsgUDSBase = 7000
    EMsgClientUDSP2PSessionStarted = 7001
    EMsgClientUDSP2PSessionEnded = 7002
    EMsgUDSRenderUserAuth = 7003
    EMsgUDSRenderUserAuthResponse = 7004
    EMsgClientInviteToGame = 7005
    EMsgUDSHasSession = 7006
    EMsgUDSHasSessionResponse = 7007
    EMsgMPASBase = 7100
    EMsgMPASVacBanReset = 7101
    EMsgKGSBase = 7200
    EMsgUCMBase = 7300
    EMsgClientUCMAddScreenshot = 7301
    EMsgClientUCMAddScreenshotResponse = 7302
    EMsgUCMResetCommunityContent = 7307
    EMsgUCMResetCommunityContentResponse = 7308
    EMsgClientUCMDeleteScreenshot = 7309
    EMsgClientUCMDeleteScreenshotResponse = 7310
    EMsgClientUCMPublishFile = 7311
    EMsgClientUCMPublishFileResponse = 7312
    EMsgClientUCMDeletePublishedFile = 7315
    EMsgClientUCMDeletePublishedFileResponse = 7316
    EMsgClientUCMUpdatePublishedFile = 7325
    EMsgClientUCMUpdatePublishedFileResponse = 7326
    EMsgUCMUpdatePublishedFile = 7327
    EMsgUCMUpdatePublishedFileResponse = 7328
    EMsgUCMUpdatePublishedFileStat = 7331
    EMsgUCMReloadPublishedFile = 7337
    EMsgUCMReloadUserFileListCaches = 7338
    EMsgUCMPublishedFileReported = 7339
    EMsgUCMPublishedFilePreviewAdd = 7341
    EMsgUCMPublishedFilePreviewAddResponse = 7342
    EMsgUCMPublishedFilePreviewRemove = 7343
    EMsgUCMPublishedFilePreviewRemoveResponse = 7344
    EMsgUCMPublishedFileSubscribed = 7349
    EMsgUCMPublishedFileUnsubscribed = 7350
    EMsgUCMPublishFile = 7351
    EMsgUCMPublishFileResponse = 7352
    EMsgUCMPublishedFileChildAdd = 7353
    EMsgUCMPublishedFileChildAddResponse = 7354
    EMsgUCMPublishedFileChildRemove = 7355
    EMsgUCMPublishedFileChildRemoveResponse = 7356
    EMsgUCMPublishedFileParentChanged = 7359
    EMsgClientUCMSetUserPublishedFileAction = 7364
    EMsgClientUCMSetUserPublishedFileActionResponse = 7365
    EMsgClientUCMEnumeratePublishedFilesByUserAction = 7366
    EMsgClientUCMEnumeratePublishedFilesByUserActionResponse = 7367
    EMsgUCMGetUserSubscribedFiles = 7369
    EMsgUCMGetUserSubscribedFilesResponse = 7370
    EMsgUCMFixStatsPublishedFile = 7371
    EMsgClientUCMEnumerateUserSubscribedFilesWithUpdates = 7378
    EMsgClientUCMEnumerateUserSubscribedFilesWithUpdatesResponse = 7379
    EMsgUCMPublishedFileContentUpdated = 7380
    EMsgClientUCMPublishedFileUpdated = 7381
    EMsgFSBase = 7500
    EMsgClientRichPresenceUpload = 7501
    EMsgClientRichPresenceRequest = 7502
    EMsgClientRichPresenceInfo = 7503
    EMsgFSRichPresenceRequest = 7504
    EMsgFSRichPresenceResponse = 7505
    EMsgFSComputeFrenematrix = 7506
    EMsgFSComputeFrenematrixResponse = 7507
    EMsgFSPlayStatusNotification = 7508
    EMsgFSAddOrRemoveFollower = 7510
    EMsgFSAddOrRemoveFollowerResponse = 7511
    EMsgFSUpdateFollowingList = 7512
    EMsgFSCommentNotification = 7513
    EMsgFSCommentNotificationViewed = 7514
    EMsgClientFSGetFollowerCount = 7515
    EMsgClientFSGetFollowerCountResponse = 7516
    EMsgClientFSGetIsFollowing = 7517
    EMsgClientFSGetIsFollowingResponse = 7518
    EMsgClientFSEnumerateFollowingList = 7519
    EMsgClientFSEnumerateFollowingListResponse = 7520
    EMsgFSGetPendingNotificationCount = 7521
    EMsgFSGetPendingNotificationCountResponse = 7522
    EMsgClientChatOfflineMessageNotification = 7523
    EMsgClientChatRequestOfflineMessageCount = 7524
    EMsgClientChatGetFriendMessageHistory = 7525
    EMsgClientChatGetFriendMessageHistoryResponse = 7526
    EMsgClientChatGetFriendMessageHistoryForOfflineMessages = 7527
    EMsgClientFSGetFriendsSteamLevels = 7528
    EMsgClientFSGetFriendsSteamLevelsResponse = 7529
    EMsgAMRequestFriendData = 7530
    EMsgDRMRange2 = 7600
    EMsgCEGVersionSetEnableDisableRequest = 7600
    EMsgCEGVersionSetEnableDisableResponse = 7601
    EMsgCEGPropStatusDRMSRequest = 7602
    EMsgCEGPropStatusDRMSResponse = 7603
    EMsgCEGWhackFailureReportRequest = 7604
    EMsgCEGWhackFailureReportResponse = 7605
    EMsgDRMSFetchVersionSet = 7606
    EMsgDRMSFetchVersionSetResponse = 7607
    EMsgEconBase = 7700
    EMsgEconTrading_InitiateTradeRequest = 7701
    EMsgEconTrading_InitiateTradeProposed = 7702
    EMsgEconTrading_InitiateTradeResponse = 7703
    EMsgEconTrading_InitiateTradeResult = 7704
    EMsgEconTrading_StartSession = 7705
    EMsgEconTrading_CancelTradeRequest = 7706
    EMsgEconFlushInventoryCache = 7707
    EMsgEconFlushInventoryCacheResponse = 7708
    EMsgEconCDKeyProcessTransaction = 7711
    EMsgEconCDKeyProcessTransactionResponse = 7712
    EMsgEconGetErrorLogs = 7713
    EMsgEconGetErrorLogsResponse = 7714
    EMsgRMRange = 7800
    EMsgRMTestVerisignOTP = 7800
    EMsgRMTestVerisignOTPResponse = 7801
    EMsgRMDeleteMemcachedKeys = 7803
    EMsgRMRemoteInvoke = 7804
    EMsgBadLoginIPList = 7805
    EMsgRMMsgTraceAddOrUpdateTrigger = 7806
    EMsgRMMsgTraceRemoveTriggers = 7807
    EMsgRMMsgTraceEvent = 7808
    EMsgUGSBase = 7900
    EMsgUGSUpdateGlobalStats = 7900
    EMsgClientUGSGetGlobalStats = 7901
    EMsgClientUGSGetGlobalStatsResponse = 7902
    EMsgStoreBase = 8000
    EMsgUMQBase = 8100
    EMsgWorkshopBase = 8200
    EMsgWebAPIBase = 8300
    EMsgWebAPIValidateOAuth2Token = 8300
    EMsgWebAPIValidateOAuth2TokenResponse = 8301
    EMsgWebAPIRegisterGCInterfaces = 8303
    EMsgWebAPIInvalidateOAuthClientCache = 8304
    EMsgWebAPIInvalidateOAuthTokenCache = 8305
    EMsgWebAPISetSecrets = 8306
    EMsgBackpackBase = 8400
    EMsgBackpackAddToCurrency = 8401
    EMsgBackpackAddToCurrencyResponse = 8402
    EMsgCREBase = 8500
    EMsgCREItemVoteSummary = 8503
    EMsgCREItemVoteSummaryResponse = 8504
    EMsgCREUpdateUserPublishedItemVote = 8507
    EMsgCREUpdateUserPublishedItemVoteResponse = 8508
    EMsgCREGetUserPublishedItemVoteDetails = 8509
    EMsgCREGetUserPublishedItemVoteDetailsResponse = 8510
    EMsgSecretsBase = 8600
    EMsgSecretsRequestCredentialPair = 8600
    EMsgSecretsCredentialPairResponse = 8601
    EMsgBoxMonitorBase = 8700
    EMsgBoxMonitorReportRequest = 8700
    EMsgBoxMonitorReportResponse = 8701
    EMsgPICSBase = 8900
    EMsgClientPICSChangesSinceRequest = 8901
    EMsgClientPICSChangesSinceResponse = 8902
    EMsgClientPICSProductInfoRequest = 8903
    EMsgClientPICSProductInfoResponse = 8904
    EMsgClientPICSAccessTokenRequest = 8905
    EMsgClientPICSAccessTokenResponse = 8906
    EMsgClientPICSPrivateBetaRequest = 8907
    EMsgClientPICSPrivateBetaResponse = 8908
    EMsgWorkerProcess = 9000
    EMsgWorkerProcessPingRequest = 9000
    EMsgWorkerProcessPingResponse = 9001
    EMsgWorkerProcessShutdown = 9002
    EMsgDRMWorkerProcess = 9100
    EMsgDRMWorkerProcessDRMAndSign = 9100
    EMsgDRMWorkerProcessDRMAndSignResponse = 9101
    EMsgDRMWorkerProcessSteamworksInfoRequest = 9102
    EMsgDRMWorkerProcessSteamworksInfoResponse = 9103
    EMsgDRMWorkerProcessInstallDRMDLLRequest = 9104
    EMsgDRMWorkerProcessInstallDRMDLLResponse = 9105
    EMsgDRMWorkerProcessSecretIdStringRequest = 9106
    EMsgDRMWorkerProcessSecretIdStringResponse = 9107
    EMsgDRMWorkerProcessInstallProcessedFilesRequest = 9110
    EMsgDRMWorkerProcessInstallProcessedFilesResponse = 9111
    EMsgDRMWorkerProcessExamineBlobRequest = 9112
    EMsgDRMWorkerProcessExamineBlobResponse = 9113
    EMsgDRMWorkerProcessDescribeSecretRequest = 9114
    EMsgDRMWorkerProcessDescribeSecretResponse = 9115
    EMsgDRMWorkerProcessBackfillOriginalRequest = 9116
    EMsgDRMWorkerProcessBackfillOriginalResponse = 9117
    EMsgDRMWorkerProcessValidateDRMDLLRequest = 9118
    EMsgDRMWorkerProcessValidateDRMDLLResponse = 9119
    EMsgDRMWorkerProcessValidateFileRequest = 9120
    EMsgDRMWorkerProcessValidateFileResponse = 9121
    EMsgDRMWorkerProcessSplitAndInstallRequest = 9122
    EMsgDRMWorkerProcessSplitAndInstallResponse = 9123
    EMsgDRMWorkerProcessGetBlobRequest = 9124
    EMsgDRMWorkerProcessGetBlobResponse = 9125
    EMsgDRMWorkerProcessEvaluateCrashRequest = 9126
    EMsgDRMWorkerProcessEvaluateCrashResponse = 9127
    EMsgDRMWorkerProcessAnalyzeFileRequest = 9128
    EMsgDRMWorkerProcessAnalyzeFileResponse = 9129
    EMsgDRMWorkerProcessUnpackBlobRequest = 9130
    EMsgDRMWorkerProcessUnpackBlobResponse = 9131
    EMsgDRMWorkerProcessInstallAllRequest = 9132
    EMsgDRMWorkerProcessInstallAllResponse = 9133
    EMsgDRMWorkerProcessSignFile = 9134
    EMsgDRMWorkerProcessSignFileResponse = 9135
    EMsgTestWorkerProcess = 9200
    EMsgTestWorkerProcessLoadUnloadModuleRequest = 9200
    EMsgTestWorkerProcessLoadUnloadModuleResponse = 9201
    EMsgTestWorkerProcessServiceModuleCallRequest = 9202
    EMsgTestWorkerProcessServiceModuleCallResponse = 9203
    EMsgQuestServerBase = 9300
    EMsgClientGetEmoticonList = 9330
    EMsgClientEmoticonList = 9331
    EMsgSLCBase = 9400
    EMsgClientSharedLibraryStopPlaying = 9406
    EMsgRemoteClientBase = 9500
    EMsgRemoteClientAuth_OBSOLETE = 9500
    EMsgRemoteClientAuthResponse_OBSOLETE = 9501
    EMsgRemoteClientAppStatus = 9502
    EMsgRemoteClientStartStream = 9503
    EMsgRemoteClientStartStreamResponse = 9504
    EMsgRemoteClientPing = 9505
    EMsgRemoteClientPingResponse = 9506
    EMsgClientUnlockH264 = 9507
    EMsgClientUnlockH264Response = 9508
    EMsgRemoteClientAcceptEULA = 9509
    EMsgRemoteClientGetControllerConfig = 9510
    EMsgRemoteClientGetControllerConfigResponse = 9511
    EMsgRemoteClientStreamingEnabled = 9512
    EMsgClientUnlockHEVC_OBSOLETE = 9513
    EMsgClientUnlockHEVCResponse_OBSOLETE = 9514
    EMsgRemoteClientStatusRequest = 9515
    EMsgRemoteClientStatusResponse = 9516
    EMsgRemoteClientAuthorizationRequest = 9517
    EMsgRemoteClientAuthorizationResponse = 9518
    EMsgRemoteClientAuthorizationCancelRequest = 9519
    EMsgRemoteClientAuthorizationConfirmed = 9520
    EMsgRemoteClientProofRequest = 9521
    EMsgRemoteClientProofResponse = 9522
    EMsgRemoteClientWifiAPStatus = 9523
    EMsgRemoteClientPairWifiAP = 9524
    EMsgRemoteClientPairWifiAPResponse = 9525
    EMsgRemoteClientDownloadScheduleChanged = 9526
    EMsgRemoteClientDownloadItemScheduleChanged = 9527
    EMsgRemoteClientAppUpdateStopped = 9528
    EMsgRemoteClientAppDownloadStats = 9529
    EMsgRemoteClientAppUploadStats = 9530
    EMsgRemoteClientAppInfoUpdateComplete = 9531
    eMsgRemoteClientDownloadsManagement = 9532
    eMsgRemoteClientDownloadingAppID = 9533
    eMsgRemoteClientPeerContentServerChanged = 9534
    eMsgRemoteClientRestrictAutoUpdatesChanged = 9535
    eMsgRemoteClientSuspendLanPeerContent = 9536
    eMsgRemoteClientUpdateDownloadsController = 9537
    EMsgRemoteClientAcceptAllEULAs = 9538
    EMsgClientConcurrentSessionsBase = 9600
    EMsgClientPlayingSessionState = 9600
    EMsgClientKickPlayingSession = 9601
    EMsgClientBroadcastBase = 9700
    EMsgClientBroadcastInit = 9700
    EMsgClientBroadcastFrames = 9701
    EMsgClientBroadcastDisconnect = 9702
    EMsgClientBroadcastUploadConfig = 9704
    EMsgBaseClient3 = 9800
    EMsgClientVoiceCallPreAuthorize = 9800
    EMsgClientVoiceCallPreAuthorizeResponse = 9801
    EMsgClientServerTimestampRequest = 9802
    EMsgClientServerTimestampResponse = 9803
    EMsgServiceMethodCallFromClientNonAuthed = 9804
    EMsgClientHello = 9805
    EMsgClientEnableOrDisableDownloads = 9806
    EMsgClientEnableOrDisableDownloadsResponse = 9807
    EMsgClientFeatureGroupInfo = 9808
    EMsgClientLANP2PBase = 9900
    EMsgClientLANP2PRequestChunk = 9900
    EMsgClientLANP2PRequestChunkResponse = 9901
    EMsgClientPeerChunkRequest = 9902
    EMsgClientPeerChunkResponse = 9903
    EMsgClientLANP2PMax = 9999
    EMsgBaseWatchdogServer = 10000
    EMsgNotifyWatchdog = 10000
    EMsgClientSiteLicenseBase = 10100
    EMsgClientSiteLicenseSiteInfoNotification = 10100
    EMsgClientSiteLicenseCheckout = 10101
    EMsgClientSiteLicenseCheckoutResponse = 10102
    EMsgClientSiteLicenseGetAvailableSeats = 10103
    EMsgClientSiteLicenseGetAvailableSeatsResponse = 10104
    EMsgClientSiteLicenseGetContentCacheInfo = 10105
    EMsgClientSiteLicenseGetContentCacheInfoResponse = 10106
    EMsgBaseChatServer = 12000
    EMsgChatServerGetPendingNotificationCount = 12000
    EMsgChatServerGetPendingNotificationCountResponse = 12001
    EMsgBaseSecretServer = 12100
    EMsgServerSecretChanged = 12100
    EMsgBaseWG = 12200
    EMsgWGConnectionProtocolError = 12200
    EMsgWGConnectionValidateUserToken = 12201
    EMsgWGConnectionValidateUserTokenResponse = 12202
    EMsgWGConnectionLegacyWGRequest = 12203
    EMsgWGConnectionLegacyWGResponse = 12204
    EMsgClientPendingGameLaunch = 12300
    EMsgClientPendingGameLaunchResponse = 12301

class EMsgClanAccountFlags(SteamIntEnum):
    EMsgClanAccountFlagPublic = 1
    EMsgClanAccountFlagLarge = 2
    EMsgClanAccountFlagLocked = 4
    EMsgClanAccountFlagDisabled = 8
    EMsgClanAccountFlagOGG = 16

class ENewSteamAnnouncementState(SteamIntEnum):
    Invalid = 0
    AllRead = 1
    NewAnnouncement = 2
    FeaturedAnnouncement = 3

class ENotificationSetting(SteamIntEnum):
    ENotificationSettingNotifyUseDefault = 0
    ENotificationSettingAlways = 1
    ENotificationSettingNever = 2

class EOSBranch(SteamIntEnum):
    Unknown = 0
    Release = 1
    ReleaseCandidate = 2
    Beta = 3
    BetaCandidate = 4
    Preview = 5
    PreviewCandidate = 6
    Main = 7
    Staging = 8

class EOverlayToggleBarLocation(SteamIntEnum):
    Bottom = 0
    Left = 1
    Right = 2
    Top = 3

class EPartnerEventDisplayLocation(SteamIntEnum):
    Invalid = 0
    AppDetailsSpotlight = 1
    LibraryOverview = 2
    StoreAppPage = 3
    EventScroller = 4
    AppDetailsActivity = 5
    CommunityHub = 6
    StoreFrontPage = 7
    NewsHub = 8
    GamepadHome = 9
    StoreHub = 10

EPartnerLinkTrackingBackfillSource = SteamIntEnum('EPartnerLinkTrackingBackfillSource', {
    'None': 0,
    'Web': 1,
    'Mobile': 2,
    'Desktop': 3,
    })

class EPhaseResultType(SteamIntEnum):
    Automatic = 1
    Blank = 2
    API = 3

class EPlaytestStatus(SteamIntEnum):
    ETesterStatusNone = 0
    ETesterStatusPending = 1
    ETesterStatusInvited = 2
    ETesterStatusGranted = 3
    ETesterStatusExpired = 4

class EPressOutletAction(SteamIntEnum):
    Invalid = 0
    Granted = 1
    Removed = 2
    Created = 3
    Updated = 4
    Deleted = 5
    Undeleted = 6
    StagedAdd = 7
    StagedDelete = 8
    EnterStaging = 9
    ExitStaging = 10
    ReverseStagedAdd = 11
    ReverseStagedDelete = 12
    MAX = 13

class EPressOutletMemberPendingState(SteamIntEnum):
    Member = 0
    StagedDelete = 1
    StagedAdd = 2
    MAX = 3

class EProfileCustomizationStyle(SteamIntEnum):
    EProfileCustomizationStyleDefault = 0
    EProfileCustomizationStyleSelected = 1
    EProfileCustomizationStyleRarest = 2
    EProfileCustomizationStyleMostRecent = 3
    EProfileCustomizationStyleRandom = 4
    EProfileCustomizationStyleHighestRated = 5

class EProfileCustomizationType(SteamIntEnum):
    EProfileCustomizationTypeInvalid = 0
    EProfileCustomizationTypeRareAchievementShowcase = 1
    EProfileCustomizationTypeGameCollector = 2
    EProfileCustomizationTypeItemShowcase = 3
    EProfileCustomizationTypeTradeShowcase = 4
    EProfileCustomizationTypeBadges = 5
    EProfileCustomizationTypeFavoriteGame = 6
    EProfileCustomizationTypeScreenshotShowcase = 7
    EProfileCustomizationTypeCustomText = 8
    EProfileCustomizationTypeFavoriteGroup = 9
    EProfileCustomizationTypeRecommendation = 10
    EProfileCustomizationTypeWorkshopItem = 11
    EProfileCustomizationTypeMyWorkshop = 12
    EProfileCustomizationTypeArtworkShowcase = 13
    EProfileCustomizationTypeVideoShowcase = 14
    EProfileCustomizationTypeGuides = 15
    EProfileCustomizationTypeMyGuides = 16
    EProfileCustomizationTypeAchievements = 17
    EProfileCustomizationTypeGreenlight = 18
    EProfileCustomizationTypeMyGreenlight = 19
    EProfileCustomizationTypeSalien = 20
    EProfileCustomizationTypeLoyaltyRewardReactions = 21
    EProfileCustomizationTypeSingleArtworkShowcase = 22
    EProfileCustomizationTypeAchievementsCompletionist = 23
    EProfileCustomizationTypeReplay = 24

class EProtoClanEventType(SteamIntEnum):
    EClanOtherEvent = 1
    EClanGameEvent = 2
    EClanPartyEvent = 3
    EClanMeetingEvent = 4
    EClanSpecialCauseEvent = 5
    EClanMusicAndArtsEvent = 6
    EClanSportsEvent = 7
    EClanTripEvent = 8
    EClanChatEvent = 9
    EClanGameReleaseEvent = 10
    EClanBroadcastEvent = 11
    EClanSmallUpdateEvent = 12
    EClanPreAnnounceMajorUpdateEvent = 13
    EClanMajorUpdateEvent = 14
    EClanDLCReleaseEvent = 15
    EClanFutureReleaseEvent = 16
    EClanESportTournamentStreamEvent = 17
    EClanDevStreamEvent = 18
    EClanFamousStreamEvent = 19
    EClanGameSalesEvent = 20
    EClanGameItemSalesEvent = 21
    EClanInGameBonusXPEvent = 22
    EClanInGameLootEvent = 23
    EClanInGamePerksEvent = 24
    EClanInGameChallengeEvent = 25
    EClanInGameContestEvent = 26
    EClanIRLEvent = 27
    EClanNewsEvent = 28
    EClanBetaReleaseEvent = 29
    EClanInGameContentReleaseEvent = 30
    EClanFreeTrial = 31
    EClanSeasonRelease = 32
    EClanSeasonUpdate = 33
    EClanCrosspostEvent = 34
    EClanInGameEventGeneral = 35
    EClanCreatorHome = 36

class EProtoExecutionSite(SteamIntEnum):
    EProtoExecutionSiteUnknown = 0
    EProtoExecutionSiteSteamClient = 2

class EProtoServiceType(SteamIntEnum):
    EProtoServiceTypeSteamMessages = 0
    EProtoServiceTypeVRGamepadUIMessages = 1

class EProvideDeckFeedbackPreference(SteamIntEnum):
    Unset = 0
    Yes = 1
    No = 2

class EPublishedFileForSaleStatus(SteamIntEnum):
    PFFSS_NotForSale = 0
    PFFSS_PendingApproval = 1
    PFFSS_ApprovedForSale = 2
    PFFSS_RejectedForSale = 3
    PFFSS_NoLongerForSale = 4
    PFFSS_TentativeApproval = 5

class EPublishedFileRevision(SteamIntEnum):
    Default = 0
    Latest = 1
    ApprovedSnapshot = 2
    ApprovedSnapshot_China = 3
    RejectedSnapshot = 4
    RejectedSnapshot_China = 5
    AuthorSnapshot = 6

class EPublishedFileStorageSystem(SteamIntEnum):
    EPublishedFileStorageSystemInvalid = 0
    EPublishedFileStorageSystemLegacyCloud = 1
    EPublishedFileStorageSystemDepot = 2
    EPublishedFileStorageSystemUGCCloud = 3

EPurchaseRequestAction = SteamIntEnum('EPurchaseRequestAction', {
    'None': 0,
    'Decline': 1,
    'Purchased': 2,
    'Abandoned': 3,
    'Cancel': 4,
    'MAX': 5,
    })

class EQueryFilesSearchTextTarget(SteamIntEnum):
    AllText = 0
    Title = 1
    Description = 2

EQueryFilesSpecialFilter = SteamIntEnum('EQueryFilesSpecialFilter', {
    'None': 0,
    'AcceptedForUse': 1,
    'FavoritedByFriends': 2,
    'CreateByFriends': 3,
    'CreatedByFollowed': 4,
    'Reported': 5,
    'ParentItems': 6,
    'ParentCollections': 7,
    })

class ERatingAgency(SteamIntEnum):
    Invalid = 0
    ESRB = 1
    PEGI = 2
    BBFC = 3
    USK = 4
    OFLC_AU = 5
    OFLC_NZ = 6
    CERO = 7
    GRAC = 8
    GMEDIA = 9
    DEJUS = 10
    IMDA = 11
    FPB = 12
    TESRI = 13
    RARS = 14
    AGCOM = 15
    IGRS = 16
    Steam_Germany = 17
    Steam_Australia = 18

class ERecordingSessionChangeNotificationType(SteamIntEnum):
    Started = 1
    Stopped = 2
    Deleted = 3
    Updated = 4

class ERemoteClientBroadcastMsg(SteamIntEnum):
    ERemoteClientBroadcastMsgDiscovery = 0
    ERemoteClientBroadcastMsgStatus = 1
    ERemoteClientBroadcastMsgOffline = 2
    ERemoteDeviceAuthorizationRequest = 3
    ERemoteDeviceAuthorizationResponse = 4
    ERemoteDeviceStreamingRequest = 5
    ERemoteDeviceStreamingResponse = 6
    ERemoteDeviceProofRequest = 7
    ERemoteDeviceProofResponse = 8
    ERemoteDeviceAuthorizationCancelRequest = 9
    ERemoteDeviceStreamingCancelRequest = 10
    ERemoteClientBroadcastMsgClientIDDeconflict = 11
    ERemoteDeviceStreamTransportSignal = 12
    ERemoteDeviceStreamingProgress = 13
    ERemoteDeviceAuthorizationConfirmed = 14
    ERemoteClientBroadcastMsgPairingState = 15
    ERemoteClientBroadcastMsgPairingExclusivity = 16

class ERemoteClientPairWifiAPResult(SteamIntEnum):
    ERemoteClientPairWifiAPOK = 1
    ERemoteClientPairWifiAPFail = 2
    ERemoteClientPairWifiAPNetworkError = 3
    ERemoteClientPairWifiAPUnauthorized = 4
    ERemoteClientPairWifiAPNoDonglePresent = 5
    ERemoteClientPairWifiAPTimeout = 6
    ERemoteClientPairWifiAPCanceled = 7

class ERemoteClientService(SteamIntEnum):
    ERemoteClientServiceNone = 0
    ERemoteClientServiceRemoteControl = 1
    ERemoteClientServiceGameStreaming = 2
    ERemoteClientServiceSiteLicense = 4
    ERemoteClientServiceContentCache = 8
    ERemoteClientServiceContentServer = 16
    ERemoteClientServiceManageDownloads = 32

class ERemoteDeviceAuthorizationResult(SteamIntEnum):
    ERemoteDeviceAuthorizationSuccess = 0
    ERemoteDeviceAuthorizationDenied = 1
    ERemoteDeviceAuthorizationNotLoggedIn = 2
    ERemoteDeviceAuthorizationOffline = 3
    ERemoteDeviceAuthorizationBusy = 4
    ERemoteDeviceAuthorizationInProgress = 5
    ERemoteDeviceAuthorizationTimedOut = 6
    ERemoteDeviceAuthorizationFailed = 7
    ERemoteDeviceAuthorizationCanceled = 8

class ERemoteDeviceStreamingResult(SteamIntEnum):
    ERemoteDeviceStreamingSuccess = 0
    ERemoteDeviceStreamingUnauthorized = 1
    ERemoteDeviceStreamingScreenLocked = 2
    ERemoteDeviceStreamingFailed = 3
    ERemoteDeviceStreamingBusy = 4
    ERemoteDeviceStreamingInProgress = 5
    ERemoteDeviceStreamingCanceled = 6
    ERemoteDeviceStreamingDriversNotInstalled = 7
    ERemoteDeviceStreamingDisabled = 8
    ERemoteDeviceStreamingBroadcastingActive = 9
    ERemoteDeviceStreamingVRActive = 10
    ERemoteDeviceStreamingPINRequired = 11
    ERemoteDeviceStreamingTransportUnavailable = 12
    ERemoteDeviceStreamingInvisible = 13
    ERemoteDeviceStreamingGameLaunchFailed = 14
    ERemoteDeviceStreamingSteamVRNotInstalled = 15

class EResolutionAutomation(SteamIntEnum):
    Manual = 0
    PartiallyAutomated = 1
    FullyAutomated = 2
    MAX = 3

class ESDCardFormatStage(SteamIntEnum):
    Invalid = 0
    Starting = 1
    Testing = 2
    Rescuing = 3
    Formatting = 4
    Finalizing = 5

class ESessionPersistence(SteamIntEnum):
    Invalid = -1
    Ephemeral = 0
    Persistent = 1

ESettingProfileMode = SteamIntEnum('ESettingProfileMode', {
    'None': 0,
    'PerGame': 1,
    'PerGamePerDisplay': 2,
    'PerDisplay': 3,
    })

class ESharedLibraryExcludeReason(SteamIntEnum):
    ESharedLibrary_Included = 0
    ESharedLibrary_AppExcluded_ByPartner = 1
    ESharedLibrary_LicenseExcluded = 2
    ESharedLibrary_FreeGame = 3
    ESharedLibrary_LicensePrivate = 4
    ESharedLibrary_AppExcluded_WrongAppType = 6
    ESharedLibrary_AppExcluded_NonrefundableDLC = 7
    ESharedLibrary_AppExcluded_UnreleasedApp = 8
    ESharedLibrary_AppExcluded_ParentAppExcluded = 9
    ESharedLibrary_PackageExcluded_ByPartner = 10
    ESharedLibrary_PackageExcluded_Special = 11
    ESharedLibrary_PackageExcluded_Dev = 12
    ESharedLibrary_PackageExcluded_FreeWeekend = 13
    ESharedLibrary_PackageExcluded_Invalid = 15
    ESharedLibrary_PackageExcluded_RecurringLicense = 16
    ESharedLibrary_PackageExcluded_WrongLicenseType = 17
    ESharedLibrary_PackageExcluded_MasterSub = 18
    ESharedLibrary_PackageExcluded_NoShareableApps = 19
    ESharedLibrary_LicenseExcluded_PaymentMasterSub = 20
    ESharedLibrary_LicenseExcluded_PaymentFamilyGroup = 21
    ESharedLibrary_LicenseExcluded_PaymentAuthorizedDevice = 22
    ESharedLibrary_LicenseExcluded_PaymentAutoGrant = 23
    ESharedLibrary_LicenseExcluded_FlagPending = 24
    ESharedLibrary_LicenseExcluded_FlagPendingRefund = 25
    ESharedLibrary_LicenseExcluded_FlagBorrowed = 26
    ESharedLibrary_LicenseExcluded_FlagAutoGrant = 27
    ESharedLibrary_LicenseExcluded_FlagTimedTrial = 28
    ESharedLibrary_LicenseExcluded_FreeSub = 29
    ESharedLibrary_LicenseExcluded_Inactive = 30

class ESLSHelper(SteamIntEnum):
    Invalid = 0
    Minidump = 1
    Kdump = 2
    Journal = 3
    Gpu = 4
    SystemInfo = 5
    Devcoredump = 6

ESpeakerConfiguration = SteamIntEnum('ESpeakerConfiguration', {
    'Other': 0,
    'Stereo': 1,
    '51': 2,
    '71': 3,
    '51_Ac3': 4,
    })

class ESplitScalingFilter(SteamIntEnum):
    Invalid = 0
    Linear = 1
    Nearest = 2
    Sharp = 3
    NIS_Deprecated = 4

class ESplitScalingScaler(SteamIntEnum):
    Invalid = 0
    Auto = 1
    Integer = 2
    Fit = 3
    Fill = 4
    Stretch = 5

class ESteamDatagramMsgID(SteamIntEnum):
    ESteamDatagramMsg_Invalid = 0
    ESteamDatagramMsg_RouterPingRequest = 1
    ESteamDatagramMsg_RouterPingReply = 2
    ESteamDatagramMsg_GameserverPingRequest = 3
    ESteamDatagramMsg_GameserverSessionRequest = 5
    ESteamDatagramMsg_GameserverSessionEstablished = 6
    ESteamDatagramMsg_NoSession = 7
    ESteamDatagramMsg_Diagnostic = 8
    ESteamDatagramMsg_DataClientToRouter = 9
    ESteamDatagramMsg_DataRouterToServer = 10
    ESteamDatagramMsg_DataServerToRouter = 11
    ESteamDatagramMsg_DataRouterToClient = 12
    ESteamDatagramMsg_Stats = 13
    ESteamDatagramMsg_ClientPingSampleRequest = 14
    ESteamDatagramMsg_ClientPingSampleReply = 15
    ESteamDatagramMsg_ClientToRouterSwitchedPrimary = 16
    ESteamDatagramMsg_RelayHealth = 17
    ESteamDatagramMsg_ConnectRequest = 18
    ESteamDatagramMsg_ConnectOK = 19
    ESteamDatagramMsg_ConnectionClosed = 20
    ESteamDatagramMsg_NoConnection = 21
    ESteamDatagramMsg_TicketDecryptRequest = 22
    ESteamDatagramMsg_TicketDecryptReply = 23
    ESteamDatagramMsg_P2PSessionRequest = 24
    ESteamDatagramMsg_P2PSessionEstablished = 25
    ESteamDatagramMsg_P2PStatsClient = 26
    ESteamDatagramMsg_P2PStatsRelay = 27
    ESteamDatagramMsg_P2PBadRoute = 28
    ESteamDatagramMsg_GameserverPingReply = 29
    ESteamDatagramMsg_LegacyGameserverRegistration = 30
    ESteamDatagramMsg_SetSecondaryAddressRequest = 31
    ESteamDatagramMsg_SetSecondaryAddressResult = 32
    ESteamDatagramMsg_RelayToRelayPingRequest = 33
    ESteamDatagramMsg_RelayToRelayPingReply = 34

class ESteamDeckCompatibilityCategory(SteamIntEnum):
    Unknown = 0
    Unsupported = 1
    Playable = 2
    Verified = 3

class ESteamDeckCompatibilityFeedback(SteamIntEnum):
    Unset = 0
    Agree = 1
    Disagree = 2
    Ignore = 3

class ESteamDeckCompatibilityResultDisplayType(SteamIntEnum):
    Invisible = 0
    Informational = 1
    Unsupported = 2
    Playable = 3
    Verified = 4

class ESteamDeckCompatibilityTestResult(SteamIntEnum):
    Invalid = 0
    NotApplicable = 1
    Pass = 2
    Fail = 3
    FailMinor = 4

class ESteamDeckKeyboardLayout(SteamIntEnum):
    QWERTY = 0
    Bulgarian = 1
    Chinese_Simplified = 2
    Chinese_Traditional = 3
    Czech = 4
    Danish = 5
    Finnish = 6
    French = 7
    German = 8
    Greek = 9
    Hungarian = 10
    Italian = 11
    Japanese = 12
    Korean = 13
    Norwegian = 14
    Polish = 15
    Portuguese = 16
    Romanian = 17
    Russian = 18
    Spanish = 19
    Swedish = 20
    Thai = 21
    Turkish_F = 22
    Turkish_Q = 23
    Ukrainian = 24
    Vietnamese = 25
    QWERTY_International = 26
    Dvorak = 27
    Colemak = 28
    Bulgarian_Phonetic_Traditional = 29
    Bulgarian_Phonetic = 30
    Chinese_Traditional_Bopomofo = 31
    Chinese_Traditional_Cangjie = 32
    Japanese_Kana = 33
    Chinese_Traditional_Quick = 34
    Indonesian = 35

class ESteamNetworkingSocketsCipher(SteamIntEnum):
    INVALID = 0
    NULL = 1
    AES_256_GCM = 2

class ESteamNetworkingUDPMsgID(SteamIntEnum):
    ESteamNetworkingUDPMsg_ChallengeRequest = 32
    ESteamNetworkingUDPMsg_ChallengeReply = 33
    ESteamNetworkingUDPMsg_ConnectRequest = 34
    ESteamNetworkingUDPMsg_ConnectOK = 35
    ESteamNetworkingUDPMsg_ConnectionClosed = 36
    ESteamNetworkingUDPMsg_NoConnection = 37

ESteamNotificationType = SteamIntEnum('ESteamNotificationType', {
    'Invalid': 0,
    'Test': 1,
    'Gift': 2,
    'Comment': 3,
    'Item': 4,
    'FriendInvite': 5,
    'MajorSale': 6,
    'PreloadAvailable': 7,
    'Wishlist': 8,
    'TradeOffer': 9,
    'General': 10,
    'HelpRequest': 11,
    'AsyncGame': 12,
    'ChatMsg': 13,
    'ModeratorMsg': 14,
    'ParentalFeatureAccessRequest': 15,
    'FamilyInvite': 16,
    'FamilyPurchaseRequest': 17,
    'ParentalPlaytimeRequest': 18,
    'FamilyPurchaseRequestResponse': 19,
    'ParentalFeatureAccessResponse': 20,
    'ParentalPlaytimeResponse': 21,
    'RequestedGameAdded': 22,
    'SendToPhone': 23,
    'ClipDownloaded': 24,
    '2FAPrompt': 25,
    'MobileConfirmation': 26,
    'PartnerEvent': 27,
    'PlaytestInvite': 28,
    'TradeReversal': 29,
    'ReportedContentAction': 30,
    })

class ESteamOSCompatibilityCategory(SteamIntEnum):
    Unknown = 0
    Unsupported = 1
    Compatible = 2

class ESteamOSCompatibilityResultDisplayType(SteamIntEnum):
    Invisible = 0
    Informational = 1
    Unsupported = 2
    Compatible = 3

class ESteamPipeOperationType(SteamIntEnum):
    Invalid = 0
    DecryptCPU = 1
    DiskRead = 2
    DiskWrite = 3

class ESteamPipeWorkType(SteamIntEnum):
    ESteamPipeClientWorkType_Invalid = 0
    ESteamPipeClientWorkType_StageFromChunkStores = 1

ESteamReviewScore = SteamIntEnum('ESteamReviewScore', {
    'OverwhelminglyPositive': 9,
    'VeryPositive': 8,
    'Positive': 7,
    'MostlyPositive': 6,
    'Mixed': 5,
    'MostlyNegative': 4,
    'Negative': 3,
    'VeryNegative': 2,
    'OverwhelminglyNegative': 1,
    'None': 0,
    })

class ESteamTVContentTemplate(SteamIntEnum):
    Invalid = 0
    Takeover = 1
    SingleGame = 2
    GameList = 3
    QuickExplore = 4
    ConveyorBelt = 5
    WatchParty = 6
    Developer = 7
    Event = 8

class EStorageBlockContentType(SteamIntEnum):
    Invalid = 0
    Unknown = 1
    FileSystem = 2
    Crypto = 3
    Raid = 4

class EStorageBlockFileSystemType(SteamIntEnum):
    Invalid = 0
    Unknown = 1
    VFat = 2
    Ext4 = 3

class EStorageDriveMediaType(SteamIntEnum):
    Invalid = 0
    Unknown = 1
    HDD = 2
    SSD = 3
    Removable = 4

class EStorageFormatStage(SteamIntEnum):
    Invalid = 0
    NotRunning = 1
    Starting = 2
    Testing = 3
    Rescuing = 4
    Formatting = 5
    Finalizing = 6

class EStoreAppType(SteamIntEnum):
    Game = 0
    Demo = 1
    Mod = 2
    Movie = 3
    DLC = 4
    Guide = 5
    Software = 6
    Video = 7
    Series = 8
    Episode = 9
    Hardware = 10
    Music = 11
    Beta = 12
    Tool = 13
    Advertising = 14

EStoreBrowseFilterFailure = SteamIntEnum('EStoreBrowseFilterFailure', {
    'None': 0,
    'Redundant': 10,
    'NotPreferred': 20,
    'NotInterested': 30,
    'UnwantedContent': 40,
    'Unavailable': 50,
    })

class EStoreCategoryType(SteamIntEnum):
    Category = 0
    SupportedPlayers = 1
    Feature = 2
    ControllerSupport = 3
    CloudGaming = 4
    MAX = 5

class EStoreDiscoveryQueueType(SteamIntEnum):
    EStoreDiscoveryQueueTypeNew = 0
    EStoreDiscoveryQueueTypeComingSoon = 1
    EStoreDiscoveryQueueTypeRecommended = 2
    EStoreDiscoveryQueueTypeEveryNewRelease = 3
    EStoreDiscoveryQueueTypeMLRecommender = 5
    EStoreDiscoveryQueueTypeWishlistOnSale = 6
    EStoreDiscoveryQueueTypeDLC = 7
    EStoreDiscoveryQueueTypeDLCOnSale = 8
    EStoreDiscoveryQueueTypeRecommendedComingSoon = 9
    EStoreDiscoveryQueueTypeRecommendedFree = 10
    EStoreDiscoveryQueueTypeRecommendedOnSale = 11
    EStoreDiscoveryQueueTypeRecommendedDemos = 12
    EStoreDiscoveryQueueTypeDLCNewReleases = 13
    EStoreDiscoveryQueueTypeDLCTopSellers = 14
    EStoreDiscoveryQueueTypeDLCUpcoming = 15
    EStoreDiscoveryQueueTypeMAX = 16

class EStoreItemType(SteamIntEnum):
    Invalid = -1
    App = 0
    Package = 1
    Bundle = 2
    Mtx = 3
    Tag = 4
    Creator = 5
    HubCategory = 6

EStoreLinkType = SteamIntEnum('EStoreLinkType', {
    'None': 0,
    'YouTube': 1,
    'Facebook': 2,
    'Twitter': 3,
    'Twitch': 4,
    'Discord': 5,
    'QQ': 6,
    'VK': 7,
    'Bilibili': 8,
    'Weibo': 9,
    'Reddit': 10,
    'Instagram': 11,
    'Tumblr': 12,
    'Tieba': 13,
    'Tiktok': 14,
    'Telegram': 15,
    'LinkedIn': 16,
    'WeChat': 17,
    'QQLink': 18,
    'Douyin': 19,
    'Bluesky': 20,
    'Mastodon': 21,
    'Threads': 22,
    'QQChannel': 23,
    'RedNote': 24,
    'MAX': 25,
    })

class EStreamActivity(SteamIntEnum):
    EStreamActivityIdle = 1
    EStreamActivityGame = 2
    EStreamActivityDesktop = 3
    EStreamActivitySecureDesktop = 4
    EStreamActivityMusic = 5

class EStreamAudioCodec(SteamIntEnum):
    EStreamAudioCodecNone = 0
    EStreamAudioCodecRaw = 1
    EStreamAudioCodecVorbis = 2
    EStreamAudioCodecOpus = 3
    EStreamAudioCodecMP3 = 4
    EStreamAudioCodecAAC = 5

class EStreamBitrate(SteamIntEnum):
    EStreamBitrateAutodetect = -1
    EStreamBitrateUnlimited = 0

class EStreamChannel(SteamIntEnum):
    EStreamChannelInvalid = -1
    EStreamChannelDiscovery = 0
    EStreamChannelControl = 1
    EStreamChannelStats = 2
    EStreamChannelDataChannelStart = 3

class EStreamColorspace(SteamIntEnum):
    Unknown = 0
    BT601 = 1
    BT601_Full = 2
    BT709 = 3
    BT709_Full = 4
    HDR10 = 5

class EStreamControllerConfigMsg(SteamIntEnum):
    RequestConfigsForApp = 0
    ConfigResponse = 1
    PersonalizationResponse = 2
    ActiveConfigChange = 3
    RequestActiveConfig = 4

class EStreamControlMessage(SteamIntEnum):
    EStreamControlAuthenticationRequest = 1
    EStreamControlAuthenticationResponse = 2
    EStreamControlNegotiationInit = 3
    EStreamControlNegotiationSetConfig = 4
    EStreamControlNegotiationComplete = 5
    EStreamControlClientHandshake = 6
    EStreamControlServerHandshake = 7
    EStreamControlStartNetworkTest = 8
    EStreamControlKeepAlive = 9
    EStreamControl_LAST_SETUP_MESSAGE = 15
    EStreamControlStartAudioData = 50
    EStreamControlStopAudioData = 51
    EStreamControlStartVideoData = 52
    EStreamControlStopVideoData = 53
    EStreamControlInputMouseMotion = 54
    EStreamControlInputMouseWheel = 55
    EStreamControlInputMouseDown = 56
    EStreamControlInputMouseUp = 57
    EStreamControlInputKeyDown = 58
    EStreamControlInputKeyUp = 59
    EStreamControlInputGamepadAttached_OBSOLETE = 60
    EStreamControlInputGamepadEvent_OBSOLETE = 61
    EStreamControlInputGamepadDetached_OBSOLETE = 62
    EStreamControlShowCursor = 63
    EStreamControlHideCursor = 64
    EStreamControlSetCursor = 65
    EStreamControlGetCursorImage = 66
    EStreamControlSetCursorImage = 67
    EStreamControlDeleteCursor = 68
    EStreamControlSetTargetFramerate = 69
    EStreamControlInputLatencyTest = 70
    EStreamControlGamepadRumble_OBSOLETE = 71
    EStreamControlOverlayEnabled = 74
    EStreamControlInputControllerAttached_OBSOLETE = 75
    EStreamControlInputControllerState_OBSOLETE = 76
    EStreamControlTriggerHapticPulse_OBSOLETE = 77
    EStreamControlInputControllerDetached_OBSOLETE = 78
    EStreamControlVideoDecoderInfo = 80
    EStreamControlSetTitle = 81
    EStreamControlSetIcon = 82
    EStreamControlQuitRequest = 83
    EStreamControlSetQoS = 87
    EStreamControlInputControllerWirelessPresence_OBSOLETE = 88
    EStreamControlSetGammaRamp = 89
    EStreamControlVideoEncoderInfo = 90
    EStreamControlInputControllerStateHID_OBSOLETE = 93
    EStreamControlSetTargetBitrate = 94
    EStreamControlSetControllerPairingEnabled_OBSOLETE = 95
    EStreamControlSetControllerPairingResult_OBSOLETE = 96
    EStreamControlTriggerControllerDisconnect_OBSOLETE = 97
    EStreamControlSetActivity = 98
    EStreamControlSetStreamingClientConfig = 99
    EStreamControlSystemSuspend = 100
    EStreamControlSetControllerSettings_OBSOLETE = 101
    EStreamControlVirtualHereRequest = 102
    EStreamControlVirtualHereReady = 103
    EStreamControlVirtualHereShareDevice = 104
    EStreamControlSetSpectatorMode = 105
    EStreamControlRemoteHID = 106
    EStreamControlStartMicrophoneData = 107
    EStreamControlStopMicrophoneData = 108
    EStreamControlInputText = 109
    EStreamControlTouchConfigActive = 110
    EStreamControlGetTouchConfigData = 111
    EStreamControlSetTouchConfigData = 112
    EStreamControlSaveTouchConfigLayout = 113
    EStreamControlTouchActionSetActive = 114
    EStreamControlGetTouchIconData = 115
    EStreamControlSetTouchIconData = 116
    EStreamControlInputTouchFingerDown = 117
    EStreamControlInputTouchFingerMotion = 118
    EStreamControlInputTouchFingerUp = 119
    EStreamControlSetCaptureSize = 120
    EStreamControlSetFlashState = 121
    EStreamControlPause = 122
    EStreamControlResume = 123
    EStreamControlEnableHighResCapture = 124
    EStreamControlDisableHighResCapture = 125
    EStreamControlToggleMagnification = 126
    EStreamControlSetCapslock = 127
    EStreamControlSetKeymap = 128
    EStreamControlStopRequest = 129
    EStreamControlTouchActionSetLayerAdded = 130
    EStreamControlTouchActionSetLayerRemoved = 131
    EStreamControlRemotePlayTogetherGroupUpdate = 132
    EStreamControlSetInputTemporarilyDisabled = 133
    EStreamControlSetQualityOverride = 134
    EStreamControlSetBitrateOverride = 135
    EStreamControlShowOnScreenKeyboard = 136
    EStreamControlControllerConfigMsg = 137
    EStreamControlControllerPersonalizationUpdate = 138
    EStreamControlEnableNeptuneData_OBSOLETE = 139
    EStreamControlDisableNeptuneData_OBSOLETE = 140
    EStreamControlStartNeptuneData_OBSOLETE = 141
    EStreamControlStopNeptuneData_OBSOLETE = 142
    EStreamControlPauseControllerInput = 143
    EStreamControlResumeControllerInput = 144
    EStreamControlVRConnectionReady = 145
    EStreamControlSetCursorScale = 146
    EStreamControlCaptureFailed = 147
    EStreamControlVideoOverflow = 148

class EStreamDataMessage(SteamIntEnum):
    EStreamDataPacket = 1
    EStreamDataLost = 2

class EStreamDeviceFormFactor(SteamIntEnum):
    EStreamDeviceFormFactorUnknown = 0
    EStreamDeviceFormFactorPhone = 1
    EStreamDeviceFormFactorTablet = 2
    EStreamDeviceFormFactorComputer = 3
    EStreamDeviceFormFactorTV = 4
    EStreamDeviceFormFactorVRHeadset = 5

class EStreamDiscoveryMessage(SteamIntEnum):
    EStreamDiscoveryPingRequest = 1
    EStreamDiscoveryPingResponse = 2

class EStreamFrameEvent(SteamIntEnum):
    EStreamInputEventStart = 0
    EStreamInputEventSend = 1
    EStreamInputEventRecv = 2
    EStreamInputEventQueued = 3
    EStreamInputEventHandled = 4
    EStreamFrameEventStart = 5
    EStreamFrameEventCaptureBegin = 6
    EStreamFrameEventCaptureEnd = 7
    EStreamFrameEventConvertBegin = 8
    EStreamFrameEventConvertEnd = 9
    EStreamFrameEventEncodeBegin = 10
    EStreamFrameEventEncodeEnd = 11
    EStreamFrameEventSend = 12
    EStreamFrameEventRecv = 13
    EStreamFrameEventDecodeBegin = 14
    EStreamFrameEventDecodeEnd = 15
    EStreamFrameEventUploadBegin = 16
    EStreamFrameEventUploadEnd = 17
    EStreamFrameEventComplete = 18

class EStreamFramerateLimiter(SteamIntEnum):
    EStreamFramerateSlowCapture = 1
    EStreamFramerateSlowConvert = 2
    EStreamFramerateSlowEncode = 4
    EStreamFramerateSlowNetwork = 8
    EStreamFramerateSlowDecode = 16
    EStreamFramerateSlowGame = 32
    EStreamFramerateSlowDisplay = 64

class EStreamFrameResult(SteamIntEnum):
    EStreamFrameResultPending = 0
    EStreamFrameResultDisplayed = 1
    EStreamFrameResultDroppedNetworkSlow = 2
    EStreamFrameResultDroppedNetworkLost = 3
    EStreamFrameResultDroppedDecodeSlow = 4
    EStreamFrameResultDroppedDecodeCorrupt = 5
    EStreamFrameResultDroppedLate = 6
    EStreamFrameResultDroppedReset = 7

class EStreamHostDisplaySetting(SteamIntEnum):
    EStreamHostDisplaySettingNone = 0
    EStreamHostDisplaySettingClient = 1
    EStreamHostDisplaySettingCustom = 2

class EStreamHostPlayAudioPreference(SteamIntEnum):
    EStreamHostPlayAudioDefault = 0
    EStreamHostPlayAudioAlways = 1

class EStreamingDataType(SteamIntEnum):
    EStreamingAudioData = 0
    EStreamingVideoData = 1
    EStreamingMicrophoneData = 2
    EStreamingNeptuneData_OBSOLETE = 3

class EStreamingDongleFixResult(SteamIntEnum):
    EStreamingDongleFixResultSuccess = 1
    EStreamingDongleFixResultFailure = 2

class EStreamInterface(SteamIntEnum):
    EStreamInterfaceDefault = 0
    EStreamInterfaceRecentGames = 1
    EStreamInterfaceBigPicture = 2
    EStreamInterfaceDesktop = 3
    EStreamInterfaceSteamVR = 4

class EStreamMouseButton(SteamIntEnum):
    EStreamMouseButtonLeft = 1
    EStreamMouseButtonRight = 2
    EStreamMouseButtonMiddle = 16
    EStreamMouseButtonX1 = 32
    EStreamMouseButtonX2 = 64
    EStreamMouseButtonUnknown = 4096

class EStreamMouseWheelDirection(SteamIntEnum):
    EStreamMouseWheelUp = 120
    EStreamMouseWheelDown = -120
    EStreamMouseWheelLeft = 3
    EStreamMouseWheelRight = 4

class EStreamP2PScope(SteamIntEnum):
    EStreamP2PScopeAutomatic = 0
    EStreamP2PScopeDisabled = 1
    EStreamP2PScopeOnlyMe = 2
    EStreamP2PScopeFriends = 3
    EStreamP2PScopeEveryone = 4

class EStreamQualityPreference(SteamIntEnum):
    EStreamQualityAutomatic = -1
    EStreamQualityFast = 1
    EStreamQualityBalanced = 2
    EStreamQualityBeautiful = 3

class EStreamStatsMessage(SteamIntEnum):
    EStreamStatsFrameEvents = 1
    EStreamStatsDebugDump = 2
    EStreamStatsLogMessage = 3
    EStreamStatsLogUploadBegin = 4
    EStreamStatsLogUploadData = 5
    EStreamStatsLogUploadComplete = 6

class EStreamTransport(SteamIntEnum):
    EStreamTransportNone = 0
    EStreamTransportUDP = 1
    EStreamTransportUDPRelay_OBSOLETE = 2
    EStreamTransportWebRTC_OBSOLETE = 3
    EStreamTransportSDR = 4
    EStreamTransportUDP_SNS = 5
    EStreamTransportUDPRelay_SNS_OBSOLETE = 6

class EStreamVersion(SteamIntEnum):
    EStreamVersionNone = 0
    EStreamVersionCurrent = 1

class EStreamVideoCodec(SteamIntEnum):
    EStreamVideoCodecNone = 0
    EStreamVideoCodecRaw = 1
    EStreamVideoCodecVP8 = 2
    EStreamVideoCodecVP9 = 3
    EStreamVideoCodecH264 = 4
    EStreamVideoCodecHEVC = 5
    EStreamVideoCodecAV1 = 8
    EStreamVideoCodecPyrowave = 9

class ESystemAudioChannel(SteamIntEnum):
    SystemAudioChannel_Invalid = 0
    SystemAudioChannel_Aggregated = 1
    SystemAudioChannel_FrontLeft = 2
    SystemAudioChannel_FrontRight = 3
    SystemAudioChannel_LFE = 4
    SystemAudioChannel_BackLeft = 5
    SystemAudioChannel_BackRight = 6
    SystemAudioChannel_FrontCenter = 7
    SystemAudioChannel_Unknown = 8
    SystemAudioChannel_Mono = 9

class ESystemAudioDirection(SteamIntEnum):
    SystemAudioDirection_Invalid = 0
    SystemAudioDirection_Input = 1
    SystemAudioDirection_Output = 2

class ESystemAudioPortDirection(SteamIntEnum):
    SystemAudioPortDirection_Invalid = 0
    SystemAudioPortDirection_Input = 1
    SystemAudioPortDirection_Output = 2

class ESystemAudioPortType(SteamIntEnum):
    SystemAudioPortType_Invalid = 0
    SystemAudioPortType_Unknown = 1
    SystemAudioPortType_Audio32f = 2
    SystemAudioPortType_Midi8b = 3
    SystemAudioPortType_Video32RGBA = 4

ESystemDisplayCompatibilityMode = SteamIntEnum('ESystemDisplayCompatibilityMode', {
    'Invalid': 0,
    'None': 1,
    'MinimalBandwith': 2,
    })

class ESystemFanControlMode(SteamIntEnum):
    SystemFanControlMode_Invalid = 0
    SystemFanControlMode_Disabled = 1
    SystemFanControlMode_Default = 2

class ESystemPowerState(SteamIntEnum):
    Invalid = 0
    Normal = 1
    LowPowerDownloads = 2
    Sleep = 3

class ESystemServiceState(SteamIntEnum):
    Unavailable = 0
    Disabled = 1
    Enabled = 2

class ESystemUpdateNotificationType(SteamIntEnum):
    Invalid = 0
    Available = 1
    NeedsRestart = 2

class ETextFilterSetting(SteamIntEnum):
    ETextFilterSettingSteamLabOptedOut = 0
    ETextFilterSettingEnabled = 1
    ETextFilterSettingEnabledAllowProfanity = 2
    ETextFilterSettingDisabled = 3

class EThumbnailFormat(SteamIntEnum):
    eJPEG = 1
    eRGB = 2

class EThumbnailTimePrecision(SteamIntEnum):
    ePrecise = 0
    eLoose = 1

class ETimelineChangeNotificationType(SteamIntEnum):
    Started = 1
    Stopped = 2
    Deleted = 3
    RecordingStarted = 4
    RecordingStopped = 5
    RecordingUpdated = 6

class ETimelineEntryType(SteamIntEnum):
    Invalid = 0
    GameMode = 1
    Event = 2
    StateDescription = 3
    Achievement = 4
    UserMarker = 5
    Screenshot = 6
    Error = 7
    Tag = 8
    GamePhase = 9

ETokenRenewalType = SteamIntEnum('ETokenRenewalType', {
    'None': 0,
    'Allow': 1,
    })

class ETouchGesture(SteamIntEnum):
    ETouchGestureNone = 0
    ETouchGestureTouch = 1
    ETouchGestureTap = 2
    ETouchGestureDoubleTap = 3
    ETouchGestureShortPress = 4
    ETouchGestureLongPress = 5
    ETouchGestureLongTap = 6
    ETouchGestureTwoFingerTap = 7
    ETouchGestureTapCancelled = 8
    ETouchGesturePinchBegin = 9
    ETouchGesturePinchUpdate = 10
    ETouchGesturePinchEnd = 11
    ETouchGestureFlingStart = 12
    ETouchGestureFlingCancelled = 13

class ETrailerCategory(SteamIntEnum):
    Invalid = 0
    Gameplay = 1
    Teaser = 2
    Cinematic = 3
    Update = 4
    Accolades = 5
    Interview = 6

class ETritonConnectionType(SteamIntEnum):
    Unknown = 0
    Puck = 1
    Machine = 2
    USB = 3
    BT = 4

ETritonPairType = SteamIntEnum('ETritonPairType', {
    'None': 0,
    'Wired': 1,
    'Wireless': 2,
    })

ETwoFactorStatusFieldFlag = SteamIntEnum('ETwoFactorStatusFieldFlag', {
    'None': 0,
    'LastUsage': 1,
    })

ETwoFactorUsageType = SteamIntEnum('ETwoFactorUsageType', {
    'Unknown': 0,
    'None': 1,
    'MobileConfirmation': 2,
    'Login': 3,
    })

class EUpdaterState(SteamIntEnum):
    Invalid = 0
    UpToDate = 2
    Checking = 3
    Available = 4
    Applying = 5
    ClientRestartPending = 6
    SystemRestartPending = 7
    RollBack = 8

class EUpdaterType(SteamIntEnum):
    Invalid = 0
    Client = 1
    OS = 2
    BIOS = 3
    Aggregated = 4
    Test1 = 5
    Test2 = 6
    Dummy = 7

EUserReviewScore = SteamIntEnum('EUserReviewScore', {
    'None': 0,
    'OverwhelminglyNegative': 1,
    'VeryNegative': 2,
    'Negative': 3,
    'MostlyNegative': 4,
    'Mixed': 5,
    'MostlyPositive': 6,
    'Positive': 7,
    'VeryPositive': 8,
    'OverwhelminglyPositive': 9,
    })

class EUserReviewScorePreference(SteamIntEnum):
    Unset = 0
    IncludeAll = 1
    ExcludeBombs = 2

class EValveIndexComponent(SteamIntEnum):
    EValveIndexComponentUnknown = 0
    EValveIndexComponentHMD = 1
    EValveIndexComponentLeftKnuckle = 2
    EValveIndexComponentRightKnuckle = 3
    EValveIndexComponentSteamFrameHMD = 4
    EValveIndexComponentSteamFrameLeftController = 5
    EValveIndexComponentSteamFrameRightController = 6
    EValveIndexComponentSteamFrameWirelessAdapter = 7

class EVideoFormat(SteamIntEnum):
    EVideoFormatNone = 0
    EVideoFormatYV12 = 1
    EVideoFormatAccel = 2

class EVRLinkCaps(SteamIntEnum):
    EVRLinkCapsUnknown = 0
    EVRLinkCapsAvailable = 1
    EVRLinkCapsUnimplemented = 2
    EVRLinkCapsMissingHardwareEncoding = 3

class EWindowStackingOrder(SteamIntEnum):
    Invalid = 0
    Top = 1
    Bottom = 2

class EWindowsUpdateInstallationImpact(SteamIntEnum):
    Unknown = -1
    Normal = 0
    Minor = 1
    ExclusiveHandling = 2

class EWindowsUpdateRebootBehavior(SteamIntEnum):
    Unknown = -1
    NeverNeedsReboot = 0
    AlwaysNeedsReboot = 1
    MightNeedReboot = 2

class GCProtoBufMsgSrc(SteamIntEnum):
    Unspecified = 0
    FromSystem = 1
    FromSteamID = 2
    FromGC = 3
    ReplySystem = 4

class PartnerEventNotificationType(SteamIntEnum):
    EEventStart = 0
    EEventBroadcastStart = 1
    EEventMatchStart = 2
    EEventPartnerMaxType = 3

__all__ = [
    'E_STAR_GlyphWriteResult',
    'EAccessibilityContrastMode',
    'EAchievementProgressType',
    'EACState',
    'EAgreementType',
    'EAppCloudStatus',
    'EAppContentDetectionType',
    'EAppControllerSupportLevel',
    'EAppGamepadGyroTrackpadSupportLevel',
    'EAppHDRSupport',
    'EAppReportType',
    'EAppTestType',
    'EAssetPropertyType',
    'EAsyncGameSessionUserState',
    'EAsyncGameSessionUserVisibility',
    'EAudioFormat',
    'EAuthenticationType',
    'EAuthSessionGuardType',
    'EAuthSessionSecurityHistory',
    'EAuthTokenAppType',
    'EAuthTokenPlatformType',
    'EAuthTokenRevokeAction',
    'EAuthTokenState',
    'EBanContentCheckResult',
    'EBatteryState',
    'EBluetoothDeviceType',
    'EBroadcastChatPermission',
    'EBroadcastEncoderSetting',
    'EBroadcastImageType',
    'EBroadcastPermission',
    'EBroadcastWatchLocation',
    'EBrowserFeatureStatus',
    'EBrowserGPUStatus',
    'ECaptureFailedReason',
    'EChatRoomGroupRank',
    'EChatRoomJoinState',
    'EChatRoomMemberStateChange',
    'EChatRoomMessageReactionType',
    'EChatRoomNotificationLevel',
    'EChatRoomServerMessage',
    'EChatSessionNotice',
    'EChildProcessQueryCommand',
    'EChildProcessQueryExitCode',
    'EClanImageFileType',
    'EClanImageGroup',
    'EClientExecutionSite',
    'EClientNotificationType',
    'EClientSettingStore',
    'ECLientTaskListType',
    'EClipRangeMethod',
    'EClipShareMethod',
    'ECloudGamingPlatform',
    'ECloudPendingRemoteOperation',
    'ECloudStoragePersistState',
    'ECodecUsagePlatform',
    'ECodecUsageReason',
    'EColorGamutLabelSet',
    'ECommentDeleteReason',
    'ECommentThreadType',
    'ECommunityItemClass',
    'ECompromiseDetectionType',
    'EContentCheckProvider',
    'EContentDeltaChunkDataLocation',
    'EContentDescriptorID',
    'EContentHubDiscountFilterType',
    'EContentModerationSanction',
    'EContentModeratorLevel',
    'EContentReportReason',
    'EContentReportResolution',
    'EContentReportSubjectAction',
    'EContentReportSubjectType',
    'EControlledLegalCategoryStatus',
    'EControllerElementType',
    'ECPUGovernor',
    'EDiskSpaceType',
    'EDisplayManagerRGBRange',
    'EDisplayPowerState',
    'EDisplayStatus',
    'EEnhancedMarketAppearanceStatus',
    'EExportCodec',
    'EExternalSaleEventType',
    'EFamilyGroupChangeLogType',
    'EFamilyGroupRole',
    'EFamilyGroupsTwoFactorMethod',
    'EForumType',
    'EFrameAccumulatedStat',
    'EFrameRateReportEnabled',
    'EGameFrameRateReportingPreference',
    'EGameRecordingErrorType',
    'EGameRecordingType',
    'EGamescopeBlurMode',
    'EGameSearchAction',
    'EGameSearchResult',
    'EGetChannelsAlgorithm',
    'EGetGamesAlgorithm',
    'EGpuDriverId',
    'EGPUPerformanceLevel',
    'EGraphicsPerfOverlayLevel',
    'EGRAudio',
    'EGRExportLimitType',
    'EGRMode',
    'EHardwareCompatibilityFeedbackDetails',
    'EHardwareUpdateDeviceType',
    'EHardwareUpdatePriority',
    'EHDRToneMapOperator',
    'EHDRVisualization',
    'EHIDDeviceDisconnectMethod',
    'EHIDDeviceLocation',
    'EInputMode',
    'EJSRegisterMethodType',
    'EKeyEscrowUsage',
    'ELEDManagerMode',
    'ELobbyStatus',
    'ELogFileType',
    'EMarketingMessageAssociationType',
    'EMarketingMessageClickLocation',
    'EMarketingMessageLookupType',
    'EMarketingMessageTemplateType',
    'EMarketingMessageType',
    'EMarketingMessageVisibility',
    'EMessageReactionType',
    'EMMSLobbyStatus',
    'EMouseMode',
    'EMsg',
    'EMsgClanAccountFlags',
    'ENewSteamAnnouncementState',
    'ENotificationSetting',
    'EOSBranch',
    'EOverlayToggleBarLocation',
    'EPartnerEventDisplayLocation',
    'EPartnerLinkTrackingBackfillSource',
    'EPhaseResultType',
    'EPlaytestStatus',
    'EPressOutletAction',
    'EPressOutletMemberPendingState',
    'EProfileCustomizationStyle',
    'EProfileCustomizationType',
    'EProtoClanEventType',
    'EProtoExecutionSite',
    'EProtoServiceType',
    'EProvideDeckFeedbackPreference',
    'EPublishedFileForSaleStatus',
    'EPublishedFileRevision',
    'EPublishedFileStorageSystem',
    'EPurchaseRequestAction',
    'EQueryFilesSearchTextTarget',
    'EQueryFilesSpecialFilter',
    'ERatingAgency',
    'ERecordingSessionChangeNotificationType',
    'ERemoteClientBroadcastMsg',
    'ERemoteClientPairWifiAPResult',
    'ERemoteClientService',
    'ERemoteDeviceAuthorizationResult',
    'ERemoteDeviceStreamingResult',
    'EResolutionAutomation',
    'ESDCardFormatStage',
    'ESessionPersistence',
    'ESettingProfileMode',
    'ESharedLibraryExcludeReason',
    'ESLSHelper',
    'ESpeakerConfiguration',
    'ESplitScalingFilter',
    'ESplitScalingScaler',
    'ESteamDatagramMsgID',
    'ESteamDeckCompatibilityCategory',
    'ESteamDeckCompatibilityFeedback',
    'ESteamDeckCompatibilityResultDisplayType',
    'ESteamDeckCompatibilityTestResult',
    'ESteamDeckKeyboardLayout',
    'ESteamNetworkingSocketsCipher',
    'ESteamNetworkingUDPMsgID',
    'ESteamNotificationType',
    'ESteamOSCompatibilityCategory',
    'ESteamOSCompatibilityResultDisplayType',
    'ESteamPipeOperationType',
    'ESteamPipeWorkType',
    'ESteamReviewScore',
    'ESteamTVContentTemplate',
    'EStorageBlockContentType',
    'EStorageBlockFileSystemType',
    'EStorageDriveMediaType',
    'EStorageFormatStage',
    'EStoreAppType',
    'EStoreBrowseFilterFailure',
    'EStoreCategoryType',
    'EStoreDiscoveryQueueType',
    'EStoreItemType',
    'EStoreLinkType',
    'EStreamActivity',
    'EStreamAudioCodec',
    'EStreamBitrate',
    'EStreamChannel',
    'EStreamColorspace',
    'EStreamControllerConfigMsg',
    'EStreamControlMessage',
    'EStreamDataMessage',
    'EStreamDeviceFormFactor',
    'EStreamDiscoveryMessage',
    'EStreamFrameEvent',
    'EStreamFramerateLimiter',
    'EStreamFrameResult',
    'EStreamHostDisplaySetting',
    'EStreamHostPlayAudioPreference',
    'EStreamingDataType',
    'EStreamingDongleFixResult',
    'EStreamInterface',
    'EStreamMouseButton',
    'EStreamMouseWheelDirection',
    'EStreamP2PScope',
    'EStreamQualityPreference',
    'EStreamStatsMessage',
    'EStreamTransport',
    'EStreamVersion',
    'EStreamVideoCodec',
    'ESystemAudioChannel',
    'ESystemAudioDirection',
    'ESystemAudioPortDirection',
    'ESystemAudioPortType',
    'ESystemDisplayCompatibilityMode',
    'ESystemFanControlMode',
    'ESystemPowerState',
    'ESystemServiceState',
    'ESystemUpdateNotificationType',
    'ETextFilterSetting',
    'EThumbnailFormat',
    'EThumbnailTimePrecision',
    'ETimelineChangeNotificationType',
    'ETimelineEntryType',
    'ETokenRenewalType',
    'ETouchGesture',
    'ETrailerCategory',
    'ETritonConnectionType',
    'ETritonPairType',
    'ETwoFactorStatusFieldFlag',
    'ETwoFactorUsageType',
    'EUpdaterState',
    'EUpdaterType',
    'EUserReviewScore',
    'EUserReviewScorePreference',
    'EValveIndexComponent',
    'EVideoFormat',
    'EVRLinkCaps',
    'EWindowStackingOrder',
    'EWindowsUpdateInstallationImpact',
    'EWindowsUpdateRebootBehavior',
    'GCProtoBufMsgSrc',
    'PartnerEventNotificationType',
    ]
