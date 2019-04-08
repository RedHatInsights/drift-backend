"""
decoded AUTH_HEADER (newlines added for readability):
{
    "identity": {
        "account_number": "1234",
        "internal": {
            "org_id": "5678"
        },
        "type": "User",
        "user": {
            "email": "test@example.com",
            "first_name": "Firstname",
            "is_active": true,
            "is_internal": true,
            "is_org_admin": false,
            "last_name": "Lastname",
            "locale": "en_US",
            "username": "test_username"
        }
    }
}
"""

AUTH_HEADER = {'X-RH-IDENTITY': 'eyJpZGVudGl0eSI6eyJhY2NvdW50X251bWJlciI6Ij'
                                'EyMzQiLCJ0eXBlIjoiVXNlciIsInVzZXIiOnsidXNl'
                                'cm5hbWUiOiJ0ZXN0X3VzZXJuYW1lIiwiZW1haWwiOi'
                                'J0ZXN0QGV4YW1wbGUuY29tIiwiZmlyc3RfbmFtZSI6'
                                'IkZpcnN0bmFtZSIsImxhc3RfbmFtZSI6Ikxhc3RuYW'
                                '1lIiwiaXNfYWN0aXZlIjp0cnVlLCJpc19vcmdfYWRt'
                                'aW4iOmZhbHNlLCJpc19pbnRlcm5hbCI6dHJ1ZSwibG'
                                '9jYWxlIjoiZW5fVVMifSwiaW50ZXJuYWwiOnsib3Jn'
                                'X2lkIjoiNTY3OCJ9fX0KCg=='}
"""
decoded AUTH_HEADER_NO_ACCT (newlines added for readablity):
{
    "identity": {
        "internal": {
            "org_id": "9999"
        },
        "type": "User",
        "user": {
            "email": "nonumber@example.com",
            "first_name": "No",
            "is_active": true,
            "is_internal": true,
            "is_org_admin": false,
            "last_name": "Number",
            "locale": "en_US",
            "username": "nonumber"
        }
    }
}
"""

AUTH_HEADER_NO_ACCT = {'X-RH-IDENTITY': 'eyJpZGVudGl0eSI6eyJ0eXBlIjoiVXNlciIsInVzZXIiO'
                                        'nsidXNlcm5hbWUiOiJub251bWJlciIsImVtYWlsIjoibm'
                                        '9udW1iZXJAZXhhbXBsZS5jb20iLCJmaXJzdF9uYW1lIjo'
                                        'iTm8iLCJsYXN0X25hbWUiOiJOdW1iZXIiLCJpc19hY3Rp'
                                        'dmUiOnRydWUsImlzX29yZ19hZG1pbiI6ZmFsc2UsImlzX'
                                        '2ludGVybmFsIjp0cnVlLCJsb2NhbGUiOiJlbl9VUyJ9LC'
                                        'JpbnRlcm5hbCI6eyJvcmdfaWQiOiI5OTk5In19fQo='}

