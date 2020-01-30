import unittest
import mock
from kerlescan.exceptions import HTTPError
from mock import MagicMock as mm

from kerlescan import view_helpers


class RBACTests(unittest.TestCase):
    @mock.patch("kerlescan.view_helpers.get_key_from_headers")
    @mock.patch("kerlescan.view_helpers.get_roles")
    def test_has_role(self, mock_get_roles, mock_get_key):
        mock_get_key.return_value = "fake key"
        mock_get_roles.return_value = ["myrole:*:*"]
        mock_request = mm()
        mock_request.path = "/some/path"
        view_helpers.ensure_has_role(
            role="myrole:*:*",
            application="app",
            app_name="app-name",
            request=mock_request,
            logger=mm(),
            request_metric=mm(),
            exception_metric=mm(),
        )

    @mock.patch("kerlescan.view_helpers.get_key_from_headers")
    @mock.patch("kerlescan.view_helpers.get_roles")
    def test_missing_role(self, mock_get_roles, mock_get_key):
        mock_get_key.return_value = "fake key"
        mock_get_roles.return_value = ["myrole:*:*"]
        mock_request = mm()
        mock_request.path = "/some/path"
        with self.assertRaises(HTTPError):
            view_helpers.ensure_has_role(
                role="r2:*:*",
                application="app",
                app_name="app-name",
                request=mock_request,
                logger=mm(),
                request_metric=mm(),
                exception_metric=mm(),
            )
