"""
decoded AUTH_HEADER (newlines added for readability):
{
    "identity": {
        "account_number": "1234",
        "org_id": "5678",
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
    "entitlements": {
        "insights": {
            "is_entitled": true
        }
    }
}
"""

AUTH_HEADER = {
    "X-RH-IDENTITY": "eyJpZGVudGl0eSI6eyJhY2NvdW50X251bWJlciI6Ij"
    "EyMzQiLCJvcmdfaWQiOiI1Njc4IiwiaW50ZXJuYWwiOnsib3JnX2lkIjoiN"
    "TY3OCJ9LCJ0eXBlIjoiVXNlciIsInVzZXIiOnsiZW1haWwiOiJ0ZXN0QGV4"
    "YW1wbGUuY29tIiwiZmlyc3RfbmFtZSI6IkZpcnN0bmFtZSIsImlzX2FjdGl"
    "2ZSI6dHJ1ZSwiaXNfaW50ZXJuYWwiOnRydWUsImlzX29yZ19hZG1pbiI6Zm"
    "Fsc2UsImxhc3RfbmFtZSI6Ikxhc3RuYW1lIiwibG9jYWxlIjoiZW5fVVMiL"
    "CJ1c2VybmFtZSI6InRlc3RfdXNlcm5hbWUifX0sImVudGl0bGVtZW50cyI6"
    "eyJpbnNpZ2h0cyI6eyJpc19lbnRpdGxlZCI6dHJ1ZX19fQo="
}

AUTH_HEADER_NO_ENTITLEMENTS = {
    "X-RH-IDENTITY": "eyJpZGVudGl0eSI6eyJhY2NvdW50X251bWJlciI6Ij"
    "EyMzQiLCJ0eXBlIjoiVXNlciIsInVzZXIiOnsidXNl"
    "cm5hbWUiOiJ0ZXN0X3VzZXJuYW1lIiwiZW1haWwiOi"
    "J0ZXN0QGV4YW1wbGUuY29tIiwiZmlyc3RfbmFtZSI6"
    "IkZpcnN0bmFtZSIsImxhc3RfbmFtZSI6Ikxhc3RuYW"
    "1lIiwiaXNfYWN0aXZlIjp0cnVlLCJpc19vcmdfYWRt"
    "aW4iOmZhbHNlLCJpc19pbnRlcm5hbCI6dHJ1ZSwibG"
    "9jYWxlIjoiZW5fVVMifSwiaW50ZXJuYWwiOnsib3Jn"
    "X2lkIjoiNTY3OCJ9fX0KCg=="
}
AUTH_HEADER_SMART_MGMT_FALSE = {
    "X-RH-IDENTITY": "eyJpZGVudGl0eSI6eyJhY2NvdW50X251bWJlciI6"
    "IjEyMzQiLCJpbnRlcm5hbCI6eyJvcmdfaWQiOiAi"
    "NTY3OCJ9LCJ0eXBlIjogIlVzZXIiLCJ1c2VyIjp7"
    "ImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSIsImZp"
    "cnN0X25hbWUiOiJGaXJzdG5hbWUiLCJpc19hY3Rp"
    "dmUiOnRydWUsImlzX2ludGVybmFsIjp0cnVlLCJp"
    "c19vcmdfYWRtaW4iOmZhbHNlLCJsYXN0X25hbWUi"
    "OiJMYXN0bmFtZSIsImxvY2FsZSI6ImVuX1VTIiwi"
    "dXNlcm5hbWUiOiJ0ZXN0X3VzZXJuYW1lIn19LCJl"
    "bnRpdGxlbWVudHMiOnsic21hcnRfbWFuYWdlbWVu"
    "dCI6eyJpc19lbnRpdGxlZCI6IGZhbHNlfX19Cg=="
}

