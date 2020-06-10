from historical_system_profiles import app

import unittest
import mock


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.rbac_patcher = mock.patch(
            "historical_system_profiles.views.v1.view_helpers.ensure_has_role"
        )
        self.fetch_systems_patcher = mock.patch(
            "historical_system_profiles.views.v1.fetch_systems_with_profiles"
        )
        patched_rbac = self.rbac_patcher.start()
        patched_rbac.return_value = None  # validate all RBAC requests
        self.patched_fetch_systems = self.fetch_systems_patcher.start()
        self.patched_fetch_systems.return_value = []

        self.addCleanup(self.stopPatches)

        test_connexion_app = app.create_app()
        self.test_flask_app = test_connexion_app.app
        self.client = self.test_flask_app.test_client()

    def addInventoryRecord(self, inventory_id, display_name):
        self.patched_fetch_systems.return_value.append(
            {"id": inventory_id, "display_name": display_name}
        )

    def stopPatches(self):
        self.rbac_patcher.stop()
        self.fetch_systems_patcher.stop()
