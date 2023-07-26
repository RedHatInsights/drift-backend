import unittest

import mock

from mock import MagicMock as mm

from kerlescan import view_helpers
from kerlescan.exceptions import HTTPError


class RBACTests(unittest.TestCase):
    @mock.patch("kerlescan.view_helpers.get_key_from_headers")
    @mock.patch("kerlescan.view_helpers.get_perms")
    def test_has_perm(self, mock_get_perms, mock_get_key):
        mock_get_key.return_value = (
            "eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAiMTIxMjcyOSIsICJ0eXBlIjogI"
            "lN5c3RlbSIsICJhdXRoX3R5cGUiOiAiY2xhc3NpYy1wcm94eSIsICJzeXN0ZW0iOiB7Im"
            "NuIjogIjIyY2Q4ZTM5LTEzYmItNGQwMi04MzE2LTg0Yjg1MGRjNTEzNiIsICJjZXJ0X3R"
            "5cGUiOiAic3lzdGVtIn0sICJpbnRlcm5hbCI6IHsib3JnX2lkIjogIjAwMDAwMSJ9fX0K"
        )
        mock_get_perms.return_value = ["myperm:*:*"]
        mock_request = mm()
        mock_request.path = "/some/path"
        self.assertIsNone(
            view_helpers.ensure_has_permission(
                permissions=[["myperm:*:*"]],
                application="app",
                app_name="app-name",
                request=mock_request,
                logger=mm(),
                request_metric=mm(),
                exception_metric=mm(),
            )
        )

    @mock.patch("kerlescan.view_helpers.get_key_from_headers")
    @mock.patch("kerlescan.view_helpers.get_perms")
    def test_missing_perm(self, mock_get_perms, mock_get_key):
        mock_get_key.return_value = (
            "eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAiMTIxMjcyOSIsICJ0eXBlIjogI"
            "lN5c3RlbSIsICJhdXRoX3R5cGUiOiAiY2xhc3NpYy1wcm94eSIsICJzeXN0ZW0iOiB7Im"
            "NuIjogIjIyY2Q4ZTM5LTEzYmItNGQwMi04MzE2LTg0Yjg1MGRjNTEzNiIsICJjZXJ0X3R"
            "5cGUiOiAic3lzdGVtIn0sICJpbnRlcm5hbCI6IHsib3JnX2lkIjogIjAwMDAwMSJ9fX0K"
        )
        mock_get_perms.return_value = ["myperm:*:*"]
        mock_request = mm()
        mock_request.path = "/some/path"
        with self.assertRaises(HTTPError):
            view_helpers.ensure_has_permission(
                permissions=["r2:*:*"],
                application="app",
                app_name="app-name",
                request=mock_request,
                logger=mm(),
                request_metric=mm(),
                exception_metric=mm(),
            )