# this can't happen in real life, adding test anyway
AUTH_HEADER_NO_ACCT_BUT_HAS_ENTS = {
    "X-RH-IDENTITY": "eyJpZGVudGl0eSI6eyJpbnRlcm5hbCI6eyJvcmdf"
    "aWQiOiAiNTY3OCJ9LCJ0eXBlIjogIlVzZXIiLCJ1"
    "c2VyIjp7ImVtYWlsIjoidGVzdEBleGFtcGxlLmNv"
    "bSIsImZpcnN0X25hbWUiOiJGaXJzdG5hbWUiLCJp"
    "c19hY3RpdmUiOnRydWUsImlzX2ludGVybmFsIjp0"
    "cnVlLCJpc19vcmdfYWRtaW4iOmZhbHNlLCJsYXN0"
    "X25hbWUiOiJMYXN0bmFtZSIsImxvY2FsZSI6ImVu"
    "X1VTIiwidXNlcm5hbWUiOiJ0ZXN0X3VzZXJuYW1l"
    "In19LCJlbnRpdGxlbWVudHMiOnsic21hcnRfbWFu"
    "YWdlbWVudCI6eyJpc19lbnRpdGxlZCI6IHRydWV9"
    "fX0K"
}

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

AUTH_HEADER_NO_ACCT = {
    "X-RH-IDENTITY": "eyJpZGVudGl0eSI6eyJ0eXBlIjoiVXNlciIsInVzZXIiO"
    "nsidXNlcm5hbWUiOiJub251bWJlciIsImVtYWlsIjoibm"
    "9udW1iZXJAZXhhbXBsZS5jb20iLCJmaXJzdF9uYW1lIjo"
    "iTm8iLCJsYXN0X25hbWUiOiJOdW1iZXIiLCJpc19hY3Rp"
    "dmUiOnRydWUsImlzX29yZ19hZG1pbiI6ZmFsc2UsImlzX"
    "2ludGVybmFsIjp0cnVlLCJsb2NhbGUiOiJlbl9VUyJ9LC"
    "JpbnRlcm5hbCI6eyJvcmdfaWQiOiI5OTk5In19fQo="
}

"""
decoded AUTH_HEADER_SERVICE_ACCOUNT (newlines added for readablity):
{
  "entitlements": {},
  "identity": {
    "auth_type": "jwt-auth",
    "internal": {
      "auth_time": 500,
      "cross_access": false,
      "org_id": "9999"
    },
    "org_id": "9999",
    "service_account": {
      "client_id": "b69eaf9e-e6a6-4f9e-805e-02987daddfxd",
      "username": "service-account-b69eaf9e-e6a6-4f9e-805e-02987daddfxd"
    },
    "type": "ServiceAccount"
  }
}
"""

AUTH_HEADER_SERVICE_ACCOUNT = {
    "X-RH-IDENTITY": "ewogICJlbnRpdGxlbWVudHMiOiB7fSwKICAiaWRlbnRpdHki"
    "OiB7CiAgICAiYXV0aF90eXBlIjogImp3dC1hdXRoIiwKICAg"
    "ICJpbnRlcm5hbCI6IHsKICAgICAgImF1dGhfdGltZSI6IDUwM"
    "CwKICAgICAgImNyb3NzX2FjY2VzcyI6IGZhbHNlLAogICAgI"
    "CAib3JnX2lkIjogIjk5OTkiCiAgICB9LAogICAgIm9yZ19pZ"
    "CI6ICI5OTk5IiwKICAgICJzZXJ2aWNlX2FjY291bnQiOiB7C"
    "iAgICAgICJjbGllbnRfaWQiOiAiYjY5ZWFmOWUtZTZhNi00Z"
    "jllLTgwNWUtMDI5ODdkYWRkZnhkIiwKICAgICAgInVzZXJuYW"
    "1lIjogInNlcnZpY2UtYWNjb3VudC1iNjllYWY5ZS1lNmE2LT"
    "RmOWUtODA1ZS0wMjk4N2RhZGRmeGQiCiAgICB9LAogICAgIn"
    "R5cGUiOiAiU2VydmljZUFjY291bnQiCiAgfQp9"
}

