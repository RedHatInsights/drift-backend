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
    },
    "entitlements": {
        "smart_management": {
            "is_entitled": true
        }
    }
}
"""

AUTH_HEADER = {
    "X-RH-IDENTITY": (
        "eyJpZGVudGl0eSI6eyJhY2NvdW50X251bWJlciI6"
        "IjEyMzQiLCJvcmdfaWQiOiI1Njc4IiwiaW50ZXJu"
        "YWwiOnsib3JnX2lkIjoiNTY3OCJ9LCJ0eXBlIjoi"
        "VXNlciIsInVzZXIiOnsiZW1haWwiOiJ0ZXN0QGV4"
        "YW1wbGUuY29tIiwiZmlyc3RfbmFtZSI6IkZpcnN0"
        "bmFtZSIsImlzX2FjdGl2ZSI6dHJ1ZSwiaXNfaW50"
        "ZXJuYWwiOnRydWUsImlzX29yZ19hZG1pbiI6ZmFs"
        "c2UsImxhc3RfbmFtZSI6Ikxhc3RuYW1lIiwibG9j"
        "YWxlIjoiZW5fVVMiLCJ1c2VybmFtZSI6InRlc3Rf"
        "dXNlcm5hbWUifX0sImVudGl0bGVtZW50cyI6eyJz"
        "bWFydF9tYW5hZ2VtZW50Ijp7ImlzX2VudGl0bGVk"
        "Ijp0cnVlfX19Cg=="
    )
}


HISTORICAL_PROFILE = {
    "inventory_id": "cd54d888-4ccb-11ea-8627-98fa9b07d419",
    "profile": {
        "salutation": "hi",
        "display_name": "test-system",
        "system_profile_exists": True,
        "installed_packages": [
            "openssl-1.1.1c-2.fc30.x86_64",
            "python2-libs-2.7.16-2.fc30.x86_64",
        ],
        "id": "bbbbbbbb-28ae-11e9-afd9-c85b761454fa",
    },
}

FETCH_SYSTEMS_WITH_PROFILES_RESULT = (
    {
        "account": "9876543",
        "bios_uuid": "e380fd4a-28ae-11e9-974c-c85b761454fb",
        "created": "2018-01-31T13:00:00.100010Z",
        "display_name": "tartuffe",
        "fqdn": "hostname_one",
        "id": "cd54d888-4ccb-11ea-8627-98fa9b07d419",
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
    },
)

EVENT_MESSAGE_VALUE_WITH_ACCOUNT = {
    "host": {
        "account": "5432",
        "org_id": "5678",
        "display_name": "9c033db1729c",
        "id": "6388350e-b18d-11ea-ad7f-98fa9b07d419",
        "insights_id": "cd9b8cda-607c-4359-9425-b6a0299a26a2",
        "fqdn": "my-fqdn",
        "updated": "2021-04-21T15:03:44.887439+00:00",
        "tags": [],
        "system_profile": {"captured_date": "2020-06-18T17:11:05+00:00"},
    },
    "platform_metadata": {"request_id": "123456"},
    "type": "created",
}

EVENT_MESSAGE_VALUE_WITHOUT_ACCOUNT = {
    "host": {
        "org_id": "5678",
        "display_name": "9c033db1729c",
        "id": "6388350e-b18d-11ea-ad7f-98fa9b07d419",
        "insights_id": "cd9b8cda-607c-4359-9425-b6a0299a26a2",
        "fqdn": "my-fqdn",
        "updated": "2021-04-21T15:03:44.887439+00:00",
        "tags": [],
        "system_profile": {"captured_date": "2020-06-18T17:11:05+00:00"},
    },
    "platform_metadata": {"request_id": "123456"},
    "type": "created",
}