FETCH_SYSTEMS_WITH_PROFILES_RESULT = [
    {
      "account": "9876543",
      "bios_uuid": "e380fd4a-28ae-11e9-974c-c85b761454fa",
      "created": "2019-01-31T13:00:00.100010Z",
      "display_name": None,
      "fqdn": "fake_system_99.example.com",
      "id": "fc1e497a-28ae-11e9-afd9-c85b761454fa",
      "insights_id": "01791a58-28af-11e9-9ab0-c85b761454fa",
      "ip_addresses": [
        "10.0.0.3",
        "2620:52:0:2598:5054:ff:fecd:ae15"
      ],
      "mac_addresses": [
        "52:54:00:cd:ae:00",
        "00:00:00:00:00:00"
      ],
      "rhel_machine_id": None,
      "satellite_id": None,
      "subscription_manager_id": "RHN Classic and Red Hat Subscription Management",
      "system_profile": {'salutation': "hello",
                         'installed_packages': ["0:bash-4.4.23-6.fc29.x86_64",
                                                "this isn't parsable",
                                                "no_epoch-1.0-1.fc99.8088"],
                         'cpu_flags': ['maryland'],
                         'yum_repos': [{'name': 'yummy', 'enabled': False}, {'no_name': 'bleh'}],
                         'network_interfaces': [{'name': 'eth99', 'mtu': 3}, {'no_name': 'foo'}],
                         "id": "fc1e497a-28ae-11e9-afd9-c85b761454fa"},
      "tags": [],
      "updated": "2019-01-31T14:00:00.500000Z"
    },
    {
      "account": "9876543",
      "bios_uuid": "e380fd4a-28ae-11e9-974c-c85b761454fb",
      "created": "2018-01-31T13:00:00.100010Z",
      "display_name": "hello",
      "fqdn": "fake_system_99.example.com",
      "id": "bbbbbbbb-28ae-11e9-afd9-c85b761454fa",
      "insights_id": "00000000-28af-11e9-9ab0-c85b761454fa",
      "ip_addresses": [
        "10.0.0.3",
        "2620:52:0:2598:5054:ff:fecd:ae15"
      ],
      "mac_addresses": [
        "52:54:00:cd:ae:00",
        "00:00:00:00:00:00"
      ],
      "rhel_machine_id": None,
      "satellite_id": None,
      "subscription_manager_id": "RHN Classic and Red Hat Subscription Management",
      "system_profile": {'salutation': "hi",
                         "id": "bbbbbbbb-28ae-11e9-afd9-c85b761454fa"},
      "tags": [],
      "updated": "2018-01-31T14:00:00.500000Z"},
    {
      "account": "9876543",
      "bios_uuid": "e380fd4a-28ae-11e9-974c-c85b761454fb",
      "created": "2018-01-31T13:00:00.100010Z",
      "display_name": None,
      "fqdn": None,
      "id": "bbbbbbbb-28ae-11e9-afd9-c85b761454fa",
      "insights_id": "00000000-28af-11e9-9ab0-c85b761454fa",
      "ip_addresses": [
        "10.0.0.3",
        "2620:52:0:2598:5054:ff:fecd:ae15"
      ],
      "mac_addresses": [
        "52:54:00:cd:ae:00",
        "00:00:00:00:00:00"
      ],
      "rhel_machine_id": None,
      "satellite_id": None,
      "subscription_manager_id": "RHN Classic and Red Hat Subscription Management",
      "system_profile": {'salutation': "hi",
                         "id": "bbbbbbbb-28ae-11e9-afd9-c85b761454fa"},
      "tags": [],
      "updated": "2018-01-31T14:00:00.500000Z"}
    ]

FETCH_SYSTEM_PROFILES_INV_SVC = '''
{
  "count": 1,
  "page": 1,
  "per_page": 50,
  "results": [
    {
      "id": "243926fa-262f-11e9-a632-c85b761454fa",
      "system_profile": {
        "arch": "x86_64",
        "bios_vendor": "SeaBIOS",
        "bios_version": "?-20180531_142017-buildhw-08.phx2.fedoraproject.org-1.fc28",
        "cores_per_socket": 1,
        "cpu_flags": [ "fpu", "vme" ],
        "enabled_services": ["auditd", "chronyd", "crond" ],
        "infrastructure_type": "virtual",
        "infrastructure_vendor": "kvm",
        "installed_packages": ["0:bash-4.4.19-7.el8", "0:chrony-3.3-3.el8",
                               "0:dnf-4.0.9.2-4.el8", "1:NetworkManager-1.14.0-14.el8"],
        "installed_services": [ "arp-ethers", "auditd", "autovt@", "chronyd", "cpupower"],
        "kernel_modules": [ "kvm", "pcspkr", "joydev", "xfs"],
        "last_boot_time": "2019-03-25T19:32:18",
        "network_interfaces": [
          {
            "ipv4_addresses": ["127.0.0.1"],
            "ipv6_addresses": ["::1"],
            "mac_address": "00:00:00:00:00:00",
            "mtu": 65536,
            "name": "lo",
            "state": "UNKNOWN",
            "type": "loopback"
          },
          {
            "ipv4_addresses": ["192.168.0.1"],
            "ipv6_addresses": ["fe80::5054:ff::0001"],
            "mac_address": "52:54:00:00:00:00",
            "mtu": 1500,
            "name": "eth0",
            "state": "UP",
            "type": "ether"
          }
        ],
        "number_of_cpus": 2,
        "number_of_sockets": 2,
        "os_kernel_version": "4.18.0",
        "running_processes": [ "watchdog/1", "systemd-logind", "md", "ksmd", "sshd" ],
        "system_memory_bytes": 1917988864,
        "yum_repos": [
          {
            "base_url": "https://cdn.example.com/content/freedos/1.0/i386/os",
            "enabled": true,
            "gpgcheck": true,
            "name": "freedos 1.0 repo i386"
          },
          {
            "base_url": "https://cdn.example.com/content/freedos/1.0/z80/os",
            "enabled": false,
            "gpgcheck": true,
            "name": "freedos 1.0 repo z80"
          }
        ]
      }
    }
  ],
  "total": 1
}
'''

