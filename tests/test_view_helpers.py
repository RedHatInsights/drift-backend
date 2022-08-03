import base64

import mock

from kerlescan import view_helpers


IDENTITY_NO_ACCOUNT_NUMBER_ASSOCIATE_JSON = """{
  "identity": {
    "associate": {
      "Role": [
        "some-ldap-group",
        "another-ldap-group"
      ],
      "email": "jschmoe@redhat.com",
      "givenName": "Joseph",
      "rhatUUID": "01234567-89ab-cdef-0123-456789abcdef",
      "surname": "Schmoe"
    },
    "auth_type": "saml-auth",
    "type": "Associate"
  }
}"""

IDENTITY_ACCOUNT_NUMBER_ASSOCIATE_JSON = """{
  "identity": {
    "account_number": "1234",
    "associate": {
      "Role": [
        "some-ldap-group",
        "another-ldap-group"
      ],
      "email": "jschmoe@redhat.com",
      "givenName": "Joseph",
      "rhatUUID": "01234567-89ab-cdef-0123-456789abcdef",
      "surname": "Schmoe"
    },
    "auth_type": "saml-auth",
    "type": "Associate"
  }
}"""

IDENTITY_NO_ORG_ID_ASSOCIATE_JSON = """{
  "identity": {
    "associate": {
      "Role": [
        "some-ldap-group",
        "another-ldap-group"
      ],
      "email": "jschmoe@redhat.com",
      "givenName": "Joseph",
      "rhatUUID": "01234567-89ab-cdef-0123-456789abcdef",
      "surname": "Schmoe"
    },
    "auth_type": "saml-auth",
    "type": "Associate"
  }
}"""

IDENTITY_ORG_ID_ASSOCIATE_JSON = """{
  "identity": {
    "org_id": "5678",
    "associate": {
      "Role": [
        "some-ldap-group",
        "another-ldap-group"
      ],
      "email": "jschmoe@redhat.com",
      "givenName": "Joseph",
      "rhatUUID": "01234567-89ab-cdef-0123-456789abcdef",
      "surname": "Schmoe"
    },
    "auth_type": "saml-auth",
    "type": "Associate"
  }
}"""


def test_check_request_from_drift_service():
    """
    TODO: write a specific test for this method.
    """
    assert 1 == 1


@mock.patch("kerlescan.view_helpers.get_key_from_headers")
def test_get_account_number_not_present(mocked_get_key_from_headers):
    mocked_get_key_from_headers.return_value = base64.b64encode(
        bytes(IDENTITY_NO_ACCOUNT_NUMBER_ASSOCIATE_JSON, "utf-8")
    )
    mocked_request = mock.Mock()
    result = view_helpers.get_account_number(mocked_request)
    assert result is None


@mock.patch("kerlescan.view_helpers.get_key_from_headers")
def test_get_account_number_is_present(mocked_get_key_from_headers):
    mocked_get_key_from_headers.return_value = base64.b64encode(
        bytes(IDENTITY_ACCOUNT_NUMBER_ASSOCIATE_JSON, "utf-8")
    )
    mocked_request = mock.Mock()
    result = view_helpers.get_account_number(mocked_request)
    assert result == "1234"


@mock.patch("kerlescan.view_helpers.get_key_from_headers")
def test_get_org_id_not_present(mocked_get_key_from_headers):
    mocked_get_key_from_headers.return_value = base64.b64encode(
        bytes(IDENTITY_NO_ORG_ID_ASSOCIATE_JSON, "utf-8")
    )
    mocked_request = mock.Mock()
    result = view_helpers.get_org_id(mocked_request)
    assert result is None


@mock.patch("kerlescan.view_helpers.get_key_from_headers")
def test_get_org_id_is_present(mocked_get_key_from_headers):
    mocked_get_key_from_headers.return_value = base64.b64encode(
        bytes(IDENTITY_ORG_ID_ASSOCIATE_JSON, "utf-8")
    )
    mocked_request = mock.Mock()
    result = view_helpers.get_org_id(mocked_request)
    assert result == "5678"