FETCH_BASELINES_RESULT = [
    {
        "id": "ff35596c-f98e-11e9-aea9-98fa9b07d419",
        "account": "1212729",
        "display_name": "baseline1",
        "fact_count": 1,
        "created": "2019-10-17T16:23:34.238952Z",
        "updated": "2019-10-17T16:25:34.041645Z",
        "baseline_facts": [{"name": "fqdn", "value": "test.example1.com"}],
    },
    {
        "id": "89df6310-f98e-11e9-8a65-98fa9b07d419",
        "account": "1212729",
        "display_name": "baseline2",
        "fact_count": 1,
        "created": "2019-10-17T16:23:34.238952Z",
        "updated": "2019-10-17T16:25:34.041645Z",
        "baseline_facts": [{"name": "arch", "value": "golden"}],
    },
]

FETCH_SYSTEMS_WITH_PROFILES_CAPTURED_DATE_RESULT = [
    {
        "account": "9876543",
        "bios_uuid": "e380fd4a-28ae-11e9-974c-c85b761454fa",
        "created": "2019-01-31T13:00:00.100010Z",
        "display_name": None,
        "fqdn": "fake_system_99.example.com",
        "id": "fc1e497a-28ae-11e9-afd9-c85b761454fa",
        "insights_id": "01791a58-28af-11e9-9ab0-c85b761454fa",
        "ip_addresses": ["10.0.0.3", "2620:52:0:2598:5054:ff:fecd:ae15"],
        "mac_addresses": ["52:54:00:cd:ae:00", "00:00:00:00:00:00"],
        "rhel_machine_id": None,
        "satellite_id": None,
        "subscription_manager_id": "RHN Classic and Red Hat Subscription Management",
        "system_profile": {
            "captured_date": "2020-03-30T18:42:23+00:00",
            "salutation": "hello",
            "fqdn": "hostname_two",
            "stale_warning_timestamp": "2018-12-31T12:00:00.000000Z",
            "enabled_services": ["insights_client"],
            "installed_packages": [
                "0:bash-4.4.23-6.fc29.x86_64",
                "this isn't parsable",
                "no_epoch-1.0-1.fc99.8088",
            ],
            "cpu_flags": ["maryland"],
            "system_memory_bytes": 640,
            "yum_repos": [{"name": "yummy", "enabled": False}, {"no_name": "bleh"}],
            "network_interfaces": [
                {
                    "name": "eth99",
                    "mtu": 3,
                    "ipv4_addresses": ["8.7.6.5"],
                    "ipv6_addresses": ["00:00:02"],
                },
                {"no_name": "foo"},
            ],
            "system_profile_exists": True,
            "id": "fc1e497a-28ae-11e9-afd9-c85b761454fa",
        },
        "tags": [],
        "updated": "2019-01-31T14:00:00.500000Z",
    },
    {
        "account": "9876543",
        "bios_uuid": "e380fd4a-28ae-11e9-974c-c85b761454fb",
        "created": "2018-01-31T13:00:00.100010Z",
        "display_name": "hello",
        "fqdn": "fake_system_99.example.com",
        "id": "bbbbbbbb-28ae-11e9-afd9-c85b761454fa",
        "insights_id": "00000000-28af-11e9-9ab0-c85b761454fa",
        "ip_addresses": ["10.0.0.3", "2620:52:0:2598:5054:ff:fecd:ae15"],
        "mac_addresses": ["52:54:00:cd:ae:00", "00:00:00:00:00:00"],
        "rhel_machine_id": None,
        "satellite_id": None,
        "subscription_manager_id": "RHN Classic and Red Hat Subscription Management",
        "system_profile": {
            "captured_date": "2020-03-30T18:42:23+00:00",
            "salutation": "hi",
            "fqdn": "hostname_one",
            "system_profile_exists": True,
            "id": "bbbbbbbb-28ae-11e9-afd9-c85b761454fa",
            "stale_warning_timestamp": "2018-12-31T12:00:00.000000Z",
            "enabled_services": ["insights_client"],
            "installed_packages": [
                "0:bash-4.4.23-6.fc29.x86_64",
                "this isn't parsable",
                "no_epoch-1.0-1.fc99.8088",
            ],
            "network_interfaces": [
                {
                    "name": "eth99",
                    "mtu": 3,
                    "ipv4_addresses": ["8.7.6.5"],
                    "ipv6_addresses": ["00:00:01"],
                },
                {"no_name": "foo"},
            ],
        },
        "tags": [],
        "updated": "2018-01-31T14:00:00.500000Z",
    },
    {
        "account": "9876543",
        "bios_uuid": "e380fd4a-28ae-11e9-974c-c85b761454fb",
        "created": "2018-01-31T13:00:00.100010Z",
        "display_name": None,
        "fqdn": "hostname_one",
        "id": "bbbbbbbb-28ae-11e9-afd9-c85b761454fa",
        "insights_id": "00000000-28af-11e9-9ab0-c85b761454fa",
        "ip_addresses": ["10.0.0.3", "2620:52:0:2598:5054:ff:fecd:ae15"],
        "mac_addresses": ["52:54:00:cd:ae:00", "00:00:00:00:00:00"],
        "rhel_machine_id": None,
        "satellite_id": None,
        "subscription_manager_id": "RHN Classic and Red Hat Subscription Management",
        "system_profile": {
            "captured_date": "2020-03-30T18:42:23+00:00",
            "salutation": "hi",
            "fqdn": "hostname_one",
            "system_profile_exists": False,
            "id": "bbbbbbbb-28ae-11e9-afd9-c85b761454fa",
            "stale_warning_timestamp": "2018-12-31T12:00:00.000000Z",
            "enabled_services": ["insights_client"],
            "installed_packages": [
                "0:bash-4.4.23-6.fc29.x86_64",
                "this isn't parsable",
                "no_epoch-1.0-1.fc99.8088",
            ],
            "network_interfaces": [
                {
                    "name": "eth99",
                    "mtu": 3,
                    "ipv4_addresses": ["8.7.6.5"],
                    "ipv6_addresses": ["00:00:01"],
                },
                {"no_name": "foo"},
            ],
        },
        "tags": [],
        "updated": "2018-01-31T14:00:00.500000Z",
    },
]
FETCH_SYSTEMS_WITH_PROFILES_RESULT = [
    {
        "account": "9876543",
        "org_id": "5678",
        "bios_uuid": "e380fd4a-28ae-11e9-974c-c85b761454fa",
        "created": "2019-01-31T13:00:00.100010Z",
        "display_name": None,
        "fqdn": "fake_system_99.example.com",
        "id": "fc1e497a-28ae-11e9-afd9-c85b761454fa",
        "insights_id": "01791a58-28af-11e9-9ab0-c85b761454fa",
        "ip_addresses": ["10.0.0.3", "2620:52:0:2598:5054:ff:fecd:ae15"],
        "mac_addresses": ["52:54:00:cd:ae:00", "00:00:00:00:00:00"],
        "rhel_machine_id": None,
        "satellite_id": None,
        "subscription_manager_id": "RHN Classic and Red Hat Subscription Management",
        "system_profile": {
            "salutation": "hello",
            "fqdn": "hostname_two",
            "installed_packages": [
                "0:bash-4.4.23-6.fc29.x86_64",
                "this isn't parsable",
                "no_epoch-1.0-1.fc99.8088",
            ],
            "cpu_flags": ["maryland"],
            "system_memory_bytes": 640,
            "yum_repos": [{"name": "yummy", "enabled": False}, {"no_name": "bleh"}],
            "network_interfaces": [
                {
                    "name": "eth99",
                    "mtu": 3,
                    "ipv4_addresses": ["8.7.6.5"],
                    "ipv6_addresses": ["00:00:02"],
                },
                {"no_name": "foo"},
            ],
            "enabled_services": ["insights_client"],
            "system_profile_exists": True,
            "id": "fc1e497a-28ae-11e9-afd9-c85b761454fa",
            "stale_warning_timestamp": "2018-12-31T12:00:00.000000Z",
            "systemd": {"state": "running", "failed": 0, "jobs_queued": 0},
        },
        "tags": [],
        "updated": "2019-01-31T14:00:00.500000Z",
    },
    {
        "account": "9876543",
        "bios_uuid": "e380fd4a-28ae-11e9-974c-c85b761454fb",
        "created": "2018-01-31T13:00:00.100010Z",
        "display_name": "hello",
        "fqdn": "fake_system_99.example.com",
        "id": "bbbbbbbb-28ae-11e9-afd9-c85b761454fa",
        "insights_id": "00000000-28af-11e9-9ab0-c85b761454fa",
        "ip_addresses": ["10.0.0.3", "2620:52:0:2598:5054:ff:fecd:ae15"],
        "mac_addresses": ["52:54:00:cd:ae:00", "00:00:00:00:00:00"],
        "rhel_machine_id": None,
        "satellite_id": None,
        "subscription_manager_id": "RHN Classic and Red Hat Subscription Management",
        "system_profile": {
            "salutation": "hi",
            "fqdn": "hostname_one",
            "system_profile_exists": True,
            "id": "bbbbbbbb-28ae-11e9-afd9-c85b761454fa",
            "stale_warning_timestamp": "2018-12-31T12:00:00.000000Z",
            "enabled_services": ["insights_client"],
            "installed_packages": [
                "0:bash-4.4.23-6.fc29.x86_64",
                "this isn't parsable",
                "no_epoch-1.0-1.fc99.8088",
            ],
            "network_interfaces": [
                {
                    "name": "eth99",
                    "mtu": 3,
                    "ipv4_addresses": ["8.7.6.5"],
                    "ipv6_addresses": ["00:00:01"],
                },
                {"no_name": "foo"},
            ],
            "systemd": {"state": "running", "failed": 0, "jobs_queued": 0},
        },
        "tags": [],
        "updated": "2018-01-31T14:00:00.500000Z",
    },
    {
        "account": "9876543",
        "bios_uuid": "e380fd4a-28ae-11e9-974c-c85b761454fb",
        "created": "2018-01-31T13:00:00.100010Z",
        "display_name": None,
        "fqdn": "hostname_one",
        "id": "bbbbbbbb-28ae-11e9-afd9-c85b761454fa",
        "insights_id": "00000000-28af-11e9-9ab0-c85b761454fa",
        "ip_addresses": ["10.0.0.3", "2620:52:0:2598:5054:ff:fecd:ae15"],
        "mac_addresses": ["52:54:00:cd:ae:00", "00:00:00:00:00:00"],
        "rhel_machine_id": None,
        "satellite_id": None,
        "subscription_manager_id": "RHN Classic and Red Hat Subscription Management",
        "system_profile": {
            "salutation": "hi",
            "fqdn": "hostname_one",
            "system_profile_exists": False,
            "id": "bbbbbbbb-28ae-11e9-afd9-c85b761454fa",
            "stale_warning_timestamp": "2018-12-31T12:00:00.000000Z",
            "enabled_services": ["insights_client"],
            "installed_packages": [
                "0:bash-4.4.23-6.fc29.x86_64",
                "this isn't parsable",
                "no_epoch-1.0-1.fc99.8088",
            ],
            "network_interfaces": [
                {
                    "name": "eth99",
                    "mtu": 3,
                    "ipv4_addresses": ["8.7.6.5"],
                    "ipv6_addresses": ["00:00:01"],
                },
                {"no_name": "foo"},
            ],
            "systemd": {"state": "running", "failed": 0, "jobs_queued": 0},
        },
        "tags": [],
        "updated": "2018-01-31T14:00:00.500000Z",
    },
]

