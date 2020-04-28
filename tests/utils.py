from historical_system_profiles import app

import unittest
import mock


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.rbac_patcher = mock.patch(
            "historical_system_profiles.views.v1.view_helpers.ensure_has_role"
        )
        patched_rbac = self.rbac_patcher.start()
        patched_rbac.return_value = None  # validate all RBAC requests

        self.addCleanup(self.stopPatches)

        test_connexion_app = app.create_app()
        self.test_flask_app = test_connexion_app.app
        self.client = self.test_flask_app.test_client()

    def stopPatches(self):
        self.rbac_patcher.stop()