FETCH_SYSTEMS_WITH_PROFILES_SAME_FACTS_RESULT = [
    {
      "account": "9876543",
      "bios_uuid": "e380fd4a-28ae-11e9-974c-c85b761454fa",
      "created": "2019-01-31T13:00:00.100010Z",
      "display_name": None,
      "system_profile": {'salutation': "howdy",
                         "id": "fc1e497a-28ae-11e9-afd9-c85b761454fa"},
      "fqdn": "fake_system_99.example.com",
      "id": "fc1e497a-28ae-11e9-afd9-c85b761454fa",
      "insights_id": "01791a58-28af-11e9-9ab0-c85b761454fa",
      "ip_addresses": [
        "10.0.0.3",
        "2620:52:0:2598:5054:ff:fecd:ae15"
      ],
      "mac_addresses": [
        "52:54:00:cd:ae:00",
        "00:00:00:00:00:00"
      ],
      "rhel_machine_id": None,
      "satellite_id": None,
      "subscription_manager_id": "RHN Classic and Red Hat Subscription Management",
      "tags": [],
      "updated": "2019-01-31T14:00:00.500000Z"
    },
    {
      "account": "9876543",
      "bios_uuid": "e380fd4a-28ae-11e9-974c-c85b761454fb",
      "created": "2018-01-31T13:00:00.100010Z",
      "display_name": None,
      "system_profile": {'salutation': "howdy",
                         "id": "bbbbbbbb-28ae-11e9-afd9-c85b761454fa"},
      "fqdn": "fake_system_99.example.com",
      "id": "bbbbbbbb-28ae-11e9-afd9-c85b761454fa",
      "insights_id": "00000000-28af-11e9-9ab0-c85b761454fa",
      "ip_addresses": [
        "10.0.0.3",
        "2620:52:0:2598:5054:ff:fecd:ae15"
      ],
      "mac_addresses": [
        "52:54:00:cd:ae:00",
        "00:00:00:00:00:00"
      ],
      "rhel_machine_id": None,
      "satellite_id": None,
      "subscription_manager_id": "RHN Classic and Red Hat Subscription Management",
      "tags": [],
      "updated": "2018-01-31T14:00:00.500000Z"}
    ]

FETCH_SYSTEMS_INV_SVC = '''
    {
      "count": 2,
      "page": 1,
      "per_page": 50,
      "results": [
    {
      "account": "1234567",
      "bios_uuid": "dc43976c263411e9bcf0c85b761454fa",
      "created": "2018-12-01T12:00:00.000000Z",
      "display_name": "system1.example.com",
      "fqdn": "system.example.com",
      "id": "243926fa-262f-11e9-a632-c85b761454fa",
      "insights_id": "TEST-ID00-0000-0000",
      "ip_addresses": [
        "10.0.0.1",
        "10.0.0.2"
      ],
      "mac_addresses": [
        "c2:00:d0:c8:00:01"
      ],
      "subscription_manager_id": "1234FAKE1234",
      "tags": [],
      "updated": "2018-12-31T12:00:00.000000Z"
    },
    {
      "account": "1234567",
      "bios_uuid": "ec43976c263411e9bcf0c85b761454fa",
      "created": "2018-12-01T12:00:00.000000Z",
      "display_name": "system2.example.com",
      "fqdn": "system2.example.com",
      "id": "264fb5b2-262f-11e9-9b12-c85b761454fa",
      "insights_id": "TEST-ID22-2222-2222",
      "ip_addresses": [
        "10.0.0.3",
        "10.0.0.4"
      ],
      "mac_addresses": [
        "ec2:00:d0:c8:00:01"
      ],
      "subscription_manager_id": "2222FAKE2222",
      "tags": [],
      "updated": "2018-12-31T12:00:00.000000Z"
    }
    ]}'''

SYSTEM_NOT_FOUND_TEMPLATE = '''
    {
      "count": 0,
      "page": 1,
      "per_page": 50,
      "results": [],
      "total": 0
    }
    '''