FETCH_SYSTEM_PROFILES_INV_SVC = """
{
  "count": 1,
  "total": 1,
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
"""

FETCH_SYSTEMS_WITH_PROFILES_SAME_FACTS_RESULT = [
    {
        "account": "9876543",
        "bios_uuid": "e380fd4a-28ae-11e9-974c-c85b761454fa",
        "created": "2019-01-31T13:00:00.100010Z",
        "display_name": None,
        "system_profile": {
            "salutation": "howdy",
            "system_profile_exists": True,
            "id": "fc1e497a-28ae-11e9-afd9-c85b761454fa",
            "stale_warning_timestamp": "2018-12-31T12:00:00.000000Z",
            "enabled_services": ["insights_client"],
            "installed_packages": [
                "0:bash-4.4.23-6.fc29.x86_64",
                "this isn't parsable",
                "no_epoch-1.0-1.fc99.8088",
            ],
        },
        "fqdn": "fake_system_99.example.com",
        "id": "fc1e497a-28ae-11e9-afd9-c85b761454fa",
        "insights_id": "01791a58-28af-11e9-9ab0-c85b761454fa",
        "ip_addresses": ["10.0.0.3", "2620:52:0:2598:5054:ff:fecd:ae15"],
        "mac_addresses": ["52:54:00:cd:ae:00", "00:00:00:00:00:00"],
        "rhel_machine_id": None,
        "satellite_id": None,
        "subscription_manager_id": "RHN Classic and Red Hat Subscription Management",
        "tags": [],
        "updated": "2019-01-31T14:00:00.500000Z",
    },
    {
        "account": "9876543",
        "bios_uuid": "e380fd4a-28ae-11e9-974c-c85b761454fb",
        "created": "2018-01-31T13:00:00.100010Z",
        "display_name": None,
        "system_profile": {
            "salutation": "howdy",
            "system_profile_exists": True,
            "id": "bbbbbbbb-28ae-11e9-afd9-c85b761454fa",
            "stale_warning_timestamp": "2018-12-31T12:00:00.000000Z",
            "enabled_services": ["insights_client"],
            "installed_packages": [
                "0:bash-4.4.23-6.fc29.x86_64",
                "this isn't parsable",
                "no_epoch-1.0-1.fc99.8088",
            ],
        },
        "fqdn": "fake_system_99.example.com",
        "id": "bbbbbbbb-28ae-11e9-afd9-c85b761454fa",
        "insights_id": "00000000-28af-11e9-9ab0-c85b761454fa",
        "ip_addresses": ["10.0.0.3", "2620:52:0:2598:5054:ff:fecd:ae15"],
        "mac_addresses": ["52:54:00:cd:ae:00", "00:00:00:00:00:00"],
        "rhel_machine_id": None,
        "satellite_id": None,
        "subscription_manager_id": "RHN Classic and Red Hat Subscription Management",
        "tags": [],
        "updated": "2018-01-31T14:00:00.500000Z",
    },
]

FETCH_SYSTEM_TAGS = """
{
  "total": 1,
  "count": 1,
  "page": 1,
  "per_page": 50,
  "results": {
    "ec67f65c-2bc8-4ce8-82e2-6a27cada8d31": [
      {
        "namespace": "insights-client",
        "key": "group",
        "value": "XmygroupX"
      }
    ]
  }
}
"""
FETCH_SYSTEMS_INV_SVC = """
    {
      "count": 2,
      "total": 2,
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
      "updated": "2018-12-31T12:00:00.000000Z",
      "stale_warning_timestamp": "2018-12-31T12:00:00.000000Z"
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
      "updated": "2018-12-31T12:00:00.000000Z",
      "stale_warning_timestamp": "2018-12-31T12:00:00.000000Z"
    }
    ]}"""

SYSTEM_NOT_FOUND_TEMPLATE = """
    {
      "count": 0,
      "page": 1,
      "per_page": 50,
      "results": [],
      "total": 0
    }
    """
