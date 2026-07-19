import re
from importlib import import_module

service_lookup = {  # MARK_SERVICE_START
    'AccountHardware':                  'steam.protobufs.steammessages_accounthardware_pb2',
    'Authentication':                   'steam.protobufs.steammessages_auth_pb2',
    'AuthenticationSupport':            'steam.protobufs.steammessages_auth_pb2',
    'CloudGaming':                      'steam.protobufs.steammessages_auth_pb2',
    'Broadcast':                        'steam.protobufs.steammessages_broadcast_pb2',
    'BroadcastClient':                  'steam.protobufs.steammessages_broadcast_pb2',
    'Chat':                             'steam.protobufs.steammessages_chat_pb2',
    'ChatRoom':                         'steam.protobufs.steammessages_chat_pb2',
    'ClanChatRooms':                    'steam.protobufs.steammessages_chat_pb2',
    'ChatRoomClient':                   'steam.protobufs.steammessages_chat_pb2',
    'ChatUsability':                    'steam.protobufs.steammessages_chat_pb2',
    'ChatUsabilityClient':              'steam.protobufs.steammessages_chat_pb2',
    'ClientMetrics':                    'steam.protobufs.steammessages_clientmetrics_pb2',
    'Cloud':                            'steam.protobufs.steammessages_cloud_pb2',
    'CloudClient':                      'steam.protobufs.steammessages_cloud_pb2',
    'Community':                        'steam.protobufs.steammessages_community_pb2',
    'ContentServerDirectory':           'steam.protobufs.steammessages_contentsystem_pb2',
    'DepotContentDetection':            'steam.protobufs.steammessages_contentsystem_pb2',
    'Credentials':                      'steam.protobufs.steammessages_credentials_pb2',
    'DataPublisher':                    'steam.protobufs.steammessages_datapublisher_pb2',
    'ValveHWSurvey':                    'steam.protobufs.steammessages_datapublisher_pb2',
    'ContentBuilder':                   'steam.protobufs.steammessages_depotbuilder_pb2',
    'DeviceAuth':                       'steam.protobufs.steammessages_deviceauth_pb2',
    'Econ':                             'steam.protobufs.steammessages_econ_pb2',
    'FamilyGroups':                     'steam.protobufs.steammessages_familygroups_pb2',
    'FamilyGroupsClient':               'steam.protobufs.steammessages_familygroups_pb2',
    'FriendMessages':                   'steam.protobufs.steammessages_friendmessages_pb2',
    'FriendMessagesClient':             'steam.protobufs.steammessages_friendmessages_pb2',
    'GameNetworking':                   'steam.protobufs.steammessages_gamenetworking_pb2',
    'GameNotifications':                'steam.protobufs.steammessages_gamenotifications_pb2',
    'GameNotificationsClient':          'steam.protobufs.steammessages_gamenotifications_pb2',
    'GameRecordingClip':                'steam.protobufs.steammessages_gamerecording_pb2',
    'VideoClip':                        'steam.protobufs.steammessages_gamerecording_pb2',
    'GameServers':                      'steam.protobufs.steammessages_gameservers_pb2',
    'GameServerClient':                 'steam.protobufs.steammessages_gameservers_pb2',
    'Inventory':                        'steam.protobufs.steammessages_inventory_pb2',
    'InventoryClient':                  'steam.protobufs.steammessages_inventory_pb2',
    'CommunityLinkFilter':              'steam.protobufs.steammessages_linkfilter_pb2',
    'LobbyMatchmakingLegacy':           'steam.protobufs.steammessages_lobbymatchmaking_pb2',
    'EconMarket':                       'steam.protobufs.steammessages_market_pb2',
    'MarketingMessages':                'steam.protobufs.steammessages_marketingmessages_pb2',
    'SteamNotificationClient':          'steam.protobufs.steammessages_notifications_pb2',
    'Offline':                          'steam.protobufs.steammessages_offline_pb2',
    'Parental':                         'steam.protobufs.steammessages_parental_pb2',
    'ParentalClient':                   'steam.protobufs.steammessages_parental_pb2',
    'Parties':                          'steam.protobufs.steammessages_parties_pb2',
    'PartnerApps':                      'steam.protobufs.steammessages_partnerapps_pb2',
    'Player':                           'steam.protobufs.steammessages_player_pb2',
    'PlayerClient':                     'steam.protobufs.steammessages_player_pb2',
    'PublishedFile':                    'steam.protobufs.steammessages_publishedfile_pb2',
    'PublishedFileClient':              'steam.protobufs.steammessages_publishedfile_pb2',
    'QueuedMatchmaking':                'steam.protobufs.steammessages_qms_pb2',
    'QueuedMatchmakingGameHost':        'steam.protobufs.steammessages_qms_pb2',
    'RemoteClient':                     'steam.protobufs.steammessages_remoteclient_service_pb2',
    'RemoteClientSteamClient':          'steam.protobufs.steammessages_remoteclient_service_pb2',
    'Secrets':                          'steam.protobufs.steammessages_secrets_pb2',
    'Shader':                           'steam.protobufs.steammessages_shader_pb2',
    'SiteManagerClient':                'steam.protobufs.steammessages_site_license_pb2',
    'SiteLicense':                      'steam.protobufs.steammessages_site_license_pb2',
    'STAR':                             'steam.protobufs.steammessages_star_pb2',
    'SteamTV':                          'steam.protobufs.steammessages_steamtv_pb2',
    'Store':                            'steam.protobufs.steammessages_store_pb2',
    'StoreClient':                      'steam.protobufs.steammessages_store_pb2',
    'StoreBrowse':                      'steam.protobufs.steammessages_storebrowse_pb2',
    'TimedTrial':                       'steam.protobufs.steammessages_timedtrial_pb2',
    'TwoFactor':                        'steam.protobufs.steammessages_twofactor_pb2',
    'TestSteamClient':                  'steam.protobufs.steammessages_unified_test_pb2',
    'TestServerFromClient':             'steam.protobufs.steammessages_unified_test_pb2',
    'TestExternalPrivilege':            'steam.protobufs.steammessages_unified_test_pb2',
    'UserAccount':                      'steam.protobufs.steammessages_useraccount_pb2',
    'EmbeddedClient':                   'steam.protobufs.steammessages_useraccount_pb2',
    'FileVerification':                 'steam.protobufs.steammessages_vac_pb2',
    'Video':                            'steam.protobufs.steammessages_video_pb2',
    'VideoClient':                      'steam.protobufs.steammessages_video_pb2',
    'FovasVideo':                       'steam.protobufs.steammessages_video_pb2',
    'Workshop':                         'steam.protobufs.steammessages_workshop_pb2',
    'Achievements':                     'steam.protobufs.webuimessages_achievements_pb2',
    'Audio':                            'steam.protobufs.webuimessages_audio_pb2',
    'BluetoothManager':                 'steam.protobufs.webuimessages_bluetooth_pb2',
    'GameNotes':                        'steam.protobufs.webuimessages_gamenotes_pb2',
    'GameRecording':                    'steam.protobufs.webuimessages_gamerecording_pb2',
    'Gamescope':                        'steam.protobufs.webuimessages_gamescope_pb2',
    'HardwareUpdate':                   'steam.protobufs.webuimessages_hardwareupdate_pb2',
    'LEDManager':                       'steam.protobufs.webuimessages_leds_pb2',
    'Screensaver':                      'steam.protobufs.webuimessages_screensaver_pb2',
    'SharedJSContext':                  'steam.protobufs.webuimessages_sharedjscontext_pb2',
    'SleepManager':                     'steam.protobufs.webuimessages_sleep_pb2',
    'SteamEngine':                      'steam.protobufs.webuimessages_steamengine_pb2',
    'SteamInputManager':                'steam.protobufs.webuimessages_steaminput_pb2',
    'SteamOSManager':                   'steam.protobufs.webuimessages_steamos_pb2',
    'SteamOSSLS':                       'steam.protobufs.webuimessages_steamos_pb2',
    'StorageDeviceManager':             'steam.protobufs.webuimessages_storagedevicemanager_pb2',
    'SystemManager':                    'steam.protobufs.webuimessages_systemmanager_pb2',
    'TransportAuth':                    'steam.protobufs.webuimessages_transport_pb2',
    'TransportValidation':              'steam.protobufs.webuimessages_transportvalidation_pb2',
    'TransportValidationClient':        'steam.protobufs.webuimessages_transportvalidation_pb2',
    'User':                             'steam.protobufs.webuimessages_user_pb2',
}  # MARK_SERVICE_END

method_lookup = {}


def get_um(method_name, response=False):
    """Get protobuf for given method name

    :param method_name: full method name (e.g. ``Player.GetGameBadgeLevels#1``)
    :type method_name: :class:`str`
    :param response: whether to return proto for response or request
    :type response: :class:`bool`
    :return: protobuf message
    """
    key = (method_name, response)

    if key not in method_lookup:
        match = re.findall(r'^([a-z]+)\.([a-z]+)#(\d)?$', method_name, re.I)
        if not match:
            return None

        interface, method, version = match[0]

        if interface not in service_lookup:
            return None

        package = import_module(service_lookup[interface])

        service = getattr(package, interface, None)
        if service is None:
            return None

        for method_desc in service.GetDescriptor().methods:
            name = "%s.%s#%d" % (interface, method_desc.name, 1)

            method_lookup[(name, False)] = getattr(package, method_desc.input_type.full_name, None)
            method_lookup[(name, True)] = getattr(package, method_desc.output_type.full_name, None)

    return method_lookup[key]
