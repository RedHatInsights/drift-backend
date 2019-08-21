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
    "entitlements": {
        "smart_management": {
            "is_entitled": true
        }
    }
}
"""

AUTH_HEADER = {
    "X-RH-IDENTITY": "eyJpZGVudGl0eSI6eyJhY2NvdW50X251bWJlciI6"
    "IjEyMzQiLCJpbnRlcm5hbCI6eyJvcmdfaWQiOiI1"
    "Njc4In0sInR5cGUiOiJVc2VyIiwidXNlciI6eyJl"
    "bWFpbCI6InRlc3RAZXhhbXBsZS5jb20iLCJmaXJz"
    "dF9uYW1lIjoiRmlyc3RuYW1lIiwiaXNfYWN0aXZl"
    "Ijp0cnVlLCJpc19pbnRlcm5hbCI6dHJ1ZSwiaXNf"
    "b3JnX2FkbWluIjpmYWxzZSwibGFzdF9uYW1lIjoi"
    "TGFzdG5hbWUiLCJsb2NhbGUiOiJlbl9VUyIsInVz"
    "ZXJuYW1lIjoidGVzdF91c2VybmFtZSJ9fSwiZW50"
    "aXRsZW1lbnRzIjogeyJzbWFydF9tYW5hZ2VtZW50"
    "IjogeyJpc19lbnRpdGxlZCI6IHRydWUgfX19Cg=="
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

BASELINE_ONE_LOAD = {
    "baseline_facts": [
        {"name": "arch", "value": "x86_64"},
        {"name": "phony.arch.fact", "value": "some value"},
    ],
    "display_name": "arch baseline",
}
BASELINE_TWO_LOAD = {
    "baseline_facts": [
        {"name": "memory", "value": "64GB"},
        {"name": "cpu_sockets", "value": "16"},
    ],
    "display_name": "cpu + mem baseline",
}
BASELINE_THREE_LOAD = {
    "baseline_facts": [
        {"name": "nested", "values": [{"name": "cpu_sockets", "value": "16"}]}
    ],
    "display_name": "cpu + mem baseline",
}

BASELINE_PARTIAL_ONE = {"baseline_facts": [{"name": "hello", "value": "world"}]}
BASELINE_PARTIAL_TWO = {
    "display_name": "ABCDE",
    "baseline_facts": [
        {
            "name": "hello",
            "values": [
                {"name": "nested_one", "value": "one"},
                {"name": "nested_two", "value": "two"},
            ],
        }
    ],
}
CREATE_FROM_INVENTORY = {
    "display_name": "created_from_inventory",
    "inventory_uuid": "df925152-c45d-11e9-a1f0-c85b761454fa",
}

SYSTEM_WITH_PROFILE = {
    "account": "9876543",
    "bios_uuid": "e380fd4a-28ae-11e9-974c-c85b761454fb",
    "created": "2018-01-31T13:00:00.100010Z",
    "display_name": None,
    "fqdn": None,
    "id": "bbbbbbbb-28ae-11e9-afd9-c85b761454fa",
    "insights_id": "00000000-28af-11e9-9ab0-c85b761454fa",
    "ip_addresses": ["10.0.0.3", "2620:52:0:2598:5054:ff:fecd:ae15"],
    "mac_addresses": ["52:54:00:cd:ae:00", "00:00:00:00:00:00"],
    "rhel_machine_id": None,
    "satellite_id": None,
    "subscription_manager_id": "RHN Classic and Red Hat Subscription Management",
    "system_profile": {
        "salutation": "hi",
        "system_profile_exists": False,
        "installed_packages": [
            "openssl-1.1.1c-2.fc30.x86_64",
            "python2-libs-2.7.16-2.fc30.x86_64",
        ],
        "id": "bbbbbbbb-28ae-11e9-afd9-c85b761454fa",
    },
    "tags": [],
    "updated": "2018-01-31T14:00:00.500000Z",
}
