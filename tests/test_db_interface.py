import json

from historical_system_profiles import db_interface

from . import fixtures
from . import utils


class DBInterfaceTests(utils.ApiTest):
    def test_save_model(self):
        # confirm there are zero records to start
        response = self.client.get(
            "/api/historical-system-profiles/v1/systems/29dbe6ce-897f-11ea-8f75-98fa9b07d419",
            headers=fixtures.AUTH_HEADER,
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)

        # add one record, confirm count
        with self.test_flask_app.app_context():
            db_interface.create_profile(
                "29dbe6ce-897f-11ea-8f75-98fa9b07d419", {}, "1234"
            )

        response = self.client.get(
            "/api/historical-system-profiles/v1/systems/29dbe6ce-897f-11ea-8f75-98fa9b07d419",
            headers=fixtures.AUTH_HEADER,
        )
        data = json.loads(response.data)
        self.assertEquals(1, len(data["data"][0]["profiles"]))

        # delete all records, confirm count
        with self.test_flask_app.app_context():
            db_interface.delete_hsps_by_inventory_id(
                "29dbe6ce-897f-11ea-8f75-98fa9b07d419"
            )

        response = self.client.get(
            "/api/historical-system-profiles/v1/systems/29dbe6ce-897f-11ea-8f75-98fa9b07d419",
            headers=fixtures.AUTH_HEADER,
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
