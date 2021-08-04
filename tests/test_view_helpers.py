IDENTITY_ASSOCIATE_JSON = """{
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


def test_check_request_from_drift_service():
    """
    TODO: write a specific test for this method.
    """
    assert 1 == 1
