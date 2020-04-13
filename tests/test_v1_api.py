import json

from historical_system_profiles import app

import unittest
import mock
from mock import patch
from . import fixtures


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.rbac_patcher = patch(
            "historical_system_profiles.views.v1.view_helpers.ensure_has_role"
        )
        patched_rbac = self.rbac_patcher.start()
        patched_rbac.return_value = None  # validate all RBAC requests
        self.addCleanup(self.stopPatches)
        test_connexion_app = app.create_app()
        test_flask_app = test_connexion_app.app
        self.client = test_flask_app.test_client()
        self.rbac_patcher = mock.patch(
            "historical_system_profiles.views.v1.view_helpers.ensure_has_role"
        )
        patched_rbac = self.rbac_patcher.start()
        patched_rbac.return_value = None  # validate all RBAC requests
        self.addCleanup(self.stopPatches)

    def stopPatches(self):
        self.rbac_patcher.stop()


class HSPApiTests(ApiTest):
    def test_status_bad_uuid(self):
        response = self.client.get(
            "/api/historical-system-profiles/v1/profiles/1",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("too short", json.loads(response.data)["detail"])
