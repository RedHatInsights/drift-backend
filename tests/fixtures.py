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

FETCH_SYSTEMS_RESULT = [
    {
      "account": "9876543",
      "bios_uuid": "e380fd4a-28ae-11e9-974c-c85b761454fa",
      "created": "2019-01-31T13:00:00.100010Z",
      "display_name": None,
      "facts": [],
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
    }]

SYSTEMS_TEMPLATE = '''
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
      "facts": [
        {
          "facts": {},
          "namespace": "string"
        }
      ],
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
      "facts": [
        {
          "facts": {},
          "namespace": "string"
        }
      ],
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
