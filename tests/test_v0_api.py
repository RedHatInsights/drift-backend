import json

from historical_system_profiles import app

import unittest
import mock
from . import fixtures


class ApiTests(unittest.TestCase):
    def setUp(self):
        test_connexion_app = app.create_app()
        test_flask_app = test_connexion_app.app
        self.client = test_flask_app.test_client()
        self.rbac_patcher = mock.patch(
            "historical_system_profiles.views.v0.view_helpers.ensure_has_role"
        )
        patched_rbac = self.rbac_patcher.start()
        patched_rbac.return_value = None  # validate all RBAC requests
        self.addCleanup(self.stopPatches)

    def stopPatches(self):
        self.rbac_patcher.stop()

    def test_status_bad_uuid(self):
        response = self.client.get(
            "/api/historical-system-profiles/v0/profiles/1",
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("too short", json.loads(response.data)["detail"])

    def test_valid_post(self):
        response = self.client.post(
            "/api/historical-system-profiles/v0/profiles",
            json=fixtures.HISTORICAL_PROFILE,
            headers=fixtures.AUTH_HEADER,
        )
        self.assertEqual(response.status_code, 200)
        profile = json.loads(response.data)
        self.assertEqual(profile["account"], "1234")
        self.assertEqual(profile["display_name"], "test-system")
        self.assertEqual(profile["id"], profile["system_profile"]["id"])
        self.assertEqual(
            profile["inventory_id"], "cd54d888-4ccb-11ea-8627-98fa9b07d419"
        )
        response = self.client.get(
            "/api/historical-system-profiles/v0/profiles/%s" % profile["id"],
            headers=fixtures.AUTH_HEADER,
        )
        fetched_profile = json.loads(response.data)["data"][0]
        self.assertEqual(profile, fetched_profile)
