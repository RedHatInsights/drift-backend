import unittest

import mock

from system_baseline import app

from . import fixtures


class GlobalHelpersApiTest(unittest.TestCase):
    def setUp(self):
        self.mock_logger = mock.Mock()
        self.rbac_patcher = mock.patch(
            "system_baseline.views.v1.view_helpers.ensure_has_permission"
        )
        patched_rbac = self.rbac_patcher.start()
        patched_rbac.return_value = None  # validate all RBAC requests
        self.addCleanup(self.stopPatches)
        test_connexion_app = app.create_app()
        test_flask_app = test_connexion_app.app
        self.client = test_flask_app.test_client()

    def stopPatches(self):
        self.rbac_patcher.stop()


class GlobalHelpersEnsureOrgIdTest(GlobalHelpersApiTest):
    @mock.patch("kerlescan.view_helpers.ensure_org_id", return_value=None)
    def test_calls_kerlescan_view_helpers_ensure_org_id_is_called(
        self, mocked_kerlescan_ensure_method
    ):
        response = self.client.get("api/system-baseline/v1/baselines", headers=fixtures.AUTH_HEADER)
        mocked_kerlescan_ensure_method.assert_called_once()
        self.assertEqual(response.status_code, 200)
